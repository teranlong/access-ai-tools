"""Shared Win32 message-passing helpers implementing the handoff methodology.

Technique (from handoff, NOT from the solution package):
  - COM/DAO stages: launch Access, open form, navigate.
  - Win32 PostMessage(WM_CHAR) acts: type into the focused OKttbx control.
  - COM/DAO verifies: query the underlying table.

Nothing here imports access_eval_suite. Implemented from the handoff alone.
"""
from __future__ import annotations

import ctypes
import threading
import time
from ctypes import wintypes

import win32com.client
import win32con
import win32gui

# --- Win32 constants (from handoff) ---
WM_CHAR = 0x0102
EM_SETSEL = 0x00B1
WM_CLEAR = 0x0303
BM_CLICK = 0x00F5
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_SPACE = 0x20

# --- Access COM enum constants ---
AC_FORM = 2            # acForm
AC_SAVE_NO = 2         # acSaveNo
AC_NEW_REC = 5         # acNewRec
AC_QUIT_SAVE_NONE = 2  # acQuitSaveNone
# NOTE: The handoff states "acCmdSaveRecord (=21)". That is WRONG: RunCommand(21)
# is acCmdSaveAs, which opens a modal "Save As" dialog and blocks COM. The correct
# acCmdSaveRecord value is 97. Verified empirically (21 hung on a Save As dialog).
AC_CMD_SAVE_RECORD = 97  # acCmdSaveRecord (handoff's "21" is acCmdSaveAs -- a bug)

_user32 = ctypes.windll.user32
_user32.GetWindowThreadProcessId.restype = wintypes.DWORD


def _access_ui_thread_id(access) -> int:
    """Thread id that owns the Access UI (and its focused control HWND)."""
    raw = access.hWndAccessApp
    if callable(raw):
        raw = raw()
    hwnd = int(raw)
    pid = wintypes.DWORD(0)
    tid = _user32.GetWindowThreadProcessId(wintypes.HWND(hwnd), ctypes.byref(pid))
    return int(tid)


def type_into_field(access, field_name: str, value: str, char_delay: float = 0.015) -> None:
    """Focus `field_name` via COM, clear it, and post each character via WM_CHAR.

    Does NOT commit -- caller must move focus afterward (focus-out commit).
    """
    access.DoCmd.GoToControl(field_name)
    time.sleep(0.1)

    my_tid = ctypes.windll.kernel32.GetCurrentThreadId()
    access_tid = _access_ui_thread_id(access)
    _user32.AttachThreadInput(my_tid, access_tid, True)
    try:
        hwnd = win32gui.GetFocus()
        if not hwnd:
            raise RuntimeError(f"GetFocus() returned 0 for field {field_name!r}")
        cls = win32gui.GetClassName(hwnd)
        # Select-all + clear (NOT Ctrl+A, which leaves a stray leading char).
        win32gui.SendMessage(hwnd, EM_SETSEL, 0, -1)
        win32gui.SendMessage(hwnd, WM_CLEAR, 0, 0)
        for ch in value:
            win32gui.PostMessage(hwnd, WM_CHAR, ord(ch), 0)
            time.sleep(char_delay)
        return cls
    finally:
        _user32.AttachThreadInput(my_tid, access_tid, False)


def read_focused_value(access, field_name: str) -> str:
    """Read a control's live text via GetWindowText (handoff: OKttbx returns value)."""
    access.DoCmd.GoToControl(field_name)
    time.sleep(0.05)
    my_tid = ctypes.windll.kernel32.GetCurrentThreadId()
    access_tid = _access_ui_thread_id(access)
    _user32.AttachThreadInput(my_tid, access_tid, True)
    try:
        hwnd = win32gui.GetFocus()
        return win32gui.GetWindowText(hwnd) if hwnd else ""
    finally:
        _user32.AttachThreadInput(my_tid, access_tid, False)


def commit_focus_out(access, other_field: str) -> None:
    """Move focus to another control so Access writes the bound field."""
    access.DoCmd.GoToControl(other_field)
    time.sleep(0.1)


