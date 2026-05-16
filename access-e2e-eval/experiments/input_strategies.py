"""
Focused experiments to solve the keyboard/UI input challenge.
Tests multiple creative approaches to get text into Access form controls.
"""
from __future__ import annotations

import shutil
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from access_eval_suite.config import DEFAULT_DATABASE
from access_eval_suite import constants as ac

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)


def fresh_db() -> Path:
    ts = time.strftime("%H%M%S")
    dest = EVIDENCE_DIR / f"input_exp_{ts}.accdb"
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

    for backend in ("uia", "win32"):
        try:
            w = Desktop(backend=backend).window(handle=handle)
            w.wait("visible ready", timeout=10)
            return app, w
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


def run_all():
    experiments = [
        ("1. Enable Content button", try_enable_content),
        ("2. Click into controls via UIA", try_click_into_controls),
        ("3. UIA SetValue pattern", try_uia_set_value),
        ("4. Record nav via UIA buttons", try_record_nav_buttons),
        ("5. Clipboard paste approach", try_clipboard_paste),
        ("6. Combined best approach", try_combined_approach),
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
        # Kill any lingering Access
        try:
            import subprocess
            subprocess.run(["tasklist", "/FI", "IMAGENAME eq MSACCESS.EXE"],
                           capture_output=True, text=True)
        except Exception:
            pass


def try_enable_content():
    """Click 'Enable Content' to allow macros, then test if Submit button works."""
    db = fresh_db()
    app, window = open_access(db)
    try:
        screenshot_win(window, "before_enable_content")

        # Find and click the Enable Content button
        try:
            btn = window.child_window(title="Enable Content", control_type="Button")
            btn.wait("visible ready", timeout=5)
            print("  Found 'Enable Content' button — clicking it")
            btn.click_input()
            time.sleep(2)
            screenshot_win(window, "after_enable_content")
            print("  ✅ Enable Content clicked — security warning should be dismissed")
        except Exception as exc:
            print(f"  ❌ Could not click Enable Content: {exc}")

        # Now test if keyboard input works better after enabling content
        from pywinauto.keyboard import send_keys
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.3)
        window.set_focus()
        send_keys("^a{BACKSPACE}")
        send_keys("555-ENABLED", with_spaces=True, pause=0.02)
        time.sleep(0.5)

        val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
        print(f"  Phone after typing: {val!r}")
        if val == "555-ENABLED":
            print("  ✅ Keyboard input WORKS after Enable Content!")
        else:
            print("  ❌ Keyboard input still not reaching controls")

        screenshot_win(window, "after_enable_typing")
    finally:
        close(app)


def try_click_into_controls():
    """Click directly into Edit controls via UIA before typing."""
    db = fresh_db()
    app, window = open_access(db)
    try:
        # First enable content
        try:
            btn = window.child_window(title="Enable Content", control_type="Button")
            btn.click_input()
            time.sleep(1.5)
        except Exception:
            pass

        from pywinauto.keyboard import send_keys

        # Try to find the Phone edit control via UIA and click into it
        approaches = [
            ("title='Phone', control_type='Edit'", {"title": "Phone", "control_type": "Edit"}),
            ("title_re='.*Phone.*'", {"title_re": ".*Phone.*", "control_type": "Edit"}),
            ("auto_id='Phone'", {"auto_id": "Phone"}),
        ]

        for desc, kwargs in approaches:
            try:
                ctrl = window.child_window(**kwargs)
                ctrl.wait("visible", timeout=3)
                print(f"  Found control via {desc}")
                print(f"    Window text: {ctrl.window_text()!r}")
                print(f"    Rectangle: {ctrl.rectangle()}")

                # Click into it
                ctrl.click_input()
                time.sleep(0.3)

                # Select all and type
                send_keys("^a{BACKSPACE}")
                send_keys("555-CLICKED", with_spaces=True, pause=0.02)
                time.sleep(0.5)

                # Check via COM
                val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
                print(f"    COM value after click+type: {val!r}")
                screenshot_win(window, f"click_approach_{desc[:10].replace(' ','_')}")

                if "555-CLICKED" in val:
                    print(f"    ✅ Click-then-type WORKS via {desc}!")
                    return
                else:
                    # Also check what UIA says
                    try:
                        uia_text = ctrl.window_text()
                        print(f"    UIA text: {uia_text!r}")
                    except Exception:
                        pass
            except Exception as exc:
                print(f"  ❌ {desc}: {exc}")

        print("  ❌ No click approach worked")
    finally:
        close(app)


