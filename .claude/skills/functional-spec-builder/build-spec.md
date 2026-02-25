# Build Functional Spec — Step-by-Step Instructions

Follow these steps in order. Do not skip steps. Do not combine steps.

---

## Step 0: Resolve Inputs

Identify from the user's message or ask for:

- `template_folder` — path to the template resource folder
- `project_folder` — path to the AI-compatible project data folder
- `output_folder` — root directory for output files

Then derive:

- `template_name` — the second-to-last path segment of `template_folder`
  - Example: `.teran/functional-spec-builder/v0` → `functional-spec-builder`
- `version` — the last path segment of `template_folder`
  - Example: `.teran/functional-spec-builder/v0` → `v0`
- `output_path` — `{output_folder}/{template_name}/{version}/`

Confirm these values before proceeding. If any parameter is missing, ask before continuing.

---

## Step 1: Load Template Resources

List all files in `template_folder`. Read every file. As you read each one, classify it by role:

| Role | Typical indicators | How you'll use it |
|------|--------------------|-------------------|
| **Information taxonomy** | Numbered categories; lists questions and sub-questions; maps info to spec sections | Use as a checklist: assess whether the project data covers each category |
| **Document scaffold** | Section headings, placeholder tables, form type abbreviations (SLF/DF/ELF/R) | Follow this structure exactly when drafting the spec |
| **Writing guidelines** | Rules for language, format, naming conventions, date format, column headers, action structure | Apply throughout drafting; do not deviate without noting it |
| **Scoring rubric** | Numbered criteria with 1–5 descriptors and a total score threshold | Use in Step 6 self-review |
| **Acceptance checklist** | Pass/Fail/N/A items organized by spec section | Use in Step 6 self-review |
| **Interview guide** | Questions organized by audience (business user, technical expert) | Use to identify what information was never captured in the project data |
| **Supplementary** | Insights, recommendations, future thoughts | Inform your drafting approach; do not cite these in the spec output |

After reading all template files, summarize for yourself:

1. What sections the output spec must contain (from the scaffold)
2. What writing rules are non-negotiable (from the guidelines)
3. What information categories are required (from the taxonomy)
4. What the quality threshold is (from the rubric)

If any files in the template folder do not fit a known role, treat them as supplementary guidance.

---

## Step 2: Survey the Project Folder

**Do not read every file.** Build a reading plan.

**First, list all files** in `project_folder`. Note file names, types, and sizes.

**Then read these high-priority discovery files immediately (if present):**

1. `CLAUDE.md` — project-specific guidance and constraints; treat as authoritative for this project
2. `ai-compatible-summary.md` — inventory of all project files, their conversion status, and a domain overview
3. Any file whose name includes: `SOW`, `requirements`, `design-brief`, `design-requirements`, `scope`
4. Any file whose name includes: `summary`, `overview`, `notes-summary`, or `meeting-summary`

**After reading discovery files, build a targeted reading plan** based on the information taxonomy from Step 1. Map each taxonomy category to the file(s) most likely to answer it:

| Taxonomy category | Likely source files |
|-------------------|---------------------|
| Project identity & document control | SOW, design brief, CLAUDE.md |
| High-level purpose and scope | SOW, design brief, meeting summaries |
| Users and access control | Design brief, requirements, meeting notes |
| Module and navigation structure | Wireframes, SOW, screen flow documents |
| Database and data model | Schema CSVs, ERD markdown, SQL files |
| Screen details (SLF/DF/ELF/R) | Wireframes (Excalidraw or PNG), screen samples, meeting notes |
| Business rules and calculations | SQL queries, meeting notes, client example documents |
| Workflow and status transitions | Meeting notes, load manager plans, design requirements |
| Configuration and admin values | Design brief, meeting notes, SQL config tables |
| Notifications and integrations | SOW, meeting notes, requirements |

Read files in the priority order your plan produces. Stop reading a file when you have what you need from it; move on.

**Skip without reading:**
- Binary-only stubs (`.xcf`, `.pbix`, `.mp4`, `.zip`, `.bacpac`)
- Image files (`.png`, `.jpg`) unless they are the only source for a wireframe
- Files named `PW.txt`, `database_creds.txt`, or anything that appears to contain credentials or passwords
- Budget and financial estimate spreadsheets (unless the spec requires financial calculation rules)

---

## Step 3: Information Coverage Assessment

Using the information taxonomy from Step 1, assess the project data you have read:

For each category in the taxonomy:
- **✅ Covered** — the project data provides clear, specific answers
- **⚠️ Partial** — some information exists but gaps remain; you can draft with assumptions
- **❌ Missing** — no project data addresses this category at all

Build a coverage table. Be specific about what is covered and what is not.

This table becomes the core of `gap-report.md`.

---

## Step 4: Determine Scope

From the project data, identify:

1. **Module list** — What are the major functional modules? (source: SOW, design brief, navigation wireframes)
2. **Screen inventory** — For each module, what screens exist? (source: wireframes, meeting notes, screen flow documents)
3. **Screen type per screen** — Classify each screen:
   - **SLF** — Searchable list form (grid of records with search/filter; no inline editing)
   - **DF** — Detail form (single record; create, view, edit)
   - **ELF** — Editable list form (inline-editable grid of records; typically for lookup/config tables)
   - **R** — Report (read-only output; printed or exported)

If the project has 5 or more modules, or more than 15 screens total, **scope the draft to the most critical or best-documented module first**. Use the SOW priority order or the module with the most wireframe coverage. Note deferred modules in the gap report.

State the scope explicitly before starting Step 5: "I will draft the spec for [Module Name], which contains [N] screens: [screen list with types]."

