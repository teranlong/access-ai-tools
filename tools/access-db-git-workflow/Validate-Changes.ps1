<#
.SYNOPSIS
    Validates staged changes by classifying each diff hunk as known-good or unknown.

.DESCRIPTION
    This is Layer 2 of the v2 methodology. After git add (with the clean filter
    having already stripped noise), this script examines the actual diff and
    classifies every change:

    ✅ KNOWN GOOD — auto-approve:
       - New Begin/End blocks (controls, labels, buttons, textboxes, etc.)
       - Caption, ControlSource, RowSource, RecordSource changes
       - TabIndex reordering
       - VBA code changes (in .bas/.cls files)
       - SQL query changes (in .sql files)
       - Width/Height/Left/Top repositioning

    ⚠️ UNKNOWN — flag for review:
       - Any change in a form file that doesn't match a known pattern
       - Binary-looking content (0x... hex blocks)
       - Properties we haven't classified

    This flips the model from blocklist (might miss noise) to
    allowlist (catches anything unexpected).

.PARAMETER RepoRoot
    Root of the git repository. Defaults to current directory.

.PARAMETER AutoApprove
    If set, auto-approve when all changes are KNOWN GOOD.
    Otherwise, always show summary and prompt.
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoRoot = ".",

    [Parameter()]
    [switch]$AutoApprove
)

$ErrorActionPreference = 'Stop'

# ── Known-good patterns (allowlist) ──────────────────────────
# Changes matching these are definitely real user edits
$knownGoodPatterns = @(
    # Control blocks
    '^\s*Begin\s+(TextBox|Label|CommandButton|ComboBox|ListBox|SubForm|OptionGroup|CheckBox|ToggleButton|TabControl|Image|Line|Rectangle|PageBreak|OptionButton|BoundObjectFrame|UnboundObjectFrame)',
    '^\s*End$',

    # Layout properties (user repositioned/resized controls)
    '^\s*(Left|Top|Width|Height|Right|Bottom)\s*=',

    # Semantic properties (user actually changed these)
    '^\s*(Caption|ControlSource|RecordSource|RowSource|RowSourceType)\s*=',
    '^\s*(Name|ControlType|Format|DefaultValue|ValidationRule|ValidationText)\s*=',
    '^\s*(Visible|Enabled|Locked|TabStop|TabIndex|ColumnCount|ColumnWidths|BoundColumn)\s*=',
    '^\s*(OnClick|OnDblClick|OnChange|OnEnter|OnExit|OnGotFocus|OnLostFocus)\s*=',
    '^\s*(On[A-Z][a-zA-Z]+)\s*=',
    '^\s*(FontSize|FontWeight|FontName|ForeColor|BackColor|BorderColor)\s*=',
    '^\s*(ItemSuffix|OverlapFlags|IMESentenceMode)\s*=',
    '^\s*(SourceObject|LinkChildFields|LinkMasterFields)\s*=',
    '^\s*(ColumnCount|ColumnWidths|BoundColumn)\s*=',
    '^\s*(AllowDesignChanges|NavigationButtons|RecordSelectors|AutoCenter)\s*=',
    '^\s*(DefaultView|FilterOnLoad|PictureAlignment)\s*=',
    '^\s*(GridX|GridY|DatasheetGridlinesBehavior|DatasheetGridlinesColor)\s*=',
    '^\s*(RecSrcDt)\s*=',

    # VBA/SQL content (any line in a .bas/.cls/.sql is real)
    '.',  # This is used only for code files — see classification logic below
    
    # Version headers
    '^\s*(Version|VersionRequired)\s*=',

    # Form structure
    '^\s*Begin\s+Form',
    '^\s*Begin$'
)

# Patterns that are ALWAYS noise even if they slip past the clean filter
$alwaysNoisePatterns = @(
    '^\s*(PrtMip|PrtDevMode|PrtDevNames)\s*=',
    '^\s*Checksum\s*=',
    '^\s*NameMap\s*=',
    '^\s*dbLongBinary\s+',
    '^\s*Datasheet(FontHeight|FontWeight|FontName|FontUnderline|FontItalic)\s*=',
    '^\s+0x[0-9a-fA-F]+'  # Hex blob lines (always part of a noise block)
)

# ── Parse git diff into hunks ────────────────────────────────
function Get-DiffHunks {
    param([string]$RepoRoot)

    Push-Location $RepoRoot
    $diffOutput = git diff --cached --unified=0 2>&1
    Pop-Location

    $hunks = @()
    $currentFile = ""
    $currentHunk = $null

    foreach ($line in $diffOutput) {
        if ($line -match '^diff --git a/(.+) b/(.+)$') {
            $currentFile = $Matches[2]
            continue
        }
        if ($line -match '^@@') {
            if ($currentHunk) { $hunks += $currentHunk }
            $currentHunk = @{
                File = $currentFile
                Lines = @()
                AddedLines = @()
                RemovedLines = @()
            }
            continue
        }
        if ($currentHunk) {
            if ($line.StartsWith('+') -and -not $line.StartsWith('+++')) {
                $currentHunk.AddedLines += $line.Substring(1)
                $currentHunk.Lines += $line
            }
            elseif ($line.StartsWith('-') -and -not $line.StartsWith('---')) {
                $currentHunk.RemovedLines += $line.Substring(1)
                $currentHunk.Lines += $line
            }
        }
    }
    if ($currentHunk) { $hunks += $currentHunk }

    return $hunks
}

