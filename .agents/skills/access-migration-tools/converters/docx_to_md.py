"""
docx_to_md.py — Convert .docx/.doc to Markdown using mammoth + markdownify.

Optimized for:
1. Accurate Bullet Hierarchy
2. Mojibake cleanup (UTF-8 encoding issues)
3. Clean image embedding with URL-encoded relative paths
4. Removing conversion bloat (warnings, redundant logs)
"""

from __future__ import annotations

import zipfile
import re
import urllib.parse
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
    # URL encode the dir name to handle spaces in Markdown paths
    encoded_images_dir_name = urllib.parse.quote(images_dir_name)
    images_dir = make_output_dir(source, output_root, project_root) / images_dir_name

    # --- Convert HTML → Markdown -------------------------------------------
    try:
        # Standard style mapping for lists
        style_map = """
        p[style-name='List Paragraph'] => li
        p[style-name='List Bullet'] => li
        p[style-name='List Number'] => li
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
            # Use URL-encoded relative path for the HTML src
            return {"src": f"{encoded_images_dir_name}/{img_filename}"}

        with source.open("rb") as f:
            result = mammoth.convert_to_html(
                f, 
                convert_image=mammoth.images.img_element(_handle_image),
                style_map=style_map
            )

        html = result.value
        messages = result.messages

        if messages:
            warnings_text = "\n".join(f"- [{m.type}] {m.message}" for m in messages)

        # Convert HTML to MD
        markdown = md(
            html, 
            heading_style="ATX", 
            bullets="-",
            strip=['script', 'style', 'br'],
            wrap=False
        )

    except Exception as exc:
        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=str(exc)
        )

    # --- Post-process -------------------------------------------------------
    
    # 1. Vector Formats fixup (already using encoded path in markdown)
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
                # Replace both the old extension and ensure the path is encoded
                markdown = markdown.replace(f"{encoded_images_dir_name}/{img_filename}", f"{encoded_images_dir_name}/{png_dest.name}")
                output_files.append(png_dest)
            except Exception:
                output_files.append(img_path)
        else:
            output_files.append(img_path)

    # 2. MOJIBAKE CLEANUP
    mojibake_map = {
        "â€“": "–",
        "â€”": "—",
        "â€™": "'",
        "â€œ": '"',
        "â€": '"',
        "Â ": " ",
        "â€¢": "•",
        "â€¦": "...",
        "\u00e2\u20ac\u201c": "–",
        "\u00e2\u20ac\u201d": "—",
        "\u00e2\u20ac\u2122": "'",
    }
    for old, new in mojibake_map.items():
        markdown = markdown.replace(old, new)

    # 3. Double Bullet / List merging fixes
    markdown = re.sub(r'^(\s*)-\s+- ', r'\1  - ', markdown, flags=re.MULTILINE)
    markdown = re.sub(r'([a-zA-Z0-9:])\n-', r'\1\n\n-', markdown)

    # 4. Clean alt-text bloat (Updated for newer Word patterns)
    # This also collapses internal newlines that were causing the "A screenshot of a project" gap
    markdown = re.sub(r'!\[A (screenshot|picture|white|close-up|table).*?(Description automatically generated|AI-generated content may be incorrect).*?\]', '![image]', markdown, flags=re.DOTALL)

    # 5. Final Formatting cleanup
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()

    # --- Output -------------------------------------------------------------
    header = f"# {source.name}\n\n"
    if context == "visual" and extracted_images:
        header += f"*(Visual mode: {len(extracted_images)} images embedded)*\n\n"

    out_path.write_text(header + markdown + "\n", encoding="utf-8")
    output_files.insert(0, out_path)

    warning = warnings_text.strip() or None
    return ConversionResult(success=True, output_files=output_files, action="converted", warning=warning)
