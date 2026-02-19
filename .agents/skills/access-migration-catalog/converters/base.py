"""
base.py — Shared types, path utilities, and context detection.

Every converter module imports from here. Nothing here imports from converters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional


# ---------------------------------------------------------------------------
# Conversion result
# ---------------------------------------------------------------------------

@dataclass
class ConversionResult:
    success: bool
    output_files: list[Path] = field(default_factory=list)
    skipped: bool = False
    action: str = ""           # "converted" | "copied" | "stubbed" | "skipped" | "error"
    context_decision: str = "" # e.g., "flow mode: 'screen flow' in filename"
    error: Optional[str] = None
    warning: Optional[str] = None


# ---------------------------------------------------------------------------
# proposed_conversion values that mean "do nothing"
# ---------------------------------------------------------------------------

SKIP_CONVERSIONS: set[str] = {"keep-as-is", "keep-as-reference"}


# ---------------------------------------------------------------------------
# Context detection
# ---------------------------------------------------------------------------

VISUAL_SIGNALS = ["sketch", "mockup", "wireframe", "screen design", "ui design", "figma", "design"]
FLOW_SIGNALS   = ["screen flow", "flow", "workflow", "process", "state diagram"]
SPEC_SIGNALS   = ["functional spec", " fs ", "module", "requirements", "specification", "sow"]

# Content overrides: paths matching these are treated as content regardless of other signals.
# Prevents meeting transcripts / notes from triggering visual mode via folder names like
# "Design Meeting Transcripts".
CONTENT_OVERRIDES = ["transcript", "meeting notes", "meeting recording", "walk through", "walkthrough"]


def detect_context(file_record: dict) -> Literal["visual", "flow", "content"]:
    """Return the document's communication purpose based on path/name signals."""
    path = (file_record.get("relative_path", "") + " " + file_record.get("file_name", "")).lower()
    # Content overrides take highest priority — never mis-classify meeting notes as visual
    if any(s in path for s in CONTENT_OVERRIDES):
        return "content"
    if any(s in path for s in FLOW_SIGNALS):
        return "flow"
    if any(s in path for s in VISUAL_SIGNALS):
        return "visual"
    return "content"


def context_reason(file_record: dict, context: str) -> str:
    """Return a human-readable reason string for the context decision."""
    path = (file_record.get("relative_path", "") + " " + file_record.get("file_name", "")).lower()
    if context == "content":
        override = next((s for s in CONTENT_OVERRIDES if s in path), "")
        if override:
            return f"content mode: '{override}' in path (content override)"
    if context == "flow":
        matched = next((s for s in FLOW_SIGNALS if s in path), "")
        return f"flow mode: '{matched}' in path"
    if context == "visual":
        matched = next((s for s in VISUAL_SIGNALS if s in path), "")
        return f"visual mode: '{matched}' in path"
    return "content mode: no visual/flow signals"


# ---------------------------------------------------------------------------
# Path utilities
# ---------------------------------------------------------------------------

def make_output_path(
    source: Path,
    output_root: Path,
    project_root: Path,
    suffix: str,
) -> Path:
    """
    Mirror the source path under output_root and append a suffix.

    Example:
        source      = project_root / "Specs/SOW.pdf"
        output_root = agent-data/.../ProjectName
        suffix      = ".pdf.md"
        → output_root / "Specs/SOW.pdf.md"
    """
    rel = source.relative_to(project_root)
    out = output_root / rel.parent / (source.name + suffix)
    out.parent.mkdir(parents=True, exist_ok=True)
    return out


def make_output_dir(
    source: Path,
    output_root: Path,
    project_root: Path,
) -> Path:
    """
    Return (and create) the mirrored directory for files generated alongside source.

    Example:
        source      = project_root / "Specs/SOW.pdf"
        output_root = agent-data/.../ProjectName
        → output_root / "Specs/"  (created, returned)
    """
    rel = source.relative_to(project_root)
    out_dir = output_root / rel.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_size(size_bytes: int) -> str:
    """Return a human-friendly file size string."""
    if size_bytes < 0:
        return "unknown"
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
