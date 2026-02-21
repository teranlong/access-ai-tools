"""
vsdx_to_text.py — Extract shape labels from a VSDX file as Markdown bullet lists.

VSDX is a ZIP archive containing XML. This converter reads visio/pages/page*.xml
and extracts all <Text> elements, deduplicating within each page.
Used as content/fallback mode and as the visual-mode text sidecar.
"""

from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path

from .base import ConversionResult, make_output_path


_NS = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}


def _get_page_names(z: zipfile.ZipFile) -> dict[int, str]:
    """Return {page_index: page_name} from visio/pages/pages.xml."""
    names: dict[int, str] = {}
    if "visio/pages/pages.xml" not in z.namelist():
        return names
    from lxml import etree
    tree = etree.fromstring(z.read("visio/pages/pages.xml"))
    for i, page_el in enumerate(tree.findall(".//v:Page", _NS)):
        name = page_el.get("Name", f"Page {i + 1}")
        names[i] = name
    return names


def _extract_page_labels(z: zipfile.ZipFile, page_index: int) -> list[str]:
    """Return deduplicated text labels from a single page XML."""
    page_file = f"visio/pages/page{page_index + 1}.xml"
    if page_file not in z.namelist():
        return []

    from lxml import etree
    tree = etree.fromstring(z.read(page_file))

    seen: set[str] = set()
    labels: list[str] = []

    for text_el in tree.findall(".//v:Text", _NS):
        # Gather all text content from child elements and mixed content
        raw = "".join(text_el.itertext()).strip()
        # Unescape HTML entities, collapse whitespace
        clean = html.unescape(raw)
        clean = re.sub(r"\s+", " ", clean).strip()
        if clean and clean not in seen:
            seen.add(clean)
            labels.append(clean)

    return labels


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Extract shape text from VSDX and write as a per-page Markdown bullet list."""
    try:
        from lxml import etree  # noqa: F401 — trigger ImportError early if missing
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install lxml",
        )

    out_path = make_output_path(source, output_root, project_root, ".md")

    try:
        with zipfile.ZipFile(source, "r") as z:
            page_names = _get_page_names(z)
            page_files = sorted(
                n for n in z.namelist()
                if re.match(r"visio/pages/page\d+\.xml$", n)
            )
            num_pages = len(page_files)

            sections: list[str] = [f"# Visio Shape Labels: {source.name}\n"]

            for i in range(num_pages):
                name = page_names.get(i, f"Page {i + 1}")
                labels = _extract_page_labels(z, i)
                bullet_list = "\n".join(f"- {lbl}" for lbl in labels) if labels else "_No text labels found._"
                sections.append(f"## {name}\n\n{bullet_list}\n")

    except Exception as exc:
        out_path.write_text(
            f"# Conversion Error: {source.name}\n\n**Error:** `{exc}`\n",
            encoding="utf-8",
        )
        return ConversionResult(
            success=False,
            output_files=[out_path],
            action="error",
            error=str(exc),
        )

    out_path.write_text("\n---\n\n".join(sections), encoding="utf-8")

    return ConversionResult(
        success=True,
        output_files=[out_path],
        action="converted",
    )
