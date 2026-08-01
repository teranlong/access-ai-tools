# Handoff Effectiveness Test — Report

**Verdict up front:** the handoff's core methodology is sound and I reproduced it
end-to-end against a **real, live Microsoft Access** instance. TASK A (create via UI)
and TASK B (edit via UI) both **PASSED** — every value was written through
`PostMessage(WM_CHAR)` and verified independently via COM/DAO against the `Contacts`
table. **However**, following the handoff *verbatim* causes an **indefinite hang**
because of one wrong constant (details below), which I had to correct empirically.

All results in this report are **EXECUTED** (not dry-run). Windows/ARM64 host,
Access reachable via COM, Python 3.14 (AMD64) in a venv.

---

## What I built (all under `access-e2e-eval/handoff_test/`, no `access_eval_suite` import)

- `handoff_lib.py` — Win32 message-passing helpers implemented from the handoff:
  `type_into_field` (GoToControl → AttachThreadInput → GetFocus → EM_SETSEL/WM_CLEAR →
  WM_CHAR per char), `commit_focus_out`, `layered_save`, COM/DAO verify, plus a
  `DialogWatchdog` safety net I had to add (see gap #1).
- `inspect_db.py` — TASK 0 schema/control inspection via COM/DAO.
- `create_contact.py` — TASK A.
- `edit_contact.py` — TASK B.

Sources used: **the handoff only** for the technique; `db_builder.py`/`config.py` for
form + field + control *names* (explicitly allowed); runtime COM/DAO schema inspection.
**No forbidden file was opened or needed.**

---

## TASK 0 — setup & schema (EXECUTED)

```
DB path: ...\generated\access_e2e_sample.accdb
DB exists: True
User tables: ['AuditEvents', 'Cases', 'Companies', 'Contacts', 'Users']
Contacts fields (name : type_code : required):
  ContactID : 4 : required=False        (AutoNumber PK)
  CompanyID : 4 : required=True         (Long)
  ContactType : 10 : required=True      (Text)
  ContactValue : 10 : required=True     (Text)
  IsPreferred : 1 : required=False      (Yes/No)
ContactEditor controls (name : controltype):
  Label0:100  CompanyID:109  Label2:100  ContactType:109
  Label4:100  ContactValue:109  Label6:100  IsPreferred:106  btnSubmit:104
```

> **Note on the task's suggested values.** The prompt suggested
> `FirstName/LastName/Email`, but the real `Contacts` schema has no such fields.
> I mapped the intent onto the actual required fields:
> `CompanyID=1, ContactType='Email', ContactValue='ada.lovelace@example.com'`.

---

## TASK A — create via UI (EXECUTED, **PASS**)

```
=== TASK A: create contact via UI (PostMessage) ===
Live control values after typing: {'CompanyID': '', 'ContactType': '', 'ContactValue': ''}
Save ladder: BM_CLICK-posted | RunCommand(acCmdSaveRecord=97)-ok | already-clean
DB rows matching ContactValue='ada.lovelace@example.com': [{'ContactID': 4, 'CompanyID': 1,
  'ContactType': 'Email', 'ContactValue': 'ada.lovelace@example.com', 'IsPreferred': False}]
PASS: contact created via UI and verified in DB (ContactID=4).
```

The row exists in the table with the exact typed values — proving the WM_CHAR keystrokes
reached the bound controls and the focus-out + layered save committed them.

## TASK B — edit via UI (EXECUTED, **PASS**)

```
=== TASK B: edit contact via UI (PostMessage) ===
Before edit: {'ContactID': 4, ..., 'ContactValue': 'ada.lovelace@example.com'}
Save ladder: BM_CLICK-posted | RunCommand(acCmdSaveRecord=97)-ok | already-clean
After edit:  {'ContactID': 4, ..., 'ContactValue': 'ada.byron@example.com'}
PASS: ContactID=4 ContactValue changed to 'ada.byron@example.com' and verified.
```

---

## TASK C — pitfall confirmation (from the handoff, in my own words)

1. **Why `Ctrl+S` alone is unreliable & the fallback.** In an agent/remote session,
   anything that synthesizes keystrokes through `SendInput` (which is what a simulated
   Ctrl+S would use) is blocked, and even when a keystroke lands, Access does not
   guarantee a record commit from Ctrl+S in every form state. The handoff prescribes a
   **layered save ladder** that does not depend on Ctrl+S: try the Submit button
   (`PostMessage(BM_CLICK)` on its HWND, which fires the button's save macro/VBA), then
   fall back to a COM `DoCmd.RunCommand(acCmdSaveRecord)`, and finally the most reliable
   rung — set the form's `Dirty = False` over COM, which forces the pending record to
   be written.

2. **Why you must move focus after typing.** Access only writes a bound control's edited
   text back to the underlying record **when the control loses focus** (the focus-out
   commit). If you type into a field and then immediately read the record without moving
   focus, you get the *old* value — which looks exactly like PostMessage failed even
   though the characters were delivered. So after typing each field you must
   `GoToControl` a different control to force the commit.

3. **What you must NOT click and why.** Do **not** click the **"Enable Content"**
   security-warning banner/button. Clicking it reopens the form in **Design View**, which
   breaks every subsequent field/save operation. VBA macros are blocked in this context
   anyway, so you rely on the macro-expression / COM save fallbacks instead of trusting
   the trust prompt.

---

## Ratings

| Dimension | Score | Rationale |
|-----------|:-----:|-----------|
| Completeness | **4/5** | Covers the whole winning pipeline: why naive input fails, the WM_CHAR pipeline, AttachThreadInput/GetFocus, EM_SETSEL+WM_CLEAR clearing, focus-out commit, layered save, ODBC→COM/DAO fallback ladder, capability probe, control classes, pitfalls. Missing: (a) that a modal dialog *hangs COM entirely*, (b) OpenForm/GoToRecord DataMode constants, (c) field/control-name enumeration (fair — it says inspect the schema). |
| Correctness | **3/5** | The PostMessage core is correct and fully reproduced. But one constant is **wrong in a way that hangs the run** (see gap #1), and the "GetWindowText returns the current value" claim did **not** reproduce for me on read-back (see gap #2). |
| Clarity | **4/5** | Well structured, explicit "WORKS vs BLOCKED" list, named gotchas, precise constants block. Loses a point only because a precisely-stated constant is precisely wrong. |

---

## Ambiguities / errors / gaps I hit (the important deliverable)

1. **WRONG CONSTANT → indefinite hang (most serious).** The handoff says
   `DoCmd.RunCommand(acCmdSaveRecord)(=21)`. **21 is actually `acCmdSaveAs`**, which opens
   a modal **"Save As"** dialog. A modal Win32 dialog owned by Access **blocks every
   subsequent COM call synchronously** (it does not raise — it just hangs forever). My
   first run hung >3 min with no output; I found a live `#32770 "Save As"` window owning
   the Access thread. The correct `acCmdSaveRecord` value is **97**. After changing 21→97
   the save works cleanly and no dialog appears. I discovered this **empirically**, not
   from any forbidden file. (`db_builder.py` carries the *same* mislabel in its macro
   fallback `=DoCmd.RunCommand(21)` commented "acCmdSaveRecord=21", so a form whose VBA is
   blocked would also pop Save As on Submit.)

2. **"GetWindowText returns current value" not reproduced.** The handoff's control-class
   notes say `OKttbx` "GetWindowText returns current value." My read-back of the controls
   via GetFocus+GetWindowText after the focus-out returned **empty strings**, even though
   the DB verify proves the values were correctly typed and committed. The handoff's
   *capability probe* instead reads `.Value` via COM — which is a different (and evidently
   more reliable) read path. The two statements pull in different directions; ground truth
   was the DB query, not GetWindowText.

3. **No warning that a modal dialog hangs COM.** The pitfalls call out "Enable Content"
   but never say that *any* stray modal blocks all COM synchronously with no exception.
   Combined with gap #1 this is a real trap. I added a background `DialogWatchdog` that
   posts `WM_CLOSE` to `#32770` dialogs so a run can never hang again — the handoff should
   recommend something like this.

4. **Missing DoCmd navigation constants.** The handoff assumes COM/DoCmd familiarity and
   never lists the enums needed to *stage* records: `acNewRec=5` (go to new record),
   `acFormEdit=1`/`acFormAdd=0` (OpenForm DataMode), `acSaveNo=2`, `acForm=2`. A truly
   cold agent must already know these or look them up; they aren't in the handoff.

5. **`hWndAccessApp` binding quirk (minor).** Under win32com late binding,
   `access.hWndAccessApp` came back as a *callable method*, not a plain int, so I had to
   call it before `GetWindowThreadProcessId`. The handoff mentions AttachThreadInput but
   not how to obtain the Access thread id, so this small step is left to the reader.

6. **Field/control names not enumerated (expected, not a defect).** The handoff lists
   tables and form names but not their fields/controls. It *does* tell you to verify via
   COM/DAO, and TASK 0 covered it, so this is acceptable — just call it out so a cold
   agent knows to inspect first.

## Did I need any forbidden-file information?

**No.** Everything needed came from the handoff, the allowed `db_builder.py`/`config.py`
(names only), and live COM/DAO inspection. The one place the handoff was *wrong*
(constant 21) I corrected by observing the running system (a Save As dialog), not by
reading the solution. That said, the fact that I had to *discover* the correct save
constant myself is exactly the kind of gap this test is meant to surface.

---

## Bottom line

**Yes — a fresh agent can be effective with this handoff alone**, with one important
caveat. The methodology is correct and complete enough that I created and edited real
Access records purely through the UI on the first serious attempt (2/2 PASS). But an
agent following it *literally* will hit the `RunCommand(21)` Save-As hang and must be
skilled enough to diagnose a silent COM deadlock and correct the constant to 97. Fix that
one line (and add a note that modal dialogs block COM), and this handoff is a genuinely
strong, self-contained guide.
