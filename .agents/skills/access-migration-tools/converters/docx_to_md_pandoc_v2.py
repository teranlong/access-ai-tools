"""
docx_to_md_pandoc_v2.py — Convert .docx/.doc to Markdown using Pandoc.

Clean rewrite of docx_to_md_pandoc.py with:
- Generic image path replacement (handles all extracted images, not just specific filenames)
- No debug print statements
- Temp directory always cleaned up via finally block
- Redundant entity-unescape pass removed (html.unescape handles it)
"""

import html
import re
import shutil
import urllib.parse
from pathlib import Path

try:
    import pypandoc
except ImportError:
    pypandoc = None

try:
    from markdownify import markdownify as md
except ImportError:
    md = None

from .base import ConversionResult, make_output_path, make_output_dir


def _fix_image_references(markdown: str, encoded_images_dir: str) -> str:
    """Replace all pandoc temp-media paths with final relative paths.

    Pandoc writes extracted images to a temp directory and embeds those
    paths in its output.  After we move images to their permanent sidecar
    directory we need to update every reference so the markdown stays valid.

    Handles two cases:
    1. Markdown image syntax  ![alt](any/path/media/filename.ext)
    2. Raw <img> tags left behind by markdownify (edge cases)
    """
    # 1. Markdown image syntax produced by pandoc GFM output or markdownify
    markdown = re.sub(
        r'!\[([^\]]*)\]\([^)]*[/\\]media[/\\]([^)\s]+)\)',
        lambda m: f'![{m.group(1) or "image"}]({encoded_images_dir}/{urllib.parse.quote(m.group(2))})',
        markdown,
    )

    # 2. Raw HTML <img> tags that markdownify may leave in some edge cases
    def _replace_img_tag(m: re.Match) -> str:
        src_match = re.search(r'src=["\']([^"\']+)["\']', m.group(0))
        if src_match:
            filename = Path(src_match.group(1)).name
            return f'![image]({encoded_images_dir}/{urllib.parse.quote(filename)})'
        return m.group(0)

    markdown = re.sub(r'<img[^>]+>', _replace_img_tag, markdown)
    return markdown


def _fix_math_escaping(markdown: str) -> str:
    """Remove GFM over-escaping from inside LaTeX math blocks.

    Pandoc escapes underscores for GFM even inside dollar-sign delimiters,
    turning subscript notation (e.g. x_i) into x\\_i which KaTeX/MathJax
    cannot parse as a subscript. Strip the spurious backslash before _ inside
    math spans only. Other intentional sequences (backslash-space, \\frac, etc.)
    are untouched.
    """
    def unescape_subscripts(m: re.Match) -> str:
        return re.sub(r'\\_', '_', m.group(0))

    # Display math blocks: $$...$$
    markdown = re.sub(r'\$\$[\s\S]*?\$\$', unescape_subscripts, markdown)
    # Inline math: $...$ (skip $$ by using negative lookahead/lookbehind)
    markdown = re.sub(r'(?<!\$)\$(?!\$).+?(?<!\$)\$(?!\$)', unescape_subscripts, markdown)
    return markdown


def _convert_vector_images(
    images_dir: Path, markdown: str, encoded_images_dir: str
) -> tuple[str, list[Path]]:
    """Convert EMF/WMF files in images_dir to PNG and update markdown references.

    Must be called after _fix_image_references so that markdown already contains
    clean encoded_images_dir/filename references (not temp paths).

    Returns the updated markdown and a list of final image Paths.
    """
    try:
        from PIL import Image as PILImage
        pil_available = True
    except ImportError:
        pil_available = False

    final_paths: list[Path] = []
    if not images_dir.exists():
        return markdown, final_paths

    for img_path in sorted(images_dir.iterdir()):
        if not img_path.is_file():
            continue
        if pil_available and img_path.suffix.lower() in (".emf", ".wmf"):
            try:
                png_dest = img_path.with_suffix(".png")
                with PILImage.open(img_path) as im:
                    im.load(dpi=150)
                    im.save(str(png_dest))
                img_path.unlink()
                old_ref = f"{encoded_images_dir}/{urllib.parse.quote(img_path.name)}"
                new_ref = f"{encoded_images_dir}/{urllib.parse.quote(png_dest.name)}"
                markdown = markdown.replace(old_ref, new_ref)
                final_paths.append(png_dest)
            except Exception:
                # Conversion failed; keep the original file as-is
                final_paths.append(img_path)
        else:
            final_paths.append(img_path)

    return markdown, final_paths


