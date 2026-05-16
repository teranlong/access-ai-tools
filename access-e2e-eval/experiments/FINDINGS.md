# Access E2E Experimentation Lab — Findings

> **Date:** 2026-05-15  
> **Purpose:** Systematically evaluate approaches for human-like UI testing of Microsoft Access desktop applications from automated agent sessions.

---

## Executive Summary

We discovered that **Win32 `PostMessage(WM_CHAR)`** is the reliable path for typing into Access form controls from agent/remote sessions where `SendInput` and `SetCursorPos` are blocked. This approach was integrated into the evaluation suite's `AccessUiDriver`, achieving **13/14 tests passing** (the 1 failure is a known Access behavior, not an automation issue).

---

## Experiment Progression

### Phase 1: Baseline — Screenshot All Forms (`lab.py`)

**Goal:** Open every form in the database and capture screenshots to understand the visual layout.

**Results:**
- All 8 forms opened successfully via COM `DoCmd.OpenForm`
- Editor forms (CompanyEditor, UserEditor, etc.) render fields and Submit buttons correctly
- List/Lookup forms (CompanyList, CompanyUserLookup, UserList) render blank in the detail area — Datasheet view forms created programmatically don't auto-display columns

**Key finding:** The **Security Warning** banner ("Some active content has been disabled") is always present, indicating VBA macros are blocked. The Submit button's `[Event Procedure]` handler won't fire; the suite correctly falls back to the macro expression `=DoCmd.RunCommand(21)`.

**Evidence:** `211613_form_CompanyEditor.png` through `211620_form_TestFormDesignerCheck.png`

---

### Phase 2: Control Tree Dump (`lab.py`)

**Goal:** Map the full UIA control tree to understand what pywinauto can see and interact with.

**Results — UIA tree structure:**
```
Access Window (Dialog)
├── MsoDockTop → Business Bar → Security Warning → [Enable Content] button
├── Ribbon → Quick Access Toolbar, Tab controls, etc.
├── Workspace → CompanyEditor pane
│   ├── [Edit] 'Detail Section, CompanyName'
│   ├── [Edit] 'Industry'
│   ├── [Edit] 'Status', 'Phone', 'Email', 'City', 'State'
│   ├── [Button] 'Submit'
│   └── Record Navigator → First/Previous/Next/Last/New record buttons
├── Navigation Pane → Tables list, Forms list
├── Document Tabs → Tab for each open form
└── Status Bar → View buttons, Zoom slider
```

**Key finding:** All form controls are accessible via UIA with titles matching field names. The Record Navigator buttons ("First record", "New (blank) record", etc.) are individually addressable.

**Evidence:** `211725_control_tree.txt`

---

### Phase 3: Keyboard Input Failure Analysis (`lab.py`, `input_strategies.py`)

**Goal:** Type values into form fields and verify they reach the Access controls.

**Results — FAILURE for all standard approaches:**

| Approach | Result | Error |
|----------|--------|-------|
| pywinauto `send_keys()` | ❌ | `SendInput() inserted only 0 out of 2 keyboard events` |
| pywinauto `click_input()` | ❌ | `SetCursorPos: The system cannot find the file specified` (error 2) |
| pywinauto `type_keys()` on UIA control | ❌ | Same `SetCursorPos` error |
| pywinauto `set_text()` / `set_edit_text()` | ❌ | `Member not found` — Access controls don't support UIA ValuePattern |
| WScript.Shell `SendKeys` | ❌ | Characters not received by Access controls |
| .NET `System.Windows.Forms.SendKeys` | ❌ | Characters not received |
| `SetForegroundWindow` + `SendInput` | ❌ | `SendInput` still blocked even with foreground |

**Root cause:** The agent session environment blocks `SendInput()` and `SetCursorPos()` at the Windows API level. This is common in:
- Remote desktop sessions managed by agents
- Sessions where the input desktop isn't the interactive desktop
- DPI-scaled or multi-monitor configurations where cursor positioning fails

**Evidence:** `211742_after_typing_all_fields.png` (fields still show original data), `212320_foreground_test.png`

---

