# Functional Specification Template

**Purpose:** This file defines the structure for writing functional specifications. Use Template B for all new projects. Template A is documented for reference only and reflects an older, simpler style.

**Source:** Derived from analysis of 4 sample projects: Heartland Bank, KnightG (Knight Guardian), Statewide, and Youngdahl.

---

## Template B – Current Standard (Form-centric)

Used in: KnightG, Statewide, Youngdahl

This is the recommended template. It uses formal field definition tables, named form types, and a companion Master Design document.

---

### Document: Master Design

The Master Design is a separate document written once per project. All module specs reference it rather than repeating global rules.

```
# [Application Name] – Functional Specifications – Master Design

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
| 1.0     | [Date] |         | [Initials] | Initial version |

## General Application Features

[Describe global UI elements: application name in browser title, logo placement,
navigation behavior, footer content, session handling, and any global links
(e.g., My Settings, Help).]

## Home Page (DF)

[Describe the default screen shown after login.]

## UI Rules

[Global rules for layout, spacing, color, and typography that apply to all screens.]

## Search Pages – Criteria

[Standard behavior for search/filter forms: how Reset works, what triggers a search,
default sort order behavior, empty result handling.]

## Grid Features

[Standard behavior for all list/grid displays: column sorting, row selection,
inline edit mode, pagination, row highlighting, empty state message.]

## Detail Pages

[Standard behavior for all detail forms: Edit/Save/Cancel button lifecycle,
required field validation, unsaved-change warnings, created-by/updated-by display.]
```

---

### Document: Module Functional Spec

One document per functional module. Modules group related screens by user workflow area.

```
# [Application Name] – Functional Specifications – Module [N]: [Module Name]

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
| 1.0     | [Date] |         | [Initials] | Initial version |

## General Application Features

[Reference the Master Design. List any module-specific overrides or additions here.]

## Application User Access

[List the capabilities required to access this module and what each capability grants.
Use the format: Capability Name → What the user can do.]

| Capability | Access Granted |
|-----------|----------------|
| [CapabilityName]_View | View records; no edit or delete. |
| [CapabilityName]_MaintainFull | Create, edit, and delete records. |

## Sketches

[List references to UI mockups, Figma frames, or Visio diagrams.
Include: sketch name, source (Figma link or file path), and what it depicts.]

---

## [Form Name] ([FormType])

> **Form types:** SLF = Search List Form | DF = Detail Form | ELF = Editable List Form |
> SELF = Search/Entry/List Form | R = Report | Modal Popup = Overlay dialog

#### Designer Notes

[Optional. Include when the form has non-obvious business context.
Explain: what this form is for, why it exists, key business rules that drive the design.
Do not repeat information that belongs in field definitions or actions.]

#### Access Level

[State which capability a user must have to view and/or edit this form.]

#### Search Criteria

[SLF and SELF forms only. List the fields the user can use to filter the list.]

| Element Name | Field Type | Req (X,C) | Notes |
|---|---|---|---|
| [Field Label] | [Type] | [X or C] | [Selection source, default value, or behavior note] |

#### Elements / Grid Elements

[The field definition table. Use "Elements" for DF forms. Use "Grid Elements" for SLF/SELF forms.
For SLF forms, include both a Search Criteria table above and a Grid Elements table here.]

| Element Name | Field Type | Sort (X) | Req (X,C) | Edit (R,E,C) | Notes |
|---|---|---|---|---|---|
| [Field Label] | [Type] | [X or blank] | [X, C, or blank] | [R, E, or C] | [See notation guide below] |

**Field Type values:** `Text-[n]` (max character length), `Text-MAX` (unlimited), `Text-CALC` (calculated, not stored), `int`, `Bit` (boolean), `Date`, `DateTime`, `Decimal`, `Currency`

**Sort:** `X` = column is sortable by the user. Blank = not sortable.

**Req:** `X` = always required. `C` = conditionally required (condition explained in Notes). Blank = optional.

**Edit:** `R` = read-only always. `E` = editable. `C` = conditionally editable (condition in Notes).

**Notes column notation:**
- `Selection: // [table].[field], sorted [direction]` — dropdown or lookup source
- `Format: [Checkbox | Icon | Link | Color Block | m/d/yyyy]` — how the field is displayed
- `Dev Note: // [instruction]` — implementation detail for the developer
- Validation rules, default values, and conditional logic are also placed here.

