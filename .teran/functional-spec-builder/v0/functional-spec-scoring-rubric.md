# Functional Specification – Scoring Rubric

Use this rubric to evaluate the quality of a completed functional specification module. Score each criterion from 1 to 5 using the descriptions below. A score of 3 represents a minimally complete spec; 4–5 represents a well-crafted, reviewer-ready spec. A score of 1–2 identifies a spec that requires revision before development can begin.

**Scoring summary:** Calculate a total score out of 50 (10 criteria × 5 points each). A score of 40 or above is considered Dev Ready quality.

---

## Criterion 1: Document Header and Version Table

Evaluates whether the document is properly identified and its revision history is complete and accurate.

| Score | Description |
| --- | --- |
| 5 | Two H1 title lines present. Cross-reference boilerplate present. Version table present with all five columns. All rows have Version, Date, Edited By, and Notes populated. Dev Ready marked X on appropriate rows. Date format is consistent (M/D/YYYY). Notes describe what changed per version. |
| 4 | All required elements present. Minor inconsistency: one date format deviation, one Notes entry that describes the document rather than the change, or Dev Ready is blank on a row that is clearly finalized. |
| 3 | Version table present. At least two columns populated per row. Dev Ready column present but inconsistently used. Notes column contains at least one meaningful entry. |
| 2 | Version table present but missing one or more columns. Multiple rows have blank Notes or blank Edited By fields. |
| 1 | Version table absent, or only a document title is present with no version information. |

---

## Criterion 2: Application User Access (Module Level)

Evaluates whether the module's capabilities are defined clearly enough for a developer to implement access control.

| Score | Description |
| --- | --- |
| 5 | Capabilities table present with all columns populated. Every capability used in per-screen User Access sections is listed here. Capability names follow a consistent naming convention. Descriptions distinguish what each capability allows versus restricts. |
| 4 | Capabilities table present. All capabilities used in the doc are listed. Minor: one capability description is vague or one capability is referenced in a screen section without being in this table. |
| 3 | Capabilities table present. At least two capabilities defined. Not all capabilities referenced in screen sections appear in this table, but the gap is minor (1–2 missing). |
| 2 | Capabilities table present but contains only one capability, or descriptions are identical for all capabilities, making them indistinguishable. |
| 1 | No Application User Access section present. Access control is not addressed. |

---

## Criterion 3: Per-Screen User Access Declarations

Evaluates whether each screen section specifies who can access it and at what level.

| Score | Description |
| --- | --- |
| 5 | Every screen section contains a User Access declaration. Each declaration names the specific capability that grants access. Restrictions (e.g., "Edit action hidden for ReadOnly") are stated per-action in the Actions section, not vaguely. |
| 4 | All screen sections have a User Access declaration. One or two screens state access vaguely (e.g., "Admin only" without referencing a named capability). |
| 3 | Most screen sections have a User Access declaration. Up to two screens are missing the declaration but their access requirements can be inferred from context. |
| 2 | Fewer than half of screen sections have User Access declarations. Access control approach is unclear or inconsistent. |
| 1 | No per-screen User Access declarations. Access control is unaddressed at the screen level. |

---

## Criterion 4: Actions Section Completeness

Evaluates whether every screen's actions are fully specified so that a developer can implement behavior without follow-up questions.

| Score | Description |
| --- | --- |
| 5 | Every action on every screen has: a label, a Format sub-bullet (Button/Icon/Link), an on-select behavior description, a capability guard where applicable, an exact confirmation message where applicable, and a Dev Note where a technical detail is needed. Multi-step actions describe each step. Paired actions (Edit/Save/Cancel/Done) are present on all DF screens. |
| 4 | All actions are documented. One or two actions are missing a Format sub-bullet or have a vague behavior description ("open the record" without specifying which form or mode). Dev Notes are present for most non-obvious behaviors. |
| 3 | All major actions are documented. Some actions lack Format sub-bullets. Confirmation dialogs are described but message text is not quoted. Dev Notes are present for fewer than half the actions that need them. |
| 2 | Some actions are documented but significant gaps exist. One or more screens have an Actions section that lists only button labels without behavior descriptions. |
| 1 | Actions section absent from one or more screens, or so sparse (e.g., "standard actions apply") that a developer cannot implement the screen from the spec. |

