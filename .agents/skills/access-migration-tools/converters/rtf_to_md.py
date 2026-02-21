"""
rtf_to_md.py — Convert RTF files to plain-text Markdown using striprtf.

RTF containers use Latin-1 encoding; read with errors='replace' to be safe.
"""

from __future__ import annotations

import re
from pathlib import Path

from .base import ConversionResult, make_output_path


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Strip RTF control codes and write the plain text as Markdown."""
    try:
        from striprtf.striprtf import rtf_to_text
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install striprtf",
        )

    out_path = make_output_path(source, output_root, project_root, ".md")

    try:
        raw = source.read_text(encoding="latin-1", errors="replace")
        plain = rtf_to_text(raw)

        # Normalize excessive blank lines → at most two
        plain = re.sub(r"\n{3,}", "\n\n", plain).strip()

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

    content = f"# RTF Text: {source.name}\n\n---\n\n{plain}\n"
    out_path.write_text(content, encoding="utf-8")

    return ConversionResult(
        success=True,
        output_files=[out_path],
        action="converted",
    )
