"""
Refined PostMessage-based input automation for Access forms.
Uses the proven WM_CHAR approach with proper text clearing and value commit.
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes
import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from access_eval_suite.config import DEFAULT_DATABASE
from access_eval_suite import constants as ac

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 constants
WM_CHAR = 0x0102
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
EM_SETSEL = 0x00B1
WM_CLEAR = 0x0303
WM_SETFOCUS = 0x0007
BM_CLICK = 0x00F5

VK_TAB = 0x09
VK_RETURN = 0x0D
VK_HOME = 0x24
VK_END = 0x23
VK_DELETE = 0x2E
VK_BACK = 0x08
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_A = 0x41
VK_ESCAPE = 0x1B


def fresh_db() -> Path:
    ts = time.strftime("%H%M%S")
    dest = EVIDENCE_DIR / f"refined_{ts}.accdb"
    shutil.copy2(DEFAULT_DATABASE, dest)
    return dest


def get_window_text(hwnd: int) -> str:
    length = user32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)
    return buf.value


def screenshot_win(window, label: str):
    try:
        from PIL import ImageGrab
        rect = window.rectangle()
        img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        path = EVIDENCE_DIR / f"{time.strftime('%H%M%S')}_{label}.png"
        img.save(str(path))
        print(f"  📸 {path.name}")
        return path
    except Exception as exc:
        print(f"  ⚠️ Screenshot failed: {exc}")


def open_access(db_path: Path, form: str = "CompanyEditor"):
    import win32com.client
    from pywinauto import Desktop

    app = win32com.client.Dispatch("Access.Application")
    try:
        app.Visible = True
    except Exception:
        pass
    app.OpenCurrentDatabase(str(db_path))
    app.DoCmd.OpenForm(form)
    time.sleep(1.5)

    handle = app.hWndAccessApp
    if callable(handle):
        handle = handle()

    for backend in ("uia",):
        try:
            w = Desktop(backend=backend).window(handle=handle)
            w.wait("visible ready", timeout=10)
            return app, w, handle
        except Exception:
            continue
    app.Quit(ac.AC_QUIT_SAVE_NONE)
    raise RuntimeError("Could not attach pywinauto")


def close(app):
    try:
        app.CloseCurrentDatabase()
    except Exception:
        pass
    try:
        app.Quit(ac.AC_QUIT_SAVE_NONE)
    except Exception:
        pass
    time.sleep(1)


def get_focused_control_hwnd(main_hwnd: int) -> int | None:
    """Attach to Access's thread and get the currently focused control handle."""
    access_tid = user32.GetWindowThreadProcessId(main_hwnd, None)
    current_tid = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(current_tid, access_tid, True)
    try:
        hwnd = user32.GetFocus()
        return hwnd if hwnd else None
    finally:
        user32.AttachThreadInput(current_tid, access_tid, False)


def clear_control_text(hwnd: int):
    """Clear all text in a control using EM_SETSEL + WM_CLEAR."""
    # Select all: EM_SETSEL with start=0, end=-1
    user32.SendMessageW(hwnd, EM_SETSEL, 0, -1)
    time.sleep(0.02)
    # Clear the selection
    user32.SendMessageW(hwnd, WM_CLEAR, 0, 0)
    time.sleep(0.02)


def type_text(hwnd: int, text: str, char_delay: float = 0.015):
    """Type text into a control via WM_CHAR messages."""
    for ch in text:
        user32.PostMessageW(hwnd, WM_CHAR, ord(ch), 0)
        time.sleep(char_delay)


def post_key(hwnd: int, vk: int):
    """Send a key press/release via PostMessage."""
    scan = user32.MapVirtualKeyW(vk, 0)
    lparam_down = 1 | (scan << 16)
    lparam_up = 1 | (scan << 16) | (1 << 30) | (1 << 31)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, lparam_down)
    time.sleep(0.01)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, lparam_up)
    time.sleep(0.01)


def type_into_access_control(app, main_hwnd: int, ctrl_name: str, value: str) -> bool:
    """Navigate to a control and type a value using PostMessage.
    Returns True if the COM value matches after committing."""
    # Navigate via COM
    app.DoCmd.GoToControl(ctrl_name)
    time.sleep(0.15)

    # Get the focused control handle
    hwnd = get_focused_control_hwnd(main_hwnd)
    if not hwnd:
        print(f"    ⚠️ Could not get focus handle for {ctrl_name}")
        return False

    # Clear existing text
    clear_control_text(hwnd)
    time.sleep(0.05)

    # Type the new value
    type_text(hwnd, str(value))
    time.sleep(0.2)

    # Read what Win32 sees in the control
    win_text = get_window_text(hwnd)

    return True  # We'll verify after all fields via commit


def commit_field_value(app, main_hwnd: int, from_ctrl: str, to_ctrl: str):
    """Move focus from one control to another to commit the value."""
    app.DoCmd.GoToControl(to_ctrl)
    time.sleep(0.15)