def try_uia_set_value():
    """Use UIA ValuePattern.SetValue to directly set control text."""
    db = fresh_db()
    app, window = open_access(db)
    try:
        try:
            btn = window.child_window(title="Enable Content", control_type="Button")
            btn.click_input()
            time.sleep(1.5)
        except Exception:
            pass

        # Find the Phone edit control
        try:
            ctrl = window.child_window(title="Phone", control_type="Edit")
            ctrl.wait("visible", timeout=5)

            # Try set_text (pywinauto wrapper around SetValue)
            try:
                ctrl.set_text("555-UIA-SET")
                time.sleep(0.5)
                com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
                uia_val = ctrl.window_text()
                print(f"  set_text: COM={com_val!r}, UIA={uia_val!r}")
                if "555-UIA-SET" in com_val or "555-UIA-SET" in uia_val:
                    print("  ✅ UIA set_text works!")
            except Exception as exc:
                print(f"  set_text failed: {exc}")

            # Try set_edit_text
            try:
                ctrl.set_edit_text("555-UIA-EDIT")
                time.sleep(0.5)
                com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
                uia_val = ctrl.window_text()
                print(f"  set_edit_text: COM={com_val!r}, UIA={uia_val!r}")
                if "555-UIA-EDIT" in com_val or "555-UIA-EDIT" in uia_val:
                    print("  ✅ UIA set_edit_text works!")
            except Exception as exc:
                print(f"  set_edit_text failed: {exc}")

            # Try type_keys (sends to the specific control)
            try:
                ctrl.click_input()
                time.sleep(0.2)
                ctrl.type_keys("^a{BACKSPACE}555-TYPE-KEYS", with_spaces=True, pause=0.02)
                time.sleep(0.5)
                com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
                uia_val = ctrl.window_text()
                print(f"  type_keys: COM={com_val!r}, UIA={uia_val!r}")
                if "555-TYPE-KEYS" in com_val or "555-TYPE-KEYS" in uia_val:
                    print("  ✅ UIA type_keys works!")
            except Exception as exc:
                print(f"  type_keys failed: {exc}")

        except Exception as exc:
            print(f"  ❌ Could not find Phone control: {exc}")

        screenshot_win(window, "uia_set_value")
    finally:
        close(app)


def try_record_nav_buttons():
    """Navigate records using UIA buttons in the Record Navigator."""
    db = fresh_db()
    app, window = open_access(db)
    try:
        try:
            btn = window.child_window(title="Enable Content", control_type="Button")
            btn.click_input()
            time.sleep(1.5)
        except Exception:
            pass

        def current_company():
            try:
                return str(app.Screen.ActiveForm.Controls("CompanyName").Value or "")
            except Exception:
                return "???"

        print(f"  Current record: {current_company()!r}")

        # Navigate using UIA buttons
        nav_actions = [
            ("Next record", "Next record"),
            ("Last record", "Last record"),
            ("First record", "First record"),
            ("New (blank) record", "New (blank) record"),
        ]

        for label, title in nav_actions:
            try:
                btn = window.child_window(title=title, control_type="Button")
                btn.click_input()
                time.sleep(0.5)
                print(f"  After '{label}': {current_company()!r}")
            except Exception as exc:
                print(f"  ❌ '{label}': {exc}")

        screenshot_win(window, "record_nav")

        # Check if we're on a new record
        try:
            form = app.Screen.ActiveForm
            print(f"  NewRecord property: {form.NewRecord}")
            if form.NewRecord:
                print("  ✅ Successfully navigated to new record via UIA button!")
        except Exception as exc:
            print(f"  NewRecord check: {exc}")

    finally:
        close(app)


def try_clipboard_paste():
    """Use clipboard to paste values into controls — alternative to send_keys."""
    db = fresh_db()
    app, window = open_access(db)
    try:
        try:
            btn = window.child_window(title="Enable Content", control_type="Button")
            btn.click_input()
            time.sleep(1.5)
        except Exception:
            pass

        import subprocess

        # Go to Phone field
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.3)
        window.set_focus()

        # Put value on clipboard using PowerShell
        value = "555-PASTED"
        subprocess.run(
            ["powershell", "-Command", f"Set-Clipboard -Value '{value}'"],
            capture_output=True, timeout=5,
        )
        time.sleep(0.2)

        from pywinauto.keyboard import send_keys
        # Select all, then paste from clipboard
        send_keys("^a^v")
        time.sleep(0.5)

        com_val = str(app.Screen.ActiveForm.Controls("Phone").Value or "")
        print(f"  After clipboard paste: COM={com_val!r}")
        if value in com_val:
            print("  ✅ Clipboard paste WORKS!")
        else:
            print("  ❌ Clipboard paste didn't reach control")

        screenshot_win(window, "clipboard_paste")
    finally:
        close(app)


