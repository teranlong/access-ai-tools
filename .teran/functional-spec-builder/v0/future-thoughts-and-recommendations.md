# Future Thoughts and Recommendations

Specific, actionable recommendations for improving the functional specification process. Each recommendation identifies the problem it solves, the recommended change, and the effort level required to implement it.

Recommendations are ordered from lowest to highest implementation effort. Items marked **[Quick Win]** can be applied immediately to new documents without retroactive changes. Items marked **[Retroactive]** benefit from being applied to existing documents as well.

---

## 1. Publish the Template and Guidelines as a Shared Reference [Quick Win]

**Problem:** Conventions currently exist only in practice, not in a written standard. New contributors cannot learn the format without reading existing documents and inferring the rules.

**Recommendation:** Distribute the template and guidelines produced by this process builder to all contributors. Store them in a shared location accessible during document creation. Establish a rule: every new module spec starts from the template, not from a copy of a prior module spec.

**Impact:** Eliminates per-author format variation. New contributors produce spec-compliant documents from the first draft.

---

## 2. Standardize the Date Format in Version Tables [Quick Win]

**Problem:** Version table dates use inconsistent formats across documents: M/D/YYYY, MM/DD/YYYY, M/D/YY, and combinations. A reviewer cannot sort or compare dates without reformatting.

**Recommendation:** Adopt M/D/YYYY as the single standard (no leading zeros). State this rule in the guidelines. Apply it to all new version table rows. Retroactively correct existing rows when a document is next revised.

**Impact:** Low effort; eliminates ambiguity in version history reading.

---

## 3. Adopt a Consistent Heading Hierarchy for All New Projects [Quick Win]

**Problem:** The desktop application project uses H4–H6 for all screen-level content. Web application projects use H2–H4. Documents from both formats may coexist in a reader's workflow.

**Recommendation:** For all new documents (regardless of platform), use: H2 for screen headings, H3 for subsections (Actions, Elements, Designer Notes), H4 for sub-subsections within a screen. Do not use H4 for screen headings. Document this as a fixed rule in the guidelines.

**Impact:** Enables consistent navigation, table-of-contents generation, and AI parsing across all project documents.

---

## 4. Create an Error Message Catalog Section [Quick Win for New Projects]

**Problem:** Error message text is inconsistently specified. Some messages have exact text; others say "show message similar to." Developers make discretionary decisions that result in inconsistent user-facing language across the product.

**Recommendation:** Add an appendix section at the end of each module spec titled "Error Messages." List every validation or confirmation message defined in the module with its exact text. Reference the messages from the Actions section by message ID rather than quoting inline. Example:

```
MSG-001: "Legal name must be unique. Please enter a different name."
MSG-002: "Are you sure you want to delete this record? This cannot be undone."
```

In the Actions section: "If Legal Name is not unique, show MSG-001."

**Impact:** Eliminates developer discretion on user-facing language. Enables a UX review pass on all messages as a batch.

---

## 5. Add a "Data Model Notes" Section to Each Module Spec [Quick Win for New Projects]

**Problem:** Field type notation in element tables (Text-75, Currency, Bit) is functional but does not map to database schema. Developers must infer SQL data types, nullability, and column names from element names and Dev Notes.

**Recommendation:** Add an optional "Data Model Notes" section at the end of each module spec (before the Version Log). This section contains a two-column table: Element Name | Database Mapping. Populate it only for non-obvious mappings (complex calculated fields, fields stored in unexpected columns, fields that write to multiple tables).

This is not a replacement for a database schema — it is a bridge between the spec and the schema for ambiguous cases.

**Impact:** Reduces developer back-and-forth during implementation. Particularly valuable for modules with calculated fields or shared lookup tables.

---

## 6. Standardize Version Log Placement and Format [Retroactive]

**Problem:** Version history is kept in three different places depending on the project: entirely in the opening table (two projects), in a "Past Updates" section at the end (one project), and in a "Version Log" section at the end with a pointer row in the opening table (one project). A reviewer switching between projects must know which convention applies.

**Recommendation:** Adopt the pointer row + Version Log convention for all projects:
- Opening table: retain the 5 most recent versions. Add a pointer row at the bottom: "Previous versions: see Version Log."
- End of document: add a Version Log section with the full history.
- Retroactively apply to existing documents when they are next revised.

**Impact:** Opening table stays readable. Full history is preserved and findable.

---

## 7. Elevate Callouts to a Standard Module-Level Section in All Projects [Quick Win for New Projects]

**Problem:** Callout usage is inconsistent: per-screen scope in one project, module-level scope in another, absent in two. Logic that is referenced from multiple screens is duplicated verbatim in the two projects without callouts.

**Recommendation:** Include a module-level Callouts section in the template as a standard section (not optional). For projects that currently have no callouts, add the section header with an empty table. When complex logic is first needed in two or more screen sections, extract it to the Callouts table rather than duplicating it. Apply the // prefix to all callout Dev Notes.

**Impact:** Eliminates logic duplication. Provides a single place to update complex business rules when they change.

---

## 8. Replace "Show Message Similar To" with an Explicit Convention [Quick Win]

**Problem:** "Show message similar to" is used throughout the corpus as a hedge, leaving message wording to developer discretion. This produces inconsistent user-facing text.

**Recommendation:** Replace "show message similar to" with one of two explicit alternatives:
- "Show message: '[exact text]'" — when the exact wording is specified.
- "Show message: [MSG-NNN]" — when using the Error Message Catalog (see Recommendation 4).

