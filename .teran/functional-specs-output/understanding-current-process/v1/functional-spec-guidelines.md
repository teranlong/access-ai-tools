# Functional Specification Writing Guidelines

**Purpose:** Guidelines and best practices for writing functional specifications that match the quality and style observed in the sample projects.

**Source:** Derived from analysis of 4 sample projects: Heartland Bank, KnightG, Statewide, and Youngdahl.

---

## 1. Document Organization

### 1.1 One Module Per Document

Each functional specification document covers one functional module — a logical grouping of screens that serve a shared user workflow. Do not combine unrelated workflows into a single document.

- **Do:** Separate Administration, Customers, Jobs, and Reports into distinct module documents.
- **Do not:** Write one large document covering the entire application.

### 1.2 Companion Master Design Document

Every project must have a Master Design document that captures global application behavior: navigation, session handling, button lifecycle, grid behavior, and UI rules. Module specs reference the Master Design rather than repeating these rules.

- **Do:** Write "See Master Design – Grid Features" when standard grid behavior applies.
- **Do not:** Re-specify sort, pagination, or row-click behavior in every module.

### 1.3 Form Order Reflects User Workflow

Within a module, order the form sections in the sequence a user would encounter them during normal use. Start with list/search views, then detail views, then popups triggered from those detail views.

- **Example order:** Customers (SLF) → Customer Detail (DF) → Add Contact Modal Popup

### 1.4 Version History at the Top

The first content after the document title is always a version history table. Keep it updated with each change.

```
| Version | Date | Dev Ready | Edited By | Notes |
|---------|------|-----------|-----------|-------|
```

- **Version:** Increment the minor version (e.g., 1.0 → 1.1) for content changes. Increment the major version (e.g., 1.x → 2.0) for significant scope additions.
- **Dev Ready:** Mark with `X` only when the spec is complete and ready for a developer to implement. Leave blank while still drafting.
- **Notes:** Describe what changed in this version specifically enough that a reader can locate the change. "Updated field table for Customer DF" is good. "Minor edits" is not.

---

## 2. Section-by-Section Guidelines

### 2.1 General Application Features

**Include:**
- Any module-specific overrides of Master Design behavior.
- Application-level config values that affect this module (e.g., `tsysConfig.DefaultState`).

**Do not include:**
- A full restatement of Master Design rules.
- Navigation or layout rules that are already in the Master Design.

### 2.2 Application User Access

**Include:**
- Every capability that controls access to this module.
- A clear description of what each capability grants and denies.
- The format: `[CapabilityName] → [what the user can do]`.

**Do not include:**
- Role names (roles are composed of capabilities — specify capabilities, not roles).
- Implementation details about how capabilities are checked.

**Example:**
```
| Capability | Access Granted |
|---|---|
| Administration_View | View users and roles. Cannot create, edit, or delete. |
| Administration_MaintainFull | Create, edit, delete users and roles. |
```

### 2.3 Sketches

**Include:**
- A reference to each UI mockup relevant to this module.
- The source: Figma frame name and link, Visio file name, or PDF page reference.
- A brief label describing what the sketch depicts.

**Do not include:**
- The mockup images inline in the spec (reference them, do not embed).
- Sketches for screens not covered in this module.

### 2.4 Designer Notes

**Include:**
- Business context that is not obvious from the field names alone.
- The "why" behind the design: what business problem this form solves.
- Key business rules that drive field behavior or conditional logic.
- Historical context when it affects current design (e.g., "In September 2024, locations were introduced, so items now track location-specific inventory").

**Do not include:**
- Implementation details (those go in Dev Notes).
- Field-by-field descriptions (those go in the field table).
- Generic statements like "This form allows users to manage customers." Only write Designer Notes when there is genuinely non-obvious context.

### 2.5 Field Definition Tables

The field table is the core of any DF or SLF specification. Every field visible to the user must appear in the table.

**Columns and valid values:**

| Column | Meaning | Valid Values |
|---|---|---|
| Element Name | The label shown to the user | Exact UI label text |
| Field Type | Data type of the stored or displayed value | `Text-[n]`, `Text-MAX`, `Text-CALC`, `int`, `Bit`, `Date`, `DateTime`, `Decimal`, `Currency` |
| Sort (X) | Whether the user can sort the list by this column | `X` = sortable; blank = not sortable |
| Req (X,C) | Whether the field is required | `X` = always required; `C` = conditionally required; blank = optional |
| Edit (R,E,C) | Whether the field is editable | `R` = read-only; `E` = editable; `C` = conditionally editable |
| Notes | Everything else | See notation guide below |