def layered_save(access, form_name: str) -> str:
    """Save the record using the handoff's fallback ladder.

    Ctrl+S alone is unreliable, so: BM_CLICK on Submit -> COM RunCommand(21)
    -> COM Dirty=False. Returns a string describing which layer succeeded.
    """
    outcome = []

    # Layer 1: PostMessage(BM_CLICK) on the Submit button HWND.
    try:
        access.DoCmd.GoToControl("btnSubmit")
        time.sleep(0.1)
        my_tid = ctypes.windll.kernel32.GetCurrentThreadId()
        access_tid = _access_ui_thread_id(access)
        _user32.AttachThreadInput(my_tid, access_tid, True)
        try:
            hwnd = win32gui.GetFocus()
            if hwnd:
                win32gui.PostMessage(hwnd, BM_CLICK, 0, 0)
                outcome.append("BM_CLICK-posted")
        finally:
            _user32.AttachThreadInput(my_tid, access_tid, False)
        time.sleep(0.3)
    except Exception as exc:  # noqa: BLE001
        outcome.append(f"BM_CLICK-failed({exc})")

    # Layer 2: COM DoCmd.RunCommand(acCmdSaveRecord).
    try:
        access.DoCmd.RunCommand(AC_CMD_SAVE_RECORD)
        outcome.append("RunCommand(acCmdSaveRecord=97)-ok")
    except Exception as exc:  # noqa: BLE001
        outcome.append(f"RunCommand(21)-failed({exc})")

    # Layer 3: final fallback -- set the form's Dirty=False via COM.
    try:
        frm = access.Forms(form_name)
        if frm.Dirty:
            frm.Dirty = False
            outcome.append("Dirty=False-applied")
        else:
            outcome.append("already-clean")
    except Exception as exc:  # noqa: BLE001
        outcome.append(f"Dirty=False-failed({exc})")

    return " | ".join(outcome)


def open_access(db_path: str, visible: bool = True):
    access = win32com.client.Dispatch("Access.Application")
    try:
        access.Visible = visible
    except Exception:  # noqa: BLE001
        pass
    access.OpenCurrentDatabase(str(db_path))
    time.sleep(0.5)
    return access


def close_access(access) -> None:
    try:
        access.CloseCurrentDatabase()
    except Exception:  # noqa: BLE001
        pass
    try:
        access.Quit(AC_QUIT_SAVE_NONE)
    except Exception:  # noqa: BLE001
        pass


class DialogWatchdog:
    """Safety net: background thread that dismisses stray modal dialogs.

    A modal Win32 dialog (#32770) owned by Access blocks all COM calls
    synchronously, so a try/except cannot recover from it. This watchdog
    posts WM_CLOSE (i.e. Cancel/Escape) to any such dialog so an unexpected
    modal never permanently hangs a test run. Titles seen are printed.
    """

    def __init__(self, poll: float = 0.5):
        self._poll = poll
        self._stop = threading.Event()
        self._thread = None
        self.dismissed: list[str] = []

    def _scan(self):
        def cb(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return True
            cls = win32gui.GetClassName(hwnd)
            if cls == "#32770":  # standard dialog box class
                title = win32gui.GetWindowText(hwnd)
                self.dismissed.append(title)
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            return True

        try:
            win32gui.EnumWindows(cb, None)
        except Exception:  # noqa: BLE001
            pass

    def _run(self):
        while not self._stop.is_set():
            self._scan()
            self._stop.wait(self._poll)

    def __enter__(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        return False


def query_contacts(db_path: str, contact_value: str):
    """COM/DAO verification query -- returns list of dict rows matching value."""
    engine = win32com.client.Dispatch("DAO.DBEngine.120")
    db = engine.OpenDatabase(str(db_path))
    try:
        safe = contact_value.replace("'", "''")
        sql = (
            "SELECT ContactID, CompanyID, ContactType, ContactValue, IsPreferred "
            f"FROM Contacts WHERE ContactValue = '{safe}'"
        )
        rs = db.OpenRecordset(sql)
        rows = []
        while not rs.EOF:
            rows.append(
                {
                    "ContactID": int(rs.Fields("ContactID").Value),
                    "CompanyID": int(rs.Fields("CompanyID").Value),
                    "ContactType": str(rs.Fields("ContactType").Value),
                    "ContactValue": str(rs.Fields("ContactValue").Value),
                    "IsPreferred": bool(rs.Fields("IsPreferred").Value),
                }
            )
            rs.MoveNext()
        rs.Close()
        return rows
    finally:
        db.Close()
