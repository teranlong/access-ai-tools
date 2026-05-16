"""
Access E2E Experimentation Lab
==============================
Rapid-iteration script for testing human-like UI automation approaches
against a live Access application. Each experiment is a small, independent
function that opens Access, tries something, captures evidence (screenshots,
control dumps, COM state), then tears down.

Usage:
    cd access-e2e-eval
    .\.venv\Scripts\Activate.ps1
    python experiments\lab.py [experiment_name ...]

    # Run all experiments:
    python experiments\lab.py

    # Run specific ones:
    python experiments\lab.py screenshot_forms tab_navigation
"""
from __future__ import annotations

import datetime
import json
import os
import shutil
import sys
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# Ensure the parent package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from access_eval_suite.config import DEFAULT_DATABASE, AccessEvalConfig
from access_eval_suite import constants as ac

EVIDENCE_DIR = Path(__file__).resolve().parent / "evidence"
EVIDENCE_DIR.mkdir(exist_ok=True)

# ── Helpers ──────────────────────────────────────────────────────────────────

def timestamp() -> str:
    return datetime.datetime.now().strftime("%H%M%S")


def screenshot(label: str) -> Path | None:
    """Capture full-screen screenshot and save to evidence folder."""
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab()
        path = EVIDENCE_DIR / f"{timestamp()}_{label}.png"
        img.save(str(path))
        print(f"  📸 Screenshot saved: {path.name}")
        return path
    except Exception as exc:
        print(f"  ⚠️  Screenshot failed: {exc}")
        return None


def screenshot_window(window, label: str) -> Path | None:
    """Capture just the Access window."""
    try:
        from PIL import ImageGrab
        rect = window.rectangle()
        img = ImageGrab.grab(bbox=(rect.left, rect.top, rect.right, rect.bottom))
        path = EVIDENCE_DIR / f"{timestamp()}_{label}.png"
        img.save(str(path))
        print(f"  📸 Window screenshot saved: {path.name}")
        return path
    except Exception as exc:
        print(f"  ⚠️  Window screenshot failed: {exc}")
        return None


def fresh_db_copy() -> Path:
    """Copy the built database to a temp location for isolated experiments."""
    dest = EVIDENCE_DIR / f"exp_{timestamp()}.accdb"
    shutil.copy2(DEFAULT_DATABASE, dest)
    return dest


def open_access_session(db_path: Path, startup_form: str = "CompanyList"):
    """Open Access via COM + pywinauto, return (com_app, pywinauto_window)."""
    import win32com.client
    from pywinauto import Desktop

    app = win32com.client.Dispatch("Access.Application")
    try:
        app.Visible = True
    except Exception:
        pass
    app.OpenCurrentDatabase(str(db_path))
    app.DoCmd.OpenForm(startup_form)
    time.sleep(1.5)

    handle = app.hWndAccessApp
    if callable(handle):
        handle = handle()

    window = None
    for backend in ("uia", "win32"):
        try:
            w = Desktop(backend=backend).window(handle=handle)
            w.wait("visible ready", timeout=10)
            window = w
            break
        except Exception:
            continue

    if window is None:
        app.Quit(ac.AC_QUIT_SAVE_NONE)
        raise RuntimeError("Could not attach pywinauto to Access window")

    return app, window


def close_access(app):
    try:
        app.CloseCurrentDatabase()
    except Exception:
        pass
    try:
        app.Quit(ac.AC_QUIT_SAVE_NONE)
    except Exception:
        pass
    time.sleep(1)


def cleanup_lock(db_path: Path):
    lock = db_path.with_suffix(".laccdb")
    for _ in range(10):
        if not lock.exists():
            return
        time.sleep(0.5)
    try:
        lock.unlink()
    except OSError:
        pass


# ── Experiment registry ──────────────────────────────────────────────────────

@dataclass
class ExperimentResult:
    name: str
    success: bool
    duration_ms: int
    findings: list[str] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)
    error: str | None = None


_registry: dict[str, Callable[[], ExperimentResult]] = {}


def experiment(fn):
    _registry[fn.__name__] = fn
    return fn


# ══════════════════════════════════════════════════════════════════════════════
#   EXPERIMENTS
# ══════════════════════════════════════════════════════════════════════════════

