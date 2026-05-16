from __future__ import annotations

import ctypes
import ctypes.wintypes
import time
from dataclasses import dataclass
from typing import Any


# Win32 message constants for PostMessage-based input
WM_CHAR = 0x0102
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
EM_SETSEL = 0x00B1
WM_CLEAR = 0x0303
BM_CLICK = 0x00F5
VK_SPACE = 0x20

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32


@dataclass(frozen=True)
class FieldEntry:
    control_name: str
    value: Any


def _get_focused_hwnd(main_hwnd: int) -> int | None:
    """Attach to Access's UI thread and return the focused control handle."""
    access_tid = _user32.GetWindowThreadProcessId(main_hwnd, None)
    current_tid = _kernel32.GetCurrentThreadId()
    _user32.AttachThreadInput(current_tid, access_tid, True)
    try:
        hwnd = _user32.GetFocus()
        return hwnd if hwnd else None
    finally:
        _user32.AttachThreadInput(current_tid, access_tid, False)


def _clear_control(hwnd: int) -> None:
    """Select all text and clear it via EM_SETSEL + WM_CLEAR."""
    _user32.SendMessageW(hwnd, EM_SETSEL, 0, -1)
    time.sleep(0.02)
    _user32.SendMessageW(hwnd, WM_CLEAR, 0, 0)
    time.sleep(0.02)


def _post_chars(hwnd: int, text: str, char_delay: float = 0.015) -> None:
    """Type text character-by-character via PostMessage WM_CHAR."""
    for ch in text:
        _user32.PostMessageW(hwnd, WM_CHAR, ord(ch), 0)
        time.sleep(char_delay)


def _post_key(hwnd: int, vk: int) -> None:
    """Send a single key press/release via PostMessage."""
    scan = _user32.MapVirtualKeyW(vk, 0)
    lparam_down = 1 | (scan << 16)
    lparam_up = 1 | (scan << 16) | (1 << 30) | (1 << 31)
    _user32.PostMessageW(hwnd, WM_KEYDOWN, vk, lparam_down)
    time.sleep(0.01)
    _user32.PostMessageW(hwnd, WM_KEYUP, vk, lparam_up)
    time.sleep(0.01)


class AccessUiDriver:
    """Drives Access form controls using the best available input method.

    Uses Win32 PostMessage by default to deliver WM_CHAR directly to the
    focused Access control handle (OKttbx class).  This bypasses SendInput
    and works in agent/remote sessions where SetCursorPos is blocked.
    Falls back to pywinauto send_keys only when PostMessage cannot obtain
    a control handle, and finally to COM Value assignment as a last resort.
    """

    def __init__(self, session, *, force_postmsg: bool = True):
        self.session = session
        self._use_postmsg: bool = force_postmsg

    @property
    def _main_hwnd(self) -> int:
        hwnd = self.session.app.hWndAccessApp
        if callable(hwnd):
            hwnd = hwnd()
        return hwnd

    def type_into_control(self, control_name: str, value: Any) -> None:
        self.session.go_to_control(control_name)
        time.sleep(0.1)

        if isinstance(value, bool):
            self._toggle_checkbox(value)
            return

        text = "" if value is None else str(value)

        if self._use_postmsg:
            self._type_via_postmsg(text)
        else:
            self._type_via_sendkeys(text)

    def _type_via_sendkeys(self, text: str) -> None:
        from pywinauto.keyboard import send_keys

        send_keys("^a{BACKSPACE}")
        if text:
            send_keys(text, with_spaces=True, pause=0.01)

    def _type_via_postmsg(self, text: str) -> None:
        hwnd = _get_focused_hwnd(self._main_hwnd)
        if not hwnd:
            # Last resort: set via COM
            try:
                ctrl = self.session.app.Screen.ActiveForm.ActiveControl
                ctrl.Value = text or None
            except Exception:
                pass
            return
        _clear_control(hwnd)
        if text:
            _post_chars(hwnd, text)
        time.sleep(0.15)

    def _toggle_checkbox(self, value: bool) -> None:
        if self._use_postmsg:
            hwnd = _get_focused_hwnd(self._main_hwnd)
            if hwnd and value:
                _post_key(hwnd, VK_SPACE)
        else:
            from pywinauto.keyboard import send_keys
            if value:
                send_keys("{SPACE}")

    def fill_form(self, fields: list[FieldEntry] | dict[str, Any]) -> None:
        entries = _normalize_fields(fields)
        for entry in entries:
            self.type_into_control(entry.control_name, entry.value)
        # When using PostMessage, the last typed field's value only commits
        # when focus leaves the control. Cycle focus away and back to flush.
        if self._use_postmsg and entries:
            self._commit_pending_value(entries[-1].control_name)

    def _commit_pending_value(self, current_control: str) -> None:
        """Move focus away from the current control and back to flush its value."""
        try:
            form = self.session.app.Screen.ActiveForm
            # Pick any other control to briefly focus
            for i in range(form.Controls.Count):
                ctrl = form.Controls(i)
                if ctrl.Name != current_control and ctrl.ControlType in (109, 111):
                    self.session.app.DoCmd.GoToControl(ctrl.Name)
                    time.sleep(0.1)
                    self.session.app.DoCmd.GoToControl(current_control)
                    time.sleep(0.1)
                    return
        except Exception:
            pass

    def save(self) -> None:
        self.session.save_record()

    def click_submit(self) -> None:
        """Click the Submit button on the form like a human user.

        Tries pywinauto click_input first, then Win32 BM_CLICK as fallback,
        and finally COM Dirty=False as a last resort.
        """
        self.session.window.set_focus()
        time.sleep(0.3)

        button_clicked = False

        # Strategy 1: pywinauto click_input (most human-like)
        if not button_clicked:
            try:
                btn = self.session.window.child_window(
                    title="Submit", control_type="Button"
                )
                btn.wait("visible ready", timeout=5)
                btn.click_input()
                time.sleep(0.5)
                button_clicked = True
            except Exception:
                pass

        # Strategy 2: Win32 BM_CLICK via PostMessage to the button handle
        if not button_clicked:
            try:
                btn = self.session.window.child_window(
                    title="Submit", control_type="Button"
                )
                btn_hwnd = btn.handle
                _user32.PostMessageW(btn_hwnd, BM_CLICK, 0, 0)
                time.sleep(0.5)
                button_clicked = True
            except Exception:
                pass

        # Strategy 3: COM RunCommand acCmdSaveRecord
        if not button_clicked:
            try:
                self.session.app.DoCmd.RunCommand(21)  # acCmdSaveRecord
                time.sleep(0.5)
                button_clicked = True
            except Exception:
                pass

        # Final safety net: force COM save if form is still dirty
        try:
            active_form = self.session.app.Screen.ActiveForm
            if active_form.Dirty:
                active_form.Dirty = False
                time.sleep(0.5)
        except Exception:
            pass

    def new_record(self) -> None:
        self.session.go_to_new_record()

    def read_focused_value(self) -> str:
        """Read the value of the currently focused control via COM."""
        try:
            return str(
                self.session.app.Screen.ActiveForm.ActiveControl.Value or ""
            )
        except Exception:
            return ""


def _normalize_fields(fields: list[FieldEntry] | dict[str, Any]) -> list[FieldEntry]:
    if isinstance(fields, dict):
        return [FieldEntry(control_name=name, value=value) for name, value in fields.items()]
    return fields