### Phase 4: Win32 Child Window Enumeration (`win32_input.py`)

**Goal:** Map the raw Win32 window hierarchy to find control handles.

**Results — Window class mapping:**

| Win32 Class | Count | Purpose |
|-------------|-------|---------|
| `OForm` | 1 | Access form container ("CompanyEditor") |
| `OFormSub` | 3 | Form sub-sections |
| `OKttbx` | 1 | **Access text box control** (shows "Contoso Health") |
| `OFEDT` | 1 | Access edit control variant |
| `OSUI` | 1 | Access SUI container |
| `RICHEDIT60W` | 2 | Record navigator ("1 of 2") and Search box |
| `MDIClient` | 1 | MDI container |
| `NetUIHWND` | 10 | Ribbon/UI framework controls |

**Key finding:** The `OKttbx` class is the Access form text box. When focused via COM `GoToControl`, `GetFocus()` (after `AttachThreadInput`) returns the `OKttbx` handle, and its `GetWindowText` returns the current field value.

---

### Phase 5: PostMessage Breakthrough (`win32_input.py`)

**Goal:** Test whether `PostMessage(WM_CHAR)` can bypass the `SendInput` block.

**Method:**
1. COM `GoToControl("Phone")` to focus the field
2. `AttachThreadInput` to access the UI thread
3. `GetFocus()` → returns `OKttbx` handle with text `'206-555-0100'`
4. `PostMessage(WM_CHAR, ch)` for each character

**Result: ✅ SUCCESS** — Win32 text buffer showed `'a555-POSTED'` (the 'a' was leftover because the initial clear method was incorrect).

**Key insight:** `PostMessage(WM_CHAR)` delivers characters directly to the control's message queue without going through `SendInput`. The Windows input security model blocks `SendInput` (which simulates hardware input) but allows `PostMessage` (which sends application-level messages).

**Follow-up finding:** The COM bound value didn't update immediately — Access only commits a control's value to the bound field when the control loses focus.

---

### Phase 6: Refined PostMessage Approach (`refined_postmsg.py`)

**Goal:** Build a complete, reliable input pipeline using PostMessage.

**Method:**
1. `EM_SETSEL(0, -1)` + `WM_CLEAR` to select-all and clear (replaces the failed Ctrl+A approach)
2. `PostMessage(WM_CHAR, ch)` for each character (15ms delay between chars)
3. COM `GoToControl(next_field)` to commit the current field's value

**Results — ALL 4 EXPERIMENTS PASSED:**

| Experiment | Result | Details |
|------------|--------|---------|
| Single field clear+type+verify | ✅ | Phone: `'206-555-0100'` → cleared → typed `'555-REFINED'` → committed → COM reads `'555-REFINED'` |
| Full form fill (7 fields) + save | ✅ | All 7 fields typed correctly, record saved and verified in database |
| Multi-form workflow (company → user) | ✅ | Created company (ID=2), switched to UserEditor, created user with correct CompanyID reference |
| Edit existing record | ✅ | Changed Phone and City on Fabrikam Logistics, verified in database |

**Evidence:** `212522_single_field.png`, `212535_full_form_before_save.png`, `212552_multi_form.png`, `212603_edit_existing.png`

---

### Phase 7: Integration into Test Suite

**Goal:** Replace the `send_keys`-only approach with PostMessage as the primary input method.

**Changes made:**
- `uia.py` — Rewrote `AccessUiDriver` to use PostMessage by default with SendInput fallback
- `uia.py` — Added `_commit_pending_value()` to flush the last field after `fill_form()`
- `uia.py` — Added layered `click_submit()`: pywinauto → `BM_CLICK` → `DoCmd.RunCommand` → COM `Dirty=False`
- `access_app.py` — Made `save_record()` and `refresh()` tolerate `SendInput` failures
- `test_access_e2e.py` — Updated `access_session` fixture to not skip when only `SendInput` fails
- `test_access_e2e.py` — Wrapped raw `send_keys` calls in try/except for SendInput resilience

**Result: 13 passed, 1 failed** (same known failure as before — `test_required_company_name_is_enforced`)

---

