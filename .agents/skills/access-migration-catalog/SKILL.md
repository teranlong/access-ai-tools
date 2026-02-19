---
name: access-migration-catalog
version: 1.1.0
description: Catalog all files in an Access DB migration project folder and produce a structured Markdown report covering file types, AI readability, proposed conversion formats, and project phase relevance. Use when asked to evaluate, catalog, or triage an Access DB migration project.
---

# access-migration-catalog

You are acting as a senior engineer, project manager, and Microsoft Access DB migration expert. Your task is to catalog every file in a given project folder and produce a structured report that can be used to evaluate the project's current state and plan migration work.

---

## Step 1: Get the Project Directory

If the user has not provided a project folder path, ask for it before proceeding. The **project name** is the last segment of the folder path (e.g., `Youngdahl` from `.../SampleProjects/Youngdahl`).

---

## Step 2: Run the Python File Scanner

**First, resolve the catalog VERSION** (so all path references below are accurate):

```bash
python -c "import sys; sys.path.insert(0,'.agents/skills/access-migration-catalog'); from catalog import VERSION; print(VERSION)"
```

Use the printed value wherever `{VERSION}` appears in this document.

Run the catalog script to produce the raw file inventory and PNG charts:

```bash
python .agents/skills/access-migration-catalog/catalog.py "<project_directory_path>" --charts
```

This writes to:
```
agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/files.json
agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/chart-phase-count.png
agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/chart-capability-pie.png
agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/chart-extension-bar.png
agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/chart-size-map.png
```

Confirm the files were written successfully, then read `files.json` into context before proceeding.

---

## Step 3: Review the File Inventory

Read `files.json`. You now have a complete list of every file with:
- `file_name`, `extension`, `relative_path`, `parent_folder`
- `size_bytes`, `last_modified`
- `agent_capability`, `proposed_conversion` (pre-classified by the script — do not recalculate)

> **Note:** `parent_folder` is `"."` for files sitting at the project root. For these files, classification must rely entirely on `extension` and `file_name`.

---

## Step 4: Classify Project Phases

For **each file**, reason about:
- **Source Phase** — Which phase of the migration project did this file originate from?
- **Relevant Phases** — Which other migration phases will directly use or reference this file?

### Project Phases

| Phase | Description |
|-------|-------------|
| **Project-Origin** | Files from the existing Access DB implementation, usually provided directly by the client. Includes `.accdb` databases, legacy exports, VBA source files (`.bas`, `.cls`), zip archives of the Access application. |
| **Planning** | Business-focused phase: project plan, SOW, budget, estimates, timelines, resource allocation, risk management. |
| **Design-Requirements** | Functional and nonfunctional specifications, requirements gathering, analysis, and documentation. |
| **Design-Visual** | Creating visual and interactive elements: wireframes, screen flows, Figma files, Excalidraw diagrams, sketches, Visio UI diagrams, PNG mockups. |
| **Engineering-Frontend** | All files related to building the replacement web or desktop frontend application. |
| **Engineering-Backend** | All files related to migrating the legacy Access DB to SQL Server. Includes `.bacpac` files, SQL scripts, schema definitions, data models, ERDs. |
| **Q/A** | Test plans, test data sets, QA artifacts, test tracking spreadsheets. |

### Folder-to-Phase Heuristics

Apply these rules **first**. Folder context takes precedence over guessing from file names alone.

| Folder Name Pattern | Primary Source Phase | Also Relevant To |
|---------------------|---------------------|-----------------|
| `Functional Specifications/` | Design-Requirements | Planning, Engineering-Frontend, Engineering-Backend |
| `Sketches/` | Design-Visual | Engineering-Frontend |
| `Testing/` | Q/A | Engineering-Frontend, Engineering-Backend |
| `Architectural Framework/` | Planning | Design-Requirements, Engineering-Backend |
| `Access Development/` | Project-Origin | Engineering-Backend |
| `Design Meeting Transcripts/` | Design-Requirements | Planning |
| `Build resources/` | Engineering-Backend | Planning |
| `Client Resources/` | Project-Origin | Design-Requirements |
| Root-level `.accdb` or `.mdb` files (`parent_folder: "."`) | Project-Origin | Engineering-Backend |
| Root-level `.sql` files (`parent_folder: "."`) | Engineering-Backend | Q/A |

**Edge cases:**
- If `parent_folder` does not match any known folder name, walk up the full `relative_path` to find a known ancestor folder that does (e.g., `parent_folder: "Figma Backups"` → ancestor is `Sketches/` → Design-Visual).
- Files inside `Architectural Framework/` must be classified **individually by file name**, not uniformly — this folder contains mixed phases (SOW docs → Planning, requirements → Design-Requirements, ERD PNGs → Design-Visual, `.bacpac` → Engineering-Backend).

### When to Load File Contents

Load a file's content **only** when its purpose is genuinely ambiguous from name and folder path alone. This preserves your context window.

**Load when:**
- File name gives no clear category hint (e.g., `feedback.txt` at the project root)
- A root-level file's name is a company name or generic title with no phase signal