---

## Criterion 5: Elements Table Completeness

Evaluates whether every field on every screen is specified with enough detail for a developer to implement it.

| Score | Description |
| --- | --- |
| 5 | Every screen has an Elements table. All six columns are present with correct headers. Every row has a Field Type, a Req/Edit value, and a Notes entry with at minimum a sample value or format. Calculated fields have a formula or callout reference. Conditional fields have the condition stated. Dev Notes for field-level implementation detail are present for every non-obvious field. |
| 4 | All screens have an Elements table. Most rows are complete. Up to three Notes cells are blank. Calculated fields have a formula. Minor: one or two conditional fields are missing the explicit condition. |
| 3 | All screens have an Elements table. Req and Edit columns are populated for most rows. Notes cells are populated for at least 50% of rows. Some field types are missing or use non-standard type names. |
| 2 | Elements tables present but incomplete: more than a third of rows have blank Notes cells, or Field Type column is inconsistently filled. Conditional and calculated fields are not distinguished from standard fields. |
| 1 | One or more screens are missing an Elements table, or the table exists with only field names and no other columns populated. |

---

## Criterion 6: Designer Notes Quality

Evaluates whether the business context provided in Designer Notes is sufficient for a business analyst or stakeholder to confirm the spec is correct.

| Score | Description |
| --- | --- |
| 5 | A module-level Designer Note section explains the module's business purpose in full sentences. Every screen that involves non-obvious business logic has a screen-level Designer Note. Notes use plain business language (no database names, no field-level implementation detail). Conditional business rules state the condition before the consequence. |
| 4 | Module-level Designer Note present. Most screens with non-obvious logic have a Designer Note. One or two Designer Notes are sparse (a single sentence where a paragraph is needed) or contain Dev Note content mixed in. |
| 3 | Module-level Designer Note present. Fewer than half of screen sections have Designer Notes. For screens that do have them, the note provides enough context to understand the screen's purpose. |
| 2 | Module-level Designer Note is a placeholder (e.g., "xxxx" or "TBD"). Per-screen Designer Notes are absent from the majority of screens. |
| 1 | No Designer Notes present anywhere in the document. |

---

## Criterion 7: Dev Notes Specificity

Evaluates whether Dev Notes provide enough technical detail for a developer to implement the behavior without asking follow-up questions.

| Score | Description |
| --- | --- |
| 5 | Dev Notes are present for every non-obvious technical behavior. Each Dev Note states a specific database column, formula, sort order, validation rule, or default value. No Dev Note uses vague language ("handle appropriately", "as needed"). // prefix is used consistently for all Dev Notes in web app specs. |
| 4 | Dev Notes are present for most non-obvious behaviors. One or two Dev Notes are present but vague (state what to do but not how). // prefix used consistently. |
| 3 | Dev Notes cover the most critical implementation details (sort order, required field validation, default values). Some non-obvious behaviors are not covered by Dev Notes. // prefix used inconsistently. |
| 2 | Dev Notes are sparse. Only a few are present. Major implementation questions (how calculated fields are computed, what triggers conditional behavior) are left unanswered. |
| 1 | No Dev Notes present. All technical implementation detail is absent from the document. |

---

## Criterion 8: Callout Usage (if applicable)

Evaluates whether reusable logic blocks are extracted into callouts and referenced correctly. If the module has no logic referenced from two or more locations, score this criterion 5 (N/A).

