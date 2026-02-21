"""
copy_native.py — Verbatim copy for files that are already AI-readable as-is.

Used for .bas and .cls VBA source files: copy byte-for-byte, no suffix added.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from .base import ConversionResult


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Copy source verbatim to the mirrored output path (no suffix appended)."""
    rel = source.relative_to(project_root)
    dest = output_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)

    try:
        shutil.copy2(source, dest)
        return ConversionResult(
            success=True,
            output_files=[dest],
            action="copied",
        )
    except Exception as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=str(exc),
        )
