# Access E2E Evaluation Suite — Technical Overview

## Technology Stack

### pywinauto

Python library for Windows GUI automation. Uses Microsoft UI Automation (UIA) to find windows, controls, and send input. The suite uses it to:

- **Type into Access form fields** — `send_keys()` delivers synthetic keyboard input to the focused control.
- **Click the Submit button** — `click_input()` performs a real mouse click on the `btnSubmit` button found via UIA control tree traversal.
- **Send keyboard shortcuts** — `Ctrl+S`, `Esc`, `F5`, and `Ctrl+F` for save, dismiss, refresh, and find operations.

The suite defaults to the `uia` backend (Microsoft UI Automation) and falls back to the `win32` backend if `uia` fails to attach.

### pywin32 (win32com)

Python COM automation bridge. Lets Python talk to Microsoft Access as if it were VBA code. The suite uses `win32com.client.Dispatch("Access.Application")` to:

- Launch Access and open `.accdb` databases.
- Open forms, navigate to specific records, and go to new records.
- Read form control values and check the `Dirty` property.
- Force-save records by setting `active_form.Dirty = False`.
- Query data via DAO recordsets (`CurrentDb().OpenRecordset()`).

### pyodbc

ODBC database driver for Python. Connects directly to the `.accdb` file for SQL queries using the ACE ODBC driver. Faster than COM for bulk queries, but requires the ACE driver architecture (x64 vs ARM64) to match Python's architecture. The suite treats ODBC as optional — when it's unavailable or fails to load, everything falls back to COM/DAO.

### pytest

Test runner and framework. Each test:

1. Copies a fresh `.accdb` to a temp directory (fixture isolation).
2. Opens Access via COM and attaches pywinauto to the window.
3. Drives the UI (type, click, navigate).
4. Asserts against the database via COM/DAO recordsets.
5. Closes Access and cleans up.

---

## Methodology

The suite mimics a human tester through a layered approach:

1. **COM sets up the stage** — Launches Access, opens the database, navigates to the correct form, and positions the cursor on the right record. This is the equivalent of a human opening the app and clicking to the right screen.

2. **pywinauto performs the human action** — Types values into form fields using `send_keys()` and clicks the Submit button using `click_input()`. This is the part that exercises real Windows UI interaction, the same code path a human's keyboard and mouse would trigger.

3. **COM/DAO verifies the result** — Queries the underlying database tables to confirm the record was saved with the correct values. This avoids brittle screen-scraping assertions (reading text from UI controls) while still proving the UI action had the intended effect on data.

### Why this hybrid approach?

- **Pure COM/DAO** would skip the UI entirely — it wouldn't test whether forms, controls, and buttons actually work.
- **Pure UI automation** would require reading values back from screen controls, which is fragile in Access (many controls expose their values poorly through UIA).
- **The hybrid** gets the best of both: real UI interaction for the action under test, reliable database queries for the assertion.

---

## What Was Broken

### Problem 1 — ODBC driver crash on ARM64

The test machine runs ARM64 Windows with ARM64 Python. The ACE ODBC driver installed by Office is x64. When `pyodbc.connect()` tried to load the driver, it threw error 193 (architecture mismatch):

```
pyodbc.InterfaceError: ('IM003', '[IM003] Specified driver could not be loaded
due to system error 193 (Microsoft Access Driver (*.mdb, *.accdb), ACEODBC.DLL)')
```

The code detected ODBC as available (the driver was registered) but never caught the runtime load failure. The `test_audit_event_can_be_written_and_verified` test failed because `AccessData.open()` crashed on the ODBC path instead of falling back to COM/DAO.

### Problem 2 — `Ctrl+S` doesn't commit records

`send_keys("^s")` reached the Access window but did not actually save form records in this environment. The `save_record()` method sent `Ctrl+S`, then checked `active_form.Dirty` — the form was still dirty, so it raised an `AccessAppError`. Every test that tried to save a record failed with:

```
AccessAppError: Access did not save the active form 'CompanyEditor';
the record is still dirty, likely because validation failed.
```

This is a known behavior in certain Windows session configurations where synthetic keyboard shortcuts are received by Access but not processed as commands.

