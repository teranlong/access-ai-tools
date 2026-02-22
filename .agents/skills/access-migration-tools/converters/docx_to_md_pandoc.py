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
    prefer_pipe_tables: bool = False,
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
        lua_filter_path = Path(__file__).parent / "clean_layout.lua"
        
        extra_args = [
            f'--extract-media={temp_extract_dir}',
            '--wrap=none',
            f'--lua-filter={lua_filter_path}'
        ]

        if prefer_pipe_tables or kwargs.get("prefer_pipe_tables"):
            # If pipe tables are preferred, we use Pandoc to get HTML first,
            # then use markdownify to get guaranteed pipe tables.
            html = pypandoc.convert_file(
                str(source),
                'html',
                format='docx',
                extra_args=extra_args
            )
            from markdownify import markdownify as md
            # strip some common bloat that interferes with tables
            markdown = md(html, heading_style="ATX", bullets="-", strip=['script', 'style', 'br'], tables=True)
        else:
            format_str = 'gfm'
            markdown = pypandoc.convert_file(
                str(source),
                format_str,
                format='docx',
                extra_args=extra_args
            )

        # Pandoc puts images in temp_extract_dir/media/
        pandoc_media_dir = temp_extract_dir / "media"
        extracted_image_names = []
        if pandoc_media_dir.exists():
            for img_file in pandoc_media_dir.iterdir():
                if img_file.is_file():
                    dest_file = images_dir / img_file.name
                    shutil.move(str(img_file), str(dest_file))
                    extracted_image_names.append(img_file.name)
                    output_files.append(dest_file)
            
            # Cleanup temp dir
            shutil.rmtree(temp_extract_dir)
        elif temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)

        # Fix image paths in markdown
        # 1. Handle HTML <img> tags (often emitted for complex layouts)
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

    # 1. Clean up residual HTML from Pandoc tables that it couldn't turn into pipes
    # Remove colgroup and width styles which cause "squishing" in many previews
    markdown = re.sub(r'<colgroup>.*?</colgroup>', '', markdown, flags=re.DOTALL)
    markdown = re.sub(r' style="width:[^"]*"', '', markdown)
    markdown = re.sub(r'width="[^"]*"', '', markdown)

    # Use BeautifulSoup for smarter HTML table cell cleanup if bs4 is available
    try:
        from bs4 import BeautifulSoup
        # Wrap in a root tag to make it a valid fragment
        soup = BeautifulSoup(f"<div>{markdown}</div>", "html.parser")
        
        # Find all cells and list items
        for tag in soup.find_all(['td', 'th', 'li']):
            # If the tag contains ONLY one or more paragraphs and nothing else, unwrap them
            paras = tag.find_all('p', recursive=False)
            if paras:
                for p in paras:
                    p.unwrap()
        
        # Get back the modified HTML (strip the temporary div)
        markdown = str(soup.div.decode_contents())
    except ImportError:
        # Fallback to regex if bs4 not installed
        markdown = re.sub(r'<(td|li|th|p)>\s*<p>(.*?)</p>\s*</\1>', r'<\1>\2</\1>', markdown, flags=re.DOTALL)
    
    # Final cleanup of common stray tags
    markdown = re.sub(r'</td>\s*<p>', '</td>\n', markdown)
    markdown = re.sub(r'</p>\s*</td>', '\n</td>', markdown)

    # 2. Vector Formats fixup (EMF/WMF to PNG)
    # Ported from docx_to_md.py for consistency
    final_output_files = []
    # Preserve the original order but update entries if converted
    for out_f in output_files:
        if out_f.suffix.lower() in (".emf", ".wmf"):
            try:
                from PIL import Image
                png_dest = out_f.with_suffix(".png")
                with Image.open(out_f) as im:
                    im.load(dpi=150)
                    im.save(str(png_dest))
                
                # Update markdown references
                markdown = markdown.replace(
                    f"{encoded_images_dir_name}/{out_f.name}", 
                    f"{encoded_images_dir_name}/{png_dest.name}"
                )
                
                # Also try matching un-quoted for the replacement just in case
                markdown = markdown.replace(
                    f"{images_dir_name}/{out_f.name}", 
                    f"{images_dir_name}/{png_dest.name}"
                )
                
                out_f.unlink()
                final_output_files.append(png_dest)
            except Exception:
                final_output_files.append(out_f)
        else:
            final_output_files.append(out_f)
    output_files = final_output_files

    # 2. MOJIBAKE CLEANUP (from original docx_to_md.py)
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