**Do NOT load:**
- Binary files (`.accdb`, `.fig`, `.vsdx`, `.xcf`, `.bacpac`, `.zip`) — cannot be read directly
- Image files (`.png`, `.jpg`) — phase is clear from folder context
- Files whose names include keywords like: `FS`, `Module`, `Test Plan`, `SOW`, `Budget`, `Sketch`, `Design`, `Requirements`, `Schema`

---

## Step 5: Write the Catalog Report

Write the report to:
```
agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/catalog-report.md
```

The report must contain the following four sections in order.

---

### Section 1: Project Summary

```markdown
# Access Migration Catalog: {Project Name}

**Scanned:** {date}
**Total Files:** {count}
**Project Path:** {path}

## Summary by Phase

| Phase | File Count |
|-------|------------|
| Project-Origin | N |
| Planning | N |
| Design-Requirements | N |
| Design-Visual | N |
| Engineering-Frontend | N |
| Engineering-Backend | N |
| Q/A | N |

## Summary by Agent Capability

| Agent Capability | File Count |
|-----------------|------------|
| native | N |
| vision | N |
| structured | N |
| binary | N |
| unsupported | N |

## Visual Summary

| | |
|---|---|
| ![Files by Phase](chart-phase-count.png) | ![Files by Agent Capability](chart-capability-pie.png) |
| ![Files by Extension](chart-extension-bar.png) | ![File Size Map](chart-size-map.png) |
```

---

### Section 2: File Catalog Table

One row per file, sorted by `relative_path`. Use the pre-classified `agent_capability` and `proposed_conversion` from `files.json` — do not override these.

```markdown
## File Catalog

| File Name | File Type | Agent Capability | Proposed Conversion Format | Source Phase | Relevant Phases |
|-----------|-----------|-----------------|---------------------------|--------------|-----------------|
| GEMS Interface 5.0.00 DEV.accdb | .accdb | binary | schema-export | Project-Origin | Engineering-Backend |
| Youngdahl FS Module 1.docx | .docx | native | markdown | Design-Requirements | Planning, Engineering-Frontend, Engineering-Backend |
```

---

### Section 3: Files Requiring Attention

List files that are binary or unsupported (cannot be read by the AI without pre-processing), unusually large (> 5 MB), or have no extension / unrecognized type.

```markdown
## Files Requiring Attention

### Binary Files (Require Pre-Processing)
These files cannot be read directly and need conversion or extraction before use in this project.

| File | Type | Recommended Action |
|------|------|--------------------|
| GEMS Interface 5.0.00 DEV.accdb | .accdb | Run MSACCESS-VCS export or use pyodbc to extract schema as SQL |
| DB Schema.bacpac | .bacpac | Restore to SQL Server, then export schema as .sql |

### Large Files (> 5 MB)
| File | Size | Note |
|------|------|------|

### Unknown / No Extension
| File | Path | Note |
|------|------|------|
```

Omit any subsection that is empty.

---

### Section 4: Phase Readiness Assessment

Write a **3–6 sentence prose paragraph per phase** describing: which files are present, what appears to be missing or incomplete, and an overall readiness signal for that phase. This is the high-value analysis section — go beyond what the table alone conveys.

```markdown
## Phase Readiness Assessment

### Project-Origin
[Paragraph]

### Planning
[Paragraph]

### Design-Requirements
[Paragraph]

### Design-Visual
[Paragraph]

### Engineering-Frontend
[Paragraph]

### Engineering-Backend
[Paragraph]

### Q/A
[Paragraph]
```

---

## File Compatibility Reference

The Python script pre-classifies these. Included here for your phase-reasoning reference only.

| Extension | Agent Capability | Proposed Conversion | Notes |
|-----------|-----------------|---------------------|-------|
| .accdb / .mdb | binary | schema-export | Access DB — cannot read directly |
| .docx / .doc | native | markdown | Word document |
| .xlsx / .xls | structured | csv-or-markdown-table | Excel spreadsheet |
| .pdf | vision | markdown | PDF via vision or text extraction |
| .png / .jpg / .jpeg / .bmp | vision | keep-as-reference | Raster images |
| .svg | native | keep-as-is | Vector — readable as XML |
| .vsdx / .vsd | binary | png-export | Visio diagram — export to PNG for AI |
| .excalidraw | native | keep-as-is | JSON-based wireframe format |
| .fig | binary | figma-api-or-export | Figma binary backup |
| .bacpac | binary | sql-server-restore | SQL Server backup archive |
| .bas / .cls | native | vba-to-csharp | VBA module/class source (MSACCESS-VCS export) |
| .sql | native | keep-as-is | SQL script — may need dialect conversion |
| .xml / .json / .md / .txt | native | keep-as-is | Fully readable structured/plain text |
| .csv | structured | keep-as-is | Tabular plain text |
| .rtf | native | markdown | Rich text — simplify to Markdown |
| .xcf | binary | png-export | GIMP image — export to PNG |
| .zip | binary | extract-and-catalog | Compressed archive — unzip then re-catalog |
| .pbix | binary | unsupported | Power BI — no standard conversion path |
| .mp4 / .mov / .avi | binary | transcription | Video recording — transcribe audio |
| .pptx / .ppt | native | markdown | PowerPoint presentation |
| (no ext / unknown) | unsupported | manual-review | Unrecognized format |
