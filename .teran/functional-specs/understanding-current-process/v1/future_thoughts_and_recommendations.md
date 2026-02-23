# Future Thoughts and Recommendations

**Purpose:** Specific, actionable recommendations for improving the functional spec process, based on gaps and inconsistencies observed in the 4 sample projects.

**Source:** Derived from analysis of Heartland Bank, KnightG, Statewide, and Youngdahl functional specification documents.

---

## Rec-01 – Standardize Form Type Taxonomy

**Observation:** Three distinct naming conventions are in use across 4 projects — ICF/DF (Heartland), SLF/LF/DF/R (KnightG, Statewide), and SLF/DF/SELF/R/Modal Popup (Youngdahl). There is no master register of valid form types.

**Recommendation:** Define a canonical list of form type suffixes with short definitions. Publish this in a project-start checklist and in the guidelines. Retire ICF in favor of SLF for new projects. Decide whether SELF is a distinct type or a variant of SLF, and document that decision.

**Impact:** Low effort, high value. Eliminates ambiguity for new team members and AI-assisted spec generation.

---

## Rec-02 – Make the Master Design a Required Project Artifact

**Observation:** Three of four projects have a Master Design document. Heartland Bank does not, resulting in repeated inline rules and some global behaviors that are implied rather than stated.

**Recommendation:** Require a Master Design document for every new project, written at project start before any module specs begin. The Master Design template should be provided alongside the module spec template (this is already represented in `functional-spec-template.md`). At minimum, a Master Design must cover: navigation, session handling, Edit/Save/Cancel lifecycle, grid behavior, and empty state handling.

**Impact:** Medium effort at project start, high ongoing value — eliminates repeated copy-paste of global rules across modules.

---

## Rec-03 – Formalize the Callout Format

**Observation:** Callouts are used in all 4 projects but with different formats: prose blocks (Heartland), numbered with cross-references (Youngdahl), structured tables (Statewide). There is no shared convention.

**Recommendation:** Adopt the Youngdahl numbered Callout pattern as the standard: `Callout #[N] – [Descriptive Name]`. Require numbered cross-references when a form section depends on a Callout (e.g., "See Callout #4"). In addition, for Callouts involving tables of effects (like Statewide's inventory transaction table), use a structured table format rather than prose.

**Impact:** Low effort per spec, high cumulative value for anyone reading multiple specs or generating test cases.

---

## Rec-04 – Add a Formal Spec Completion Gate Beyond "Dev Ready"

**Observation:** The Dev Ready column in the version history is the only signal that a spec is complete. It is self-assessed by the author with no documented review criteria.

**Recommendation:** Define explicit criteria that must be met before Dev Ready is marked. The acceptance criteria in `acceptance-criteria-template.md` represent a good starting point for this gate. Consider adding a "Reviewed By" column to the version history to capture at minimum a second-person review.

**Impact:** Medium effort to establish the process gate; the acceptance criteria template is already written and can be the basis immediately.

---

## Rec-05 – Standardize the Dependency Table Format

**Observation:** Youngdahl Module 3 introduced Dependency Tables to document cascading field recalculation rules — a genuinely useful pattern for complex forms. Statewide's inventory pattern table serves a similar purpose. Neither format is formally named or defined.

**Recommendation:** Define a standard Dependency Table format in the guidelines and include it in the module spec template as an optional section. Use format: `When [this field] changes → re-evaluate [these fields]`. This pattern is most valuable for forms with 3 or more interdependent calculated or conditionally required fields.

**Impact:** Low effort to standardize; prevents missing cascading logic in implementation and testing.

---

## Rec-06 – Create a Formal "Business Rules" Section to Complement Designer Notes

**Observation:** Important business rules are currently embedded in Designer Notes, which are written as narrative context. Designer Notes are valuable but are not searchable as discrete rules, not numbered, and not directly linked to the field or action they govern.

**Recommendation:** Consider adding an optional "Business Rules" section per module (not per form) that lists critical rules as discrete, numbered statements. Designer Notes can still exist for narrative context, but rules that would appear in test cases should also appear in a Business Rules list. Example: `BR-01: Dividends are calculated on granted shares, not vested shares. Source: Designer Notes – Module 4.`

**Note:** Only introduce this section for modules with 3 or more non-obvious business rules. Not every module needs one.

**Impact:** Medium effort per spec. High value for test case generation and for any process where specs are consumed by someone other than the original author.

---

## Rec-07 – Distinguish "Spec for New System" from "Documentation of Existing System" Visually

**Observation:** Youngdahl Module 1 mixes sections specifying the new web application with sections documenting the existing Access desktop application. Both appear at the same heading level with no visual distinction.

**Recommendation:** In any spec that documents an existing system alongside the new system, prefix existing-system sections with a consistent label: `[Legacy Reference]` or `[Existing System – Do Not Build]`. This prevents a developer from accidentally implementing something that already exists.

**Impact:** Low effort, prevents implementation errors.

---

## Rec-08 – Track the Access Migration-Specific Spec Types Separately

**Observation:** Two spec types appear in the samples that are unique to Access migration projects but are not formally named or templated: the Data Migration and Conversion spec (Youngdahl) and the API spec (KnightG). Both follow patterns that could be templated.

**Recommendation:** Add the Data Migration spec template and API spec template to the project-start checklist as optional artifacts. Include them in the project-level spec inventory (a document listing which spec documents exist for a given project and their current Dev Ready status).

**Impact:** Low effort. Prevents these doc types from being written ad hoc or inconsistently across future projects.
