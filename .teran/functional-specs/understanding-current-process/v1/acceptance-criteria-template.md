# Acceptance Criteria Template – Functional Specification

**Purpose:** Define the acceptance criteria for evaluating whether a functional specification is complete and ready for development. These criteria apply to the spec document itself, not to the software being built.

**Source:** Derived from consistent patterns observed across 4 sample projects: Heartland Bank, KnightG, Statewide, and Youngdahl.

**How to use this template:** Apply these criteria when reviewing a functional spec before marking "Dev Ready" in the version history. Every criterion in the Required Criteria section must pass before the spec is handed to a developer.

---

## Required Criteria (All Must Pass Before Dev Ready)

### AC-01 – Document Header and Version History

**Description:** The spec must begin with a properly formatted version history table.

**Pass Conditions (all must be true):**
- [ ] The document title identifies the application name, module number, and module name.
- [ ] A version history table is present immediately after the title, with columns: Version | Date | Dev Ready | Edited By | Notes.
- [ ] At least one version row exists.
- [ ] The "Dev Ready" column for the current version is either blank (in-progress) or marked `X` (ready).
- [ ] The Notes column for each version row describes what changed in that version (not "minor edits" or blank).

---

### AC-02 – General Application Features and User Access

**Description:** The spec must establish what access is required to use the module.

**Pass Conditions (all must be true):**
- [ ] A "General Application Features" section is present. It either states module-specific overrides or explicitly references the Master Design.
- [ ] An "Application User Access" section is present.
- [ ] Every capability that grants access to this module is listed by name.
- [ ] Each capability's description states specifically what the user can and cannot do (view, create, edit, delete).

---

### AC-03 – All Screens Are Specified

**Description:** Every screen the user interacts with in this module has a dedicated section in the spec.

**Pass Conditions (all must be true):**
- [ ] Each screen section is named and includes a form type suffix in parentheses (e.g., SLF, DF, ELF, R, Modal Popup).
- [ ] Sections are ordered in user workflow sequence (list views before detail views, detail views before modal popups they trigger).
- [ ] No screen referenced in a Designer Note, Action, or sketch is missing its own section.

---

### AC-04 – Field Definition Tables Are Complete

**Description:** Every field visible to the user on each screen is defined in the field definition table with all required columns populated.

**Pass Conditions (all must be true):**
- [ ] Every visible field appears in the table. No fields are described only in prose without a table row.
- [ ] Every field has a non-blank Field Type.
- [ ] Every field has a value in the Req column (X, C, or blank — not missing).
- [ ] Every field has a value in the Edit column (R, E, or C — not missing).
- [ ] Every field where Req = C has the condition for when it becomes required stated in the Notes column.
- [ ] Every field where Edit = C has the condition for when it becomes editable (or disabled) stated in the Notes column.
- [ ] Every dropdown or autocomplete field has a `Selection: //` note stating the source table and field.
- [ ] Every Bit (boolean) field has a `Format:` note stating how it is rendered (e.g., Checkbox, Icon).
- [ ] Every calculated field (Text-CALC) references a Callout or states the formula directly in the Notes column.

---

### AC-05 – SLF/SELF Forms Have Both Search Criteria and Grid Element Tables

**Description:** Search list forms define both the filter inputs and the result columns.

**Applies to:** Forms of type SLF and SELF only.

**Pass Conditions (all must be true):**
- [ ] A Search Criteria table is present, listing the filter fields with their Field Type, Req, and Notes.
- [ ] A Grid Elements table is present, listing the result columns with Sort, Req, Edit, and Notes.
- [ ] The default sort column and direction are stated (either in the Grid Elements table or a note below it).

---

### AC-06 – Actions Are Fully Defined

**Description:** Every user-initiated action on every screen is defined with enough detail for a developer to implement it without guessing.

