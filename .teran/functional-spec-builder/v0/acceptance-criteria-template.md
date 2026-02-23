# Functional Specification – Acceptance Criteria Checklist

Use this checklist to verify that a functional specification module is complete before marking it Dev Ready. Each item is a binary pass/fail gate. A document cannot be marked Dev Ready if any item in the **Required** sections is marked Fail.

**Instructions:** Work through each section. Mark each item Pass, Fail, or N/A. Record the version number and date of the document reviewed at the top.

---

**Document reviewed:** ___________________________
**Module:** ___________________________
**Version reviewed:** ___________________________
**Date reviewed:** ___________________________
**Reviewed by:** ___________________________

---

## Section 1: Document Header

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 1.1 | Document opens with two H1 lines: project/application name and "Functional Specifications – Module N [Name]". | | |
| 1.2 | Cross-reference boilerplate sentence is present immediately after the H1 lines. | | |
| 1.3 | Version table is present with all five columns: Version, Date, Dev Ready, Edited By, Notes. | | |
| 1.4 | At least one version row has Dev Ready = X. | | |
| 1.5 | All version rows have Date, Edited By, and Notes populated. | | |
| 1.6 | Date format is M/D/YYYY consistently across all rows. | | |
| 1.7 | Version Notes column describes what changed in that version (not a general document description). | | |

---

## Section 2: Module-Level Sections

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 2.1 | A Designer Note section (module-level) is present and contains non-placeholder content. | | |
| 2.2 | A "General Application Features" section is present pointing to the Master Design. | | |
| 2.3 | An Application User Access table is present with at least two capabilities defined. | | |
| 2.4 | Every capability referenced in any per-screen User Access section is listed in the Application User Access table. | | |
| 2.5 | If callouts are referenced anywhere in the document, a module-level Callouts table is present defining all referenced callouts. | | |
| 2.6 | A Sketches section with a Figma URL is present, OR the absence of Figma sketches is explicitly noted. | | |

---

## Section 3: Screen Sections — Structure

Evaluate this section for every screen in the document. If any screen fails an item, mark the item Fail and list the screen name(s) in the Notes column.

| # | Criterion | Pass / Fail / N/A | Notes (screen name if failed) |
| --- | --- | --- | --- |
| 3.1 | Every screen heading (H2) includes a form type abbreviation in parentheses: SLF, ELF, DF, R, or equivalent. | | |
| 3.2 | Every screen section contains a User Access declaration immediately below the H2 heading. | | |
| 3.3 | Every User Access declaration references a named capability (not a generic role like "admin" or "all users"). | | |
| 3.4 | Every screen section contains a Designer Notes subsection. | | |
| 3.5 | Every screen section contains an Actions subsection. | | |
| 3.6 | Every screen that displays a data grid has a Grid Actions subsection. | | |
| 3.7 | Every screen section contains an Elements table. | | |
| 3.8 | The subsections within each screen appear in the correct order: User Access → Designer Notes → Actions → Grid Actions → Elements. | | |

---

## Section 4: Actions

Evaluate this section for every screen's Actions section.

| # | Criterion | Pass / Fail / N/A | Notes (screen name / action if failed) |
| --- | --- | --- | --- |
| 4.1 | Every action has a Format sub-bullet specifying Button, Icon, or Link. | | |
| 4.2 | Every action has an on-select behavior description. | | |
| 4.3 | Every action that is conditionally visible or enabled states the condition using "Only present if…" or "Only enabled if…". | | |
| 4.4 | Every destructive action (Delete, Discard, Overwrite) includes a confirmation dialog with the message text quoted. | | |
| 4.5 | Every DF screen includes the paired action set: Edit (View mode), Save (Edit mode), Cancel (Edit mode), Done (View mode). | | |
| 4.6 | Every action that writes to the database has a Dev Note specifying the write operation (table, fields, values). | | |
| 4.7 | Every action that navigates to another screen names the target screen with its form type abbreviation. | | |
| 4.8 | Validation failure messages are quoted or explicitly referenced ("show message similar to…"). No action states "show an error" without specifying what the error communicates. | | |

---

## Section 5: Elements Tables

Evaluate this section for every screen's Elements table.

