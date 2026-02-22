---
name: document-process-builder
description: >
  Analyze a corpus of sample documents and produce a standardized, reusable set of process
  artifacts for reproducing documents of that type. Use when a user provides sample documents
  (functional specs, SOWs, user stories, test plans, etc.) and wants to understand the current
  process for writing them, create a reusable template and guidelines, define quality criteria,
  or build a repeatable system for producing similar documents in the future. Trigger phrases
  include "build a process from these samples", "templatize this document type", "create a
  template from examples", "create guidelines based on these docs", or "I want to understand
  the pattern in these documents".
---

# Document Process Builder

Analyze sample documents and produce a standardized set of process artifacts that can be used to reproduce documents of that type reliably in the future.

## Process Overview

1. Identify and read all sample documents
2. Clarify output location and document type name (if not provided)
3. Analyze the samples for structure, style, and patterns
4. Share a brief analysis summary with the user before writing
5. Produce the 6 standard deliverables
6. Report what was created and where

Follow these steps in order. Do not skip the analysis summary step.

## Accepting Input

The user may specify sample documents in various ways:

- **Folder path**: Read all readable files in the folder (markdown, .md, .txt, .docx converted to markdown)
- **File list**: Read each file explicitly
- **Document type in folder**: e.g., "all functional specs in SampleProjects/" — glob for matching filenames
- **Mixed**: combine folder and file references

If the input is ambiguous or the paths cannot be confirmed, ask before reading.

If the user provides pre-converted markdown files (e.g., from mammoth or pandoc), read those. If only .docx files are available, use available conversion tools.

## Clarifying Questions

Ask if not provided:

- **Output location**: Where should the deliverables be written? (Default: `[nearest project root]/[doc-type-slug]-analysis/v1/`)
- **Document type name**: What should the document type be called? Used to name output files (e.g., "functional spec" -> `functional-spec-template.md`)
- **Any specific focus areas**: Are there aspects of the documents the user wants to prioritize?

Do not ask more than 2-3 questions at once. Ask the most important ones first.

## Analysis Summary

Before writing any deliverables, share a brief summary (not a full report) covering:
- Number of samples reviewed
- High-level structural patterns observed (sections, naming, format style)
- Any notable variation across samples (e.g., evolved format, multiple styles)
- Any access or readability issues encountered

Ask the user to confirm before proceeding, or invite corrections.

## Deliverables

Write all 6 files to the output location. Use the document type name as a prefix for the first 3 files.

| File | Purpose |
|---|---|
| `[doc-type]-template.md` | Section structure and scaffold for new documents |
| `[doc-type]-guidelines.md` | Best practices and writing rules derived from the samples |
| `[doc-type]-scoring-rubric.md` | Scoring rubric (1-5 per criterion) for evaluating document quality |
| `acceptance-criteria-template.md` | Checklist of pass/fail criteria for document completeness |
| `insights-on-current-process.md` | Observations about the current process inferred from the samples |
| `future-thoughts-and-recommendations.md` | Specific, actionable improvement recommendations |

See `references/deliverable-specs.md` for the detailed specification of each deliverable.

## Writing Style Rules

Apply to all output files:

- **Atomic**: One behavior or rule per bullet or table row.
- **Measurable**: Phrase behaviors so a reviewer can say pass or fail based on observable outcomes.
- **No vague language**: Do not use "etc.", "as appropriate", "handle all edge cases", or "similar to above." State specifics.
- **Conditional requirements explicit**: If a rule applies only under conditions, state the condition first.
- **Present tense**: Describe what the system/document does, not what it should do.
- **Mark nice-to-haves**: Label lower-priority or future items explicitly so they are not mistaken for requirements.
- **Anchor in samples**: Do not invent patterns not supported by what you actually observed. If a pattern is inferred, say so.

## Constraints

- Do not include real customer names, proprietary data, or confidential values from the samples in any output file.
- Use placeholder values in examples (e.g., "[CustomerName]", "Example Inc.").
- If sample access is blocked or files cannot be read, report this clearly before proceeding.
- Do not create deliverable #7 (process instructions) unless explicitly requested. That is a separate future phase.