**Pass Conditions (all must be true):**
- [ ] Every button, link, and icon action on the screen is listed.
- [ ] For each action: the label, the required capability (who can see/use it), and the enabling condition are stated.
- [ ] For each action: the step-by-step behavior is described, including: what validates first, what writes to the database, what the user sees after success, and what the user sees after failure (if applicable).
- [ ] Confirmation dialogs, if required, include the exact message text and button labels.
- [ ] Actions that trigger email notifications reference the email template by name or key.
- [ ] Actions that change record status explicitly state the new status value.

---

### AC-07 – Formulas and Calculations Are Explicit

**Description:** Any field whose value is derived from other values must have a precise formula.

**Pass Conditions (all must be true):**
- [ ] Every derived/calculated field either has the formula stated in the Notes column or references a named Callout.
- [ ] Every Callout is self-contained: it defines all variables used and states the formula precisely.
- [ ] No formula uses ambiguous language such as "sum of related records" without specifying which table, which field, and which filter conditions apply.

---

### AC-08 – Complex Workflows Have State or Dependency Documentation

**Description:** Records with multi-step status workflows, or forms where changing one field recalculates others, have explicit documentation of those rules.

**Applies to:** Any form where a record has a status field with restricted transitions, or any form where changing one field affects the required or displayed values of another.

**Pass Conditions (all must be true):**
- [ ] Status workflows include: each valid status value, the actions that trigger transitions, and any conditions on those transitions.
- [ ] Forms with cascading field dependencies include a Dependency Table or equivalent section listing what is re-evaluated when each trigger field changes.

---

### AC-09 – No Proprietary Customer Data in the Document

**Description:** The spec contains no real customer names, real data values, or confidential business information that would prevent the spec from being shared within the project team.

**Pass Conditions (all must be true):**
- [ ] Field examples use placeholder values (e.g., "[CustomerName]", "Example Inc."), not real customer records.
- [ ] Configuration values referenced as examples are described in terms of their purpose, not their actual production values.

---

## Conditional Criteria (Apply When Relevant)

### AC-10 – API Spec Is Complete (if module includes an API)

**Pass Conditions (all must be true):**
- [ ] Each API endpoint has a defined argument list with Name, Type, Required, and Description for each argument.
- [ ] Each API endpoint has a defined return schema with Name, Type, and Description for each returned field.
- [ ] Authentication requirements are stated.
- [ ] Call sequencing dependencies between endpoints are documented (e.g., "New Referral requires a SearchID from a prior New Search call").

---

### AC-11 – Data Migration Spec Is Complete (if module includes legacy data migration)

**Pass Conditions (all must be true):**
- [ ] Every source table or object being migrated is identified.
- [ ] The target table or object for each source is identified.
- [ ] Each field mapping includes a transformation rule: copy as-is, format conversion, derivation formula, or default value.
- [ ] Null handling for source fields is specified.

---

## Acceptance Criteria in Given/When/Then Format

The following represent the most critical acceptance conditions expressed as testable scenarios.

**AC-01: Version History**
> Given a functional spec document,
> When I open it,
> Then the first content after the title is a version history table with columns Version, Date, Dev Ready, Edited By, and Notes, and every row has a non-empty Notes entry describing the change.

**AC-04: Field Definition Completeness**
> Given any form section in the spec,
> When I review the field definition table,
> Then every field visible on that form appears in the table, every field has a non-blank Field Type, every Req=C field has its condition stated, every Edit=C field has its condition stated, and every dropdown field has a Selection source noted.

**AC-06: Action Completeness**
> Given any button or icon action defined on a form,
> When I read its specification,
> Then I can answer all of the following without asking a follow-up question: Who can see this action? When is it enabled? What happens step by step when clicked? What does the user see on success?

**AC-07: Calculation Precision**
> Given any field of type Text-CALC or any Callout in the spec,
> When I read the formula,
> Then I can compute the correct result given specific input values, without making any assumptions about which table, field, or filter condition to use.
