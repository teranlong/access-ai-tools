#!/usr/bin/env python3
"""
catalog.py - Access Migration Project File Cataloger

Scans a project folder and produces a files.json inventory with file metadata,
AI agent capability classification, and proposed conversion format for each file.

Usage:
    python catalog.py <project_directory> [--output-dir <path>] [--skip <name> ...]
                      [--charts]

Output:
    agent-data/project-reports/access-migration-catalog/v{VERSION}/{project-name}/files.json
    (relative to the repo root, computed from the script's location)

With --charts, also writes PNG visualizations to the same output directory:
    chart-phase-count.png   — treemap: file count by migration phase
    chart-capability-pie.png — pie: files by AI agent capability
    chart-extension-bar.png — bar: files by extension
    chart-size-map.png      — treemap: files sized by bytes (SpaceSniffer-style)

Requires for --charts:
    pip install matplotlib squarify
    (squarify is optional; bar/pie fallbacks are used if it is not installed)
"""

import argparse
import json
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

VERSION = "1.1.0"

# ---------------------------------------------------------------------------
# Extension → (agent_capability, proposed_conversion)
#
# agent_capability values:
#   native      - Claude reads the file directly as text
#   vision      - Claude reads via image rendering (multimodal)
#   structured  - Parseable via library (openpyxl, csv) into structured data
#   binary      - Opaque binary; requires external conversion before AI use
#   unsupported - No viable path to AI-readable form without specialized tooling
# ---------------------------------------------------------------------------
CAPABILITY_MAP: dict[str, tuple[str, str]] = {
    ".accdb":       ("binary",      "schema-export"),
    ".mdb":         ("binary",      "schema-export"),
    ".docx":        ("native",      "markdown"),
    ".doc":         ("native",      "markdown"),
    ".xlsx":        ("structured",  "csv-or-markdown-table"),
    ".xls":         ("structured",  "csv-or-markdown-table"),
    ".pdf":         ("vision",      "markdown"),
    ".png":         ("vision",      "keep-as-reference"),
    ".jpg":         ("vision",      "keep-as-reference"),
    ".jpeg":        ("vision",      "keep-as-reference"),
    ".bmp":         ("vision",      "keep-as-reference"),
    ".svg":         ("native",      "keep-as-is"),
    ".vsdx":        ("binary",      "png-export"),
    ".vsd":         ("binary",      "png-export"),
    ".excalidraw":  ("native",      "keep-as-is"),
    ".fig":         ("binary",      "figma-api-or-export"),
    ".bacpac":      ("binary",      "sql-server-restore"),
    ".bas":         ("native",      "vba-to-csharp"),
    ".cls":         ("native",      "vba-to-csharp"),
    ".sql":         ("native",      "keep-as-is"),
    ".xml":         ("native",      "keep-as-is"),
    ".md":          ("native",      "keep-as-is"),
    ".txt":         ("native",      "keep-as-is"),
    ".csv":         ("structured",  "keep-as-is"),
    ".rtf":         ("native",      "markdown"),
    ".xcf":         ("binary",      "png-export"),
    ".zip":         ("binary",      "extract-and-catalog"),
    ".json":        ("native",      "keep-as-is"),
    ".pbix":        ("binary",      "unsupported"),
    ".mp4":         ("binary",      "transcription"),
    ".mov":         ("binary",      "transcription"),
    ".avi":         ("binary",      "transcription"),
    ".pptx":        ("native",      "markdown"),
    ".ppt":         ("native",      "markdown"),
    ".html":        ("native",      "keep-as-is"),
    ".htm":         ("native",      "keep-as-is"),
    ".css":         ("native",      "keep-as-is"),
    ".js":          ("native",      "keep-as-is"),
    ".ts":          ("native",      "keep-as-is"),
    ".py":          ("native",      "keep-as-is"),
    ".ps1":         ("native",      "keep-as-is"),
    ".sh":          ("native",      "keep-as-is"),
    ".bat":         ("native",      "keep-as-is"),
    ".cmd":         ("native",      "keep-as-is"),
}

