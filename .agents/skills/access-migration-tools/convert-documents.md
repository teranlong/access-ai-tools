# Ability: convert-documents

You are acting as a senior engineer and Microsoft Access DB migration expert. Your task is to convert every file in a given project folder into AI-readable formats (primarily Markdown), mirroring the directory structure so documents can be loaded directly into AI context for downstream migration work.

> **Tip:** Run [catalog-documents](catalog-documents.md) first. The converter automatically picks up the catalog's `files.json` for richer metadata — but it works without one too.

---

## Step 1: Get the Project Directory

If the user has not provided a project folder path, ask for it before proceeding. The **project name** is the last segment of the folder path (e.g., `Youngdahl` from `.../SampleProjects/Youngdahl`).

---

## Step 2: Ensure the Virtual Environment is Active

Check that the venv exists and dependencies are installed:

```bash
python -c "import pypandoc; print('venv OK')" 2>nul || echo "venv NOT ready"
```

If the venv is not ready, set it up first:

```bash
cd .agents/skills/access-migration-tools
setup_venv.bat
```

Then activate it:

```bash
.agents/skills/access-migration-tools/.venv/Scripts/activate
```

---

## Step 3: Resolve the Converter VERSION

```bash
python -c "import sys; sys.path.insert(0,'.agents/skills/access-migration-tools'); from convert_to_ai_compatible import VERSION; print(VERSION)"
```

Use the printed value wherever `{VERSION}` appears in this document.

---

## Step 4: Run the Converter

```bash
python .agents/skills/access-migration-tools/convert_to_ai_compatible.py "<project_directory_path>"
```

**Optional flags:**

| Flag | Purpose |
|------|---------|
| `--force` | Re-convert files even if output is already up-to-date |
| `--output-dir <path>` | Override the default output location |

**Default output location:**
```
agent-data/ai-compatible/v{VERSION}/{project-name}/
```

The converter mirrors the original directory structure. For each file it will:
- **convert** — produce a `.md` equivalent (Word, Excel, PDF, Visio, RTF, PowerPoint)
- **copy** — copy verbatim without changes (VBA `.bas`/`.cls` source files)
- **stub** — write a `.md` stub explaining why the file cannot be auto-converted (Access `.accdb`, Figma `.fig`, Power BI `.pbix`, video files, etc.)
- **skip** — leave native-format files in place (`keep-as-is` and `keep-as-reference`)
- **idempotent** — skip files whose output is already newer than the source (re-run safe)

---

## Step 5: Read and Summarize the Conversion Report

After the run completes, read the summary report:

```
agent-data/ai-compatible/v{VERSION}/{project-name}/ai-compatible-summary.md
```

Present the user with:
1. **Totals table** — how many files were converted, copied, stubbed, skipped, or errored
2. **Contextual decisions** — any files where the converter chose a non-default mode
3. **Errors** — any files that failed, and suggested manual actions
4. **Stubbed files** — files that require manual action before they can be used by AI (list the stub `.md` files so the user knows what to handle next)

---

## Step 6: Flag Files Needing Manual Attention

After presenting the summary, explicitly call out any stubbed or errored files and suggest next steps:

| File Type | Why Stubbed | Suggested Action |
|-----------|-------------|-----------------|
| `.accdb` / `.mdb` | Access DB — cannot read directly | Run MSACCESS-VCS export or use pyodbc to extract schema as SQL |
| `.bacpac` | SQL Server backup archive | Restore to SQL Server, then export schema as `.sql` |
| `.fig` | Figma binary backup | Open in Figma → export frames as PNG, or use Figma API |
| `.vsd` | Old Visio binary | Open in Visio → export as PNG or VSDX |
| `.pbix` | Power BI — no conversion path | Open in Power BI Desktop → export report pages as PDF |
| `.mp4` / `.mov` / `.avi` | Video recording | Transcribe audio with a speech-to-text tool |
| `.xcf` | GIMP image | Export as PNG from GIMP |
| `.zip` | Compressed archive | Unzip, then re-run converter on the extracted folder |

---

## Converter Output Reference

### What gets converted to Markdown

| Source Format | Converter | Notes |
|--------------|-----------|-------|
| `.docx` / `.doc` | mammoth → markdownify (or pandoc fallback) | Tables, headings, lists preserved |
| `.xlsx` / `.xls` | openpyxl / xlrd | Each sheet becomes a Markdown table |
| `.pdf` | pymupdf4llm (text) or fitz (images) | Text-first; falls back to page images |
| `.pptx` / `.ppt` | python-pptx | Slide titles and text bodies extracted |
| `.rtf` | striprtf | Control codes stripped to plain text |
| `.vsdx` | lxml + aspose-diagram | Shapes and text extracted; optionally rendered as PNG |
| `.accdb` / `.mdb` | pyodbc | Table schema and row samples extracted |

### What is copied or skipped

| Format | Action | Reason |
|--------|--------|--------|
| `.bas` / `.cls` | copy verbatim | VBA source — already plain text |
| `.md` / `.txt` / `.sql` / `.json` / `.xml` / `.svg` / `.csv` | skip | Native — no conversion needed |
| `.png` / `.jpg` / `.jpeg` / `.bmp` / `.excalidraw` | skip | Keep as reference — AI can read directly |
