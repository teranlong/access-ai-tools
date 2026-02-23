# [Project Name] – [Application Name] – [Platform: Access/SQL | Web Application]
# Functional Specifications – Module [N] [Module Name]

This document is intended to be used in conjunction with each of the module-specific functional specification documents.

| Version | Date | Dev Ready | Edited By | Notes |
| --- | --- | --- | --- | --- |
| 1.0 | [M/D/YYYY] | | [Initials] | Initial draft |

---

## Designer Note

- [Describe what this module covers at a business level. Who uses it? What business problem does it solve?]
- [List any module-wide business rules that apply across all screens in this module.]

---

## General Application Features

See Master Design for additional general application features.

---

## Application User Access

List all capabilities that control access within this module. Each capability name must be defined here before it is referenced in per-screen User Access sections.

| Access Level Name (Capability) | Description |
| --- | --- |
| [Module]_MaintainFull | Full create, edit, and delete access to all [module name] screens. |
| [Module]_ReadOnly | View-only access to all [module name] screens. |

---

## Callouts

Callouts document reusable logic blocks referenced from two or more screens within this module. Add a row for each named callout used in this document. Omit this section if no callouts are used.

| Callout | Dev Note |
| --- | --- |
| [Callout Name or Number] | // [Detailed logic description. Include all conditions, formulas, and field references needed for a developer to implement this without additional context.] |

---

## Sketches

- Figma: [Figma URL]
- Note: Sketches represent the web application layout. Legacy Access application screens are prefixed with `[Access]` in their section headings.

---
---

## [Screen Name] (SLF)

_Use (SLF) for searchable list/grid screens. Replace with the appropriate form type: SLF, ELF, DF, R. See guidelines for full list._

User Access:
- [Module]_MaintainFull: Full access.
- [Module]_ReadOnly: Read-only. New, Edit, and Delete actions are hidden.

### Designer Notes

- [Why this screen exists. What business task does the user perform here?]
- [Who is the primary user of this screen?]
- [Any business rules that determine what records are displayed or filtered by default.]

### Actions

- Search
  - Format: Button
  - On select, refresh grid with results filtered by the current Search Criteria selections.
- Reset
  - Format: Button
  - On select, reset all Search Criteria fields to their default values and refresh the grid.
- New [Entity Name]
  - Format: Button
  - On select, open [Entity Name] (DF) in Edit mode with a new blank record.
  - Only present if user has [Module]_MaintainFull.
  - Dev Note:
    - // [Any technical notes specific to creating a new record from this screen]
- Dev Note:
  - // Default sort: [Field Name] ascending.
  - // [Any other page-level technical requirements]

### Grid Actions

- Details
  - Format: Icon
  - On select, open [Entity Name] (DF) in View mode for the selected row.
- Edit
  - Format: Icon
  - On select, open [Entity Name] (DF) in Edit mode for the selected row.
  - Only present if user has [Module]_MaintainFull.
- Delete
  - Format: Icon
  - Show confirmation: "Are you sure you want to delete [entity description]? This cannot be undone."
    - If Cancel: Dismiss confirmation. Take no action.
    - If OK: Delete the record. Refresh the grid.
  - Only present if user has [Module]_MaintainFull.

### Search Criteria

Sort/Req/Edit Values: X = Required, R = Read Only, E = Edit, and C = Conditional. Refer to Dev Notes when 'C'.

| Element Name | Field Type | ~~Sort (X)~~ | ~~Req (X,C)~~ | Edit (R,E,C) | Notes: FS Lite = Sample, Format and Selection notations only. |
| --- | --- | --- | --- | --- | --- |
| [Search Field] | Text-75 | | | E | Sample: [Example Value]. Default to blank. |
| [Status Filter] | Dropdown | | | E | Selection: Active, Inactive, All. Default to Active. |

### Elements

Sort/Req/Edit Values: X = Required, R = Read Only, E = Edit, and C = Conditional. Refer to Dev Notes when 'C'.

| Grid Element Name | Field Type | Sort (X) | ~~Req (X,C)~~ | Edit (R,E,C) | Notes: FS Lite = Sample, Format and Selection notations only. |
| --- | --- | --- | --- | --- | --- |
| [Column 1 Name] | Text-75 | X | | R | Sample: [Example Value]. |
| [Column 2 Name] | Date | X | | R | Format: m/d/yyyy. Sample: 1/15/2025. |
| [Column 3 Name] | Currency | | | R | Format: $0.00 with comma separator. Right-aligned. Sample: $1,234.56. |

---

## [Entity Name] (DF)

User Access:
- [Module]_MaintainFull: Full access.
- [Module]_ReadOnly: Read-only. Edit action is hidden.

### Designer Notes

- [What information is displayed or captured on this form?]
- [Any business rules that control which fields are editable or visible under specific conditions.]

### Actions

- Edit
  - Format: Button
  - On select, place the form in Edit mode.
  - Only present in View mode and if user has [Module]_MaintainFull.
- Save
  - Format: Button
  - On select, validate all required fields. If validation passes, save the record and return to View mode.
  - If a required field is empty, show message similar to "[Field Name] is required."
  - Only present in Edit mode.
