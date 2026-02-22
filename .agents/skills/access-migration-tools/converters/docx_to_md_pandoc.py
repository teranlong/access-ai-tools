"""
docx_to_md_pandoc.py — Convert .docx/.doc to Markdown using Pandoc.

Optimized for:
1. High-fidelity structure via Pandoc
2. Clean image extraction and path normalization
3. Mojibake cleanup (UTF-8 encoding issues)
4. Consistent image embedding with URL-encoded relative paths
"""

from __future__ import annotations

import re
import urllib.parse
import shutil
from pathlib import Path

from .base import ConversionResult, make_output_path, make_output_dir


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    context: str = "content",
    **kwargs,
) -> ConversionResult:
    """Convert a Word document to Markdown using Pandoc."""
    try:
        import pypandoc
    except ImportError:
        return ConversionResult(
            success=False,
            action="error",
            error="Missing dependency: pypandoc. Run: pip install pypandoc",
        )

    # Verify pandoc is installed
    try:
        pypandoc.get_pandoc_version()
    except OSError:
        return ConversionResult(
            success=False,
            action="error",
            error="Pandoc not found. Please install pandoc on your system.",
        )

    out_path = make_output_path(source, output_root, project_root, ".md")
    output_files: list[Path] = []
    
    # Sidecar directory for images
    images_dir_name = f"{source.name}_images"
    encoded_images_dir_name = urllib.parse.quote(images_dir_name)
    images_dir = make_output_dir(source, output_root, project_root) / images_dir_name
    
    # Pandoc creates a 'media' subfolder inside the extract-media path
    # We'll extract to a temporary location and then move them to match our convention
    temp_extract_dir = images_dir / "_temp_pandoc"
    temp_extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Convert docx to markdown
        # We use 'gfm' (GitHub Flavored Markdown) for best compatibility
        markdown = pypandoc.convert_file(
            str(source),
            'gfm',
            format='docx',
            extra_args=[f'--extract-media={temp_extract_dir}']
        )

        # Pandoc puts images in temp_extract_dir/media/
        pandoc_media_dir = temp_extract_dir / "media"
        extracted_images = []
        if pandoc_media_dir.exists():
            for img_file in pandoc_media_dir.iterdir():
                if img_file.is_file():
                    dest_file = images_dir / img_file.name
                    shutil.move(str(img_file), str(dest_file))
                    extracted_images.append(img_file.name)
                    output_files.append(dest_file)
            
            # Cleanup temp dir
            shutil.rmtree(temp_extract_dir)
        elif temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)

        # Fix image paths in markdown
        # Pandoc might emit standard Markdown ![alt](path) or HTML <img> tags
        # It often uses absolute paths to the temp media dir.
        # We want: source_name_images/image1.png (relative)
        
        # 1. Handle HTML <img> tags (often emitted for complex layouts)
        # Match src="..." where path ends in our temp media folder
        img_tag_pattern = re.compile(r'src=".*?[/\\\\]_temp_pandoc[/\\\\]media[/\\\\](.*?)"')
        markdown = img_tag_pattern.sub(f'src="{encoded_images_dir_name}/\\1"', markdown)

        # 2. Handle Markdown ![]() tags
        md_tag_pattern = re.compile(r'!\[.*?\]\((?:.*?[/\\\\]_temp_pandoc[/\\\\]media[/\\\\])(.*?)\)')
        markdown = md_tag_pattern.sub(f'![image]({encoded_images_dir_name}/\\1)', markdown)

    except Exception as exc:
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)
        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=str(exc)
        )

    # --- Post-process -------------------------------------------------------
    
    # 1. MOJIBAKE CLEANUP (from original docx_to_md.py)
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

    # 2. Clean alt-text bloat
    markdown = re.sub(r'!\[A (screenshot|picture|white|close-up|table).*?(Description automatically generated|AI-generated content may be incorrect).*?\]', '![image]', markdown, flags=re.DOTALL)

    # 3. Final Formatting cleanup
    markdown = re.sub(r'\n{3,}', '\n\n', markdown).strip()

    # --- Output -------------------------------------------------------------
    header = f"# {source.name}\n\n"
    if context == "visual" and extracted_images:
        header += f"*(Visual mode: {len(extracted_images)} images embedded)*\n\n"

    out_path.write_text(header + markdown + "\n", encoding="utf-8")
    output_files.insert(0, out_path)

    return ConversionResult(success=True, output_files=output_files, action="converted")