**Notes column notation guide:**

- `Selection: // [source table].[field], sorted [direction]` — where a dropdown or autocomplete pulls its options from.
- `Format: [Checkbox | Icon | Link | Color Block | m/d/yyyy | etc.]` — how the value is rendered (for Bit fields, always specify Format: Checkbox or equivalent).
- `Dev Note: // [instruction]` — implementation detail. Can appear multiple times, separated by `//`.
- State the validation rule directly: `// Must be unique`, `// Must be greater than 0`, `// Cannot be a future date`.
- State default values directly: `// Default: True`, `// Default: current date`.
- State conditional behavior: `// Disabled unless [FieldName] is checked`.

**Rules for completeness:**
- Every field marked `Req: C` must have a condition stated in the Notes column.
- Every field marked `Edit: C` must have a condition stated in the Notes column.
- Every dropdown or autocomplete field must have a `Selection: //` note.
- Every Bit (boolean) field must have a `Format:` note specifying how it renders.
- Every calculated field (`Text-CALC`) must either reference a Callout or include the formula inline.

**SLF forms have two tables:**
- A **Search Criteria** table: the filter fields above the results list. Typically not sortable, often pre-populated with defaults.
- A **Grid Elements** table: the columns shown in the search results. Apply Sort, Req, Edit rules to the grid columns.

### 2.6 Actions

**Include:**
- Every button, icon action, and link visible on the form.
- For each action: the label, who can see it, when it is enabled, and exactly what happens step by step when triggered.
- Confirmation dialogs, if any: exact message text and button labels.
- What happens on success and on error.

**Do not include:**
- Vague descriptions like "saves the record." Specify: which fields are written, what validation fires first, what the user sees after.

**Format:**
```
**[Action Name]**
- Visible to: [capability]
- Enabled when: [condition, or "Always"]
- Behavior: [Step-by-step what happens]
```

**Example:**
```
**Lock Event**
- Visible to: Dividends_MaintainFull
- Enabled when: Event status is "Unlocked" and at least one dividend row exists
- Behavior: Sets DividendEventStatus to "Locked". All fields on the form become read-only.
  The Lock Event button is replaced by an Unlock Event button.
```

### 2.7 Dev Notes

**Include:**
- Database table and field references used by this form.
- Encryption or masking requirements.
- Email template references (by key or name).
- Background processing triggered by a user action.
- Non-obvious query logic (e.g., "filter to ACTIVE records only").

**Do not include:**
- UI styling details (those belong in the Master Design or field Format notes).
- Business rules (those belong in Designer Notes or the field table).

Dev Notes can appear inline in the field table Notes column (preferred for field-specific notes) or as a standalone section (preferred for form-level notes).

---

## 3. Special Section Types

### 3.1 Callouts

Use Callouts for formulas, calculations, and business rules that are too complex or important to bury inline in a Notes column. Callouts should be:

- Explicitly labeled (e.g., **Callout: Calculate Net Granted**).
- Self-contained: define all variables used.
- Precise: use exact field or variable names, not approximations.

**Example:**
```
**Callout: Calculate Shareholder Dividend Amount**
- Dividend Amount = (Share Count × Amount Per Share) + Sum of all Adjustments for this shareholder
- Dividend Withheld = Dividend Amount × Withhold Percentage (only if Shareholder Tax Withhold Flag = True)
- Net Payment = Dividend Amount – Dividend Withheld
```

### 3.2 Dependency Tables

Use Dependency Tables when a change to one field triggers recalculation of other fields. This is common in forms with cascading logic.

Format: List each trigger event and the fields that must be re-evaluated.

**Example:**
```
| When this changes... | Re-evaluate these fields... |
|---|---|
| Location Selection | Available inventory, In-Use inventory |
| Grade/DFG value | Relative Compaction %, Pass/Fail result |
| Project Specification | Acceptable range min/max values |
```

### 3.3 State Transition Diagrams

When a record has a status field with defined allowed transitions, document the transitions explicitly. List: each state, the actions that move from one state to another, and any conditions on those transitions.