---

## Step 5: Draft the Functional Spec

Follow the **document scaffold** from the template exactly. Apply all **writing guidelines** as you write.

**Core writing rules** (supplement with whatever the template's guidelines specify):
- Write in present tense, active voice
- Use plain business language in Designer Notes — no technical terms, no database field names, no code references
- Prefix Dev Notes with `//` — place them in the Notes cell of Elements tables or inline in Actions where the guideline permits
- Use the correct form type abbreviations (SLF, DF, ELF, R) — not custom labels
- Keep Elements tables to the standard column structure defined in the template
- Never leave a section structurally empty — if you lack information, insert a placeholder

**Placeholder conventions:**
- `[QUESTION: …]` — information the client or PM must provide; describe exactly what is needed
- `[ASSUMED: …]` — a reasonable inference you made; state the assumption explicitly

These placeholders are acceptable within the spec draft. Do not leave entire sections blank.

**Draft structure** (adapt to the scaffold; this is the expected order for functional-spec-builder):

```
# [Module Name] — [Form Type Abbreviation]

[Cross-reference to Master Design document]

| Version | Date | Author | Notes |
|---------|------|--------|-------|
| 0.1     | [date] | [AI draft] | Initial draft |

## Designer Notes

[Module-level business context: what this module is for, who uses it, key workflows]

## General Application Features

[Shared behaviors that apply across all screens in this module]

## Application User Access

| Capability | [Role 1] | [Role 2] | … |
|------------|----------|----------|---|
| …          | …        | …        | … |

## Callouts

[Reusable logic referenced from 2+ screens — define here, reference by name elsewhere]
[Omit this section if no reusable logic is identified]

## Sketches

[Link to wireframes or Figma file]
[QUESTION: Provide Figma or Excalidraw link for this module]

---

## [SLF/DF/ELF/R] — [Screen Name]

**User Access:** [Named capability from the Application User Access table]

### Designer Notes

[Screen-level business context]

### Actions

- **[Action Name]**
  - Format: [Button / Link / Icon / etc.]
  - [Behavior description]
  - [Access guards if applicable]
  - [Confirmation dialog if applicable]

### Grid Actions
[If the screen has a grid with row-level actions — otherwise omit this section]

### Search Criteria
[SLF only — list each searchable field and its behavior]

### Elements

| Field | Field Type | Req | Edit | Notes |
|-------|------------|-----|------|-------|
| …     | …          | …   | …    | …     |

---
[Repeat per screen]

---

## Version Log

| Version | Date | Description |
|---------|------|-------------|
| 0.1     | [date] | Initial AI draft |
```

Write the spec at whatever length the information supports. Do not pad. Do not omit required sections.

---

## Step 6: Self-Review

After completing the draft, apply the template's **acceptance checklist**:

- Go through every pass/fail item
- Mark each: **Pass**, **Fail**, or **N/A**
- For each Fail, note what would fix it

Then apply the **scoring rubric**:

- Score each criterion 1–5 based on the rubric's descriptors
- Sum the scores
- Note what the total means in terms of spec readiness

Record all results — they become `review-score.md`.

---

## Step 7: Write Output Files

Create the output directory `{output_path}` if it does not exist.

Write exactly three files:

---

### File 1: `functional-spec-{module-slug}.md`

The draft spec from Step 5 — clean and complete as a spec document.

- The filename slug is the module name in lowercase kebab-case
  - Example: "Load Validation" → `functional-spec-load-validation.md`
- Do not add any process commentary inside this file
- `[QUESTION: …]` and `[ASSUMED: …]` placeholders are acceptable
- Do not include your self-review notes, coverage assessment, or gap analysis inside this file

If you drafted multiple modules, write one file per module.

---

### File 2: `gap-report.md`

```markdown
# Gap Report: {Project Name}

## Coverage Assessment

| Information Category | Status | Notes |
|---------------------|--------|-------|
| [Category from taxonomy] | ✅ / ⚠️ / ❌ | [What was found / what is missing] |
…

## Assumptions Made

- **[Section of spec]:** [ASSUMED: …] — rationale for the assumption
…

## Open Questions

### [Section Name]
- [QUESTION: …] — where this appears in the draft
…

## Deferred Modules

[If applicable — list modules not covered in this draft and why]

## Recommended Next Steps

1. [Highest-priority gap to close — who to ask, what to ask]
2. …
```

---

### File 3: `review-score.md`

```markdown
# Spec Review: {Module Name}

## Acceptance Checklist

| Item | Result | Notes |
|------|--------|-------|
| [Checklist item from template] | Pass / Fail / N/A | [What is missing or wrong] |
…

## Rubric Score

| Criterion | Score (1–5) | Notes |
|-----------|-------------|-------|
| [Criterion from rubric] | [1–5] | [Why this score] |
| **Total** | **{score}/50** | |

## Assessment

[Score interpretation per the rubric's thresholds]
[What is needed to reach Dev Ready status]
```

---

## Notes and Edge Cases

- If the template folder is missing expected files (e.g., no rubric), skip that step gracefully and note the omission in `review-score.md`.
- If a `CLAUDE.md` exists in the project folder, its project-specific instructions supplement — but do not override — the template resource guidelines.
- If the project folder contains an `ai-compatible-summary.md`, read it first; it is the fastest way to understand what data is available.
- Do not include credential files, passwords, or customer PII in any output file.
- If no module scope can be determined from the project data, stop and ask the user before drafting.
- If the project folder uses a different naming convention than expected, use the discovery files to orient yourself before reading deeper.
