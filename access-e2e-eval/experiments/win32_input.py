"""
Low-level Win32 message-based UI automation for Access.
Bypasses SendInput/SetCursorPos by posting WM_CHAR, WM_KEYDOWN,
and BM_CLICK directly to window handles.
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

# Win32 message constants
WM_CHAR = 0x0102
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
WM_SETTEXT = 0x000C
WM_GETTEXT = 0x000D
WM_GETTEXTLENGTH = 0x000E
WM_SETFOCUS = 0x0007
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
BM_CLICK = 0x00F5
VK_TAB = 0x09
VK_RETURN = 0x0D
VK_BACK = 0x08
VK_DELETE = 0x2E
VK_HOME = 0x24
VK_END = 0x23
VK_CONTROL = 0x11
VK_A = 0x41


def fresh_db() -> Path:
    ts = time.strftime("%H%M%S")
    dest = EVIDENCE_DIR / f"win32_exp_{ts}.accdb"
    shutil.copy2(DEFAULT_DATABASE, dest)
    return dest


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


def post_string(hwnd: int, text: str):
    """Send a string to a window handle via WM_CHAR messages."""
    for ch in text:
        user32.PostMessageW(hwnd, WM_CHAR, ord(ch), 0)
        time.sleep(0.01)


def post_key(hwnd: int, vk: int):
    """Send a keydown+keyup to a window handle."""
    scan = user32.MapVirtualKeyW(vk, 0)
    lparam_down = 1 | (scan << 16)
    lparam_up = 1 | (scan << 16) | (1 << 30) | (1 << 31)
    user32.PostMessageW(hwnd, WM_KEYDOWN, vk, lparam_down)
    time.sleep(0.01)
    user32.PostMessageW(hwnd, WM_KEYUP, vk, lparam_up)
    time.sleep(0.01)


def post_ctrl_a(hwnd: int):
    """Send Ctrl+A to select all."""
    scan_ctrl = user32.MapVirtualKeyW(VK_CONTROL, 0)
    scan_a = user32.MapVirtualKeyW(VK_A, 0)
    user32.PostMessageW(hwnd, WM_KEYDOWN, VK_CONTROL, 1 | (scan_ctrl << 16))
    time.sleep(0.01)
    user32.PostMessageW(hwnd, WM_KEYDOWN, VK_A, 1 | (scan_a << 16))
    time.sleep(0.01)
    user32.PostMessageW(hwnd, WM_KEYUP, VK_A, 1 | (scan_a << 16) | (1 << 30) | (1 << 31))
    time.sleep(0.01)
    user32.PostMessageW(hwnd, WM_KEYUP, VK_CONTROL, 1 | (scan_ctrl << 16) | (1 << 30) | (1 << 31))
    time.sleep(0.01)


def select_all_delete(hwnd: int):
    """Select all text and delete it."""
    post_ctrl_a(hwnd)
    time.sleep(0.05)
    post_key(hwnd, VK_DELETE)
    time.sleep(0.05)


def click_button_msg(hwnd: int):
    """Click a button via BM_CLICK message."""
    user32.PostMessageW(hwnd, BM_CLICK, 0, 0)


def get_window_text(hwnd: int) -> str:
    length = user32.SendMessageW(hwnd, WM_GETTEXTLENGTH, 0, 0)
    if length == 0:
        return ""
    buf = ctypes.create_unicode_buffer(length + 1)
    user32.SendMessageW(hwnd, WM_GETTEXT, length + 1, buf)
    return buf.value


def find_child_hwnd_by_class(parent: int, class_name: str) -> list[int]:
    """Enumerate child windows of a given class."""
    results = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

    def callback(hwnd, lparam):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, buf, 256)
        if class_name.lower() in buf.value.lower():
            results.append(hwnd)
        return True

    user32.EnumChildWindows(parent, WNDENUMPROC(callback), 0)
    return results


def enumerate_all_children(parent: int) -> list[tuple[int, str, str]]:
    """Enumerate ALL child windows with their class name and text."""
    results = []
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.wintypes.BOOL, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)

    def callback(hwnd, lparam):
        class_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, class_buf, 256)
        text = get_window_text(hwnd)
        results.append((hwnd, class_buf.value, text))
        return True

    user32.EnumChildWindows(parent, WNDENUMPROC(callback), 0)
    return results


def run_all():
    experiments = [
        ("1. Enumerate Win32 child windows", enumerate_children),
        ("2. PostMessage keyboard input", try_post_message_input),
        ("3. SetForegroundWindow + SendInput retry", try_foreground_and_sendinput),
        ("4. Shell.Application SendKeys", try_shell_sendkeys),
        ("5. Full workflow via best method", try_full_workflow),
    ]
    for name, fn in experiments:
        print(f"\n{'='*60}")
        print(f"  {name}")
        print(f"{'='*60}")
        try:
            fn()
        except Exception as exc:
            import traceback
            print(f"  ❌ CRASHED: {exc}")
            traceback.print_exc()


def enumerate_children():
    """Enumerate all Win32 child windows to find control handles."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        print(f"  Main window handle: {main_hwnd} (0x{main_hwnd:X})")

        children = enumerate_all_children(main_hwnd)
        print(f"  Total child windows: {len(children)}")
        print()

        # Look for interesting controls
        for hwnd, cls, text in children:
            if text and len(text) > 0 and len(text) < 200:
                print(f"    0x{hwnd:08X} [{cls}] '{text}'")

        # Specifically look for OFormSub (Access form controls) and other Access classes
        access_classes = {}
        for hwnd, cls, text in children:
            if cls not in access_classes:
                access_classes[cls] = []
            access_classes[cls].append((hwnd, text))

        print(f"\n  Window classes found:")
        for cls, items in sorted(access_classes.items()):
            print(f"    {cls}: {len(items)} windows")
            for hwnd, text in items[:3]:
                if text:
                    print(f"      0x{hwnd:08X} '{text[:60]}'")

    finally:
        close(app)


