# Functional Specification – Writing Guidelines

Derived from analysis of 20 functional specification samples across four projects. Rules apply to web application module specs unless noted. Deviations from these rules should be documented in a Designer Note.

---

## 1. Document Setup

- The document opens with two H1 lines: (1) project name and application type, (2) "Functional Specifications – Module N [Module Name]".
- The cross-reference sentence follows immediately after the H1 lines: "This document is intended to be used in conjunction with each of the module-specific functional specification documents."
- The version table immediately follows the cross-reference sentence. No other content appears before the version table.
- A `---` horizontal rule separates the version table from the body sections when used for visual clarity.
- Module specs do not repeat content from the Master Design. Any reference to a global UI rule reads "See Master Design for [topic]."

---

## 2. Version Table

- The version table uses exactly five columns in this order: Version | Date | Dev Ready | Edited By | Notes.
- Version numbers use single-decimal notation: 1.0, 1.1, 1.2. Reserve sub-minor versions (1.0.1) only for corrections to a Dev Ready version.
- Date format: M/D/YYYY (no leading zeros on month or day). Example: 3/21/2024, not 03/21/2024.
- Dev Ready column: leave blank while in draft. Set to `X` only when the version is complete and cleared for developer implementation.
- Edited By: use the same initials or short name code consistently across all documents in the project.
- Notes column: state what changed in this version, not what the document contains. Use screen names as anchors for multi-item changes. Example: "Customer (SLF): Added Active filter. Customer (DF): Added Phone field."
- Do not delete version rows. Add new rows at the top of the table; keep all prior versions below.
- When the opening table grows beyond 8 rows, move all but the 3 most recent versions to the Version Log section at the end of the document. Add a row in the opening table: "1.0–[N]: See Version Log for previous versions."

---

## 3. Module-Level Sections (Order)

The following sections appear in this order in every module spec, before any screen sections:

1. Designer Note (module-level)
2. General Application Features (pointer to Master Design)
3. Application User Access (capabilities table)
4. Callouts (if used)
5. Sketches (Figma link)

No module-level section is omitted even if it contains only a placeholder. If no callouts are used, omit the Callouts section. If no Figma link is available, omit the Sketches section.

---

## 4. Screen Section Structure and Order

Every screen section contains the following subsections in this order:

1. Screen heading (H2) with form type abbreviation
2. User Access (immediately below the heading, no sub-heading)
3. Designer Notes (H3)
4. Actions (H3, or labeled "Actions:")
5. Grid Actions (H3, or labeled "Grid Actions:") — only for screens with a data grid
6. Search Criteria table — only for SLF and search-entry screens
7. Elements table (H3, or labeled "Elements:")

No screen section skips a step. If a subsection has no content (e.g., no grid actions on a DF screen), omit that subsection rather than leaving it empty.

---

## 5. Form Type Abbreviations

Use the abbreviation in parentheses immediately after the screen name in the H2 heading.

| Abbreviation | Full Name | When to Use |
| --- | --- | --- |
| SLF | Searchable List Form | A grid with Search Criteria fields above it. The primary entry point for managing a record type. |
| ELF | Editable List Form | A grid where rows are edited inline without a separate detail form. Used for simple lookup/reference tables. |
| DF | Detail Form | A full-page form for viewing and editing a single record. |
| R | Report | A printable or exportable formatted output. |
| [Access] prefix | Legacy Access screen | A screen in the original Access application documented alongside the new web replacement. |

---

## 6. User Access (Per-Screen)

- The User Access declaration appears immediately below the H2 screen heading, before Designer Notes. It is not a sub-heading; it is a labeled list.
- Format: `User Access:` on its own line, followed by one bullet per capability that grants access to this screen.
- Each bullet states the capability name, a colon, and the access level granted: Full access / Read-only / [Specific restriction].
- Every capability referenced in a per-screen User Access section must be defined in the module-level Application User Access table.
- If a screen is accessible to all authenticated users regardless of capability, state: "User Access: All authenticated users."

---

## 7. Designer Notes

- Designer Notes are written for business stakeholders, not developers. Do not include database table names, column names, or technical implementation detail.
- Use full sentences. Explain the business purpose, business rules, and user context.
- Place Designer Notes before Actions in every screen section.
- A module-level Designer Note section appears near the top of the document and describes the module as a whole. Per-screen Designer Notes describe the individual screen.
- If a Designer Note contains conditional business rules (e.g., "When a shareholder is inactive, their shares are excluded from dividend calculations"), state the condition explicitly before the consequence.

---

## 8. Dev Notes

- Dev Notes are written for the developer only. They contain implementation detail: database column mappings, sort orders, default values, validation rules, calculation formulas, and conditional logic.
- In web application specs: prefix each Dev Note item with `//`. Example: `// Default sort: Last Name ascending.`
- In the Actions section: Dev Notes appear as an indented sub-bullet labeled `Dev Note:` under the action they modify, or as a standalone `Dev Note:` bullet at the bottom of the Actions section for page-level technical requirements.
- In the Elements table: Dev Notes appear in the Notes cell of the row they describe, following any user-facing format or sample notes, prefixed with `//`.
- Do not mix Designer Note content and Dev Note content in the same labeled block. If a note is both explanatory and technical, split it into a Designer Note (business context) and a Dev Note (technical detail) in the appropriate labeled section.

---

## 9. Actions Section