| # | Criterion | Pass / Fail / N/A | Notes (screen name / field if failed) |
| --- | --- | --- | --- |
| 5.1 | Elements table uses the standard 6-column format: Element Name, Field Type, Sort, Req, Edit, Notes. | | |
| 5.2 | The Sort column header is struck through (~~Sort~~) on DF screens. | | |
| 5.3 | The Req column header is struck through (~~Req~~) on grid/list screens. | | |
| 5.4 | The legend line "Sort/Req/Edit Values: X = Required, R = Read Only, E = Edit, and C = Conditional…" appears above every Elements table. | | |
| 5.5 | Every row has a Field Type value using the project's type vocabulary (Text-N, Currency, Date, Dropdown, Bit, Integer, etc.). | | |
| 5.6 | Every row has a Req or Edit value specified (not blank). | | |
| 5.7 | Every row's Notes cell contains at minimum one of: a sample value, a format specification, or a selection source. | | |
| 5.8 | Every field marked Edit = C (Conditional) has the condition stated in the Notes cell or in an adjacent Dev Note. | | |
| 5.9 | Every calculated field (Field Type includes CALC or Edit = R with a formula) has the calculation formula or a callout reference in the Notes cell. | | |
| 5.10 | Dev Notes within table cells use the // prefix. | | |

---

## Section 6: Designer Notes

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 6.1 | The module-level Designer Note contains non-placeholder text (not "xxxx", "TBD", or an empty bullet). | | |
| 6.2 | Designer Notes use plain business language. No database table names, column names, or SQL syntax appear in Designer Notes. | | |
| 6.3 | Every screen whose behavior is not self-evident from the screen name has a Designer Note with at least one sentence of business context. | | |
| 6.4 | Conditional business rules in Designer Notes state the condition before the consequence. | | |

---

## Section 7: Dev Notes

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 7.1 | Dev Notes are present for all fields or actions where the implementation is not obvious from the spec. | | |
| 7.2 | Dev Notes do not use vague language ("handle appropriately", "as needed", "standard behavior"). Each Dev Note states a specific value, column, formula, or rule. | | |
| 7.3 | Dev Notes in web application specs use the // prefix consistently. | | |
| 7.4 | Dev Notes in the Actions section appear as a labeled "Dev Note:" bullet within the relevant action or as a standalone section at the bottom of the Actions block. | | |

---

## Section 8: Cross-References and Callouts

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 8.1 | Every cross-reference to another screen names the screen with its form type abbreviation. | | |
| 8.2 | No spec content is duplicated verbatim across two or more screen sections within the same document (content that appears in multiple places is either a callout or a reference). | | |
| 8.3 | Every callout reference uses the phrasing "See [Callout Name] callout" or "See callout #N." | | |
| 8.4 | No module spec repeats content from the Master Design. References to the Master Design use "See Master Design for [topic]." | | |

---

## Section 9: Version Log

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 9.1 | If the opening version table contains more than 8 rows, a Version Log section exists at the end of the document containing the full history, and the opening table contains a pointer row ("See Version Log for previous versions"). | | |
| 9.2 | If the opening version table contains 8 or fewer rows, a Version Log section is either absent or contains only rows not present in the opening table. | | |

---

## Section 10: Formatting and Consistency

| # | Criterion | Pass / Fail / N/A | Notes |
| --- | --- | --- | --- |
| 10.1 | Screen headings consistently use H2. Subsection headings within screens consistently use H3. | | |
| 10.2 | No Mammoth conversion artifacts remain in the document body (no stray warning text, no garbled characters from the conversion header). | | |
| 10.3 | Strikethrough is used for all superseded content; no content appears to have been silently deleted between versions (as indicated by version notes referencing removed features that do not appear struck through). | | |
| 10.4 | Quoted message text uses double quotes consistently. | | |
| 10.5 | The form type abbreviation in every screen heading matches the screen's actual function (DF is used only for single-record detail forms, SLF only for searchable grids, etc.). | | |

---

## Final Gate

| Gate | Condition | Pass / Fail |
| --- | --- | --- |
| Dev Ready | All items in Sections 1–8 marked Pass or N/A. | |
| Approved for Handoff | Dev Ready gate passed AND reviewer has no outstanding questions for the spec author. | |

**Reviewer sign-off:** ___________________________ **Date:** ___________
