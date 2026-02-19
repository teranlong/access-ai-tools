"""
docx_to_md.py — Convert .docx/.doc to Markdown using mammoth + markdownify.

Always extracts embedded images from word/media/ into a sidecar dir.
Visual mode adds a header line noting the image count.
Base64 data URIs from mammoth are suppressed; images are saved as files instead.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

from .base import ConversionResult, make_output_path, make_output_dir


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    context: str = "content",
    **kwargs,
) -> ConversionResult:
    """Convert a Word document to Markdown."""
    try:
        import mammoth
        from markdownify import markdownify as md
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install mammoth markdownify",
        )

    out_path = make_output_path(source, output_root, project_root, ".md")
    output_files: list[Path] = []
    warnings_text = ""
    extracted_images: list[str] = []

    # --- Convert HTML → Markdown -------------------------------------------
    try:
        def _strip_image(image):
            return {"src": ""}  # replaces <img src="data:..."> with <img src="">

        with source.open("rb") as f:
            result = mammoth.convert_to_html(
                f, convert_image=mammoth.images.img_element(_strip_image)
            )

        html = result.value
        messages = result.messages

        if messages:
            warnings_text = "\n".join(
                f"- [{m.type}] {m.message}" for m in messages
            )

        markdown = md(html, heading_style="ATX", bullets="-")

    except Exception as exc:
        err_str = str(exc)
        # "File is not a zip file" means this is a legacy binary .doc (pre-2007)
        # masquerading with a .docx extension, or the file is corrupted.
        if "not a zip" in err_str.lower() or "invalid file" in err_str.lower():
            note = (
                "This file could not be read as a .docx (ZIP-based) document. "
                "It may be a legacy binary Word .doc file saved with a .docx extension, "
                "or the file may be corrupted or password-protected.\n\n"
                "**Manual steps:**\n"
                "1. Open the file in Microsoft Word.\n"
                "2. File → Save As → Word Document (.docx) to re-save in the correct format.\n"
                "3. Re-run the converter on the saved copy.\n"
            )
        else:
            note = f"**Error:** `{err_str}`\n"
        out_path.write_text(
            f"# Conversion Error: {source.name}\n\n"
            f"Failed to convert document.\n\n{note}",
            encoding="utf-8",
        )
        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=err_str,
        )

    # --- Extract embedded images (always, not just visual mode) -------------
    try:
        images_dir = make_output_dir(source, output_root, project_root) / f"{source.name}_images"
        images_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(source, "r") as z:
            media_files = [n for n in z.namelist() if n.startswith("word/media/")]
            for media_name in media_files:
                img_name = Path(media_name).name
                img_dest = images_dir / img_name
                img_dest.write_bytes(z.read(media_name))

                # Attempt Pillow conversion for Windows vector formats
                if img_dest.suffix.lower() in (".emf", ".wmf"):
                    try:
                        from PIL import Image
                        png_dest = img_dest.with_suffix(".png")
                        with Image.open(img_dest) as im:
                            im.load(dpi=150)
                            im.save(str(png_dest))
                        img_dest.unlink()  # remove unreadable original
                        extracted_images.append(png_dest.name)
                        output_files.append(png_dest)
                    except Exception as vec_exc:
                        # Keep original, note failure
                        extracted_images.append(img_name)
                        output_files.append(img_dest)
                        warnings_text += f"\n- [emf-conversion] {img_name}: {vec_exc}"
                else:
                    extracted_images.append(img_name)
                    output_files.append(img_dest)

        if extracted_images:
            image_list = "\n".join(f"- `{n}`" for n in extracted_images)
            markdown += (
                f"\n\n---\n\n## Embedded Images\n\n"
                f"Images saved to `{source.name}_images/`:\n\n{image_list}\n"
            )
    except Exception as exc:
        # Non-fatal — images not critical
        warnings_text += f"\n- [image-extraction] {exc}"

    # --- Build output file ---------------------------------------------------
    header_lines = [f"# Converted: {source.name}", ""]
    if context == "visual" and extracted_images:
        header_lines += [f"_Visual mode: {len(extracted_images)} image(s) extracted._", ""]
    if warnings_text:
        header_lines += ["## Mammoth Warnings", "", warnings_text, ""]
    header_lines += ["---", ""]

    header = "\n".join(header_lines)
    out_path.write_text(header + markdown, encoding="utf-8")
    output_files.insert(0, out_path)

    warning = warnings_text.strip() or None
    return ConversionResult(
        success=True,
        output_files=output_files,
        action="converted",
        warning=warning,
    )