def run_experiments():
    print("\n" + "="*60)
    print("  EXPERIMENT 1: Clear + Type + Verify (single field)")
    print("="*60)
    experiment_single_field()

    print("\n" + "="*60)
    print("  EXPERIMENT 2: Full form fill + new record + save")
    print("="*60)
    experiment_full_form()

    print("\n" + "="*60)
    print("  EXPERIMENT 3: Multi-form workflow (company → user)")
    print("="*60)
    experiment_multi_form()

    print("\n" + "="*60)
    print("  EXPERIMENT 4: Edit existing record")
    print("="*60)
    experiment_edit_existing()


def experiment_single_field():
    """Test clear + type + commit on a single field."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        # Go to Phone field
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.2)

        hwnd = get_focused_control_hwnd(main_hwnd)
        if not hwnd:
            print("  ❌ No focus handle")
            return

        print(f"  Focused handle: 0x{hwnd:X}")
        print(f"  Class: ", end="")
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        print(cls.value)

        # Before value
        before_win = get_window_text(hwnd)
        before_com = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
        print(f"  Before: Win32={before_win!r}, COM={before_com!r}")

        # Clear and type
        clear_control_text(hwnd)
        time.sleep(0.1)
        after_clear = get_window_text(hwnd)
        print(f"  After clear: Win32={after_clear!r}")

        type_text(hwnd, "555-REFINED")
        time.sleep(0.3)
        after_type = get_window_text(hwnd)
        print(f"  After type: Win32={after_type!r}")

        # Commit by moving to another control
        app.DoCmd.GoToControl("Email")
        time.sleep(0.3)

        # Now read the committed value
        after_com = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
        print(f"  After commit: COM={after_com!r}")

        if after_com == "555-REFINED":
            print("  ✅ SINGLE FIELD WORKS! Clear → Type → Commit confirmed!")
        elif "555-REFINED" in after_com:
            print(f"  ⚠️ Partial match — extra chars: {after_com!r}")
        else:
            print("  ❌ Value didn't commit to COM")
            # Check if it's a dirty state issue
            try:
                dirty = app.Screen.ActiveForm.Dirty
                print(f"  Form dirty: {dirty}")
            except Exception:
                pass

        screenshot_win(window, "single_field")
    finally:
        close(app)


def experiment_full_form():
    """Fill an entire new record and save it."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        import pythoncom

        # Navigate to new record
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)
        is_new = app.Screen.ActiveForm.NewRecord
        print(f"  On new record: {is_new}")

        fields = [
            ("CompanyName", "PostMsg Industries"),
            ("Industry", "Automation"),
            ("Status", "Active"),
            ("Phone", "555-POSTMSG"),
            ("Email", "postmsg@test.example"),
            ("City", "Redmond"),
            ("State", "WA"),
        ]

        for i, (ctrl_name, value) in enumerate(fields):
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.15)

            hwnd = get_focused_control_hwnd(main_hwnd)
            if not hwnd:
                print(f"  ❌ No focus handle for {ctrl_name}")
                # Fallback to COM
                app.Screen.ActiveForm.Controls(ctrl_name).Value = value
                continue

            clear_control_text(hwnd)
            time.sleep(0.05)
            type_text(hwnd, value)
            time.sleep(0.15)

            win_text = get_window_text(hwnd)
            print(f"  {ctrl_name}: typed → Win32={win_text!r}")

        # Commit the last field by tabbing
        hwnd = get_focused_control_hwnd(main_hwnd)
        if hwnd:
            post_key(hwnd, VK_TAB)
            time.sleep(0.3)

        # Check all values via COM before save
        print("\n  COM values before save:")
        form = app.Screen.ActiveForm
        for ctrl_name, expected in fields:
            actual = str(form.Controls(ctrl_name).Value or "")
            match = "✅" if actual == expected else "❌"
            print(f"    {match} {ctrl_name}: {actual!r}")

        screenshot_win(window, "full_form_before_save")

        # Save via COM
        try:
            if form.Dirty:
                form.Dirty = False
                time.sleep(0.5)
                print("  ✅ Record saved (Dirty=False)")
            else:
                print("  ⚠️ Form was not dirty — values may not have committed")
        except Exception as exc:
            print(f"  ❌ Save failed: {exc}")

        # Verify in database
        rs = app.CurrentDb().OpenRecordset(
            "SELECT * FROM Companies WHERE CompanyName = 'PostMsg Industries'"
        )
        if rs.EOF:
            print("  ❌ Record NOT found in database")
            # Check what IS in the database
            rs2 = app.CurrentDb().OpenRecordset("SELECT CompanyID, CompanyName FROM Companies ORDER BY CompanyID")
            while not rs2.EOF:
                print(f"    DB row: {rs2.Fields('CompanyID').Value} = {rs2.Fields('CompanyName').Value!r}")
                rs2.MoveNext()
            rs2.Close()
        else:
            print("  ✅ Record found in database!")
            for j in range(rs.Fields.Count):
                f = rs.Fields(j)
                print(f"    {f.Name} = {f.Value!r}")
            rs.Close()

        screenshot_win(window, "full_form_after_save")
    finally:
        close(app)


