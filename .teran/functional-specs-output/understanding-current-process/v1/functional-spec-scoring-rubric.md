# Functional Specification Scoring Rubric

**Purpose:** Define a scoring rubric for evaluating the quality of functional specifications. Use this rubric to assess a spec before marking it Dev Ready, during peer review, or when comparing specs across projects.

**Source:** Derived from quality patterns observed across 4 sample projects: Heartland Bank, KnightG, Statewide, and Youngdahl.

**Scoring scale:** 1–5 per criterion. Scores below 3 in any Required criterion indicate the spec is not ready for development.

---

## Scoring Summary Table

| # | Criterion | Weight | Score (1–5) | Notes |
|---|---|---|---|---|
| 1 | Structure and Format Adherence | Required | | |
| 2 | Field Definition Quality | Required | | |
| 3 | Action and Behavior Completeness | Required | | |
| 4 | Clarity and Precision | Required | | |
| 5 | Access Control Specification | Required | | |
| 6 | Business Rule Documentation | Required | | |
| 7 | Testability | Required | | |
| 8 | Version History Quality | Informational | | |

**Aggregate score:** Sum of all 8 criteria / 8 = Average score (max 5.0)

A spec scoring below 3 on any Required criterion should not be marked Dev Ready.

---

## Criterion 1 – Structure and Format Adherence

**Description:** The document follows the established template structure: title, version history, General Application Features, Application User Access, form sections in workflow order, and Version Log at the end. Form sections are correctly named with type suffixes (SLF, DF, ELF, SELF, R, Modal Popup).

| Score | Description |
|---|---|
| 5 | All sections present, in the correct order, with correct form type suffixes on every section. A Master Design is referenced or provided for the project. |
| 4 | All sections present with minor ordering issues or one missing form type suffix. Master Design is referenced. |
| 3 | Most sections present but one or two are missing (e.g., no Sketches section, or User Access section is empty). Form type suffixes are sometimes missing. |
| 2 | Several structural elements are missing or out of order. Form sections are not consistently named. No Master Design reference. |
| 1 | The document has no consistent structure. Sections are ad hoc, named inconsistently, or missing entirely. |

**Anchor examples:**
- Score 5: Statewide Module 3 — every section present, SLF/DF/R naming consistent, explicit Master Design reference.
- Score 3: Heartland Module 2 — ICF/DF naming used, field table present but no formal Sort/Req/Edit columns.
- Score 1: A document that is only prose paragraphs with no section headers or tables.

---

## Criterion 2 – Field Definition Quality

**Description:** Every user-visible field on every form appears in a field definition table with correct Field Type, Sort, Req, Edit, and Notes values. Conditional fields have their conditions stated. Dropdowns have their source stated. Calculated fields have their formula stated.

| Score | Description |
|---|---|
| 5 | Every field is in the table. Every conditional Req or Edit has the condition stated. Every dropdown has a `Selection: //` note. Every calculated field references a Callout or states the formula. Every Bit field has a `Format:` note. |
| 4 | Fewer than 3 fields across the spec are missing or have a missing Notes condition. No systematic gaps. |
| 3 | Several fields are missing their Req or Edit values, or conditional fields are missing their conditions. Dropdown sources are sometimes omitted. |
| 2 | Field tables exist but are significantly incomplete. Many fields lack types, required markers, or notes. |
| 1 | Fields are described only in prose, or field tables are absent from most form sections. |

**Anchor examples:**
- Score 5: Statewide Module 2 — every field has all columns populated; conditional fields have explicit enabling conditions; all dropdowns have table and field references.
- Score 3: KnightG Module 1 — fields listed but many lack Selection notes; some Req statuses implicit rather than marked.
- Score 1: A document that lists fields only as bullet points with no table.

---

## Criterion 3 – Action and Behavior Completeness

**Description:** Every button, link, and icon action on every form is defined. Each action includes: who can see it, when it is enabled, and a step-by-step description of what happens (including validation, database writes, and what the user sees on success or failure).

| Score | Description |
|---|---|
| 5 | Every action is listed. Each has an enabling condition, a visibility rule, and step-by-step behavior. Confirmation dialogs include exact text. Status-changing actions state the new status. Email-triggering actions name the template. |
| 4 | All major actions are defined. One or two secondary actions (e.g., a Cancel button) lack step-by-step detail but behavior is inferable from context. |
| 3 | Most actions are listed but several are described vaguely (e.g., "saves the record") without specifying what validates, what writes, or what the user sees. |
| 2 | Fewer than half the actions are defined. Many are named but not described. |
| 1 | Actions are mentioned in passing or not described at all. A developer would need to invent the behavior. |

**Anchor examples:**
- Score 5: Youngdahl Module 2 — DFR Submit action includes: validation conditions, what fields are written, what status is set, what email fires, and what the user sees.
- Score 4: Heartland Module 4 — Lock Event action is described but Unlock Event behavior is less explicit.
- Score 1: A form section that lists button labels only with no behavioral description.

---

## Criterion 4 – Clarity and Precision

**Description:** Requirements are stated in plain language with no vague phrases. Conditions are specific. Formulas name exact tables and fields. Nothing requires a follow-up question to implement.

| Score | Description |
|---|---|
| 5 | No vague language. Every condition is stated as a testable rule. Every formula is computable given input values. No use of "etc.", "as appropriate", "similar to above", or "handle all cases." |
| 4 | Mostly precise. One or two statements require minor interpretation but are clearly intended. |
| 3 | Several statements are ambiguous. A developer would need to ask follow-up questions about edge cases or conditions. |
| 2 | Frequent vague language. Conditions are implied rather than stated. Formulas reference concepts without naming tables or fields. |
| 1 | The spec is primarily prose description. Requirements are not stated as discrete, testable rules. |