- Every action is a top-level bullet with the button label as the bullet text.
- Every action has a `Format:` sub-bullet stating the UI control type: Button, Icon, or Link.
- Every action has a description of the on-select behavior. Use the phrase "On select, [behavior]." for the primary action bullet.
- Multi-step actions use nested bullets to describe each step in sequence.
- Confirmation dialogs: state the exact dialog message text in quotes. Then describe the Cancel path and the OK path as nested bullets.
- Access guards: state which capability is required as a bullet: "Only present if user has [Capability]." Place this bullet before any Dev Note bullets.
- Error/validation messages: state the message text in quotes. Use "show message similar to" only when the exact wording is intentionally left to the developer's discretion.
- Paired actions for detail forms: always include Edit, Save, Cancel, and Done as the standard four actions. Edit and Done are present in View mode only. Save and Cancel are present in Edit mode only.
- The Clock Icon action, when present, reads: "See Master Design for Clock Icon hover behavior." Do not respecify Clock behavior in module specs.

---

## 10. Grid Actions Section

- Grid Actions document row-level icon actions (icons that appear on each row of a data grid).
- Grid Actions are listed in a separate section from page-level Actions. Label this section "Grid Actions:" and place it immediately after the Actions section.
- Standard grid action set: Details (view), Edit (edit), Delete. Not all three are required on every grid — include only the actions that apply.
- The Delete action always includes a confirmation dialog with the exact message text.

---

## 11. Elements Table

- Every screen section that displays or captures data includes an Elements table.
- Use the standard 6-column format: Element Name | Field Type | Sort (X) | Req (X,C) | Edit (R,E,C) | Notes.
- For detail form (DF) screens: strikethrough the Sort column header (~~Sort (X)~~) to signal the column is not applicable.
- For grid/list screens: strikethrough the Req column header (~~Req (X,C)~~) to signal the column is not applicable.
- The Notes column header reads: "Notes: FS Lite = Sample, Format and Selection notations only."
- Every row in the Notes column includes at minimum one of: a sample value, a format specification, or a selection source. Do not leave the Notes cell blank.
- Field types use the project's type vocabulary: Text-N, Text-MAX, Text-CALC, Currency, Percentage, Date, Datetime, Dropdown, Bit, Integer. Do not use SQL data type names (VARCHAR, NVARCHAR, DECIMAL).
- Calculated fields: set Field Type to the output type (Currency, Text, etc.) and add `// CALC: [formula]` in the Notes cell. Mark Edit as R (read-only).
- Conditional fields: set Edit to C and add a plain-language condition in the Notes cell: "Editable when [Condition]. Read-only when [Other Condition]." Follow with `// Dev Note:` for the technical condition logic.
- The legend line "Sort/Req/Edit Values: X = Required, R = Read Only, E = Edit, and C = Conditional. Refer to Dev Notes when 'C'." appears immediately above every Elements table.

---

## 12. Report Element Tables

- Report screens use a simplified 3-column element table: Element Name | Field Type | Notes.
- Omit Sort, Req, and Edit columns (reports are read-only and unsorted by the user).
- Organize report elements by section: Report Header, Group Header, Detail Row, Group Footer, Report Footer, Page Footer.
- Each section gets its own labeled sub-table.
- Notes column specifies alignment (Left-aligned, Right-aligned, Centered), formatting, and calculation logic.

---

## 13. Callouts

- A callout is a named, reusable block of complex calculation or conditional logic referenced from two or more locations (screens or element rows) within a module.
- Define all callouts in the module-level Callouts table before they are referenced. Do not define callouts within individual screen sections.
- Reference a callout from an element row or action note using the phrase: "See [Callout Name] callout" or "See callout #N."
- Callout table columns: Callout (name or number) | Dev Note (the full logic, prefixed with //).
- A callout containing a formula states all inputs, the formula, and the output explicitly.

---

## 14. Strikethrough Convention

- Use strikethrough (`~~text~~`) to preserve superseded specification content inline rather than deleting it.
- Strikethrough is appropriate for: superseded action descriptions, removed fields, changed field names, and overridden business rules.
- A Dev Note or Designer Note may follow a strikethrough item to explain why the change was made, if the reason is not already captured in the version table Notes column.
- Do not use strikethrough for temporary placeholder text. Placeholder text is either replaced or removed before a version is marked Dev Ready.

---

## 15. Cross-Referencing

- When a screen's behavior is documented in another screen section, reference it by name and form type: "See [Screen Name] (DF) for [topic]."
- Do not repeat shared logic across multiple screen sections. Define it once and reference it.
- Do not repeat Master Design content in module specs. Reference the Master Design by section name: "See Master Design, Grid Features."

---

## 16. Writing Style

- Use present tense to describe system behavior: "On select, the system opens [form]." Not "will open" or "should open."
- Use active voice: "Show confirmation dialog." Not "A confirmation dialog is shown."
- Bullet lists are preferred over prose paragraphs for behavioral requirements. Use prose only in Designer Notes.
- Sentence fragments are acceptable in Actions and Dev Notes where the subject is unambiguous (e.g., "Default sort: Last Name ascending." is clear without "The default sort is Last Name ascending.").
- Do not use "etc.", "as appropriate", "handle all edge cases", or "similar behavior applies." State every specific case explicitly.
- Do not use "should" or "would." Use "On select, [action]" or "[Field] is required." Requirements are stated as facts about system behavior, not aspirations.
- Conditional requirements state the condition first: "When [Condition], [Behavior]." Not "[Behavior] when [Condition]."
- Quote all user-facing message text using double quotes. Example: "Are you sure you want to delete this record?"