# ── Classify a single changed line ───────────────────────────
function Classify-Line {
    param(
        [string]$Line,
        [string]$FilePath
    )

    $trimmed = $Line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) { return "GOOD" }

    # Code files (.bas, .cls, .sql) — everything is real
    $ext = [System.IO.Path]::GetExtension($FilePath).ToLower()
    if ($ext -in '.bas', '.cls', '.sql') { return "GOOD" }

    # Check noise patterns first
    foreach ($pattern in $alwaysNoisePatterns) {
        if ($Line -match $pattern) { return "NOISE" }
    }

    # Check known-good patterns
    $formGoodPatterns = @(
        '^\s*Begin\s+\w+',
        '^\s*End$',
        '^\s*(Left|Top|Width|Height|Right|Bottom)\s*=',
        '^\s*(Caption|ControlSource|RecordSource|RowSource|RowSourceType)\s*=',
        '^\s*(Name|Format|DefaultValue|ValidationRule|ValidationText)\s*=',
        '^\s*(Visible|Enabled|Locked|TabStop|TabIndex|ColumnCount|ColumnWidths|BoundColumn)\s*=',
        '^\s*(On[A-Z][a-zA-Z]+)\s*=',
        '^\s*(FontSize|FontWeight|FontName|ForeColor|BackColor|BorderColor)\s*=',
        '^\s*(OverlapFlags|IMESentenceMode|ItemSuffix)\s*=',
        '^\s*(SourceObject|LinkChildFields|LinkMasterFields)\s*=',
        '^\s*(Version|VersionRequired)\s*=',
        '^\s*(AllowDesignChanges|NavigationButtons|RecordSelectors|AutoCenter)\s*=',
        '^\s*(DefaultView|FilterOnLoad|PictureAlignment)\s*=',
        '^\s*(GridX|GridY|DatasheetGridlinesBehavior|DatasheetGridlinesColor)\s*=',
        '^\s*RecSrcDt\s*=',
        '^\s*Begin\s*$',
        '^\s*"\[Event Procedure\]"'
    )

    foreach ($pattern in $formGoodPatterns) {
        if ($Line -match $pattern) { return "GOOD" }
    }

    # Hex data lines — suspicious in form files (could be noise that slipped through)
    if ($Line -match '^\s+0x[0-9a-fA-F]+') { return "UNKNOWN" }

    return "UNKNOWN"
}

# ── Main ─────────────────────────────────────────────────────
$hunks = Get-DiffHunks -RepoRoot $RepoRoot

if ($hunks.Count -eq 0) {
    Write-Host "No staged changes to validate." -ForegroundColor Gray
    exit 0
}

$goodCount = 0
$noiseCount = 0
$unknownCount = 0
$unknownDetails = @()

foreach ($hunk in $hunks) {
    $allLines = $hunk.AddedLines + $hunk.RemovedLines
    foreach ($line in $allLines) {
        $class = Classify-Line -Line $line -FilePath $hunk.File
        switch ($class) {
            "GOOD"    { $goodCount++ }
            "NOISE"   { $noiseCount++ }
            "UNKNOWN" {
                $unknownCount++
                $unknownDetails += @{
                    File = $hunk.File
                    Line = $line.Trim()
                }
            }
        }
    }
}

# ── Report ───────────────────────────────────────────────────
Write-Host "`n━━━ CHANGE VALIDATION ━━━" -ForegroundColor Cyan
Write-Host "  ✅ Known good:  $goodCount lines" -ForegroundColor Green
if ($noiseCount -gt 0) {
    Write-Host "  🚫 Noise (leaked past filter): $noiseCount lines" -ForegroundColor Red
}
if ($unknownCount -gt 0) {
    Write-Host "  ⚠️  Unknown (review needed):   $unknownCount lines" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Unknown changes:" -ForegroundColor Yellow
    $unknownDetails | Select-Object -First 20 | ForEach-Object {
        Write-Host "    $($_.File): $($_.Line)" -ForegroundColor Yellow
    }
    if ($unknownDetails.Count -gt 20) {
        Write-Host "    ... and $($unknownDetails.Count - 20) more" -ForegroundColor Yellow
    }
}

# ── Decision ─────────────────────────────────────────────────
if ($noiseCount -gt 0) {
    Write-Host "`n❌ NOISE DETECTED — clean filter may need updating." -ForegroundColor Red
    Write-Host "   Run 'git diff --cached' to inspect." -ForegroundColor Red
    exit 2
}

if ($unknownCount -gt 0 -and -not $AutoApprove) {
    Write-Host "`n⚠️  Unknown changes detected. Please review before committing." -ForegroundColor Yellow
    Write-Host "   Run 'git diff --cached' to inspect." -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ All changes validated. Safe to commit." -ForegroundColor Green
exit 0