- Cancel
  - Format: Button
  - On select, discard all unsaved changes and return to View mode.
  - Only present in Edit mode.
- Done
  - Format: Button
  - On select, close the form and return to [Screen Name] (SLF).
  - Only present in View mode.
- [Clock Icon]
  - See Master Design for Clock Icon hover behavior.
- Dev Note:
  - // [Technical notes that apply to the form as a whole, e.g., record locking, auto-save behavior]

### Elements

Sort/Req/Edit Values: X = Required, R = Read Only, E = Edit, and C = Conditional. Refer to Dev Notes when 'C'.

| Element Name | Field Type | ~~Sort (X)~~ | Req (X,C) | Edit (R,E,C) | Notes: FS Lite = Sample, Format and Selection notations only. |
| --- | --- | --- | --- | --- | --- |
| [Field Name] | Text-75 | | X | E | Sample: [Example Value]. // Validation: Unique. Show message similar to "[Field Name] must be unique." if duplicate. |
| [Dropdown Field] | Dropdown | | X | E | Selection: [Source table or list]. Sample: [Example Value]. |
| [Calculated Field] | Currency | | | R | Format: $0.00 with comma separator. Right-aligned. // CALC: [Formula or callout reference]. |
| [Conditional Field] | Text-100 | | C | C | Required and editable when [Condition]. Read-only when [Other Condition]. // See Dev Note. Dev Note: // [Condition logic detail]. |
| Last Updated | Date | | | R | Format: m/d/yyyy h:mm AM/PM. // Auto-set on every save. |

---

## [Editable Lookup Table Name] (ELF)

_Use (ELF) for inline-editable reference/lookup tables managed directly in a grid without a separate detail form._

User Access:
- [Module]_MaintainFull: Full access.
- [Module]_ReadOnly: Read-only. Add and Delete actions are hidden.

### Designer Notes

- [What lookup values does this table manage? Why does this table exist?]

### Actions

- Add [Item]
  - Format: Button
  - On select, append a new blank row at the bottom of the grid and place it in Edit mode.
  - Only present if user has [Module]_MaintainFull.
- Save
  - Format: Button or auto-save on row exit.
  - On exit from a row in Edit mode, validate required fields. If validation passes, save the row.
  - Show message similar to "[Field] is required." if a required field is empty.
- Close
  - Format: Button
  - On select, return to [prior screen or Main Menu].
- Dev Note:
  - // Default sort: [Field Name] ascending.

### Elements

Sort/Req/Edit Values: X = Required, R = Read Only, E = Edit, and C = Conditional. Refer to Dev Notes when 'C'.

| Grid Element Name | Field Type | Sort (X) | ~~Req (X,C)~~ | Edit (R,E,C) | Notes: FS Lite = Sample, Format and Selection notations only. |
| --- | --- | --- | --- | --- | --- |
| [Column Name] | Text-75 | X | | E | Sample: [Example Value]. // Validation: Unique. |
| Last Updated | Date | | | R | Format: m/d/yyyy. // Auto-set on save. |

---

## [Report Name] (R)

User Access:
- [Module]_MaintainFull: Full access.
- [Module]_ReadOnly: View-only.

### Designer Notes

- [What does this report show? Who uses it and for what business purpose?]
- [Describe grouping, sorting, or calculation behavior in plain business terms.]

### Actions

- Run Report / Preview
  - Format: Button
  - On select, generate and display the report based on the current filter selections.
- Export to PDF
  - Format: Button
  - On select, export the rendered report as a PDF file.
- Print
  - Format: Button
  - On select, send the report to the default printer.
- Close
  - Format: Button
  - On select, close the report and return to [prior screen].

### Report Filter Criteria

| Element Name | Field Type | Edit (R,E,C) | Notes |
| --- | --- | --- | --- |
| [Date Filter] | Date | E | Format: m/d/yyyy. Default to [value]. |
| [Entity Filter] | Dropdown | E | Selection: [source]. Default to All. |

### Report Elements – [Section Name: e.g., Report Header]

| Element Name | Field Type | Notes |
| --- | --- | --- |
| Report Title | Text | Centered. Bold. Value: "[Report Title Text]" |
| [Entity Field] | Text | Left-aligned. |
| [Date Field] | Date | Format: m/d/yyyy. |
| [Currency Field] | Currency | Format: $0.00 with comma separator. Right-aligned. |

### Report Elements – [Section Name: e.g., Report Footer]

| Element Name | Field Type | Notes |
| --- | --- | --- |
| Page Number | Text | Format: "Page N of M". Right-aligned. |
| [Total Field] | Currency | Format: $0.00 with comma separator. Right-aligned. // CALC: Sum of all [Field] values on report. |

---

## Version Log

Full sequential version history. The opening version table contains only recent versions; earlier versions are recorded here.

| Version | Date | Dev Ready | Edited By | Notes |
| --- | --- | --- | --- | --- |
| 1.0 | [M/D/YYYY] | | [Initials] | Initial draft. |
