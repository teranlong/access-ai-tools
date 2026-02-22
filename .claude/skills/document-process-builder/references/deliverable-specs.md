# Deliverable Specifications

Detailed content requirements for each of the 6 standard deliverables produced by the document-process-builder skill.

In all files: replace `[doc-type]` with the actual document type name (e.g., "Functional Specification", "Statement of Work").

---

## 1. `[doc-type]-template.md`

**Purpose:** A reusable structural scaffold for writing new documents of this type.

**Content:**
- Section headings and sub-headings, in the order they should appear
- One-sentence description of what belongs in each section
- Any required tables, fields, or structural elements within each section (as empty or placeholder tables)
- If multiple materially different formats exist across samples, provide clearly labeled variants (e.g., "Template A - Flow-centric", "Template B - Form-centric")
- For the recommended/current template, indicate which sample projects it is based on

**Constraints:**
- Structure only: headings, ordering, brief descriptions, placeholder tables
- No real customer data from the samples
- High fidelity to observed patterns - do not invent sections not seen in the samples

---

## 2. `[doc-type]-guidelines.md`

**Purpose:** Actionable writing guidelines derived from patterns actually observed in the samples.

**Content sections:**

1. **Document Organization** - rules about file structure, module/section breakdown, document naming
2. **Section-by-Section Guidelines** - for each major section: what to include, what to exclude, format rules
3. **Special Elements** - any recurring structured elements (callouts, dependency tables, state transition diagrams, etc.) and how to use them
4. **Naming Conventions** - any naming patterns observed (field prefixes, form type suffixes, capability naming, etc.)
5. **Writing Style Rules** - language, tense, level of specificity, vagueness avoidance
6. **Common Anti-Patterns** - a table of observed or foreseeable mistakes, why each is a problem, and the better approach

**Format:**
- Use Do/Do not pairs for clarity
- Include concrete examples drawn from the samples (anonymized)
- Each guideline should be specific enough that a writer could apply it without asking for clarification

---

## 3. `[doc-type]-scoring-rubric.md`

**Purpose:** A scoring rubric (1-5 per criterion) for evaluating quality before the document is handed off.

**Content:**

- A scoring summary table listing all criteria, whether each is Required or Informational, and blank score/notes columns
- For each criterion:
  - Name and description grounded in how the sample docs are written
  - Score descriptions for 1, 3, and 5 (low, mid, high)
  - Anchor examples: reference a specific sample and what score it would receive
- An aggregate scoring interpretation table (e.g., 4.5-5.0 = Excellent, etc.)
- A note that any Required criterion below 3 means the document is not ready for handoff

**Required criteria (adapt names and descriptions to the doc type):**
- Structure and format adherence
- Core content completeness (the "field table equivalent" for this doc type)
- Behavioral/action completeness
- Clarity and precision
- Access or permission specification (if applicable)
- Business rule or rationale documentation
- Testability or verifiability of requirements
- Version history quality (mark as Informational)

Omit criteria that are not applicable to the document type. Add criteria specific to the type if warranted.

---

## 4. `acceptance-criteria-template.md`

**Purpose:** A pass/fail checklist a reviewer applies before marking a document complete/approved.

**Content:**

- How to use the template (one-paragraph intro)
- **Required Criteria** section: all criteria that must pass before handoff
  - Each criterion has: an ID (AC-01, AC-02...), a name, a description, and a checklist of pass conditions (all must be true)
  - Phrase each pass condition as an observable, binary check (yes/no, present/absent)
- **Conditional Criteria** section: criteria that apply only when certain features are present
  - Clearly state what condition triggers the criterion
- **Given/When/Then scenarios** for the most critical criteria
  - Write 3-5 of the most important criteria as testable scenarios in GWT format

**Constraint:** Every criterion in the Required section must be independently passable. Do not combine two checks into one criterion.

---

## 5. `insights-on-current-process.md`

**Purpose:** Capture important observations about how documents are currently produced, inferred from the samples.

**Content:**
- Each insight is a numbered section with a title, observation, and implication
- Cover: format evolution across samples, implicit conventions vs. explicit standards, process signals embedded in the documents (version history patterns, handoff signals, review evidence), inconsistencies across samples, anything that reveals friction or risk in the current process

**Format:**
- 6-12 insights typical; do not pad
- Each section: 2-4 sentences observation + 1-sentence implication
- Label inferences clearly: "This implies..." or "The documents suggest..."

**Constraint:** Only include insights that seem genuinely useful for shaping future process or tooling. Do not include generic observations that apply to any document type.

---

## 6. `future-thoughts-and-recommendations.md`

**Purpose:** Specific, actionable improvement recommendations based on observed gaps.

**Content:**
- Each recommendation is a numbered section (Rec-01, Rec-02...) with:
  - **Observation**: the specific gap, inconsistency, or opportunity seen in the samples
  - **Recommendation**: a concrete, actionable change to process, template, or tooling
  - **Impact**: effort level (Low/Medium/High) and expected value (Low/Medium/High)

**Constraints:**
- Only include recommendations strongly supported by what was observed - do not force insights
- Keep each recommendation specific: "Adopt format X for Y" not "Improve consistency"
- 5-10 recommendations is typical; quality over quantity
- Do not repeat the same insight from `insights-on-current-process.md` - this file is about what to do about it
