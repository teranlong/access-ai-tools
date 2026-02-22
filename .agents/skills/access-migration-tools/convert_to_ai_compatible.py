#!/usr/bin/env python3
"""
convert_to_ai_compatible.py — AI-Compatible File Conversion Pipeline

Converts every file in a SampleProject folder to an AI-readable format,
mirroring the directory structure under agent-data/ai-compatible/v{VERSION}/.

Never modifies original files. Never crashes the run due to a single file failure.

Usage:
    python convert_to_ai_compatible.py <project_directory> [--output-dir <path>] [--force]

    <project_directory>   Path to the SampleProject to convert
    --output-dir <path>   Override the default output location
    --force               Re-convert files even if output is newer than source

Output:
    agent-data/ai-compatible/v{VERSION}/{project-name}/
        {mirrored paths}...
        ai-compatible-summary.md
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Version — update here and the output path changes automatically
# ---------------------------------------------------------------------------
VERSION = "1.3.0"

# ---------------------------------------------------------------------------
# Locate the converters package (same directory as this script)
# ---------------------------------------------------------------------------
_SKILL_DIR = Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

import converters
from converters.base import ConversionResult, format_size


# ---------------------------------------------------------------------------
# Skip dirs (same as catalog.py)
# ---------------------------------------------------------------------------
_SKIP_DIRS: set[str] = {
    ".claude", ".agents", "_claudeartifacts", "__pycache__", ".git", "node_modules",
}
_SKIP_PREFIXES: tuple[str, ...] = ("~$",)

# Extensions/proposed-conversions that catalog marks as already-native
_NATIVE_SKIP_PROPOSED: set[str] = {"keep-as-is", "keep-as-reference"}


# ---------------------------------------------------------------------------
# File scanning (direct — does NOT require a prior catalog run)
# ---------------------------------------------------------------------------

def scan_project(project_path: Path) -> list[dict]:
    """Walk the project and return file records compatible with converters.dispatch()."""
    from converters.base import SKIP_CONVERSIONS

    # Try to load the pre-built files.json for richer metadata (proposed_conversion)
    files_json = _find_files_json(project_path)
    if files_json:
        print(f"  Using catalog: {files_json}")
        with files_json.open(encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("files", data) if isinstance(data, dict) else data
        # Filter to files that actually exist in the project
        matched = [r for r in records if (project_path / r["relative_path"]).exists()]
        if matched:
            return matched
        # Catalog paths don't match this project root — fall through to direct scan
        print("  Catalog paths don't match project root — falling back to direct scan.")

    # Fall back to direct scan
    print("  No catalog found — scanning directly.")
    from catalog import CAPABILITY_MAP, DEFAULT_SKIP_PREFIXES

    records: list[dict] = []
    for item in sorted(project_path.rglob("*")):
        if not item.is_file():
            continue
        parts_lower = {p.lower() for p in item.parts}
        if parts_lower & _SKIP_DIRS:
            continue
        if item.name.startswith(_SKIP_PREFIXES):
            continue
        if item.name.lower() == "nul":
            continue

        ext = item.suffix.lower()
        cap, conv = CAPABILITY_MAP.get(ext, ("unsupported", "manual-review"))
        rel = item.relative_to(project_path)

        try:
            size_bytes = item.stat().st_size
        except OSError:
            size_bytes = -1

        records.append({
            "file_name": item.name,
            "extension": ext,
            "relative_path": rel.as_posix(),
            "parent_folder": rel.parent.name if str(rel.parent) != "." else ".",
            "size_bytes": size_bytes,
            "agent_capability": cap,
            "proposed_conversion": conv,
        })
    return records


def _find_files_json(project_path: Path) -> Path | None:
    """Locate the latest catalog files.json for this project, if it exists."""
    repo_root = _SKILL_DIR.parent.parent.parent
    catalog_root = repo_root / "agent-data" / "project-reports" / "access-migration-catalog"
    project_name = project_path.name

    # Find the highest-versioned catalog for this project
    best: Path | None = None
    if catalog_root.exists():
        for version_dir in sorted(catalog_root.iterdir(), reverse=True):
            candidate = version_dir / project_name / "files.json"
            if candidate.exists():
                best = candidate
                break
    return best


# ---------------------------------------------------------------------------
# Idempotency check
# ---------------------------------------------------------------------------

def _is_up_to_date(source: Path, output_files: list[Path]) -> bool:
    """Return True if all output files exist and are newer than source."""
    if not output_files:
        return False
    try:
        src_mtime = source.stat().st_mtime
        return all(
            out.exists() and out.stat().st_mtime >= src_mtime
            for out in output_files
        )
    except OSError:
        return False


def _expected_output_paths(record: dict, project_root: Path, output_root: Path) -> list[Path]:
    """
    Cheaply guess what output files a converter would produce.
    Used only for idempotency checks; misses multi-file outputs, but that's fine
    — a partial miss just causes a re-run which is safe.
    """
    from converters.base import make_output_path
    ext = record.get("extension", "").lower()
    source = project_root / record["relative_path"]

    if ext in {".bas", ".cls"}:
        rel = source.relative_to(project_root)
        return [output_root / rel]
    if ext == ".pdf":
        return [make_output_path(source, output_root, project_root, ".md")]
    if ext == ".vsdx":
        return [make_output_path(source, output_root, project_root, ".md")]
    if ext in (".docx", ".doc", ".xlsx", ".xls", ".rtf", ".pptx", ".ppt", ".accdb", ".mdb"):
        return [make_output_path(source, output_root, project_root, ".md")]
    if ext in (".zip", ".fig", ".bacpac", ".pbix", ".mp4", ".mov", ".avi", ".xcf", ".vsd"):
        return [make_output_path(source, output_root, project_root, ".md")]
    return []


# ---------------------------------------------------------------------------
# Error stub writer (safety net for unexpected converter crashes)
# ---------------------------------------------------------------------------

def _write_error_stub(source: Path, output_root: Path, project_root: Path, exc: Exception) -> Path:
    """Write a minimal error stub when a converter crashes unexpectedly."""
    from converters.base import make_output_path
    out_path = make_output_path(source, output_root, project_root, ".error.md")
    tb = traceback.format_exc()
    out_path.write_text(
        f"# Conversion Error: {source.name}\n\n"
        f"**Error:** `{exc}`\n\n"
        f"```\n{tb[:2000]}\n```\n",
        encoding="utf-8",
    )
    return out_path


# ---------------------------------------------------------------------------
# Console formatting
# ---------------------------------------------------------------------------

_ACTION_WIDTH = 12

def _action_label(action: str) -> str:
    return f"[{action.upper():<{_ACTION_WIDTH - 2}}]"


# ---------------------------------------------------------------------------
# Summary report
# ---------------------------------------------------------------------------

def _write_summary(
    output_root: Path,
    project_path: Path,
    project_name: str,
    run_log: list[dict],
) -> Path:
    """Write ai-compatible-summary.md to the output root."""

    # Tally counters
    converted = [r for r in run_log if r["action"] == "converted"]
    copied    = [r for r in run_log if r["action"] == "copied"]
    stubbed   = [r for r in run_log if r["action"] == "stubbed"]
    skipped   = [r for r in run_log if r["action"] == "skipped"]
    errors    = [r for r in run_log if r["action"] == "error"]
    idempotent = [r for r in run_log if r["action"] == "idempotent"]

    # Context decisions (non-trivial entries)
    context_entries = [
        r for r in run_log
        if r.get("context_decision") and "content mode" not in r.get("context_decision", "")
    ]

    now = datetime.now().isoformat(timespec="seconds")
    lines: list[str] = [
        f"# AI-Compatible Conversion Report: {project_name}",
        f"**Tool version:** v{VERSION}",
        f"**Generated:** {now}",
        f"**Source:** `{project_path}`",
        f"**Output:** `{output_root}`",
        "",
        "## Totals",
        "| Metric | Count |",
        "|--------|-------|",
        f"| Total files | {len(run_log)} |",
        f"| Converted | {len(converted)} |",
        f"| Copied verbatim (VBA) | {len(copied)} |",
        f"| Stubbed (manual required) | {len(stubbed)} |",
        f"| Skipped (native format) | {len(skipped)} |",
        f"| Already up-to-date | {len(idempotent)} |",
        f"| Errors | {len(errors)} |",
        "",
    ]

    # Contextual decisions table
    if context_entries:
        lines += [
            "## Contextual Decisions",
            "Files where context detection influenced the conversion mode:",
            "",
            "| File | Detected Context | Reason | Mode Chosen |",
            "|------|-----------------|--------|-------------|",
        ]
        for r in context_entries:
            rel = r["relative_path"]
            ctx = r.get("context", "")
            reason = r.get("context_decision", "")
            mode = r["action"]
            lines.append(f"| `{rel}` | {ctx} | {reason} | {mode} |")
        lines.append("")

    # Converted files
    if converted:
        lines += [
            "## Converted Files",
            "",
            "| File | Output(s) | Warning |",
            "|------|-----------|---------|",
        ]
        for r in converted:
            out_names = ", ".join(f"`{Path(p).name}`" for p in r.get("output_files", []))
            warn = r.get("warning") or ""
            lines.append(f"| `{r['relative_path']}` | {out_names} | {warn} |")
        lines.append("")

    # Copied
    if copied:
        lines += [
            "## Copied Verbatim (VBA Source)",
            "",
            "| File |",
            "|------|",
        ]
        for r in copied:
            lines.append(f"| `{r['relative_path']}` |")
        lines.append("")

    # Stubs
    if stubbed:
        lines += [
            "## Stubbed Files (Manual Action Required)",
            "",
            "| File | Type | Action Required |",
            "|------|------|-----------------|",
        ]
        for r in stubbed:
            ext = Path(r["relative_path"]).suffix
            lines.append(f"| `{r['relative_path']}` | `{ext}` | See stub .md in output |")
        lines.append("")

    # Errors
    if errors:
        lines += [
            "## Errors",
            "",
            "| File | Error |",
            "|------|-------|",
        ]
        for r in errors:
            err = (r.get("error") or "unknown").replace("|", "\\|")[:200]
            lines.append(f"| `{r['relative_path']}` | {err} |")
        lines.append("")

    # Skipped
    if skipped:
        lines += [
            "## Skipped Files (Native Format — No Conversion Needed)",
            "",
        ]
        for r in skipped:
            lines.append(f"- `{r['relative_path']}`")
        lines.append("")

    summary_path = output_root / "ai-compatible-summary.md"
    summary_path.write_text("\n".join(lines), encoding="utf-8")
    return summary_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert project files to AI-compatible formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("project_dir", help="Path to the SampleProject folder")
    parser.add_argument("--output-dir", help="Override default output directory")
    parser.add_argument(
        "--force", action="store_true",
        help="Re-convert files even if output is already up-to-date",
    )
    args = parser.parse_args()

    project_path = Path(args.project_dir).resolve()
    if not project_path.is_dir():
        print(f"ERROR: Not a directory: {project_path}", file=sys.stderr)
        return 1

    project_name = project_path.name

    # Compute output root
    if args.output_dir:
        output_root = Path(args.output_dir).resolve()
    else:
        repo_root = _SKILL_DIR.parent.parent.parent
        output_root = (
            repo_root / "agent-data" / "ai-compatible" / f"v{VERSION}" / project_name
        )

    output_root.mkdir(parents=True, exist_ok=True)

    print(f"\nAccess Migration — AI-Compatible Converter  v{VERSION}")
    print(f"  Project : {project_path}")
    print(f"  Output  : {output_root}")
    print(f"  Force   : {args.force}")
    print()

    # Scan files
    records = scan_project(project_path)
    total = len(records)
    print(f"  Files to process: {total}")
    print()

    run_log: list[dict] = []
    counters: dict[str, int] = {
        "converted": 0, "copied": 0, "stubbed": 0,
        "skipped": 0, "idempotent": 0, "error": 0,
    }

    for i, record in enumerate(records, start=1):
        rel_path = record["relative_path"]
        source = project_path / rel_path
        ext = record.get("extension", "").lower()
        progress = f"({i}/{total})"

        # Idempotency check (skip if --force not set)
        if not args.force:
            expected = _expected_output_paths(record, project_path, output_root)
            if expected and _is_up_to_date(source, expected):
                print(f"  {_action_label('idempotent')} {rel_path}")
                run_log.append({
                    "relative_path": rel_path,
                    "action": "idempotent",
                    "output_files": [str(p) for p in expected],
                })
                counters["idempotent"] += 1
                continue

        # Dispatch to converter
        try:
            result: ConversionResult = converters.dispatch(record, project_path, output_root)
        except Exception as exc:
            # Safety net — should not normally be reached (converters handle their own errors)
            err_stub = _write_error_stub(source, output_root, project_path, exc)
            result = ConversionResult(
                success=False,
                output_files=[err_stub],
                action="error",
                error=str(exc),
            )

        action = result.action
        counters[action] = counters.get(action, 0) + 1

        # Console output
        suffix = f"  [ctx: {result.context_decision}]" if result.context_decision else ""
        warn_tag = f"  [warn: {result.warning[:80]}]" if result.warning else ""
        print(f"  {_action_label(action)} {rel_path}{suffix}{warn_tag}")
        if result.error and action == "error":
            print(f"    ERROR: {result.error[:120]}")

        # Log entry
        run_log.append({
            "relative_path": rel_path,
            "action": action,
            "success": result.success,
            "skipped": result.skipped,
            "context": "",
            "context_decision": result.context_decision,
            "output_files": [str(p) for p in result.output_files],
            "warning": result.warning,
            "error": result.error,
        })

    # Summary report
    print()
    summary_path = _write_summary(output_root, project_path, project_name, run_log)
    print(f"  Report  : {summary_path}")

    # Final totals
    print()
    print("  -- Totals -------------------------------------")
    for label, key in [
        ("Converted", "converted"),
        ("Copied (VBA)", "copied"),
        ("Stubbed", "stubbed"),
        ("Skipped", "skipped"),
        ("Up-to-date", "idempotent"),
        ("Errors", "error"),
    ]:
        print(f"  {label:<20} {counters.get(key, 0)}")
    print(f"  {'Total':<20} {total}")
    print()

    return 0 if counters.get("error", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
