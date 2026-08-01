# Access Database Git Workflow

A foolproof two-click workflow for collaborating on Microsoft Access databases via Git.

## The Problem

When multiple people use MS Access VCS to convert databases between binary (.accdb) and
text-based source control formats, the export generates substantial noise — especially in
forms (printer settings, GUIDs, checksums, binary blobs). This noise pollutes diffs and
causes merge conflicts that have nothing to do with actual changes.

## The Solution

Two desktop icons. Two operations. Everything else is automated.

| Icon | Script | What It Does |
|------|--------|--------------|
| 🟢 **Start Working** | `Start-AccessWork.ps1` | Pulls latest from Git → strips noise → builds .accdb via VCS |
| 🔴 **Save & Share** | `Save-AccessWork.ps1` | Exports from .accdb → strips noise → commits only real changes → pushes |

### Noise Stripping

The `Strip-AccessNoise.ps1` filter automatically removes:
- `PrtMip`, `PrtDevMode`, `PrtDevNames` (printer settings — differ per machine)
- `NameMap` binary blobs
- `dbLongBinary "SummaryInfo"` / `"DocumentMap"` sections
- `Checksum` values that regenerate on every export
- Trailing whitespace and CRLF normalization inconsistencies
- `GUID` fields that regenerate without meaningful change
- `DatasheetFontHeight`, `DatasheetFontWeight` resets

### Git Attributes

A `.gitattributes` file forces consistent line endings and marks binary files so Git
never tries to diff them.

## Setup

1. Copy this folder to your Access database project root (next to your `.accdb` file)
2. Run `Setup-Shortcuts.ps1` — creates desktop icons for Start/Save
3. Configure `config.json` with your project paths

## Requirements

- [MSAccessVCS](https://github.com/joyfullservice/msaccess-vcs-addin) installed in Access
- Git for Windows
- PowerShell 5.1+
- Microsoft Access

## Success Criteria

Multiple developers can independently:
1. Click **Start Working** → get a clean .accdb with latest team changes
2. Make changes in Access (forms, queries, modules, etc.)
3. Click **Save & Share** → only meaningful changes are committed and pushed
4. No merge conflicts from noise. No manual Git operations required.
