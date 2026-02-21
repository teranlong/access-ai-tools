"""
converters/__init__.py — Dispatch registry for the AI-compatible conversion pipeline.

Single public entry point:
    dispatch(file_record, project_root, output_root) -> ConversionResult

Adding a new converter = add one import + one branch in dispatch(). Nothing else.
"""

from __future__ import annotations

from pathlib import Path

from .base import (
    ConversionResult,
    SKIP_CONVERSIONS,
    detect_context,
    context_reason,
)
from . import (
    stub_unsupported,
    copy_native,
    docx_to_md,
    xlsx_to_md,
    pdf_to_md,
    pdf_to_images,
    rtf_to_md,
    pptx_to_md,
    vsdx_to_mermaid,
    vsdx_to_images,
    accdb_schema,
)


# ---------------------------------------------------------------------------
# Extensions that are already AI-readable — skip entirely
# ---------------------------------------------------------------------------
_NATIVE_SKIP: set[str] = {
    ".svg", ".excalidraw", ".sql", ".json", ".xml", ".md", ".txt",
    ".csv", ".html", ".htm", ".css", ".js", ".ts", ".py",
    ".ps1", ".sh", ".bat", ".cmd",
    ".png", ".jpg", ".jpeg", ".bmp",  # vision-readable
}

# Extensions that need a verbatim copy (VBA source)
_COPY_VERBATIM: set[str] = {".bas", ".cls"}

# Extensions that get stubs
_STUB_TYPES: set[str] = {".zip", ".fig", ".bacpac", ".pbix", ".mp4", ".mov", ".avi", ".xcf", ".vsd"}


# ---------------------------------------------------------------------------
# dispatch()
# ---------------------------------------------------------------------------

def dispatch(
    file_record: dict,
    project_root: Path,
    output_root: Path,
) -> ConversionResult:
    """
    Route a file to the correct converter based on extension and context.

    Returns a ConversionResult — never raises (callers still wrap in try/except
    as a safety net, but this function handles its own errors gracefully).
    """
    ext = file_record.get("extension", "").lower()
    proposed = file_record.get("proposed_conversion", "")
    source = project_root / file_record["relative_path"]

    # --- Skip: native-readable formats (no conversion needed) ---------------
    if ext in _NATIVE_SKIP or proposed in SKIP_CONVERSIONS:
        return ConversionResult(
            success=True,
            skipped=True,
            action="skipped",
        )

    # --- Verbatim copy: VBA source files ------------------------------------
    if ext in _COPY_VERBATIM:
        return copy_native.convert(source, output_root, project_root)

    # --- Stubs: unsupported / manual-required formats -----------------------
    if ext in _STUB_TYPES:
        return stub_unsupported.convert(source, output_root, project_root)

    # --- Context-aware conversions ------------------------------------------
    context = detect_context(file_record)
    reason  = context_reason(file_record, context)

    # DOCX / DOC
    if ext in (".docx", ".doc"):
        result = docx_to_md.convert(source, output_root, project_root, context=context)
        result.context_decision = reason
        return result

    # XLSX / XLS
    if ext in (".xlsx", ".xls"):
        result = xlsx_to_md.convert(source, output_root, project_root)
        result.context_decision = reason if context != "content" else ""
        return result

    # PDF — always runs both image rendering and text extraction
    if ext == ".pdf":
        result = _dispatch_pdf(source, output_root, project_root, context, reason)
        return result

    # RTF
    if ext == ".rtf":
        return rtf_to_md.convert(source, output_root, project_root)

    # PPTX / PPT
    if ext in (".pptx", ".ppt"):
        return pptx_to_md.convert(source, output_root, project_root)

    # VSDX
    if ext == ".vsdx":
        result = _dispatch_vsdx(source, output_root, project_root, context, reason)
        return result

    # ACCDB / MDB
    if ext in (".accdb", ".mdb"):
        return accdb_schema.convert(source, output_root, project_root)

    # --- Fallback: stub any truly unknown types ------------------------------
    return stub_unsupported.convert(source, output_root, project_root)


# ---------------------------------------------------------------------------
# Internal multi-mode helpers
# ---------------------------------------------------------------------------

def _dispatch_pdf(
    source: Path,
    output_root: Path,
    project_root: Path,
    context: str,
    reason: str,
) -> ConversionResult:
    """PDF: always run both image rendering (.pages.md + PNGs) and text extraction (.md)."""
    img_result  = pdf_to_images.convert(source, output_root, project_root)
    text_result = pdf_to_md.convert(source, output_root, project_root)
    combined_files = img_result.output_files + text_result.output_files
    success = img_result.success or text_result.success
    errors = [e for e in [img_result.error, text_result.error] if e]
    warnings = [w for w in [img_result.warning, text_result.warning] if w]
    action = "converted" if success else "error"
    return ConversionResult(
        success=success,
        output_files=combined_files,
        action=action,
        context_decision=reason + " (both modes)",
        warning="; ".join(warnings) or None,
        error="; ".join(errors) or None,
    )


def _dispatch_vsdx(
    source: Path,
    output_root: Path,
    project_root: Path,
    context: str,
    reason: str,
) -> ConversionResult:
    """VSDX: always run both image rendering (PNG + text labels) and Mermaid conversion."""
    img_result     = vsdx_to_images.convert(source, output_root, project_root)
    mermaid_result = vsdx_to_mermaid.convert(source, output_root, project_root)
    combined_files = img_result.output_files + mermaid_result.output_files
    success = img_result.success or mermaid_result.success
    errors = [e for e in [img_result.error, mermaid_result.error] if e]
    warnings = [w for w in [img_result.warning, mermaid_result.warning] if w]
    action = "converted" if success else "error"
    return ConversionResult(
        success=success,
        output_files=combined_files,
        action=action,
        context_decision=reason + " (both modes)",
        warning="; ".join(warnings) or None,
        error="; ".join(errors) or None,
    )