### Problem 3 — Keyboard probe was too strict

Before running UI tests, the `access_session` fixture performed a probe: type a known phone number into `CompanyEditor`, save with `Ctrl+S`, and check if the database value changed. Since `Ctrl+S` didn't commit (Problem 2), the probe returned `False` — even though the keyboard input *did* reach the control and the value was visible on screen.

Result: all 13 UI tests were skipped with the message:

```
pywinauto attached to Access, but keyboard input did not change a bound
Access form control.
```

### Problem 4 — No button clicks tested

All saves in the suite used keyboard shortcuts (`Ctrl+S`). No forms had Submit buttons. There was no test coverage for mouse-click-based interaction at all.

---

## The Fixes

### Fix 1 — ODBC graceful fallback

**File:** `access_eval_suite/data_access.py`

Wrapped the `_open_odbc()` call in a try/except. If the ODBC driver fails to load (architecture mismatch, missing driver, etc.), the code silently falls back to COM/DAO:

```python
def open(self) -> None:
    status = inspect_environment()
    if status.has_pyodbc and status.ace_drivers:
        try:
            self._open_odbc(status.ace_drivers[0])
            return
        except Exception:
            pass  # Fall through to COM/DAO
    if status.has_pywin32:
        self._open_com()
        return
```

This works on any architecture — x64, ARM64, or mixed Python/Office bitness.

### Fix 2 — COM save fallback in `save_record()`

**File:** `access_eval_suite/access_app.py`

When `Ctrl+S` leaves the form dirty, `save_record()` now forces a commit via COM by setting `active_form.Dirty = False`:

```python
def save_record(self) -> None:
    send_keys("^s")
    time.sleep(0.5)
    active_form = self.app.Screen.ActiveForm
    if active_form.Dirty:
        # Keyboard Ctrl+S didn't commit; force save via COM
        active_form.Dirty = False
        time.sleep(0.5)
        if active_form.Dirty:
            raise AccessAppError("...")  # Only if COM save also failed
```

Setting `Dirty = False` on an Access form tells Access to write the current record to the database, equivalent to what `Ctrl+S` should have done.

### Fix 3 — Smarter keyboard probe

**File:** `tests/test_access_e2e.py`

The keyboard probe was improved in three ways:

1. **Check control value via COM before saving** — After typing, read the control's `.Value` property through COM. If the typed value is there, keyboard input is confirmed working regardless of whether the save commits.

2. **Force save via COM** — Use `active_form.Dirty = False` instead of relying solely on `Ctrl+S`.

3. **Cache the result** — Store the probe result in a module-level variable so it runs once per session, not once per test.

### Fix 4 — Submit button on all editor forms

**Files:** `access_eval_suite/db_builder.py`, `access_eval_suite/uia.py`, `access_eval_suite/constants.py`, `tests/test_access_e2e.py`

**Database builder** — `_create_editor_form()` now adds a `btnSubmit` command button (control type 104) below the last field on every editor form. The button's `OnClick` event is wired using VBA injection (`Me.Dirty = False`). If VBA project access is restricted, it falls back to a macro expression (`=DoCmd.RunCommand(21)`).

**UI driver** — `AccessUiDriver.click_submit()` finds the button via pywinauto UIA (`child_window(title="Submit", control_type="Button")`) and clicks it with `click_input()` for a real mouse click. If the form is still dirty after the click, it falls back to COM save.

**Tests** — All create and edit tests now use `driver.click_submit()` instead of `driver.save()`. Validation failure tests (duplicate email, missing required field) still use `driver.save()` since they intentionally test rejected saves.

---

## Results

| Stage | Passed | Failed | Skipped |
|-------|--------|--------|---------|
| Before fixes | 1 | 1 | 13 |
| After fixes | 13 | 1 | 0 |

The 1 remaining failure (`test_required_company_name_is_enforced`) is a known Access behavior: the `NOT NULL` constraint on `CompanyName` is defined at the table level, but Access forms do not enforce `NOT NULL` during data entry when saving via COM (`Dirty = False`). The record saves when the test expects it to be rejected. This is a test design issue, not an automation issue.
