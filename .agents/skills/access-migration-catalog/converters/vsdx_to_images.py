"""
vsdx_to_images.py — Render VSDX pages as PNG images via Aspose.Diagram.

If Aspose.Diagram is not installed or fails, falls back to text labels with a warning.
Always also writes the text-label Markdown as a sidecar.
"""

from __future__ import annotations

from pathlib import Path

from .base import ConversionResult, make_output_dir
from . import vsdx_to_text


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Render VSDX to PNG via Aspose.Diagram; fall back to text labels if unavailable."""
    out_dir = make_output_dir(source, output_root, project_root)
    output_files: list[Path] = []
    warning = None

    # --- Always produce the text-label sidecar ------------------------------
    text_result = vsdx_to_text.convert(source, output_root, project_root)
    output_files.extend(text_result.output_files)

    # --- Try Aspose.Diagram for PNG export ----------------------------------
    try:
        import aspose.diagram as ad

        diagram = ad.Diagram(str(source))
        options = ad.saving.ImageSaveOptions(ad.SaveFileFormat.PNG)
        rendered = 0
        for page_index in range(diagram.pages.count):
            options.page_index = page_index
            out_png = out_dir / f"{source.name}_page_{page_index + 1:03d}.png"
            diagram.save(str(out_png), options)
            output_files.append(out_png)
            rendered += 1

        if rendered == 0:
            warning = "Aspose.Diagram produced no pages; text labels used as fallback."

    except ImportError:
        warning = "aspose-diagram not installed; shape labels extracted instead of PNG renders."
    except Exception as exc:
        warning = f"Aspose.Diagram conversion failed: {exc}; text labels used as fallback."

    return ConversionResult(
        success=bool(output_files),
        output_files=output_files,
        action="converted",
        warning=warning,
    )
