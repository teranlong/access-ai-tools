---
name: functional-spec-builder
version: 1.0.0
description: >
  Reads a template resource folder (guidelines, scaffold, rubric, information
  taxonomy) alongside an AI-compatible project data folder (schema, SOW,
  wireframes, meeting notes) and produces a draft functional specification plus
  a gap report and self-review score. Output is placed in
  {output_folder}/{template_name}/{version}/.
---

# Functional Spec Builder

Given a **template resource folder** and a **project data folder**, this skill produces a draft functional specification by:

1. Loading all template resources and understanding their roles
2. Strategically reading project data to extract requirements
3. Assessing information coverage against the template's taxonomy
4. Drafting the spec following the template structure and writing guidelines
5. Self-reviewing against the acceptance checklist and scoring rubric
6. Writing a gap report for missing information and assumptions made

→ Read **[build-spec.md](build-spec.md)** for full step-by-step instructions.

---

## Inputs

| Parameter | Description | Example |
|-----------|-------------|---------|
| `template_folder` | Path to template resource folder | `.teran/functional-spec-builder/v0` |
| `project_folder` | Path to AI-compatible project data | `agent-data/ai-compatible/v1.3.1/Sample3-Coleville` |
| `output_folder` | Root folder for output | `agent-data/specs` |

The `template_name` and `version` are derived from the last two path segments of `template_folder`.

## Outputs

Files written to `{output_folder}/{template_name}/{version}/`:

| File | Description |
|------|-------------|
| `functional-spec-{module-slug}.md` | Draft functional spec (one per module, or combined if small) |
| `gap-report.md` | Coverage assessment, assumptions, open questions, next steps |
| `review-score.md` | Acceptance checklist results and rubric score |

---

## Invoking This Skill

Provide the three parameters in any natural-language form. Examples:

> "Build a functional spec using `.teran/functional-spec-builder/v0` as the template and `agent-data/ai-compatible/v1.3.1/Sample3-Coleville` as the project. Write output to `agent-data/specs`."

> "Run functional-spec-builder on Sample3-Coleville using the v0 template. Output to agent-data/specs."
