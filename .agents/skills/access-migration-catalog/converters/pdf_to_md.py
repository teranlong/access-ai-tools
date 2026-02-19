"""
pdf_to_md.py — Convert PDF to Markdown (text/content mode).

Uses pymupdf4llm for LLM-ready Markdown extraction. Detects scanned (image-only)
PDFs and adds a clear warning rather than silently producing empty output.
"""

from __future__ import annotations

from pathlib import Path

from .base import ConversionResult, make_output_path


_MIN_TEXT_CHARS = 100  # Below this threshold → treat as image-only / scanned


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Extract text from a PDF and write it as Markdown."""
    try:
        import pymupdf4llm
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install pymupdf4llm",
        )

    out_path = make_output_path(source, output_root, project_root, ".md")
    warning = None

    try:
        markdown = pymupdf4llm.to_markdown(str(source))
    except Exception as exc:
        out_path.write_text(
            f"# Conversion Error: {source.name}\n\n**Error:** `{exc}`\n",
            encoding="utf-8",
        )
        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=str(exc),
        )

    stripped = markdown.strip()
    if len(stripped) < _MIN_TEXT_CHARS:
        warning = (
            "PDF appears image-only (scanned). No text extracted. "
            "Consider running pdf_to_images converter for visual mode instead."
        )
        markdown = f"# {source.name}\n\n> WARNING: {warning}\n\n---\n\n{markdown}"

    header = f"# PDF Text: {source.name}\n\n---\n\n"
    out_path.write_text(header + markdown, encoding="utf-8")

    return ConversionResult(
        success=True,
        output_files=[out_path],
        action="converted",
        warning=warning,
    )
