"""
stub_unsupported.py — Write a stub .md for file types that cannot be auto-converted.

Each stub explains what the file is and what manual steps are needed for AI access.
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

from .base import ConversionResult, make_output_path


# ---------------------------------------------------------------------------
# Stub templates keyed by extension (lowercase)
# ---------------------------------------------------------------------------

_STUBS: dict[str, tuple[str, str, list[str]]] = {
    ".zip": (
        "ZIP Archive",
        "A compressed archive. Contents were not cataloged or converted automatically.",
        [
            "Extract the archive to a temporary folder.",
            "Run `catalog.py` on the extracted folder to produce a new inventory.",
            "Run `convert_to_ai_compatible.py` on each extracted sub-project.",
        ],
    ),
    ".fig": (
        "Figma Design File",
        "A binary Figma design file. Requires Figma desktop or API export.",
        [
            "Open the file in Figma desktop or upload to figma.com.",
            "Export frames as PNG (File → Export) for visual reference.",
            "Or use the Figma REST API to export components programmatically.",
        ],
    ),
    ".bacpac": (
        "SQL Server BACPAC Archive",
        "A SQL Server database export. Requires SQL Server or Azure SQL to restore.",
        [
            "Restore to SQL Server via SSMS: Tasks → Import Data-tier Application.",
            "Or use `sqlpackage.exe /Action:Import /SourceFile:<file>.bacpac ...`.",
            "After restore, export schema as SQL script for AI review.",
        ],
    ),
    ".pbix": (
        "Power BI Report",
        "A Power BI Desktop report file. Requires Power BI Desktop to open.",
        [
            "Open in Power BI Desktop.",
            "Export data model: File → Export → Power BI template (.pbit).",
            "Export report pages as PDF: File → Export to PDF.",
            "For schema: use Tabular Editor or DAX Studio to extract model metadata.",
        ],
    ),
    ".mp4": (
        "Video File (MP4)",
        "A video recording. Requires transcription or manual review.",
        [
            "Use a transcription service (e.g., Whisper, Azure Speech, Otter.ai).",
            "Save transcript as .txt or .md alongside this file.",
            "Reference the transcript in your AI context instead of this binary.",
        ],
    ),
    ".mov": (
        "Video File (MOV)",
        "A QuickTime video recording. Requires transcription or manual review.",
        [
            "Use a transcription service (e.g., Whisper, Azure Speech, Otter.ai).",
            "Save transcript as .txt or .md alongside this file.",
            "Reference the transcript in your AI context instead of this binary.",
        ],
    ),
    ".avi": (
        "Video File (AVI)",
        "An AVI video recording. Requires transcription or manual review.",
        [
            "Use a transcription service (e.g., Whisper, Azure Speech, Otter.ai).",
            "Save transcript as .txt or .md alongside this file.",
            "Reference the transcript in your AI context instead of this binary.",
        ],
    ),
    ".xcf": (
        "GIMP Image File (XCF)",
        "A GIMP native image file. Requires GIMP to export.",
        [
            "Open in GIMP.",
            "File → Export As → PNG (flatten layers first if needed).",
            "The exported PNG is vision-readable by AI agents.",
        ],
    ),
    ".vsd": (
        "Visio Drawing (Legacy Binary)",
        "An older binary Visio format (.vsd, pre-2010). Cannot be parsed as ZIP/XML.",
        [
            "Open in Microsoft Visio (2010 or later).",
            "Save As → .vsdx (XML-based format) for automated conversion.",
            "Or: File → Export → PDF or PNG for visual reference.",
        ],
    ),
}

_DEFAULT_STUB = (
    "Unsupported File Type",
    "This file type has no automated conversion path.",
    [
        "Identify the application that created this file.",
        "Export or save as a text, PDF, or image format.",
        "Re-run convert_to_ai_compatible.py on the exported version.",
    ],
)


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Write a stub .md file explaining how to manually make this file AI-readable."""
    ext = source.suffix.lower()
    type_name, description, steps = _STUBS.get(ext, _DEFAULT_STUB)

    out_path = make_output_path(source, output_root, project_root, ".md")

    numbered_steps = "\n".join(f"{i+1}. {s}" for i, s in enumerate(steps))

    content = f"""\
_Stub generated for:_ `{source.name}`

# {type_name}: {source.name}

**Generated:** {datetime.now().isoformat(timespec="seconds")}
**Original path:** `{source.relative_to(project_root).as_posix()}`

## Description

{description}

## Manual Steps Required

{numbered_steps}

## Note for AI Agents

This stub replaces the original `{source.name}` in the AI-compatible output tree.
The original file was not converted automatically. Follow the manual steps above
to produce an AI-readable version, then update this stub or add the converted file
to the same directory.
"""

    try:
        out_path.write_text(content, encoding="utf-8")
        return ConversionResult(
            success=True,
            output_files=[out_path],
            action="stubbed",
        )
    except Exception as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=str(exc),
        )