def _swap_imgs_for_placeholders(
    html_content: str, encoded_images_dir: str
) -> tuple[str, dict[str, str]]:
    """Replace every <img> in the HTML with a text placeholder token.

    markdownify silently drops <img> tags that appear inside table cells when
    converting <table> to pipe-table syntax.  By swapping them to plain text
    tokens first, the tokens survive the table conversion and can be replaced
    back with proper markdown image references afterwards.

    Returns (html_with_placeholders, {token: markdown_image_ref}).
    """
    token_map: dict[str, str] = {}

    def replace_img(m: re.Match) -> str:
        src_match = re.search(r'src=["\']([^"\']+)["\']', m.group(0))
        if not src_match:
            return m.group(0)
        src = src_match.group(1)
        filename = urllib.parse.quote(Path(src.replace("\\", "/")).name)
        ref = f"![image]({encoded_images_dir}/{filename})"
        token = f"IMGTOKEN{len(token_map)}END"
        token_map[token] = ref
        return token

    return re.sub(r'<img[^>]+>', replace_img, html_content), token_map



def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    context: str = "content",
    prefer_pipe_tables: bool = False,
    **kwargs,
) -> ConversionResult:
    """Convert a Word document to Markdown using Pandoc."""
    if not pypandoc:
        return ConversionResult(success=False, action="error", error="pypandoc missing")

    out_path = make_output_path(source, output_root, project_root, ".md")
    output_files: list[Path] = []

    images_dir_name = f"{source.name}_images"
    encoded_images_dir_name = urllib.parse.quote(images_dir_name)
    images_dir = make_output_dir(source, output_root, project_root) / images_dir_name

    temp_extract_dir = images_dir / "_temp_pandoc"
    temp_extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        extra_args = [f'--extract-media={temp_extract_dir}', '--wrap=none']

        use_pipe_tables = prefer_pipe_tables or kwargs.get("prefer_pipe_tables")
        if use_pipe_tables and md:
            html_content = pypandoc.convert_file(
                str(source), 'html', format='docx', extra_args=extra_args
            )

            # Move images before markdownify so we know final filenames.
            pandoc_media_dir = temp_extract_dir / "media"
            if pandoc_media_dir.exists():
                for img_file in pandoc_media_dir.iterdir():
                    if img_file.is_file():
                        dest = images_dir / img_file.name
                        shutil.move(str(img_file), str(dest))
                        output_files.append(dest)

            # Swap <img> tags for plain-text tokens before markdownify so they
            # survive pipe-table cell conversion (markdownify silently drops <img>
            # inside <td>).  Tokens are replaced with proper image refs afterwards.
            html_content, img_tokens = _swap_imgs_for_placeholders(
                html_content, encoded_images_dir_name
            )
            markdown = md(
                html_content,
                heading_style="ATX",
                bullets="-",
                strip=['script', 'style', 'br'],
                tables=True,
            )
            for token, ref in img_tokens.items():
                markdown = markdown.replace(token, ref)
        else:
            markdown = pypandoc.convert_file(
                str(source), 'gfm', format='docx', extra_args=extra_args
            )

            # Move extracted media to the permanent sidecar directory
            pandoc_media_dir = temp_extract_dir / "media"
            if pandoc_media_dir.exists():
                for img_file in pandoc_media_dir.iterdir():
                    if img_file.is_file():
                        dest = images_dir / img_file.name
                        shutil.move(str(img_file), str(dest))
                        output_files.append(dest)

    except Exception as exc:
        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=str(exc),
        )
    finally:
        # Always remove the temp directory, even on error or when no media was found
        if temp_extract_dir.exists():
            shutil.rmtree(temp_extract_dir)

    # Post-process: unescape HTML entities, fix math escaping, fix image paths, convert vector formats
    markdown = html.unescape(markdown)
    markdown = _fix_math_escaping(markdown)
    markdown = _fix_image_references(markdown, encoded_images_dir_name)
    markdown, image_files = _convert_vector_images(images_dir, markdown, encoded_images_dir_name)

    # Rebuild output_files: markdown first, then images (vector conversion may have renamed some)
    output_files = [out_path] + image_files

    header = f"# {source.name}\n\n"
    out_path.write_text(header + markdown + "\n", encoding="utf-8")

    return ConversionResult(success=True, output_files=output_files, action="converted")
