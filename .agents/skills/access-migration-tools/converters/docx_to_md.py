"""
docx_to_md.py — Convert .docx/.doc to Markdown using mammoth + markdownify.

Optimized for:
1. Accurate Bullet Hierarchy (Fixes double bullets and indentation)
2. Mojibake cleanup (UTF-8 encoding issues)
3. Clean image embedding with relative paths
4. Removing conversion bloat (warnings, redundant logs)
"""

from __future__ import annotations

import zipfile
import re
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
    
    # Sidecar directory for images
    images_dir_name = f"{source.name}_images"
    images_dir = make_output_dir(source, output_root, project_root) / images_dir_name

    # --- Convert HTML → Markdown -------------------------------------------
    try:
        # Style map improvements:
        # We REMOVE the explicit 'li' mapping for 'List Paragraph'.
        # Mammoth is better at detecting lists using internal docx properties.
        # We only map specific character styles we want to preserve.
        style_map = """
        r[style-name='Strong'] => b
        r[style-name='Emphasis'] => i
        """

        image_counter = 0
        def _handle_image(image):
            nonlocal image_counter
            image_counter += 1
            ext = image.content_type.split("/")[-1] if image.content_type else "png"
            if "emf" in ext: ext = "emf"
            if "wmf" in ext: ext = "wmf"
            if "jpeg" in ext: ext = "jpg"
            
            img_filename = f"image_{image_counter}.{ext}"
            images_dir.mkdir(parents=True, exist_ok=True)
            img_dest = images_dir / img_filename
            
            with image.open() as img_f:
                img_dest.write_bytes(img_f.read())
            
            extracted_images.append(img_filename)
            return {"src": f"{images_dir_name}/{img_filename}"}

        with source.open("rb") as f:
            result = mammoth.convert_to_html(
                f, 
                convert_image=mammoth.images.img_element(_handle_image),
                style_map=style_map
            )

        html = result.value
        messages = result.messages

        if messages:
            warnings_text = "\n".join(
                f"- [{m.type}] {m.message}" for m in messages
            )

        # Convert to Markdown
        # Use wrap=False to prevent artificial line breaks
        markdown = md(
            html, 
            heading_style="ATX", 
            bullets="-",
            strip=['script', 'style', 'br'],
            wrap=False
        )

    except Exception as exc:
        err_str = str(exc)
        out_path.write_text(f"# Conversion Error: {source.name}\n\n**Error:** `{err_str}`\n", encoding="utf-8")
        return ConversionResult(success=False, output_files=[out_path], action="error", error=err_str)

    # --- Post-process results -----------------------------------------------
    
    # 1. Fix Image Paths (EMF to PNG)
    for img_filename in list(extracted_images):
        img_path = images_dir / img_filename
        if img_path.suffix.lower() in (".emf", ".wmf"):
            try:
                from PIL import Image
                png_dest = img_path.with_suffix(".png")
                with Image.open(img_path) as im:
                    im.load(dpi=150)
                    im.save(str(png_dest))
                img_path.unlink()
                markdown = markdown.replace(f"{images_dir_name}/{img_filename}", f"{images_dir_name}/{png_dest.name}")
                output_files.append(png_dest)
            except Exception:
                output_files.append(img_path)
        else:
            output_files.append(img_path)

    # 2. MOJIBAKE CLEANUP
    # Standard replacement for common double-encoded UTF-8 sequences
    text_replacements = {
        "â€“": "–",
        "â€”": "—",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "Â ": " ",
        "â€¢": "•",
        "â€¦": "...",
    }
    for old, new in text_replacements.items():
        markdown = markdown.replace(old, new)

    # 3. FIX DOUBLE BULLETS AND LIST MERGING
    # RCA: Catch '- - ' patterns and convert to indented bullets
    # Pattern: Line start, followed by '- - '
    markdown = re.sub(r'^(\s*)-\s+- ', r'\1  - ', markdown, flags=re.MULTILINE)
    
    # RCA: Ensure spacing between text and following lists to prevent "smushed" text
    # Look for alphanumeric character immediately followed by a bullet line
    markdown = re.sub(r'([a-zA-Z0-9:])\n-', r'\1\n\n-', markdown)

    # 4. Clean up Image Bloat
    markdown = re.sub(r'!\[A (screenshot|picture|white|close-up|table).*?Description automatically generated\]', '![image]', markdown)
    markdown = re.sub(r'\n\s*!\[', '\n![', markdown)

    # 5. Final Formatting cleanup
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()

    # --- Output --------------------------------------------------------------
    header = f"# {source.name}\n\n"
    if context == "visual" and extracted_images:
        header += f"*(Visual mode: {len(extracted_images)} images embedded)*\n\n"

    out_path.write_text(header + markdown + "\n", encoding="utf-8")
    output_files.insert(0, out_path)

    warning = warnings_text.strip() or None
    return ConversionResult(success=True, output_files=output_files, action="converted", warning=warning)