| Score | Description |
| --- | --- |
| 5 | All logic blocks referenced from two or more locations are defined as callouts. Each callout is defined in the module-level Callouts table before being referenced. References in screen sections use consistent phrasing ("See [Callout Name] callout"). Each callout entry in the table is self-contained: a developer can implement it without reading the referencing screen sections. |
| 4 | Callouts used correctly. One or two references use slightly inconsistent phrasing. All callout definitions are present but one may lack a complete formula. |
| 3 | At least one callout defined and correctly referenced. Some repeated logic exists that is not extracted into a callout (it is duplicated verbatim in multiple screen sections instead). |
| 2 | Callout section present but incomplete: references exist in screen sections that point to callouts not defined in the module-level table, or callout definitions are too vague to implement. |
| 1 | No callout mechanism used, but complex logic appears duplicated in 3 or more screen sections with slight inconsistencies between the copies. |

---

## Criterion 9: Version Control and Change Traceability

Evaluates whether the document's edit history can be reconstructed from the version table and whether superseded content is handled correctly.

| Score | Description |
| --- | --- |
| 5 | Version table Notes entries describe specific changes by screen name. Dev Ready flags are present and accurate. Superseded requirements are preserved with strikethrough and a version note explains the change. Full version history accessible (either in the opening table or split between opening table and a Version Log section at end). |
| 4 | Version table is complete. Notes describe changes adequately. One or two superseded requirements were deleted rather than struck through, but the version table Notes record the removal. |
| 3 | Version table is present and mostly complete. Some Notes entries are vague (e.g., "various changes", "updates"). Strikethrough used for at least some superseded content. |
| 2 | Version table present but Notes column is mostly blank or identical across rows. No strikethrough convention used; it is unclear what changed between versions. |
| 1 | Only one version row present (initial draft) with no subsequent version history, despite the document showing signs of significant revision (multiple Dev Ready marks, strikethrough content, or notes referencing prior versions). |

---

## Criterion 10: Consistency and Formatting

Evaluates whether the document follows the established conventions consistently from screen to screen and section to section.

| Score | Description |
| --- | --- |
| 5 | All form type abbreviations are present and correct. Heading levels are consistent throughout (H2 for screens, H3 for subsections). Element table headers are identical across all screens (same column names, same strikethrough pattern). Action bullets use consistent structure. // prefix for Dev Notes is applied uniformly. No stray formatting artifacts from conversion (unresolved Mammoth warning artifacts, broken table rows, garbled characters). |
| 4 | Consistent overall. Up to three deviations: one heading level off, one element table missing a header strikethrough, or Dev Note // prefix missing on two or three instances. |
| 3 | Generally consistent. Heading levels vary by one level in a few sections. Element table column headers vary between screens (some have strikethrough, some do not). // prefix used for most but not all Dev Notes. |
| 2 | Significant inconsistency: heading levels vary throughout, element table formats differ between screens, action format sub-bullets missing on half or more of actions. |
| 1 | No consistent formatting conventions followed. The document reads as an ad-hoc collection of notes rather than a structured specification. |

---

## Scoring Summary

| Criterion | Max Points | Score |
| --- | --- | --- |
| 1. Document Header and Version Table | 5 | |
| 2. Application User Access (Module Level) | 5 | |
| 3. Per-Screen User Access Declarations | 5 | |
| 4. Actions Section Completeness | 5 | |
| 5. Elements Table Completeness | 5 | |
| 6. Designer Notes Quality | 5 | |
| 7. Dev Notes Specificity | 5 | |
| 8. Callout Usage | 5 | |
| 9. Version Control and Change Traceability | 5 | |
| 10. Consistency and Formatting | 5 | |
| **Total** | **50** | |

**Interpretation:**
- 45–50: Exemplary. Ready for developer handoff without revision.
- 40–44: Dev Ready with minor notes. Communicate gaps to writer before handoff.
- 30–39: Requires targeted revision in identified criteria before Dev Ready.
- 20–29: Substantial revision needed. Return to writer with specific criteria feedback.
- Below 20: Restart from template. Document does not meet minimum standard for a functional specification.