#### Actions

[List every button, link, and interactive behavior on this form.
For each action: name, where it appears, what it does, and any conditions that enable/disable it.]

**[Button or Action Name]**
- Visible to: [capability or role]
- Enabled when: [condition, or "Always"]
- Behavior: [What happens step by step when the user clicks this]

#### Dev Notes

[Optional. Use for implementation details that don't fit inline in the field table.
Examples: API calls, background jobs, email templates, encryption requirements.]

---

[Repeat the form section above for each screen in this module, in user workflow order.]

---

## Version Log

[Repeat the version history table from the top of the document here, kept in sync.]

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
```

---

### Document: API Specification (Optional)

Used when the application exposes a programmatic interface to external systems.

```
# [Application Name] – Functional Specifications – API

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
| 1.0     | [Date] |         | [Initials] | Initial version |

## API User Access

[Describe how API callers authenticate. Include: account type, credential format,
and which capabilities the API account requires.]

## Assumptions and Design Decisions

[Document any non-obvious design choices that constrain the API behavior.
Examples: request/response formats, call sequencing, error handling strategy.]

## [Endpoint Name] (API Call)

**Arguments:**

| Argument | Type | Required | Description |
|---|---|---|---|
| [ArgumentName] | [Type] | Yes/No | [What it means and valid values] |

**Returns:**

| Field | Type | Description |
|---|---|---|
| [FieldName] | [Type] | [What it contains] |

**Dev Note:** [Any implementation notes for this endpoint]
```

---

### Document: Data Migration Specification (Optional)

Used when an existing system is being replaced and data must be converted.

```
# [Application Name] – Functional Specifications – Data Migration and Conversion

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
| 1.0     | [Date] |         | [Initials] | Initial version |

## [Source Table/Object] → [Target Table/Object]

[Describe what is being migrated, from where, and to where.]

| Source Field | Target Field | Transformation Rule |
|---|---|---|
| [SourceField] | [TargetField] | [Rule: copy as-is, convert format, derive from formula, or set default] |

**Notes:** [Any special handling — null treatment, deduplication, conditional mapping]
```

---

## Template A – Legacy / Simple Style

Used in: Heartland Bank (and early-stage KnightG)

This style predates the formal field definition tables. It uses ICF/DF form naming and describes fields in prose or simple bullet lists. Use this as a reference only — new specs should use Template B.

```
# [Application Name] – Functional Specifications – Module [N]: [Module Name]

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|

## General Application Features

[Reference to application-wide conventions.]

## Application User Access

[Brief description of who can access this module.]

## [Form Name] (ICF)

[Item Collection Form — a list view of records with search/filter capability.]

#### Designer Notes

[Business context for the form.]

**Columns:** [List the columns shown in the list, with notes on sorting and default order.]

**Search:** [Describe filter options.]

**Actions:** [List clickable actions available on the list.]

---

## [Form Name] (DF)

[Detail Form — view or edit a single record.]

#### Designer Notes

[Business context for the form.]

**Fields:**
- [Field Name] ([Type]): [Required/Optional]. [Description of behavior.]
- [Field Name] ([Type]): [Calculated from: formula or rule.]

#### Callouts

[Use callouts for formulas or derived values that need to be explicitly documented.]

> **[Callout Label]:** [Formula or business rule stated precisely, e.g., "Net Granted = Gross Granted – Canceled"]

**Actions:** [List buttons and their behaviors.]

---

## Version Log

| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
```