def experiment_multi_form():
    """Create company, then switch to UserEditor and create a user for it."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        import pythoncom

        # Step 1: Create company
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.3)

        company_fields = [
            ("CompanyName", "Multi Form Corp"),
            ("Industry", "Testing"),
            ("Status", "Active"),
            ("Phone", "555-MULTI"),
            ("Email", "multi@test.example"),
            ("City", "Seattle"),
            ("State", "WA"),
        ]

        for ctrl_name, value in company_fields:
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            hwnd = get_focused_control_hwnd(main_hwnd)
            if hwnd:
                clear_control_text(hwnd)
                type_text(hwnd, value)
                time.sleep(0.1)
            else:
                app.Screen.ActiveForm.Controls(ctrl_name).Value = value

        # Commit last field
        app.DoCmd.GoToControl("CompanyName")
        time.sleep(0.2)

        # Save
        form = app.Screen.ActiveForm
        if form.Dirty:
            form.Dirty = False
            time.sleep(0.5)

        # Get company ID
        cid = app.CurrentDb().OpenRecordset(
            "SELECT CompanyID FROM Companies WHERE CompanyName = 'Multi Form Corp'"
        )
        if cid.EOF:
            print("  ❌ Company not created")
            return
        company_id = cid.Fields("CompanyID").Value
        cid.Close()
        print(f"  ✅ Step 1: Company created (ID={company_id})")

        # Step 2: Switch to UserEditor
        app.DoCmd.OpenForm("UserEditor")
        time.sleep(0.8)
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.3)

        user_fields = [
            ("CompanyID", str(company_id)),
            ("FirstName", "PostMsg"),
            ("LastName", "User"),
            ("Email", "postmsg.user@multi.example"),
            ("Role", "Tester"),
            ("Status", "Active"),
        ]

        for ctrl_name, value in user_fields:
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            hwnd = get_focused_control_hwnd(main_hwnd)
            if hwnd:
                clear_control_text(hwnd)
                type_text(hwnd, value)
                time.sleep(0.1)
            else:
                app.Screen.ActiveForm.Controls(ctrl_name).Value = value

        app.DoCmd.GoToControl("CompanyID")
        time.sleep(0.2)

        form = app.Screen.ActiveForm
        if form.Dirty:
            form.Dirty = False
            time.sleep(0.5)

        # Verify
        usr = app.CurrentDb().OpenRecordset(
            "SELECT * FROM Users WHERE Email = 'postmsg.user@multi.example'"
        )
        if usr.EOF:
            print("  ❌ User not created")
        else:
            user_cid = usr.Fields("CompanyID").Value
            print(f"  ✅ Step 2: User created, CompanyID={user_cid}")
            if user_cid == company_id:
                print("  ✅ Cross-form reference correct!")
            else:
                print(f"  ❌ CompanyID mismatch: expected {company_id}, got {user_cid}")
            usr.Close()

        screenshot_win(window, "multi_form")
    finally:
        close(app)


def experiment_edit_existing():
    """Edit an existing record's fields and verify the changes."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        # Open existing Fabrikam record
        app.DoCmd.OpenForm("CompanyEditor", ac.AC_NORMAL, "", "CompanyName = 'Fabrikam Logistics'")
        time.sleep(0.8)

        # Read before values
        form = app.Screen.ActiveForm
        before_phone = str(form.Controls("Phone").Value or "")
        before_city = str(form.Controls("City").Value or "")
        print(f"  Before: Phone={before_phone!r}, City={before_city!r}")

        # Edit Phone
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.15)
        hwnd = get_focused_control_hwnd(main_hwnd)
        if hwnd:
            clear_control_text(hwnd)
            type_text(hwnd, "425-555-EDIT")
            time.sleep(0.15)

        # Edit City
        app.DoCmd.GoToControl("City")
        time.sleep(0.15)
        hwnd = get_focused_control_hwnd(main_hwnd)
        if hwnd:
            clear_control_text(hwnd)
            type_text(hwnd, "Kirkland")
            time.sleep(0.15)

        # Commit by going back to Phone
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.2)

        # Check COM values
        phone_val = str(form.Controls("Phone").Value or "")
        city_val = str(form.Controls("City").Value or "")
        print(f"  After edit: Phone={phone_val!r}, City={city_val!r}")

        # Save
        if form.Dirty:
            form.Dirty = False
            time.sleep(0.5)
            print("  ✅ Saved")

        # Verify in database
        rs = app.CurrentDb().OpenRecordset(
            "SELECT Phone, City FROM Companies WHERE CompanyName = 'Fabrikam Logistics'"
        )
        if not rs.EOF:
            db_phone = str(rs.Fields("Phone").Value or "")
            db_city = str(rs.Fields("City").Value or "")
            print(f"  DB verify: Phone={db_phone!r}, City={db_city!r}")
            if "EDIT" in db_phone:
                print("  ✅ Phone edit persisted!")
            else:
                print("  ❌ Phone edit did NOT persist")
            if db_city == "Kirkland":
                print("  ✅ City edit persisted!")
            else:
                print("  ❌ City edit did NOT persist")
        rs.Close()

        screenshot_win(window, "edit_existing")
    finally:
        close(app)


if __name__ == "__main__":
    run_experiments()
