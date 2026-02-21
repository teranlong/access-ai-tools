"""
vsdx_to_mermaid.py — Convert VSDX flow diagrams to Mermaid flowchart syntax.

Parses shape text and Connect elements from the Visio XML to build a
`flowchart LR` Mermaid diagram. Falls back to vsdx_to_text if no connects found.
"""

from __future__ import annotations

import html
import re
import zipfile
from pathlib import Path

from .base import ConversionResult, make_output_path
from . import vsdx_to_text


_NS = {"v": "http://schemas.microsoft.com/office/visio/2012/main"}

# Mermaid node ID: alphanumeric + underscore only
_ID_CLEAN = re.compile(r"[^\w]")


def _mermaid_id(shape_id: str, label: str) -> str:
    """Generate a safe, unique Mermaid node ID."""
    safe_label = _ID_CLEAN.sub("_", label[:20]).strip("_") or f"node{shape_id}"
    return f"n{shape_id}_{safe_label}"


def _mermaid_label(text: str) -> str:
    """Escape text for use inside a Mermaid node label."""
    # Replace double quotes and newlines
    return text.replace('"', "'").replace("\n", " ")


def _build_mermaid(
    shape_labels: dict[str, str],
    connections: list[tuple[str, str]],
    page_name: str,
) -> str:
    """Return a Mermaid flowchart block string."""
    lines = [f'%% Page: {page_name}', "flowchart LR"]

    # Declare all nodes that appear in connections
    connected_ids: set[str] = set()
    for from_id, to_id in connections:
        connected_ids.add(from_id)
        connected_ids.add(to_id)

    # Declare isolated nodes (not in any connection)
    all_ids = set(shape_labels.keys())
    isolated = all_ids - connected_ids
    for sid in sorted(isolated):
        label = _mermaid_label(shape_labels.get(sid, sid))
        node_id = _mermaid_id(sid, label)
        lines.append(f'    {node_id}["{label}"]')

    # Declare edges
    for from_id, to_id in connections:
        from_label = _mermaid_label(shape_labels.get(from_id, from_id))
        to_label   = _mermaid_label(shape_labels.get(to_id,   to_id))
        from_node  = _mermaid_id(from_id, from_label)
        to_node    = _mermaid_id(to_id,   to_label)
        lines.append(f'    {from_node}["{from_label}"] --> {to_node}["{to_label}"]')

    return "\n".join(lines)


def _parse_page(z: zipfile.ZipFile, page_index: int) -> tuple[dict[str, str], list[tuple[str, str]]]:
    """
    Return (shape_labels, connections) from a single page.
    shape_labels = {shape_id: text_label}
    connections  = [(from_shape_id, to_shape_id)]
    """
    page_file = f"visio/pages/page{page_index + 1}.xml"
    if page_file not in z.namelist():
        return {}, []

    from lxml import etree
    tree = etree.fromstring(z.read(page_file))

    # Build shape ID → text label map
    shape_labels: dict[str, str] = {}
    for shape_el in tree.findall(".//v:Shape", _NS):
        sid = shape_el.get("ID")
        if sid is None:
            continue
        text_parts = []
        for text_el in shape_el.findall(".//v:Text", _NS):
            raw = "".join(text_el.itertext()).strip()
            clean = html.unescape(re.sub(r"\s+", " ", raw)).strip()
            if clean:
                text_parts.append(clean)
        label = " / ".join(text_parts) if text_parts else f"Shape {sid}"
        shape_labels[sid] = label

    # Parse Connect elements
    connections: list[tuple[str, str]] = []
    for conn_el in tree.findall(".//v:Connect", _NS):
        from_id = conn_el.get("FromSheet")
        to_id   = conn_el.get("ToSheet")
        if from_id and to_id and from_id in shape_labels and to_id in shape_labels:
            connections.append((from_id, to_id))

    return shape_labels, connections


def convert(
    source: Path,
    output_root: Path,
    project_root: Path,
    **kwargs,
) -> ConversionResult:
    """Convert VSDX flow diagram to a Mermaid flowchart Markdown file."""
    try:
        from lxml import etree  # noqa: F401
    except ImportError as exc:
        return ConversionResult(
            success=False,
            action="error",
            error=f"Missing dependency: {exc}. Run: pip install lxml",
        )

    out_path = make_output_path(source, output_root, project_root, ".mermaid.md")
    warning = None

    try:
        with zipfile.ZipFile(source, "r") as z:
            # Page names
            page_names: dict[int, str] = {}
            if "visio/pages/pages.xml" in z.namelist():
                from lxml import etree
                tree = etree.fromstring(z.read("visio/pages/pages.xml"))
                for i, pg in enumerate(tree.findall(".//v:Page", _NS)):
                    page_names[i] = pg.get("Name", f"Page {i + 1}")

            page_files = sorted(
                n for n in z.namelist()
                if re.match(r"visio/pages/page\d+\.xml$", n)
            )
            num_pages = len(page_files)

            mermaid_blocks: list[str] = []
            any_connections = False

            for i in range(num_pages):
                shape_labels, connections = _parse_page(z, i)
                page_name = page_names.get(i, f"Page {i + 1}")

                if connections:
                    any_connections = True
                    diagram = _build_mermaid(shape_labels, connections, page_name)
                    mermaid_blocks.append(
                        f"## {page_name}\n\n```mermaid\n{diagram}\n```\n"
                    )
                else:
                    # No connections on this page — bullet list fallback
                    labels = list(shape_labels.values())
                    bullet_list = "\n".join(f"- {lbl}" for lbl in labels) or "_No shapes._"
                    mermaid_blocks.append(
                        f"## {page_name}\n\n"
                        f"_No connection data found — shape labels only:_\n\n"
                        f"{bullet_list}\n"
                    )

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

    if not any_connections:
        warning = "No Connect elements found in any page; Mermaid output contains shape labels only."

    header = f"# Visio Flow Diagram: {source.name}\n\n"
    if warning:
        header += f"> ⚠️ {warning}\n\n"

    body = "\n---\n\n".join(mermaid_blocks)
    out_path.write_text(header + body, encoding="utf-8")

    return ConversionResult(
        success=True,
        output_files=[out_path],
        action="converted",
        warning=warning,
    )
