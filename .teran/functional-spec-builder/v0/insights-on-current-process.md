# Insights on the Current Functional Specification Process

Observations inferred from analysis of 20 functional specification documents across four projects. These are descriptive findings about how the process appears to work in practice — not recommendations. Recommendations are in a separate document.

---

## 1. The Process Is Primarily Author-Driven, Not Template-Driven

The documents across all four projects are consistent in their core sections (version table, Actions, Elements, Designer Notes) without evidence of a shared written template. The consistency appears to come from a single primary author learning and refining the format across projects rather than from a formal template enforced by a tool or process gate. This is evident in the fact that structural conventions evolved across projects (e.g., the adoption of the // comment prefix, the shift from H4 to H2 for screen headings, the introduction of the ELF form type) without any of the older documents being retroactively updated to match.

## 2. Format Evolved Iteratively Across Projects

The four projects represent a visible maturation arc:

- The earliest project (desktop application) used a compressed heading hierarchy (H4–H6 for all content), no form-type abbreviation for List Forms beyond "LF", no Master Design document, no per-screen User Access declarations, and no // prefix for Dev Notes.
- The second project (first web application) introduced H2-level screen headings, the SLF/ELF form type vocabulary, the Master Design document, per-screen User Access declarations, the // prefix for Dev Notes, the Format: Button/Icon/Link sub-bullet, and the "Assumptions and Design Decisions" section.
- The third project carried forward those conventions with minimal change, using the same Master Design boilerplate (copy-pasted from the second project) with additions.
- The fourth project added module-level Designer Note sections, module-level Callouts sections, the Version Log section at end of document, the "Screen template – NOT FOR DEV" placeholder, and expanded Master Design rules (time display, sticky title bar, mobile scrolling, Simple HTML features).

This evolutionary pattern means the current "standard" is implicitly the most recent project's conventions, but it has never been formally documented or back-applied to earlier projects.

## 3. Designer Notes and Dev Notes Are Informally Separated

The conceptual distinction between Designer Notes (business-facing) and Dev Notes (developer-facing) is consistently present across all documents. However, the enforcement is informal — it relies on the author's judgment about which audience a note is intended for. In practice:

- Some Designer Notes contain database column references that belong in a Dev Note.
- Some Dev Notes contain business rationale that belongs in a Designer Note.
- The distinction appears to be more reliably applied in later revisions of a document than in early drafts (early versions of a section often have a single block of notes later split into audience-specific sections).

## 4. Strikethrough Is the Primary In-Document Change Record

Rather than deleting superseded requirements, the author preserves them with strikethrough formatting. This means the documents function as a living log of design decisions, not just a specification of current behavior. A reviewer can see what was considered and discarded. This practice is consistent across all four projects, suggesting it is a deliberate convention rather than an accident of tooling.

The limitation of this approach is that strikethrough accumulates over time. Long-running documents (particularly the web application module specs with 20+ version entries) become visually dense, requiring a reader to mentally filter out struck-through content when reading the current specification.

## 5. The Version Table Serves as the Change Log

There is no separate changelog file or external change tracking system visible in the documents. The version table Notes column is the sole structured record of what changed in each revision. For complex revisions affecting many screens, the Notes cell contains multi-line bulleted lists within the table cell, which renders correctly in Word but may cause formatting issues in other environments.

The version table also doubles as a workflow signal: the Dev Ready column indicates which versions are cleared for implementation. This creates a lightweight, within-document status tracking mechanism — a developer can scan the version table to know whether to act on a given version.

## 6. Master Design Documents Are Stable Reference Points

Master Design documents accumulate fewer version entries than module specs, indicating they are revised less frequently. They serve as a shared UI contract across all modules of a project. When a global UI convention changes (e.g., a new icon behavior, a new date entry pattern), it is updated in the Master Design rather than in every module spec. Module specs then inherit the change automatically via their "See Master Design" references.

This architecture works well but creates a dependency: a developer working from a module spec alone cannot fully implement the screen without also reading the Master Design. The module specs do not enumerate which Master Design sections are relevant for a given screen.

## 7. API Specifications Are Treated as a Module Variant

The API specification documents follow the same structural template as module specs — the same version table, capabilities section, and screen-level sections. The only structural difference is that screen sections become API call sections, with Arguments and Output tables replacing the Element table. This design choice keeps all specification documents in a single consistent format regardless of whether the specified "screen" is a UI form or a programmatic interface.

The earliest API document in the corpus (a brief early design note) does not follow this convention, suggesting the structured API spec format was introduced at a later point in the project's evolution.

## 8. Callouts Were Introduced to Handle Shared Calculation Logic

The callout mechanism — a named reusable logic block defined once and referenced from multiple screen sections — was introduced in the desktop application project and refined in the most recent web project. In the desktop application, callouts appear within individual screen sections (per-screen scope). In the most recent project, they are elevated to a module-level section, suggesting the author found that per-screen callout tables were being duplicated and decided to centralize them.

The two intermediate projects (web applications 2 and 3) have no callout mechanism. Complex logic that would benefit from callouts is instead duplicated verbatim in multiple screen sections in those projects.

## 9. Error Message Text Is Inconsistently Specified

Most documents specify some error messages with quoted text ("Legal name must be unique.") and others with hedged phrasing ("show message similar to…"). The phrase "show message similar to" appears to be used deliberately when the author intends to allow developer discretion on exact wording. There is no visible pattern distinguishing which messages warrant exact specification and which do not. The result is that some error messages are precisely defined across the product while others are left to developer judgment.

## 10. The Spec Format Was Not Designed for Report Screens

Report screens (R) appear in multiple projects and use a simplified element table format (3 columns instead of 6). However, the report element tables are consistently less detailed than the form element tables. Report sections tend to describe the report's grouping and filtering logic but leave layout and formatting details to developer judgment. The format was clearly designed for interactive UI forms and adapted for reports without a dedicated report-specification convention.

## 11. One Author Appears Responsible for the Majority of Document Maintenance

Initials and name codes visible in the Edited By column across all four projects point to a small number of contributors, with one individual appearing as the primary author in all four projects. Occasional entries show a second contributor. This concentration of authorship explains the high degree of consistency across documents despite the absence of a written template — the conventions live in one person's practice rather than in a shared reference artifact.

## 12. Documents Are Long-Lived and Continuously Revised

Version tables with 15–25 entries are common. Some modules show active revision from 2022 through early 2026. The documents are not treated as deliverables that are finalized and archived — they are living working documents that are updated as requirements evolve during and after the development cycle. This means the spec for a screen may be in a different state than the implemented feature, and the Dev Ready flag serves as the only formal indicator of whether the spec has been reconciled with the build.
