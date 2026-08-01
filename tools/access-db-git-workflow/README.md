# Access Database Git Workflow (v3 — Round-Trip Baseline)

A foolproof, two-click methodology for collaborating on Microsoft Access databases via Git.

## The Problem

When you export an Access database with MSAccessVCS, it generates massive noise:
- Printer settings (PrtMip, PrtDevMode, PrtDevNames)
- Binary blobs (NameMap, SummaryInfo, DocumentMap)
- Checksums (recalculated every export)
- Font/display properties (DatasheetFontHeight, etc.)

This noise pollutes Git diffs, causes false merge conflicts, and makes collaboration impossible.

## The Solution: Round-Trip Baseline Comparison

Instead of pattern-matching noise (brittle), we **capture it empirically**:

```
START:  Import → Export → Save export as .noise-baseline/ → Restore clean
SAVE:   Export → Compare against baseline → Discard identical files → Commit different ones
```

**Why this works**: Noise is the same on both exports (same machine, same printer). So `user_export - baseline_export = real_changes_only`.

## Quick Start

### 1. Setup a new project

```powershell
.\Setup-Project.ps1 -ProjectPath "C:\Projects\MyAccessApp" -AccessDbName "MyApp.accdb" -GitRemote "https://github.com/your-org/your-repo.git"
```

This creates:
- `workflow/` folder with all scripts
- `.gitignore` and `.gitattributes`
- Desktop shortcuts: **▶ START** and **💾 SAVE**

### 2. Daily workflow

| Step | Action | What happens |
|------|--------|-------------|
| 1 | Double-click **▶ START** | Pulls latest, builds .accdb, captures noise baseline, opens Access |
| 2 | Work in Access | Make your changes (forms, queries, modules, etc.) |
| 3 | Close Access | — |
| 4 | Double-click **💾 SAVE** | Exports, filters noise, shows what changed, commits & pushes |

That's it. No Git knowledge required.

## How It Works (Technical Details)

### Defense in Depth (3 layers)

1. **Round-trip baseline** (primary) — Discards entire files that are identical to the noise baseline
2. **Strip filter** (secondary) — Removes known noise patterns from files with real changes
3. **Validation** (optional) — Classifies remaining diff lines as known-good or suspicious

### Why this beats regex-only approaches

| Problem | Regex approach | Round-trip baseline |
|---------|---------------|-------------------|
| Unknown noise pattern | Misses it | **Auto-handled** (same in both exports) |
| Access version update | Must update patterns | **Just works** |
| Different printers per machine | Need all printer regexes | **Just works** (captured per-machine) |
| Corruption risk | Regex could mangle content | **Zero** (only keep/discard whole files) |
| False positives | Could strip real content | **Impossible** (never modifies content) |

### The one limitation

If Access VCS generates **non-deterministic** content between exports (e.g., random timestamps), those files would be flagged as "real changes." In practice, Access VCS noise IS deterministic per machine/session.

## File Structure

```
your-project/
├── MyApp.accdb          ← Binary DB (gitignored)
├── source/              ← MSAccessVCS text exports (tracked in Git)
│   ├── forms/
│   ├── modules/
│   ├── queries/
│   └── tables/
├── workflow/
│   ├── config.json      ← Project config (paths, options)
│   ├── Start-AccessWork-v3.ps1
│   ├── Save-AccessWork-v3.ps1
│   └── Strip-AccessNoise.ps1
├── .noise-baseline/     ← Captured noise (gitignored)
├── .gitignore
└── .gitattributes
```

## Configuration

Edit `workflow/config.json`:

```json
{
  "accessDbPath": "MyApp.accdb",
  "vcsExportFolder": "source",
  "branch": "main",
  "remoteName": "origin",
  "noiseFilter": {
    "stripPrinterSettings": true,
    "stripNameMap": true,
    "stripChecksums": true,
    "stripSummaryInfo": true,
    "stripDatasheetFont": true
  },
  "git": {
    "pushAfterCommit": true
  }
}
```

## Multi-Developer Setup

Each developer:
1. Clones the repo
2. Runs `Setup-Project.ps1` (or copies the workflow/ folder)
3. Uses their own desktop shortcuts

The noise baseline is per-machine (gitignored), so each developer captures their own machine's noise independently.

## Testing

Run the end-to-end test suite (no Access required):

```powershell
.\tests\Run-E2ETest-v3.ps1
```

Covers: pure noise, real changes + noise, new files, deletions, multi-developer simulation, idempotency, and scale (10 forms / 1 real change).

## Requirements

- PowerShell 5.1+ (Windows built-in)
- Git for Windows
- MSAccessVCS add-in (for actual Access import/export)
- Microsoft Access (for actual development)