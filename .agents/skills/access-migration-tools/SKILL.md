---
name: access-migration-tools
version: 2.0.0
description: Catalog and convert files for Microsoft Access DB migration projects. Use when asked to evaluate, catalog, or triage an Access migration project folder, OR when asked to convert project documents to AI-readable Markdown formats.
---

# access-migration-tools

You are acting as a senior engineer, project manager, and Microsoft Access DB migration expert.

This skill has two abilities. Identify which one the user needs, then read the corresponding instruction file.

---

## Choose an Ability

| Ability | Use when the user asks to… |
|---------|---------------------------|
| **catalog-documents** | Evaluate, triage, or inventory a project folder; produce a migration readiness report; understand what files exist and their AI compatibility |
| **convert-documents** | Convert project files to Markdown or AI-readable formats; prepare documents for AI analysis; run the file conversion pipeline |

**Not sure?** Catalog first — it produces the `files.json` that the converter uses for richer metadata.

---

## catalog-documents

→ Read **[catalog-documents.md](catalog-documents.md)** for full step-by-step instructions.

Runs `catalog.py` against a project folder, classifies every file by AI capability and migration phase, generates PNG charts, and writes a structured catalog report (`catalog-report.md`) covering file inventory, files requiring attention, and a phase readiness assessment.

---

## convert-documents

→ Read **[convert-documents.md](convert-documents.md)** for full step-by-step instructions.

Runs `convert_to_ai_compatible.py` against a project folder, converting Word docs, Excel sheets, PDFs, Visio diagrams, and more into Markdown. Mirrors the original directory structure under `agent-data/ai-compatible/`. Produces an `ai-compatible-summary.md` report.

---

## Environment Setup

Both abilities share a Python virtual environment. If dependencies are not installed, run once from the repo root:

```bash
cd .agents/skills/access-migration-tools && setup_venv.bat
```

Then activate before running any scripts:

```bash
.agents/skills/access-migration-tools/.venv/Scripts/activate
```