def try_post_message_input():
    """Use PostMessage WM_CHAR to send text to Access controls."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        # First, use COM to go to the Phone control
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.3)

        # Get the focused window handle
        focused_hwnd = user32.GetFocus()
        if focused_hwnd == 0:
            # GetFocus only works in the same thread. Try AttachThreadInput.
            access_tid = user32.GetWindowThreadProcessId(main_hwnd, None)
            current_tid = kernel32.GetCurrentThreadId()
            attached = user32.AttachThreadInput(current_tid, access_tid, True)
            print(f"  AttachThreadInput: {attached}")
            focused_hwnd = user32.GetFocus()
            user32.AttachThreadInput(current_tid, access_tid, False)

        if focused_hwnd:
            print(f"  Focused handle: 0x{focused_hwnd:08X}")
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(focused_hwnd, cls, 256)
            print(f"  Focused class: {cls.value}")
            print(f"  Focused text: {get_window_text(focused_hwnd)!r}")

            # Try sending text via PostMessage
            select_all_delete(focused_hwnd)
            time.sleep(0.1)
            post_string(focused_hwnd, "555-POSTED")
            time.sleep(0.5)

            # Verify
            com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
            win_val = get_window_text(focused_hwnd)
            print(f"  COM value: {com_val!r}")
            print(f"  Win32 text: {win_val!r}")
            if "555-POSTED" in com_val or "555-POSTED" in win_val:
                print("  ✅ PostMessage WM_CHAR works!")
            else:
                print("  ❌ PostMessage didn't reach the control")
        else:
            print("  ❌ Could not get focused handle")

        # Alternative: try to find the Access form sub-window and post to it
        print("\n  Trying to find OFormSub class windows...")
        form_children = find_child_hwnd_by_class(main_hwnd, "OFormSub")
        print(f"  Found {len(form_children)} OFormSub windows")
        for hwnd in form_children[:5]:
            text = get_window_text(hwnd)
            print(f"    0x{hwnd:08X}: {text!r}")

        # Also try MDIClient
        mdi_children = find_child_hwnd_by_class(main_hwnd, "MDI")
        print(f"  Found {len(mdi_children)} MDI-related windows")

    finally:
        close(app)


def try_foreground_and_sendinput():
    """Use SetForegroundWindow + explicit window positioning before SendInput."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        import win32gui
        import win32con

        # Move window to a known position on primary monitor
        print("  Moving Access window to (0, 0, 1200, 900)...")
        win32gui.SetWindowPos(
            main_hwnd,
            win32con.HWND_TOP,
            0, 0, 1200, 900,
            win32con.SWP_SHOWWINDOW,
        )
        time.sleep(0.5)

        # Force foreground
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.5)

        # Check foreground
        fg = user32.GetForegroundWindow()
        print(f"  Foreground window: 0x{fg:X}, Expected: 0x{main_hwnd:X}, Match: {fg == main_hwnd}")

        # Go to control
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.3)

        # Try sending keys
        from pywinauto.keyboard import send_keys
        try:
            send_keys("^a{BACKSPACE}", pause=0.05)
            send_keys("555-FGWIN", with_spaces=True, pause=0.02)
            time.sleep(0.5)
            com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
            print(f"  COM value: {com_val!r}")
            if "555-FGWIN" in com_val:
                print("  ✅ SendInput works after SetForegroundWindow!")
            else:
                print("  ❌ SendInput still failed after SetForegroundWindow")
        except Exception as exc:
            print(f"  ❌ SendInput error: {exc}")

        screenshot_win(window, "foreground_test")
    finally:
        close(app)