def try_combined_approach():
    """Use the best working combination: Enable Content + click into control + type.
    If that fails, try COM SetValue + clipboard as fallbacks.
    Full workflow: create new company end-to-end."""
    db = fresh_db()
    app, window = open_access(db)
    try:
        # Step 1: Enable Content
        try:
            btn = window.child_window(title="Enable Content", control_type="Button")
            btn.click_input()
            time.sleep(2)
            print("  ✅ Step 1: Enabled content")
        except Exception:
            print("  ⚠️ Step 1: Enable Content not found/already enabled")

        # Step 2: Navigate to new record via UIA button
        try:
            new_btn = window.child_window(title="New (blank) record", control_type="Button")
            new_btn.click_input()
            time.sleep(0.5)
            form = app.Screen.ActiveForm
            print(f"  Step 2: NewRecord={form.NewRecord}")
        except Exception as exc:
            print(f"  Step 2 fallback: using COM GoToRecord")
            import pythoncom
            app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
            time.sleep(0.5)

        screenshot_win(window, "combined_new_record")

        # Step 3: Fill each field using the best approach that works
        from pywinauto.keyboard import send_keys

        test_data = {
            "CompanyName": "Combined Corp",
            "Industry": "Innovation",
            "Status": "Active",
            "Phone": "555-COMBO",
            "Email": "combined@test.example",
            "City": "TestCity",
            "State": "WA",
        }

        working_method = None
        for ctrl_name, value in test_data.items():
            success = False

            # Method A: Click UIA control + type_keys on control
            if not success:
                try:
                    uia_ctrl = window.child_window(title=ctrl_name, control_type="Edit")
                    uia_ctrl.click_input()
                    time.sleep(0.15)
                    uia_ctrl.type_keys("^a{BACKSPACE}", with_spaces=True)
                    uia_ctrl.type_keys(value, with_spaces=True, pause=0.02)
                    time.sleep(0.3)
                    com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                    if com_val == value:
                        success = True
                        if working_method != "A":
                            working_method = "A"
                            print(f"  Method A works (click UIA + type_keys)")
                except Exception:
                    pass

            # Method B: COM GoToControl + global send_keys
            if not success:
                try:
                    app.DoCmd.GoToControl(ctrl_name)
                    time.sleep(0.15)
                    window.set_focus()
                    send_keys("^a{BACKSPACE}")
                    send_keys(value, with_spaces=True, pause=0.02)
                    time.sleep(0.3)
                    com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                    if com_val == value:
                        success = True
                        if working_method != "B":
                            working_method = "B"
                            print(f"  Method B works (COM GoToControl + send_keys)")
                except Exception:
                    pass

            # Method C: Click UIA + clipboard paste
            if not success:
                try:
                    import subprocess
                    uia_ctrl = window.child_window(title=ctrl_name, control_type="Edit")
                    uia_ctrl.click_input()
                    time.sleep(0.15)
                    subprocess.run(
                        ["powershell", "-Command", f"Set-Clipboard -Value '{value}'"],
                        capture_output=True, timeout=5,
                    )
                    send_keys("^a^v")
                    time.sleep(0.3)
                    com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                    if com_val == value:
                        success = True
                        if working_method != "C":
                            working_method = "C"
                            print(f"  Method C works (click UIA + clipboard paste)")
                except Exception:
                    pass

            # Method D: Direct COM Value set (least human-like, but works)
            if not success:
                try:
                    app.Screen.ActiveForm.Controls(ctrl_name).Value = value
                    time.sleep(0.1)
                    success = True
                    if working_method != "D":
                        working_method = "D"
                        print(f"  Method D fallback (COM SetValue — not human-like)")
                except Exception:
                    pass

            status = "✅" if success else "❌"
            com_val = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
            print(f"    {status} {ctrl_name}: {com_val!r}")

        screenshot_win(window, "combined_filled")

        # Step 4: Click Submit button
        try:
            submit = window.child_window(title="Submit", control_type="Button")
            submit.click_input()
            time.sleep(1)
            print("  ✅ Step 4: Submit button clicked")
        except Exception as exc:
            print(f"  ⚠️ Step 4: Submit click failed ({exc}), using COM save")
            try:
                form = app.Screen.ActiveForm
                if form.Dirty:
                    form.Dirty = False
                    time.sleep(0.5)
            except Exception:
                pass

        screenshot_win(window, "combined_after_submit")

        # Step 5: Verify
        rs = app.CurrentDb().OpenRecordset(
            "SELECT * FROM Companies WHERE CompanyName = 'Combined Corp'"
        )
        if rs.EOF:
            print("  ❌ Step 5: Record NOT found in database")
        else:
            print("  ✅ Step 5: Record saved and verified in database!")
            for i in range(rs.Fields.Count):
                f = rs.Fields(i)
                print(f"    {f.Name} = {f.Value!r}")
        rs.Close()

    finally:
        close(app)


if __name__ == "__main__":
    run_all()
