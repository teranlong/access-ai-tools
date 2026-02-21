"""
pdf_to_images.py — Render each PDF page as a PNG image (visual mode).

Uses fitz (PyMuPDF), which is bundled with the pymupdf4llm install.
Writes one PNG per page plus an index .md listing all page filenames.
"""

from __future__ import annotations

from pathlib import Path

from .base import ConversionResult, make_output_path, make_output_dir


DPI = 150


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Render each page of a PDF to a PNG and write an index Markdown file."""
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install pymupdf4llm",
        )

    out_dir = make_output_dir(source, output_root, project_root)
    output_files: list[Path] = []
    page_filenames: list[str] = []

    try:
        doc = fitz.open(str(source))
        page_count = len(doc)

        for i, page in enumerate(doc):
            page_num = i + 1
            png_name = f"{source.name}_page_{page_num:03d}.png"
            png_path = out_dir / png_name

            mat = fitz.Matrix(DPI / 72, DPI / 72)
            pix = page.get_pixmap(matrix=mat)
            pix.save(str(png_path))

            output_files.append(png_path)
            page_filenames.append(png_name)

        doc.close()
    except Exception as exc:
        md_path = make_output_path(source, output_root, project_root, ".md")
        md_path.write_text(
            f"# Conversion Error: {source.name}\n\n**Error:** `{exc}`\n",
            encoding="utf-8",
        )
        return ConversionResult(
            success=False,
            output_files=[md_path],
            action="error",
            error=str(exc),
        )

    # --- Write index Markdown ------------------------------------------------
    page_list = "\n".join(f"- `{n}`" for n in page_filenames)
    index_md = (
        f"# PDF Visual Render: {source.name}\n\n"
        f"**Pages rendered:** {page_count}  \n"
        f"**Resolution:** {DPI} DPI\n\n"
        f"---\n\n"
        f"## Page Images\n\n"
        f"{page_list}\n"
    )

    md_path = make_output_path(source, output_root, project_root, ".pages.md")
    md_path.write_text(index_md, encoding="utf-8")
    output_files.insert(0, md_path)

    return ConversionResult(
        success=True,
        output_files=output_files,
        action="converted",
    )