# Directories to skip entirely (case-insensitive match against each path part)
DEFAULT_SKIP_DIRS: set[str] = {
    ".claude", ".agents", "_claudeartifacts", "__pycache__", ".git", "node_modules"
}

# File name prefixes to skip (Office temp lock files, etc.)
DEFAULT_SKIP_PREFIXES: tuple[str, ...] = ("~$",)

# ---------------------------------------------------------------------------
# Phase classification — folder-name heuristics
# ---------------------------------------------------------------------------
PHASE_FOLDER_MAP: dict[str, str] = {
    "functional specifications": "Design-Requirements",
    "sketches":                  "Design-Visual",
    "testing":                   "Q/A",
    "architectural framework":   "Planning",
    "access development":        "Project-Origin",
    "design meeting transcripts":"Design-Requirements",
    "build resources":           "Engineering-Backend",
    "client resources":          "Project-Origin",
}

PHASE_ORDER: list[str] = [
    "Project-Origin",
    "Planning",
    "Design-Requirements",
    "Design-Visual",
    "Engineering-Frontend",
    "Engineering-Backend",
    "Q/A",
    "Unknown",
]

PHASE_COLORS: dict[str, str] = {
    "Project-Origin":       "#E74C3C",
    "Planning":             "#F39C12",
    "Design-Requirements":  "#3498DB",
    "Design-Visual":        "#9B59B6",
    "Engineering-Frontend": "#2ECC71",
    "Engineering-Backend":  "#1ABC9C",
    "Q/A":                  "#E67E22",
    "Unknown":              "#95A5A6",
}

CAPABILITY_COLORS: dict[str, str] = {
    "native":      "#2ECC71",
    "vision":      "#9B59B6",
    "structured":  "#3498DB",
    "binary":      "#E74C3C",
    "unsupported": "#95A5A6",
}


def classify(extension: str) -> tuple[str, str]:
    """Return (agent_capability, proposed_conversion) for a given file extension."""
    return CAPABILITY_MAP.get(extension.lower(), ("unsupported", "manual-review"))


def classify_phase(relative_path: str, extension: str) -> str:
    """Heuristic phase classification based on folder names in the relative path."""
    parts = Path(relative_path).parts

    # Walk all folder segments (exclude the filename at the end)
    for part in parts[:-1]:
        part_lower = part.lower()
        for key, phase in PHASE_FOLDER_MAP.items():
            if key in part_lower:
                return phase

    # Root-level file (only one path segment = just the filename)
    if len(parts) == 1:
        ext_lower = extension.lower()
        if ext_lower in (".accdb", ".mdb", ".bas", ".cls", ".zip"):
            return "Project-Origin"
        if ext_lower in (".sql", ".bacpac"):
            return "Engineering-Backend"

    return "Unknown"


def scan_project(project_path: Path, skip_dirs: set[str]) -> list[dict]:
    """Walk the project directory and collect metadata for every file."""
    files: list[dict] = []

    for item in sorted(project_path.rglob("*")):
        if not item.is_file():
            continue

        # Skip if any segment of the path matches a skip directory (case-insensitive)
        path_parts_lower = {p.lower() for p in item.parts}
        if path_parts_lower & skip_dirs:
            continue

        # Skip Office lock files and other unwanted prefixes
        if item.name.startswith(DEFAULT_SKIP_PREFIXES):
            continue

        # Skip the Windows reserved device name "nul" (appears as a file in some repos)
        if item.name.lower() == "nul":
            continue

        ext = item.suffix.lower()
        cap, conv = classify(ext)

        rel = item.relative_to(project_path)
        parent_name = rel.parent.name if str(rel.parent) != "." else "."

        try:
            stat = item.stat()
            size_bytes = stat.st_size
            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds")
        except OSError:
            size_bytes = -1
            last_modified = ""

        files.append({
            "file_name": item.name,
            "extension": ext if ext else "",
            "relative_path": rel.as_posix(),
            "parent_folder": parent_name,
            "size_bytes": size_bytes,
            "last_modified": last_modified,
            "agent_capability": cap,
            "proposed_conversion": conv,
        })

    return files