## Technical Reference

### The PostMessage Input Pipeline

```
COM GoToControl(field_name)       # Focus the target field
    ↓
AttachThreadInput(our_tid, access_tid)
    ↓
GetFocus() → OKttbx hwnd         # Get the Win32 control handle
    ↓
SendMessage(EM_SETSEL, 0, -1)    # Select all existing text
    ↓
SendMessage(WM_CLEAR)            # Delete selected text
    ↓
PostMessage(WM_CHAR, 'H')        # Type 'H'
PostMessage(WM_CHAR, 'e')        # Type 'e'
PostMessage(WM_CHAR, 'l')        # ...character by character
    ↓
COM GoToControl(next_field)       # Commit: focus change triggers AfterUpdate
```

### Why PostMessage Works When SendInput Doesn't

| API | Mechanism | Blocked in agent sessions? |
|-----|-----------|---------------------------|
| `SendInput` | Injects hardware-level input events into the global input queue | **YES** — requires UIPI elevation and active input desktop |
| `SetCursorPos` | Moves the physical mouse cursor | **YES** — requires input desktop access |
| `PostMessage(WM_CHAR)` | Posts a message to a specific window's message queue | **NO** — only needs a valid window handle |
| `SendMessage(EM_SETSEL)` | Sends a synchronous message to the control | **NO** — direct message delivery |

### Access Control Class Hierarchy

```
OForm (form container, e.g., "CompanyEditor")
├── OFormSub (form sections)
│   └── OKttbx (text box controls — field values live here)
│   └── OFEDT (edit controls)
├── OSUI → RecNavHost → RICHEDIT60W (record navigator)
└── NUIScrollbar (scroll bars)
```

### Key Win32 Constants Used

```python
WM_CHAR    = 0x0102   # Character input message
EM_SETSEL  = 0x00B1   # Select text range in edit control
WM_CLEAR   = 0x0303   # Clear selected text
BM_CLICK   = 0x00F5   # Click a button control
WM_KEYDOWN = 0x0100   # Key press (for special keys like Space)
WM_KEYUP   = 0x0101   # Key release
```

---

## Approaches That Failed (and Why)

| Approach | Why It Failed |
|----------|---------------|
| `send_keys()` (pywinauto) | Uses `SendInput` internally — blocked by UIPI in agent sessions |
| `click_input()` (pywinauto) | Calls `SetCursorPos` before clicking — blocked |
| `set_text()` / `set_edit_text()` | Access controls don't expose UIA `IValueProvider` |
| `WScript.Shell.SendKeys` | Uses `SendInput` internally under the hood |
| `.NET SendKeys.SendWait()` | Same — wraps `SendInput` |
| `SetForegroundWindow` + retry | `SendInput` is blocked regardless of foreground status |
| Clicking "Enable Content" button | Triggered form to reopen in Design View, breaking all subsequent operations |

---

## Recommendations for Future Work

1. **Checkbox toggling** — Currently uses `PostMessage(WM_KEYDOWN, VK_SPACE)`. Should verify this works for all checkbox states (checked → unchecked, unchecked → checked).

2. **Combo box / dropdown support** — Access combo boxes (`OKttbx` variant or dedicated class) may need a different PostMessage strategy. Test with `CB_SETCURSEL` or typed text + `WM_KEYDOWN(VK_RETURN)`.

3. **Dialog detection and dismissal** — Error dialogs (e.g., duplicate key violations) need detection. Approach: enumerate top-level windows after save, look for dialog class windows, read button text, and click OK/Cancel via `BM_CLICK`.

4. **Visual regression testing** — The `pixel_diff_before_after` experiment showed pixel-diff capability. Could be extended to golden-image comparison for form layout validation.

5. **Datasheet view forms** — List forms (CompanyList, UserList, CompanyUserLookup) render blank because programmatic form creation doesn't add datasheet columns. Investigate adding `AllowDatasheetView` or using `DatasheetView` property during build.

6. **CI integration** — PostMessage works without an interactive desktop, making headless CI possible. Test on a Windows CI runner (GitHub Actions `windows-latest` with Access installed).