def try_shell_sendkeys():
    """Use WScript.Shell SendKeys (old-school COM automation)."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        import win32com.client
        import win32gui
        import win32con

        # Position and focus
        win32gui.SetWindowPos(main_hwnd, win32con.HWND_TOP, 0, 0, 1200, 900, win32con.SWP_SHOWWINDOW)
        time.sleep(0.3)
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.3)

        app.DoCmd.GoToControl("Phone")
        time.sleep(0.3)

        # Use WScript.Shell SendKeys
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.AppActivate("Access")
        time.sleep(0.3)

        # Select all and delete
        shell.SendKeys("^a", 0)
        time.sleep(0.1)
        shell.SendKeys("{DELETE}", 0)
        time.sleep(0.1)

        # Type the value
        shell.SendKeys("555-WSCRIPT", 0)
        time.sleep(0.5)

        com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
        print(f"  COM value: {com_val!r}")
        if "555-WSCRIPT" in com_val:
            print("  ✅ WScript.Shell SendKeys works!")
        else:
            print("  ❌ WScript.Shell SendKeys didn't reach control")

        # Also try System.Windows.Forms.SendKeys via PowerShell
        print("\n  Trying .NET SendKeys via PowerShell...")
        import subprocess
        result = subprocess.run(
            ["powershell", "-Command",
             "Add-Type -AssemblyName System.Windows.Forms; "
             "[System.Windows.Forms.SendKeys]::SendWait('^a'); "
             "Start-Sleep -Milliseconds 100; "
             "[System.Windows.Forms.SendKeys]::SendWait('{DELETE}'); "
             "Start-Sleep -Milliseconds 100; "
             "[System.Windows.Forms.SendKeys]::SendWait('555-DOTNET')"],
            capture_output=True, text=True, timeout=10,
        )
        time.sleep(0.5)
        com_val2 = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
        print(f"  COM value after .NET SendKeys: {com_val2!r}")
        if "555-DOTNET" in com_val2:
            print("  ✅ .NET SendKeys works!")
        else:
            print("  ❌ .NET SendKeys didn't reach control")

        screenshot_win(window, "shell_sendkeys")
    finally:
        close(app)


def try_full_workflow():
    """Full end-to-end workflow using the best working method."""
    db = fresh_db()
    app, window, main_hwnd = open_access(db)
    try:
        import win32gui
        import win32con
        import win32com.client
        import pythoncom

        # Position window
        win32gui.SetWindowPos(main_hwnd, win32con.HWND_TOP, 0, 0, 1200, 900, win32con.SWP_SHOWWINDOW)
        time.sleep(0.5)
        win32gui.SetForegroundWindow(main_hwnd)
        time.sleep(0.3)

        # Navigate to new record via COM
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)

        is_new = app.Screen.ActiveForm.NewRecord
        print(f"  On new record: {is_new}")

        # Try each input method
        methods_that_work = []
        test_data = {
            "CompanyName": "E2E Test Corp",
            "Industry": "Automation",
            "Status": "Active",
            "Phone": "555-E2E",
            "Email": "e2e@test.example",
            "City": "TestCity",
            "State": "WA",
        }

        shell = win32com.client.Dispatch("WScript.Shell")

        for ctrl_name, value in test_data.items():
            success = False
            method_used = None

            # Always start by COM-navigating to the control
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.2)

            # Get focused control handle via thread attachment
            access_tid = user32.GetWindowThreadProcessId(main_hwnd, None)
            current_tid = kernel32.GetCurrentThreadId()

            # Method 1: PostMessage WM_CHAR
            if not success:
                try:
                    user32.AttachThreadInput(current_tid, access_tid, True)
                    focused = user32.GetFocus()
                    user32.AttachThreadInput(current_tid, access_tid, False)
                    if focused:
                        select_all_delete(focused)
                        time.sleep(0.05)
                        post_string(focused, value)
                        time.sleep(0.3)
                        com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                        if com_val == value:
                            success = True
                            method_used = "PostMessage"
                except Exception:
                    pass

            # Method 2: WScript.Shell SendKeys
            if not success:
                try:
                    win32gui.SetForegroundWindow(main_hwnd)
                    time.sleep(0.1)
                    shell.SendKeys("^a{DELETE}", 0)
                    time.sleep(0.1)
                    # Escape special chars for WScript SendKeys
                    safe_val = value.replace("+", "{+}").replace("^", "{^}").replace("%", "{%}")
                    safe_val = safe_val.replace("(", "{(}").replace(")", "{)}")
                    safe_val = safe_val.replace("{", "{{}").replace("}", "{}}")
                    shell.SendKeys(safe_val, 0)
                    time.sleep(0.3)
                    com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                    if com_val == value:
                        success = True
                        method_used = "WScript"
                except Exception:
                    pass

            # Method 3: pywinauto send_keys
            if not success:
                try:
                    from pywinauto.keyboard import send_keys
                    window.set_focus()
                    send_keys("^a{BACKSPACE}", pause=0.05)
                    send_keys(value, with_spaces=True, pause=0.02)
                    time.sleep(0.3)
                    com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                    if com_val == value:
                        success = True
                        method_used = "pywinauto"
                except Exception:
                    pass

            # Method 4: COM Value set (fallback)
            if not success:
                try:
                    app.Screen.ActiveForm.Controls(ctrl_name).Value = value
                    time.sleep(0.1)
                    success = True
                    method_used = "COM"
                except Exception:
                    pass

            if method_used and method_used not in methods_that_work:
                methods_that_work.append(method_used)
            com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
            status = "✅" if success else "❌"
            print(f"  {status} {ctrl_name} = {com_val!r} (via {method_used})")

        screenshot_win(window, "full_workflow_filled")

        # Save via Submit button or COM
        try:
            form = app.Screen.ActiveForm
            if form.Dirty:
                form.Dirty = False
                time.sleep(0.5)
            print("  ✅ Record saved via COM Dirty=False")
        except Exception as exc:
            print(f"  ❌ Save failed: {exc}")

        # Verify
        rs = app.CurrentDb().OpenRecordset(
            "SELECT * FROM Companies WHERE CompanyName = 'E2E Test Corp'"
        )
        if rs.EOF:
            print("  ❌ Record NOT found in database")
        else:
            print("  ✅ Record verified in database!")
        rs.Close()

        print(f"\n  Working input methods: {methods_that_work}")
        print(f"  Human-likeness ranking: PostMessage > WScript > pywinauto >> COM")

    finally:
        close(app)


if __name__ == "__main__":
    run_all()