@experiment
def screenshot_all_forms() -> ExperimentResult:
    """Open every form in the database and screenshot it."""
    findings = []
    shots = []
    db = fresh_db_copy()
    app, window = open_access_session(db)
    try:
        forms = [
            "CompanyEditor", "UserEditor", "ContactEditor", "CaseEditor",
            "CompanyUserLookup", "CompanyList", "UserList", "TestFormDesignerCheck",
        ]
        for form_name in forms:
            try:
                app.DoCmd.OpenForm(form_name, ac.AC_NORMAL)
                time.sleep(0.8)
                window.set_focus()
                s = screenshot_window(window, f"form_{form_name}")
                if s:
                    shots.append(s.name)
                findings.append(f"✅ {form_name} opened successfully")
                app.DoCmd.Close(ac.AC_FORM, form_name, ac.AC_SAVE_NO)
            except Exception as exc:
                findings.append(f"❌ {form_name} failed: {exc}")
        return ExperimentResult("screenshot_all_forms", True, 0, findings, shots)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def control_tree_dump() -> ExperimentResult:
    """Dump the full UIA control tree of CompanyEditor to understand what pywinauto sees."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        # Dump control tree
        tree_path = EVIDENCE_DIR / f"{timestamp()}_control_tree.txt"
        with open(tree_path, "w", encoding="utf-8") as f:
            import io
            buf = io.StringIO()
            window.print_control_identifiers(filename=None)
            # Fallback: manually walk the tree
            def walk_tree(ctrl, depth=0):
                try:
                    info = f"{'  '*depth}[{ctrl.friendly_class_name()}] '{ctrl.window_text()}'"
                    f.write(info + "\n")
                except Exception:
                    f.write(f"{'  '*depth}[???]\n")
                try:
                    for child in ctrl.children():
                        walk_tree(child, depth + 1)
                except Exception:
                    pass
            walk_tree(window)
        findings.append(f"Control tree dumped to {tree_path.name}")

        # Also try to enumerate controls via COM
        try:
            form = app.Screen.ActiveForm
            com_controls = []
            for i in range(form.Controls.Count):
                ctrl = form.Controls(i)
                com_controls.append(f"  [{ctrl.ControlType}] {ctrl.Name} = {ctrl.Value!r}")
            com_path = EVIDENCE_DIR / f"{timestamp()}_com_controls.txt"
            com_path.write_text("\n".join(com_controls), encoding="utf-8")
            findings.append(f"COM controls ({form.Controls.Count}) dumped to {com_path.name}")
        except Exception as exc:
            findings.append(f"COM control enum failed: {exc}")

        screenshot_window(window, "control_tree_form")
        return ExperimentResult("control_tree_dump", True, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def tab_navigation() -> ExperimentResult:
    """Test Tab-key navigation through CompanyEditor fields.
    Tab through each field, read the focused control name via COM after each tab."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys

        app.DoCmd.GoToControl("CompanyName")
        time.sleep(0.3)
        window.set_focus()

        expected_order = ["CompanyName", "Industry", "Status", "Phone", "Email", "City", "State", "btnSubmit"]
        actual_order = []

        for i in range(len(expected_order)):
            try:
                active_ctrl = app.Screen.ActiveForm.ActiveControl.Name
                actual_order.append(active_ctrl)
            except Exception:
                actual_order.append("???")
            send_keys("{TAB}")
            time.sleep(0.2)

        findings.append(f"Expected tab order: {expected_order}")
        findings.append(f"Actual tab order:   {actual_order}")
        match_count = sum(1 for e, a in zip(expected_order, actual_order) if e == a)
        findings.append(f"Tab order match: {match_count}/{len(expected_order)}")

        return ExperimentResult("tab_navigation", match_count > 0, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def keyboard_type_and_verify() -> ExperimentResult:
    """Type into every field on CompanyEditor and verify each one via COM before saving."""
    findings = []
    shots = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys
        import pythoncom

        # Go to new record
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)
        window.set_focus()

        test_values = {
            "CompanyName": "Experiment Corp",
            "Industry": "Research",
            "Status": "Active",
            "Phone": "555-0199",
            "Email": "exp@test.example",
            "City": "Lab City",
            "State": "CA",
        }

        for ctrl_name, value in test_values.items():
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            window.set_focus()
            send_keys("^a{BACKSPACE}")
            send_keys(value, with_spaces=True, pause=0.02)
            time.sleep(0.3)

            # Immediately verify via COM what the control holds
            try:
                form = app.Screen.ActiveForm
                actual = str(form.Controls(ctrl_name).Value or "")
                match = actual == value
                findings.append(f"  {ctrl_name}: typed={value!r}, COM reads={actual!r}, match={match}")
            except Exception as exc:
                findings.append(f"  {ctrl_name}: typed={value!r}, COM read failed: {exc}")

        s = screenshot_window(window, "after_typing_all_fields")
        if s:
            shots.append(s.name)

        # Now save via button click
        try:
            btn = window.child_window(title="Submit", control_type="Button")
            btn.wait("visible ready", timeout=5)
            btn.click_input()
            time.sleep(1)
            findings.append("✅ Submit button clicked")
        except Exception as exc:
            findings.append(f"⚠️  Submit button click failed: {exc}, using COM save")
            try:
                form = app.Screen.ActiveForm
                if form.Dirty:
                    form.Dirty = False
                    time.sleep(0.5)
            except Exception:
                pass

        s2 = screenshot_window(window, "after_submit")
        if s2:
            shots.append(s2.name)

        # Verify in database
        rows = app.CurrentDb().OpenRecordset(
            "SELECT * FROM Companies WHERE CompanyName = 'Experiment Corp'"
        )
        if rows.EOF:
            findings.append("❌ Record NOT found in database after save")
            return ExperimentResult("keyboard_type_and_verify", False, 0, findings, shots)
        else:
            findings.append("✅ Record found in database after save")
            return ExperimentResult("keyboard_type_and_verify", True, 0, findings, shots)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def read_form_values_via_uia() -> ExperimentResult:
    """Try reading form field values through pywinauto UIA (not COM).
    This tests whether we can do screen-reader style value extraction."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        # Navigate to first record (Contoso Health)
        app.DoCmd.OpenForm("CompanyEditor", ac.AC_NORMAL, "", "CompanyID = 1")
        time.sleep(0.8)
        window.set_focus()

        # Try various UIA approaches to read control values
        # Approach 1: child_window by automation_id / title
        for ctrl_name in ["CompanyName", "Industry", "Status", "Phone", "Email", "City", "State"]:
            uia_value = None
            approaches_tried = []

            # Try by title
            try:
                ctrl = window.child_window(title=ctrl_name, control_type="Edit")
                uia_value = ctrl.get_value()
                approaches_tried.append(f"title+Edit: {uia_value!r}")
            except Exception:
                approaches_tried.append("title+Edit: FAIL")

            # Try by automation_id
            try:
                ctrl = window.child_window(auto_id=ctrl_name)
                uia_value = ctrl.get_value() if hasattr(ctrl, 'get_value') else str(ctrl.window_text())
                approaches_tried.append(f"auto_id: {uia_value!r}")
            except Exception:
                approaches_tried.append("auto_id: FAIL")

            # COM reference value
            try:
                com_val = app.Screen.ActiveForm.Controls(ctrl_name).Value
                approaches_tried.append(f"COM: {com_val!r}")
            except Exception:
                approaches_tried.append("COM: FAIL")

            findings.append(f"  {ctrl_name}: {' | '.join(approaches_tried)}")

        return ExperimentResult("read_form_values_via_uia", True, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def dialog_and_error_handling() -> ExperimentResult:
    """Intentionally trigger Access dialogs/errors and see how we can detect and dismiss them.
    This is critical for human-like testing — real users encounter error popups."""
    findings = []
    shots = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "UserEditor")
    try:
        from pywinauto.keyboard import send_keys
        import pythoncom
        from pywinauto import Desktop

        # Try to save a record with a duplicate email (should trigger unique index error)
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)
        window.set_focus()

        fields = {
            "CompanyID": "1",
            "FirstName": "Duplicate",
            "LastName": "Test",
            "Email": "avery.stone@contoso.example",  # Already exists
            "Role": "Tester",
            "Status": "Active",
        }
        for ctrl_name, value in fields.items():
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            window.set_focus()
            send_keys("^a{BACKSPACE}")
            send_keys(str(value), with_spaces=True, pause=0.02)
            time.sleep(0.2)

        # Try to save — this should trigger a duplicate key error dialog
        send_keys("^s")
        time.sleep(1.5)

        s = screenshot(f"dialog_test_after_save")
        if s:
            shots.append(s.name)

        # Try to find any dialog/popup windows
        desktop = Desktop(backend="uia")
        all_windows = desktop.windows()
        for w in all_windows:
            try:
                title = w.window_text()
                if title and "Access" in title or "Microsoft" in title or "Error" in title:
                    findings.append(f"Found window: {title!r} (handle={w.handle})")
            except Exception:
                pass

        # Try to detect and dismiss dialog via Escape or clicking buttons
        try:
            # Look for dialog children in Access window
            dialogs = window.children(control_type="Window")
            for d in dialogs:
                findings.append(f"Dialog child: {d.window_text()!r}")
        except Exception:
            pass

        # Try Escape to dismiss any dialog
        window.set_focus()
        send_keys("{ESC}")
        time.sleep(0.5)
        send_keys("{ESC}")
        time.sleep(0.5)

        s2 = screenshot(f"dialog_test_after_dismiss")
        if s2:
            shots.append(s2.name)

        findings.append("Dialog detection experiment complete")
        return ExperimentResult("dialog_and_error_handling", True, 0, findings, shots)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def multi_form_workflow() -> ExperimentResult:
    """Simulate a real multi-step workflow: create company → create user for that company.
    This tests form switching, referencing IDs across forms, and maintaining state."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys
        import pythoncom

        # Step 1: Create a new company
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)
        window.set_focus()

        company_data = {
            "CompanyName": "Workflow Labs",
            "Industry": "Technology",
            "Status": "Active",
            "Phone": "555-WORK",
            "Email": "hello@workflow.example",
            "City": "Austin",
            "State": "TX",
        }
        for ctrl_name, value in company_data.items():
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            window.set_focus()
            send_keys("^a{BACKSPACE}")
            send_keys(value, with_spaces=True, pause=0.02)
            time.sleep(0.15)

        # Save via Submit
        try:
            btn = window.child_window(title="Submit", control_type="Button")
            btn.click_input()
            time.sleep(1)
            findings.append("✅ Step 1: Company form submitted")
        except Exception:
            try:
                form = app.Screen.ActiveForm
                if form.Dirty:
                    form.Dirty = False
                    time.sleep(0.5)
            except Exception:
                pass
            findings.append("⚠️ Step 1: Used COM fallback save")

        # Get the new company's ID
        rs = app.CurrentDb().OpenRecordset(
            "SELECT CompanyID FROM Companies WHERE CompanyName = 'Workflow Labs'"
        )
        if rs.EOF:
            findings.append("❌ Company not found after save — aborting workflow")
            return ExperimentResult("multi_form_workflow", False, 0, findings)
        new_company_id = rs.Fields("CompanyID").Value
        rs.Close()
        findings.append(f"✅ Step 2: New company ID = {new_company_id}")

        # Step 3: Switch to UserEditor and create a user for that company
        app.DoCmd.OpenForm("UserEditor", ac.AC_NORMAL)
        time.sleep(0.8)
        window.set_focus()

        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)
        window.set_focus()

        user_data = {
            "CompanyID": str(new_company_id),
            "FirstName": "Workflow",
            "LastName": "Tester",
            "Email": "workflow.tester@workflow.example",
            "Role": "Automation",
            "Status": "Active",
        }
        for ctrl_name, value in user_data.items():
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            window.set_focus()
            send_keys("^a{BACKSPACE}")
            send_keys(value, with_spaces=True, pause=0.02)
            time.sleep(0.15)

        try:
            btn = window.child_window(title="Submit", control_type="Button")
            btn.click_input()
            time.sleep(1)
            findings.append("✅ Step 3: User form submitted")
        except Exception:
            try:
                form = app.Screen.ActiveForm
                if form.Dirty:
                    form.Dirty = False
                    time.sleep(0.5)
            except Exception:
                pass
            findings.append("⚠️ Step 3: Used COM fallback save")

        # Step 4: Verify the full chain via database query
        rs = app.CurrentDb().OpenRecordset(
            f"SELECT Users.Email FROM Users WHERE Users.CompanyID = {new_company_id}"
        )
        if rs.EOF:
            findings.append("❌ No users found for new company")
            return ExperimentResult("multi_form_workflow", False, 0, findings)
        user_email = rs.Fields("Email").Value
        rs.Close()
        findings.append(f"✅ Step 4: Found user {user_email} linked to company {new_company_id}")

        # Step 5: Verify via the lookup form
        app.DoCmd.OpenForm("CompanyUserLookup")
        time.sleep(0.8)
        screenshot_window(window, "workflow_lookup")
        findings.append("✅ Step 5: CompanyUserLookup opened for visual verification")

        return ExperimentResult("multi_form_workflow", True, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def pixel_diff_before_after() -> ExperimentResult:
    """Screenshot a form before and after an edit, then compute a pixel diff
    to demonstrate visual regression testing capability."""
    findings = []
    shots = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys
        from PIL import Image, ImageChops

        app.DoCmd.OpenForm("CompanyEditor", ac.AC_NORMAL, "", "CompanyID = 1")
        time.sleep(0.8)
        window.set_focus()

        before = screenshot_window(window, "pixdiff_before")
        if before:
            shots.append(before.name)

        # Edit a field
        app.DoCmd.GoToControl("Phone")
        time.sleep(0.2)
        window.set_focus()
        send_keys("^a{BACKSPACE}")
        send_keys("999-CHANGED", with_spaces=True, pause=0.02)
        time.sleep(0.5)

        after = screenshot_window(window, "pixdiff_after")
        if after:
            shots.append(after.name)

        # Compute diff
        if before and after:
            img_before = Image.open(str(before))
            img_after = Image.open(str(after))
            diff = ImageChops.difference(img_before, img_after)
            diff_path = EVIDENCE_DIR / f"{timestamp()}_pixdiff_result.png"
            diff.save(str(diff_path))
            shots.append(diff_path.name)

            # Count changed pixels
            bbox = diff.getbbox()
            if bbox:
                findings.append(f"✅ Visual change detected in region: {bbox}")
            else:
                findings.append("⚠️ No pixel difference detected (unexpected)")
        else:
            findings.append("⚠️ Could not capture both screenshots for diff")

        return ExperimentResult("pixel_diff_before_after", True, 0, findings, shots)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def send_keys_special_chars() -> ExperimentResult:
    """Test how pywinauto handles special characters that Access might interpret:
    parentheses, curly braces, @, #, etc. — common pain points."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys
        import pythoncom

        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.5)
        window.set_focus()

        # Test special characters in different fields
        test_cases = [
            ("CompanyName", "O'Brien & Sons (West)"),
            ("Industry", "Tech/Bio-Med"),
            ("Status", "Active"),
            ("Phone", "+1 (206) 555-0100"),
            ("Email", "test+tag@example.org"),
            ("City", "St. Louis"),
            ("State", "MO"),
        ]

        for ctrl_name, value in test_cases:
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.1)
            window.set_focus()
            send_keys("^a{BACKSPACE}")
            # For special chars, use with_spaces=True
            send_keys(value, with_spaces=True, pause=0.02)
            time.sleep(0.3)

            # Read back via COM
            try:
                actual = str(app.Screen.ActiveForm.Controls(ctrl_name).Value or "")
                match = actual == value
                status = "✅" if match else "❌"
                findings.append(f"  {status} {ctrl_name}: sent={value!r}, got={actual!r}")
            except Exception as exc:
                findings.append(f"  ⚠️ {ctrl_name}: sent={value!r}, read error: {exc}")

        return ExperimentResult("send_keys_special_chars", True, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def com_vs_keyboard_speed() -> ExperimentResult:
    """Benchmark: fill a form entirely via COM (set Value) vs entirely via keyboard.
    Measures the human-likeness vs speed tradeoff."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys
        import pythoncom

        test_data = {
            "CompanyName": "Speed Test Corp",
            "Industry": "Benchmarks",
            "Status": "Active",
            "Phone": "555-FAST",
            "Email": "speed@test.example",
            "City": "FastCity",
            "State": "WA",
        }

        # Method 1: Pure COM (not human-like, but fast)
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.3)
        t0 = time.perf_counter()
        form = app.Screen.ActiveForm
        for ctrl_name, value in test_data.items():
            form.Controls(ctrl_name).Value = value
        form.Dirty = False
        time.sleep(0.3)
        com_time = (time.perf_counter() - t0) * 1000
        findings.append(f"COM-only fill+save: {com_time:.0f}ms")

        # Delete the record we just created
        app.CurrentDb().Execute(
            "DELETE FROM Companies WHERE CompanyName = 'Speed Test Corp'",
            ac.DAO_FAIL_ON_ERROR,
        )

        # Method 2: Pure keyboard (human-like)
        app.DoCmd.GoToRecord(pythoncom.Missing, pythoncom.Missing, ac.AC_NEW_REC)
        time.sleep(0.3)
        window.set_focus()
        t0 = time.perf_counter()
        for ctrl_name, value in test_data.items():
            app.DoCmd.GoToControl(ctrl_name)
            time.sleep(0.05)
            window.set_focus()
            send_keys("^a{BACKSPACE}")
            send_keys(str(value), with_spaces=True, pause=0.01)
            time.sleep(0.05)
        # Save via submit button
        try:
            btn = window.child_window(title="Submit", control_type="Button")
            btn.click_input()
            time.sleep(0.5)
        except Exception:
            form = app.Screen.ActiveForm
            if form.Dirty:
                form.Dirty = False
                time.sleep(0.3)
        keyboard_time = (time.perf_counter() - t0) * 1000
        findings.append(f"Keyboard fill+submit: {keyboard_time:.0f}ms")
        findings.append(f"Keyboard is {keyboard_time / max(com_time, 1):.1f}x slower than COM")
        findings.append(f"But keyboard exercises the real UI path a human would use")

        return ExperimentResult("com_vs_keyboard_speed", True, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


@experiment
def record_navigation() -> ExperimentResult:
    """Test navigating between records using keyboard shortcuts like a human:
    Ctrl+Home, Ctrl+End, Page Down, navigation bar."""
    findings = []
    db = fresh_db_copy()
    app, window = open_access_session(db, "CompanyEditor")
    try:
        from pywinauto.keyboard import send_keys

        app.DoCmd.OpenForm("CompanyEditor", ac.AC_NORMAL)
        time.sleep(0.8)
        window.set_focus()

        # Read current record
        def current_company():
            try:
                return str(app.Screen.ActiveForm.Controls("CompanyName").Value or "")
            except Exception:
                return "???"

        findings.append(f"Initial record: {current_company()!r}")

        # Navigate to next record via keyboard
        send_keys("^{PGDN}")  # Ctrl+PageDown = next record in some views
        time.sleep(0.5)
        findings.append(f"After Ctrl+PgDn: {current_company()!r}")

        # Navigate to first record
        send_keys("^{HOME}")
        time.sleep(0.5)
        findings.append(f"After Ctrl+Home: {current_company()!r}")

        # Navigate to last record
        send_keys("^{END}")
        time.sleep(0.5)
        findings.append(f"After Ctrl+End: {current_company()!r}")

        # Try using the Access navigation bar at the bottom
        # The "Next Record" button in Access is typically accessible
        try:
            nav_buttons = window.children(title_re=".*Next.*|.*record.*", control_type="Button")
            findings.append(f"Found {len(nav_buttons)} navigation-like buttons")
            for b in nav_buttons:
                findings.append(f"  Nav button: {b.window_text()!r}")
        except Exception as exc:
            findings.append(f"Nav button search: {exc}")

        return ExperimentResult("record_navigation", True, 0, findings)
    finally:
        close_access(app)
        cleanup_lock(db)


# ══════════════════════════════════════════════════════════════════════════════
#   RUNNER
# ══════════════════════════════════════════════════════════════════════════════

def run_experiments(names: list[str] | None = None) -> list[ExperimentResult]:
    if names:
        to_run = {n: _registry[n] for n in names if n in _registry}
        unknown = [n for n in names if n not in _registry]
        if unknown:
            print(f"⚠️  Unknown experiments: {unknown}")
            print(f"   Available: {list(_registry.keys())}")
    else:
        to_run = _registry

    results = []
    print(f"\n{'='*60}")
    print(f"  Access E2E Experimentation Lab — {len(to_run)} experiments")
    print(f"  Evidence dir: {EVIDENCE_DIR}")
    print(f"{'='*60}\n")

    for name, fn in to_run.items():
        print(f"▶ {name}")
        print(f"  {fn.__doc__.strip() if fn.__doc__ else 'No description'}")
        t0 = time.perf_counter()
        try:
            result = fn()
            result.duration_ms = int((time.perf_counter() - t0) * 1000)
        except Exception as exc:
            result = ExperimentResult(
                name=name,
                success=False,
                duration_ms=int((time.perf_counter() - t0) * 1000),
                error=traceback.format_exc(),
            )
        results.append(result)

        status = "✅ PASS" if result.success else "❌ FAIL"
        print(f"  {status} ({result.duration_ms}ms)")
        for f in result.findings:
            print(f"    {f}")
        if result.error:
            print(f"    ERROR: {result.error[:300]}")
        print()

    # Summary
    passed = sum(1 for r in results if r.success)
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{len(results)} passed")
    print(f"{'='*60}")

    # Save JSON report
    report = {
        "timestamp": datetime.datetime.now().isoformat(),
        "experiments": [
            {
                "name": r.name,
                "success": r.success,
                "duration_ms": r.duration_ms,
                "findings": r.findings,
                "screenshots": r.screenshots,
                "error": r.error,
            }
            for r in results
        ],
    }
    report_path = EVIDENCE_DIR / f"{timestamp()}_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"  Report saved: {report_path}")

    return results


if __name__ == "__main__":
    names = sys.argv[1:] if len(sys.argv) > 1 else None
    run_experiments(names)