**Example:**
```
DFR Status transitions:
- In Draft → Submitted: User clicks Submit. Requires all required fields completed.
- Submitted → In Review: Supervisor opens the DFR and clicks Begin Review.
- In Review → Approved: Supervisor clicks Approve.
- In Review → In Draft: Supervisor clicks Return to Draft (with required remarks).
- Approved → Distributed: System generates PDF and marks Distributed.
```

---

## 4. Naming Conventions

### 4.1 Database Object References

| Prefix | Meaning | Example |
|---|---|---|
| `tbl` | Main data table | `tblCustomer`, `tblDividendEvent` |
| `tlkp` | Lookup table (drives dropdowns) | `tlkpManufacturer`, `tlkpStatus` |
| `tval` | Value/configuration table | `tvalEmailTemplate` |
| `txrf` | Cross-reference (junction) table | `txrfJobItem` |
| `tsysConfig` | System configuration table | `tsysConfig.DefaultState` |

### 4.2 Field References in Text

When referencing a specific field by name in prose or action descriptions, use `[FieldName]` notation. Example: "When `[ActiveFlag]` is set to False, the record is hidden from all search results."

### 4.3 Capability References

Use `[CapabilityName?]` to indicate a conditional capability check. Example: "Show the Delete button only if `[Administration_MaintainFull?]`."

### 4.4 Form Type Suffixes

Always include the form type in parentheses after the form name in section headings.

| Suffix | Form Type |
|---|---|
| (SLF) | Search List Form |
| (DF) | Detail Form |
| (ELF) | Editable List Form |
| (SELF) | Search/Entry/List Form |
| (R) | Report |
| (Modal Popup) | Overlay dialog |
| (LF) | List Form (no search) |

---

## 5. Writing Style Rules

### 5.1 Be Atomic

Write one behavior per bullet or table row so it can be independently designed, implemented, and tested.

- **Do:** "The Delete button is hidden when the record has any associated transactions."
- **Do not:** "The Delete button behaves appropriately based on the record's state."

### 5.2 Be Measurable

Phrase behaviors so a QA engineer can say pass or fail based on an observable outcome.

- **Do:** "The Save button is disabled until all fields marked Req: X contain a non-empty value."
- **Do not:** "Validate the form before saving."

### 5.3 Avoid Vague Language

- **Do not use:** "etc.", "and so on", "handle all edge cases", "as appropriate", "similar to above."
- **Do:** State the specific items, specific cases, or specific rule.

### 5.4 Mark Conditional Requirements Explicitly

If a requirement applies only under specific conditions, state the condition first.

- **Do:** "If the customer's Credit Hold Flag is True, display a red square icon next to the customer name."
- **Do not:** "Show a warning for credit-hold customers."

### 5.5 Distinguish Must-Haves from Nice-to-Haves

Label lower-priority or future items explicitly so they are not accidentally treated as requirements.

- **Do:** `**Future:** Ability to specify a "Superseded By" link between standards.`
- **Do not:** Mix future ideas into the field table or action list without labeling them.

### 5.6 Use Present Tense for Behaviors

Describe what the system does, not what it should do or will do.

- **Do:** "The form displays the customer's current share balance."
- **Do not:** "The form should display the customer's current share balance."

---

## 6. Common Anti-Patterns to Avoid

| Anti-Pattern | Why It Is a Problem | Better Approach |
|---|---|---|
| Field listed without a type | A developer cannot determine how to store or render the value | Always specify Field Type |
| Required field with no Req marker | The developer may treat it as optional | Mark with X or C in the Req column |
| Conditional field with no condition stated | The developer will guess the condition or ask | State the condition in the Notes column |
| Action described as "saves the record" | Ambiguous — does it validate first? What is saved? What happens after? | Write step-by-step behavior |
| Business rule buried in a Dev Note | Dev Notes are for developers; business rules belong where designers and stakeholders can see them | Put business rules in Designer Notes or the Notes column |
| Designer Notes for every form | Adds noise when forms are self-explanatory | Only write Designer Notes when context is genuinely non-obvious |
| Version notes that say "minor edits" | Reviewers cannot find what changed | Describe the specific section or field that changed |
| Dropdown with no Selection source | The developer does not know where options come from | Always add `Selection: // [table].[field]` |
