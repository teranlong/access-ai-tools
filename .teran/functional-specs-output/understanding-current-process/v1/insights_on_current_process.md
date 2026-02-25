# Insights on the Current Functional Spec Process

**Purpose:** Capture important observations about how functional specs are currently produced, based on patterns inferred from the 4 sample projects.

**Source:** Derived from analysis of Heartland Bank, KnightG, Statewide, and Youngdahl functional specification documents.

**Note:** These insights are inferences from the documents themselves. They reflect what the specs imply about the writing process, not direct observations of it.

---

## 1. The Spec Format Has Evolved Over Time

The 4 sample projects show a clear evolution in spec format:

- **Heartland Bank** (oldest visible style): Uses ICF/DF form naming. Field definitions are in prose or simple lists without a formal table structure. Callouts exist but are prose-based. The style is compact and readable but relies on reader interpretation for many details.

- **KnightG**: Introduces SLF/DF naming and some tabular field definitions, but field tables are not yet fully structured (Sort/Req/Edit columns are inconsistently applied).

- **Statewide** and **Youngdahl** (most mature): Use full formal field definition tables with Sort/Req/Edit columns. Both introduce a Master Design companion document. Youngdahl adds further maturity with numbered Callouts, Dependency Tables, and state transition documentation.

**Implication:** The process has been improving organically over time. There is no single documented standard — the standard has been absorbed through project experience.

---

## 2. The Master Design Is a De Facto Convention, Not a Formal Requirement

Three of the four projects have a Master Design document. Heartland Bank does not. In all three projects that have one, it plays the same role: a single place for global UI rules that all module specs reference.

The existence of the Master Design appears to be a decision made at the start of a project, not a mandated step. The lack of a Master Design in Heartland Bank means some global rules are repeated inline within module specs, while others are simply assumed.

**Implication:** The Master Design pattern is clearly valuable and is used in most projects, but it is not consistently enforced as a starting point for every engagement.

---

## 3. The "Dev Ready" Flag Represents the BA-to-Developer Handoff

The Dev Ready column in the version history table is the primary signal that a spec is ready for a developer to act on. This column is:

- Left blank during active drafting.
- Marked with `X` when the author (business analyst) considers the spec complete.

There is no formal review gate beyond this flag — no evidence of a formal sign-off by the customer, a second reviewer, or a QA review of the spec itself before it is marked Dev Ready.

**Implication:** The Dev Ready flag carries significant weight in the process but depends entirely on the author's judgment. There is no documented acceptance gate that a spec must pass before it can be marked Dev Ready.

---

## 4. Designer Notes Carry Informal Business Rules

Designer Notes sections consistently contain business rules that are:

- Not restated in the field definition tables.
- Not captured as formal requirements.
- Often written as narrative explanation rather than testable statements.

Examples observed:
- Youngdahl: The explanation of why Standards use a text "Year" field instead of a date (to allow flexibility beyond calendar years) is only in a Designer Note.
- Statewide: The explanation of how inventory calculations change when multiple locations are introduced is embedded in a Designer Note.
- Heartland: The explanation of why dividends are paid on granted shares (not vested shares) is in a Designer Note.

These are genuine business rules. If the Designer Note were removed, the field table alone would not communicate these rules to a developer or tester.

**Implication:** Business rules are currently split between Designer Notes (informal, contextual) and field/action definitions (formal, structured). This split means important rules can be missed during review or when generating test cases, because they do not appear in the structured sections of the spec.

---

## 5. Callout Format Is Inconsistent Across Projects

Callouts are used to document calculations and formulas, but the format varies:

- **Heartland**: Callouts are inline prose blocks, typically labeled by context (e.g., "Calculate Shareholder Dividend Amount"). Formulas are stated in a single sentence.
- **Youngdahl**: Callouts are numbered (e.g., "Callout #13 – Determine Revision") and referenced by number from within form sections. This creates a cross-reference system within the document.
- **Statewide**: Callouts appear as table sections (e.g., the Inventory Patterns table listing 13 transaction patterns with their effects). The format is highly structured and testable.

There is no shared convention for: how to name a Callout, whether to number them, or how to reference them from within a form section.

**Implication:** A developer reading a Heartland spec and a Youngdahl spec for the same company would need to adapt to two different ways of interpreting formulas. There is room to standardize.

---

## 6. Youngdahl Is the Most Mature Spec in the Sample Set

Youngdahl's specs are the most detailed and structurally complete:

- Numbered Callouts referenced from form sections.
- Dependency Tables documenting cascading field effects.
- State transition diagrams for DFR status workflows.
- Modal Popups treated as first-class form entities with full field tables.
- Data Migration spec as a separate document.

The maturity likely reflects both the complexity of the Youngdahl system (field inspection with multi-step DFR workflow, lab testing, compaction calculations) and accumulated project experience.

**Implication:** Youngdahl provides the best example of a complete, developer-ready spec. Its conventions (Dependency Tables, numbered Callouts, modal popup specs) are worth standardizing for use across all projects.

---

## 7. Some Projects Mix Legacy Access App Forms with New Web Forms

Youngdahl Module 1 contains sections prefixed with `[Access]` that describe forms in the existing Microsoft Access desktop application alongside sections for the new web application being built.

These sections use a different naming convention (FU01, FE11, FA10, FP10, FP30) and appear to serve as reference documentation for the existing system — not specifications for the new one.

**Implication:** There is no clear visual distinction between "this is the spec for what we are building" and "this is documentation of the existing system." A developer scanning the document could confuse existing-system documentation with new-system requirements.

---

## 8. "SELF" Is an Undocumented Form Type Variant

Youngdahl introduces a form type called SELF (Search/Entry/List Form) that does not appear in the other three projects. It combines search, inline data entry, and list display in a single form. No definition or explanation of SELF appears in any Master Design or guidelines document — it is used without being defined.

**Implication:** Form type conventions are being extended on a per-project basis without a central register. A new team member or a future project team would not know what SELF means without being told.

---

## 9. Version Notes Vary Widely in Specificity

In the sample specs, version note quality ranges from highly specific ("Added Forced Vesting field to Module 2; updated ShareCount calculation in Dividend Event") to vague ("Updated module"). The more mature projects tend toward more specific notes, but even Youngdahl has some vague entries across its 7+ version increments.

**Implication:** Version notes are not held to a standard. Their quality depends on the author's habits at the time of writing.

---

## 10. No Evidence of a Formal Spec Review Step

The version histories show iterative drafting (often 5–10+ versions before Dev Ready), but there is no evidence of a formal review by anyone other than the author. No version notes reference "reviewed by [stakeholder]" or "approved by [customer]".

**Implication:** Spec quality gates appear to be self-assessed. The Dev Ready column reflects author confidence, not a validated review. There may be informal review steps that are simply not captured in the document — but if so, they leave no trace.