def resolve_output_dir(args_output_dir: str | None, project_name: str) -> Path:
    """Compute the output directory relative to the repo root."""
    if args_output_dir:
        return Path(args_output_dir).resolve()

    # Script lives at: <repo-root>/.agents/skills/access-migration-catalog/catalog.py
    # Walk up 3 levels to reach the repo root.
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent.parent
    return repo_root / "agent-data" / "project-reports" / "access-migration-catalog" / f"v{VERSION}" / project_name


# ---------------------------------------------------------------------------
# Chart generation
# ---------------------------------------------------------------------------

def generate_charts(file_records: list[dict], output_dir: Path, project_name: str) -> None:
    """Generate PNG charts visualizing the file inventory."""

    # --- dependency check ---------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print(
            "ERROR: matplotlib is required for --charts.\n"
            "       Install with: pip install matplotlib",
            file=sys.stderr,
        )
        return

    try:
        import squarify
        has_squarify = True
    except ImportError:
        has_squarify = False
        print(
            "Note: squarify not installed — treemap charts will use bar charts instead.\n"
            "      Install with: pip install squarify",
            file=sys.stderr,
        )

    # --- annotate records with phase ----------------------------------------
    records = [
        {**f, "phase": classify_phase(f["relative_path"], f["extension"])}
        for f in file_records
    ]

    charts_written: list[Path] = []

    def save(fig, name: str) -> None:
        path = output_dir / name
        fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
        plt.close(fig)
        charts_written.append(path)

    # -------------------------------------------------------------------------
    # Chart 1 — File count by Phase
    #   treemap (squarify) or horizontal bar fallback
    # -------------------------------------------------------------------------
    phase_counts = Counter(r["phase"] for r in records)
    phase_labels = [p for p in PHASE_ORDER if phase_counts.get(p, 0) > 0]
    phase_values = [phase_counts[p] for p in phase_labels]
    phase_colors_list = [PHASE_COLORS.get(p, "#95A5A6") for p in phase_labels]

    fig, ax = plt.subplots(figsize=(12, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    if has_squarify:
        squarify.plot(
            sizes=phase_values,
            label=[
                f"{p}\n{v} file{'s' if v != 1 else ''}"
                for p, v in zip(phase_labels, phase_values)
            ],
            color=phase_colors_list,
            alpha=0.88,
            ax=ax,
            text_kwargs={"fontsize": 11, "fontweight": "bold", "color": "white"},
            pad=2,
        )
        ax.axis("off")
    else:
        bars = ax.barh(phase_labels[::-1], phase_values[::-1],
                       color=phase_colors_list[::-1], height=0.6)
        for bar, val in zip(bars, phase_values[::-1]):
            ax.text(
                bar.get_width() + 0.08,
                bar.get_y() + bar.get_height() / 2,
                str(val),
                va="center", fontsize=11, fontweight="bold", color="#2C3E50",
            )
        ax.set_xlabel("Number of Files", fontsize=12)
        ax.set_xlim(0, max(phase_values) * 1.18)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", labelsize=11)

    ax.set_title(f"{project_name} — Files by Phase", fontsize=16, fontweight="bold", pad=16)
    save(fig, "chart-phase-count.png")

    # -------------------------------------------------------------------------
    # Chart 2 — Agent Capability (pie)
    # -------------------------------------------------------------------------
    cap_order = ["native", "vision", "structured", "binary", "unsupported"]
    cap_counts = Counter(r["agent_capability"] for r in records)
    cap_labels = [c for c in cap_order if cap_counts.get(c, 0) > 0]
    cap_values = [cap_counts[c] for c in cap_labels]
    cap_colors_list = [CAPABILITY_COLORS.get(c, "#BDC3C7") for c in cap_labels]

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    total_files = sum(cap_values)
    _pie_result = ax.pie(
        cap_values,
        labels=None,
        colors=cap_colors_list,
        autopct=lambda p: f"{p:.1f}%\n({int(round(p * total_files / 100))})",
        startangle=140,
        pctdistance=0.72,
        wedgeprops={"linewidth": 1.5, "edgecolor": "white"},
    )
    autotexts = _pie_result[2] if len(_pie_result) == 3 else []
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")

    legend_patches = [
        mpatches.Patch(color=c, label=f"{label} ({v})")
        for c, label, v in zip(cap_colors_list, cap_labels, cap_values)
    ]
    ax.legend(
        handles=legend_patches,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.06),
        ncol=3,
        fontsize=11,
        frameon=False,
    )
    ax.set_title(f"{project_name} — Files by Agent Capability",
                 fontsize=16, fontweight="bold", pad=16)
    save(fig, "chart-capability-pie.png")

    # -------------------------------------------------------------------------
    # Chart 3 — File count by Extension (horizontal bar, top 15)
    # -------------------------------------------------------------------------
    ext_counts = Counter(
        r["extension"] if r["extension"] else "(none)" for r in records
    )
    top_exts = [e for e, _ in ext_counts.most_common(15)]
    top_values = [ext_counts[e] for e in top_exts]
    bar_colors = [
        CAPABILITY_COLORS.get(classify(e if e != "(none)" else "")[0], "#BDC3C7")
        for e in top_exts
    ]

    fig, ax = plt.subplots(figsize=(11, max(5, len(top_exts) * 0.52 + 2)))
    fig.patch.set_facecolor("#F8F9FA")
    ax.set_facecolor("#F8F9FA")

    bars = ax.barh(top_exts[::-1], top_values[::-1],
                   color=bar_colors[::-1], height=0.6)
    for bar, val in zip(bars, top_values[::-1]):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            str(val),
            va="center", fontsize=11, fontweight="bold", color="#2C3E50",
        )
    ax.set_xlabel("Number of Files", fontsize=12)
    ax.set_xlim(0, max(top_values) * 1.15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", labelsize=11)

    # Legend showing capability → color mapping
    seen: set[str] = set()
    legend_patches = []
    for ext, color in zip(top_exts, bar_colors):
        cap = classify(ext if ext != "(none)" else "")[0]
        if cap not in seen:
            legend_patches.append(mpatches.Patch(color=color, label=cap))
            seen.add(cap)
    ax.legend(handles=legend_patches, loc="lower right", fontsize=10, frameon=False)

    ax.set_title(f"{project_name} — Files by Extension",
                 fontsize=16, fontweight="bold", pad=16)
    save(fig, "chart-extension-bar.png")

    # -------------------------------------------------------------------------
    # Chart 4 — Size Map (SpaceSniffer-style treemap, area = bytes)
    #   Each individual file is one rectangle; colored by phase.
    #   Falls back to a top-20 horizontal bar if squarify is not installed.
    # -------------------------------------------------------------------------
    size_records = sorted(
        [r for r in records if r["size_bytes"] > 0],
        key=lambda r: r["size_bytes"],
        reverse=True,
    )

    def fmt_size(b: int) -> str:
        if b >= 1_048_576:
            return f"{b / 1_048_576:.1f} MB"
        if b >= 1024:
            return f"{b / 1024:.0f} KB"
        return f"{b} B"

    def short_name(name: str, max_len: int = 20) -> str:
        stem = Path(name).stem
        return (stem[: max_len - 1] + "…") if len(stem) > max_len else stem

    if size_records and has_squarify:
        sizes = [r["size_bytes"] for r in size_records]
        colors = [PHASE_COLORS.get(r["phase"], "#95A5A6") for r in size_records]
        labels = [
            f"{short_name(r['file_name'])}\n{fmt_size(r['size_bytes'])}"
            for r in size_records
        ]

        fig, ax = plt.subplots(figsize=(18, 11))
        fig.patch.set_facecolor("#0D1117")
        ax.set_facecolor("#0D1117")

        squarify.plot(
            sizes=sizes,
            label=labels,
            color=colors,
            alpha=0.88,
            ax=ax,
            text_kwargs={"fontsize": 7.5, "color": "white"},
            pad=1.5,
        )
        ax.axis("off")

        # Phase legend (only phases present in this chart)
        present_phases = sorted(
            {r["phase"] for r in size_records},
            key=lambda p: PHASE_ORDER.index(p) if p in PHASE_ORDER else 99,
        )
        legend_patches = [
            mpatches.Patch(color=PHASE_COLORS.get(p, "#95A5A6"), label=p)
            for p in present_phases
        ]
        ax.legend(
            handles=legend_patches,
            loc="lower right",
            fontsize=10,
            frameon=True,
            facecolor="#1C2833",
            edgecolor="#566573",
            labelcolor="white",
        )
        ax.set_title(
            f"{project_name} — File Size Map   (area = file size)",
            fontsize=16, fontweight="bold", color="white", pad=16,
        )
        save(fig, "chart-size-map.png")

    elif size_records:
        # Fallback: top-20 files by size as a horizontal bar chart
        top = size_records[:20]
        names = [short_name(r["file_name"], 35) for r in top]
        sizes_mb = [r["size_bytes"] / 1_048_576 for r in top]
        colors = [PHASE_COLORS.get(r["phase"], "#95A5A6") for r in top]

        fig, ax = plt.subplots(figsize=(12, max(5, len(names) * 0.48 + 2)))
        fig.patch.set_facecolor("#F8F9FA")
        ax.set_facecolor("#F8F9FA")

        bars = ax.barh(names[::-1], sizes_mb[::-1], color=colors[::-1], height=0.6)
        for bar, val in zip(bars, sizes_mb[::-1]):
            ax.text(
                bar.get_width() + 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.2f} MB",
                va="center", fontsize=9, color="#2C3E50",
            )
        ax.set_xlabel("File Size (MB)", fontsize=12)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="y", labelsize=9)
        ax.set_title(f"{project_name} — Files by Size (Top 20)",
                     fontsize=16, fontweight="bold", pad=16)
        save(fig, "chart-size-map.png")

    # -------------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------------
    print(f"\nCharts written to: {output_dir}")
    for p in charts_written:
        print(f"  {p.name}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Catalog files in an Access DB migration project folder."
    )
    parser.add_argument(
        "project_dir",
        help="Path to the project directory to scan.",
    )
    parser.add_argument(
        "--output-dir",
        help="Override the output directory for files.json (and charts).",
        default=None,
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        default=[],
        help="Additional directory names to skip (case-insensitive).",
    )
    parser.add_argument(
        "--charts",
        action="store_true",
        help=(
            "Generate PNG charts in the output directory. "
            "Requires: pip install matplotlib squarify"
        ),
    )
    args = parser.parse_args()

    project_path = Path(args.project_dir).resolve()
    if not project_path.is_dir():
        print(f"ERROR: Directory not found: {project_path}", file=sys.stderr)
        sys.exit(1)

    project_name = project_path.name
    skip_dirs = DEFAULT_SKIP_DIRS | {s.lower() for s in (args.skip or [])}

    file_records = scan_project(project_path, skip_dirs)

    output = {
        "skill_version": VERSION,
        "project_name": project_name,
        "project_path": str(project_path),
        "scanned_at": datetime.now().isoformat(timespec="seconds"),
        "total_files": len(file_records),
        "files": file_records,
    }

    out_dir = resolve_output_dir(args.output_dir, project_name)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "files.json"
    out_file.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Catalog written to: {out_file}")
    print(f"Total files scanned: {len(file_records)}")

    if args.charts:
        generate_charts(file_records, out_dir, project_name)


if __name__ == "__main__":
    main()