**Anchor examples:**
- Score 5: Statewide Module 2 Callout — lists 13 inventory transaction patterns, each with explicit field effects, no ambiguity.
- Score 3: A spec that says "Sort by date" without specifying ascending or descending, or which date field.
- Score 1: A spec that says "The form should handle stock awards appropriately."

---

## Criterion 5 – Access Control Specification

**Description:** The spec defines which capabilities grant access to each form and action. The description of each capability is specific enough to implement role-based access control without guessing.

| Score | Description |
|---|---|
| 5 | Every form and every action states the required capability. The Application User Access section defines each capability with a clear description of what it grants and denies. No form or action is left without an access rule. |
| 4 | Most forms and actions have access rules. One or two secondary actions are missing explicit capability references but the pattern is clear from context. |
| 3 | Access rules are stated at the module level but not for individual actions. A developer would need to infer which actions require which capability. |
| 2 | Access is mentioned generally (e.g., "admin users only") without referencing specific capability names. |
| 1 | No access control specification. The spec does not address who can use any part of the module. |

**Anchor examples:**
- Score 5: Statewide Module 1 — each ELF and DF section lists the exact capability required; the User Access section lists all capabilities with precise descriptions.
- Score 3: A spec that says "only administrators can delete" but does not name a capability or describe what "administrator" means in the system.
- Score 1: A spec with no mention of user roles, permissions, or capabilities.

---

## Criterion 6 – Business Rule Documentation

**Description:** Non-obvious business rules are captured in Designer Notes or Callouts. The rules are traceable to the user need or business objective they serve. Business rules are not buried in Dev Notes (which are developer-facing).

| Score | Description |
|---|---|
| 5 | All non-obvious business rules have Designer Notes explaining the "why." Formulas and calculations are in Callouts with all variables defined. No business rules are hidden in Dev Notes. Future or planned rules are explicitly labeled as such. |
| 4 | Most business rules are documented. One or two are partially embedded in Dev Notes or field Notes rather than surfaced as Designer Notes or Callouts. |
| 3 | Some business rules are present but inconsistently placed. Key rules may be buried in field Notes or actions without being explicitly labeled as rules. Some rules are mentioned in passing without full explanation. |
| 2 | Business rules are largely inferred from field names or action descriptions. Designer Notes are absent or only state the obvious. |
| 1 | No business rules are documented. A developer would need to discover the rules by asking the customer. |

**Anchor examples:**
- Score 5: Youngdahl Module 3 — Dependency Table explicitly states which field changes trigger re-evaluation of which test results; Designer Notes explain the business logic of Standards, AHJ, and Superseded status.
- Score 3: Heartland Module 5 — vesting schedule rules are partially described in Designer Notes but the six-year percentage breakdown is not explicitly listed in a Callout.
- Score 1: A spec with no Designer Notes and formulas described only as "calculated per business rules."

---

## Criterion 7 – Testability

**Description:** Requirements are phrased so a QA engineer can write a test case that produces a clear pass or fail result. Observable outcomes are specified. Negative cases (what should not happen) are documented where relevant.

| Score | Description |
|---|---|
| 5 | Every requirement has an observable outcome. A QA engineer can write pass/fail test cases directly from the spec without interpretation. Both success paths and error/failure paths are specified. Negative cases are documented. |
| 4 | Most requirements are testable. A few success paths lack explicit error handling, but the spec covers enough to begin testing. |
| 3 | Requirements describe what the system does but leave out enough detail that a QA engineer would need to interpret or ask for error path behavior. |
| 2 | Requirements are stated at too high a level for direct testing. Test cases would require significant interpretation. |
| 1 | Requirements are descriptive only. A QA engineer cannot derive specific test cases from the spec without a follow-up meeting with the author. |

**Anchor examples:**
- Score 5: Statewide Module 2 — field uniqueness rule is stated as "Dev Note: Must be unique. Validation Rule – Unique Role Name enforced in DB." A QA test is: enter duplicate → see validation error.
- Score 3: A spec that says "Required fields must be filled in before saving" without listing which fields are required or what the error message is.
- Score 1: A spec that says "The application validates the form" without specifying what validates or what the user sees.

---

## Criterion 8 – Version History Quality (Informational)

**Description:** The version history accurately reflects the document's revision history. Change notes are specific enough to locate what changed. Dev Ready markers are accurate.

| Score | Description |
|---|---|
| 5 | Every version row has a specific, accurate description of what changed in that version. The Dev Ready column is marked only when the spec was actually complete. The Edited By column is populated. |
| 4 | Most version rows have specific change notes. One or two rows have vague notes (e.g., "Updated module"). |
| 3 | Several version rows have vague notes. Dev Ready marks may not accurately reflect spec readiness. |
| 2 | Version history is sparse. Many rows say "edits" or similar without specifics. |
| 1 | Version history is absent, or all rows have empty Notes fields. |

**Note:** This criterion is marked Informational because it reflects process discipline rather than spec content quality. A score below 3 here does not block Dev Ready on its own, but it indicates a process gap worth addressing.

---

## Scoring Interpretation

| Average Score | Interpretation |
|---|---|
| 4.5 – 5.0 | Excellent. Spec is complete, precise, and ready for development. |
| 3.5 – 4.4 | Good. Minor gaps exist. Review and address before marking Dev Ready. |
| 2.5 – 3.4 | Needs improvement. Several required sections are incomplete. Do not mark Dev Ready. |
| 1.5 – 2.4 | Significant gaps. Substantial revision required before the spec can be used. |
| 1.0 – 1.4 | Not usable. The spec does not meet the minimum standard for any required criterion. |