Remove "similar to" from the allowed vocabulary. If the exact wording is genuinely undecided at spec time, leave a [TODO: specify message text] placeholder that is resolved before Dev Ready is set.

**Impact:** Eliminates ambiguous language. All user-facing messages are either specified or explicitly flagged as incomplete.

---

## 9. Add a Minimum Accessibility Note to the Master Design [Medium Effort]

**Problem:** No accessibility requirements appear anywhere in any document. For web applications, the absence of WCAG compliance targets, keyboard navigation requirements, and color contrast standards means these requirements are either assumed or absent from the product.

**Recommendation:** Add an "Accessibility Standards" section to the Master Design document for each web application project. At minimum, state:
- The WCAG conformance target (e.g., WCAG 2.1 Level AA).
- Whether keyboard navigation is required for all interactive elements.
- The minimum color contrast ratio for text.
- Whether screen reader support is required.

These do not need to be per-screen specifications — a module spec inherits them from the Master Design.

**Impact:** Provides a clear, documentable accessibility commitment. Prevents accessibility issues from being discovered only after implementation.

---

## 10. Add State Transition Documentation for Workflow-Heavy Modules [Medium Effort]

**Problem:** Modules with multi-state workflows (e.g., record statuses, multi-step processing pipelines, approval flows) document each state's behavior in individual screen sections but do not provide a consolidated view of the full state machine. Developers must reconstruct the state transitions by reading multiple screen sections.

**Recommendation:** For any module containing a record type with 3 or more status values or workflow stages, add a "State Transitions" section immediately after the Application User Access section. This section contains a table:

| From State | Trigger / Action | To State | Rules |
| --- | --- | --- | --- |
| Draft | User clicks Submit | Submitted | Only allowed if all required fields are populated. |
| Submitted | Supervisor clicks Approve | Active | Notifies the record owner. |

This replaces the need to infer state logic from individual screen sections.

**Impact:** High value for workflow-heavy modules. Eliminates a common source of developer questions during implementation.

---

## 11. Distinguish Spec Completeness Status from Dev Ready Status [Medium Effort]

**Problem:** The Dev Ready column in the version table serves a dual purpose: it marks both that the spec is complete enough for development and that the developer has been notified. There is no intermediate state for "spec is substantially complete but needs one section reviewed."

**Recommendation:** Add a second status signal to the version table Notes column (or as a separate header field, not a column):

- **Spec Status:** `Draft` | `In Review` | `Final`
- **Dev Ready:** `X` when cleared for implementation

The Notes column already functions as free-form status — this recommendation formalizes it. Consider adding a one-line status block below the version table: `Spec Status: [Draft | In Review | Final] | Dev Notified: [Date or blank]`

**Impact:** Separates the writing process status from the implementation gate. Useful when a spec goes through a formal review before being handed off.

---

## 12. Create a Module-to-Master-Design Cross-Reference Index [Medium Effort]

**Problem:** Module specs defer to the Master Design with general references ("See Master Design for Grid Features") but do not specify which sections of the Master Design apply to each screen. A developer implementing a screen must read the full Master Design to know which rules apply.

**Recommendation:** Add a brief "Master Design Sections in Use" list to each module spec's "General Application Features" section. Example:

```
## General Application Features

See Master Design for additional general application features. Sections relevant to this module:
- Grid Features (all screens with data grids)
- Search Pages – Criteria (all SLF screens)
- Detail Pages (all DF screens)
- Clock Icon (Customer DF, Job DF)
- Help Sections (all screens)
```

**Impact:** Reduces Master Design reading burden per module. Developer knows exactly which global rules to apply without reading the entire Master Design.

---

## 13. Introduce a Formal Review Step Before Dev Ready Is Set [Process Change]

**Problem:** The current process shows no evidence of a structured review step between spec completion and Dev Ready. The Dev Ready flag appears to be set by the same author who wrote the spec.

**Recommendation:** Establish a two-step Dev Ready gate:
1. Author marks the spec complete and updates Spec Status to "In Review."
2. A second reviewer (project manager, lead developer, or client stakeholder) reviews the spec against the Acceptance Criteria Checklist and signs off.
3. Author sets Dev Ready = X only after sign-off.

Document the sign-off in the version table Notes: "v1.4: Dev Ready after review by [Initials] on [Date]."

**Impact:** Catches specification gaps before they become implementation surprises. Distributes spec knowledge to at least two people.

---

## 14. Add Performance Notes for Data-Heavy Screens [Low Priority / Future]

**Nice-to-have.** Currently no performance requirements appear in any spec. For screens that query large datasets (e.g., search grids over hundreds of thousands of records), a brief Dev Note stating expected record volume and acceptable query time would inform database indexing and query design decisions.

**Recommendation:** For SLF and report screens operating on large datasets, add a Dev Note: "// Expected record volume: [N] records. Maximum acceptable grid load time: [N] seconds. Ensure [relevant indexes] are in place."

---

## 15. Audit Existing Projects Against the Acceptance Criteria Checklist [Retroactive / Medium Effort]

**Recommendation:** Run the Acceptance Criteria Checklist against each existing module spec at its current version. Record the pass/fail results in a project-level audit spreadsheet. Prioritize fixing Fail items in modules that are still in active development. For modules in production, note the gaps without requiring immediate remediation — address them when the module is next revised.

**Impact:** Provides a baseline quality measure for existing work. Identifies the highest-risk spec gaps before they cause implementation problems.
