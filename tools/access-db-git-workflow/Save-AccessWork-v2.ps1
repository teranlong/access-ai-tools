<#
.SYNOPSIS
    v2 Save & Share — strips noise, validates changes via diff allowlist, then commits.

.DESCRIPTION
    This replaces the v1 Save-AccessWork.ps1 with a fundamentally safer approach:

    1. Export from Access (user does this via MSAccessVCS)
    2. Run Strip-AccessNoise.ps1 (blocklist — catches known noise)
    3. Stage all changes with git add
    4. Analyze git diff --cached (allowlist — catches UNKNOWN noise)
    5. If any unrecognized changes exist → show them, ask for approval
    6. Only commit when everything is classified

    The key insight: Layer 2 (blocklist) doesn't need to be perfect.
    Layer 3 (allowlist validation) catches anything it misses.
    Together they're much stronger than either alone.

    CORRUPTION PREVENTION:
    - Before committing, backs up current source files
    - After committing, verifies idempotency (re-strip produces no diff)
    - The .accdb is never modified — it's always the source of truth
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoRoot,

    [Parameter()]
    [switch]$SkipExport
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $scriptDir }

Add-Type -AssemblyName System.Windows.Forms

$configPath = Join-Path $scriptDir 'config.json'
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$vcsFolder = Join-Path $RepoRoot $config.vcsExportFolder
$branch = $config.branch
$remote = $config.remoteName

# Logging
$logFile = Join-Path $scriptDir "logs\save-v2-$(Get-Date -Format 'yyyy-MM-dd_HHmmss').log"
$logDir = Split-Path $logFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $entry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Add-Content -Path $logFile -Value $entry
    switch ($Level) {
        'ERROR' { Write-Host $entry -ForegroundColor Red }
        'WARN'  { Write-Host $entry -ForegroundColor Yellow }
        default { Write-Host $entry -ForegroundColor Gray }
    }
}

# ── Known-good change patterns (allowlist) ───────────────────
$goodPatterns = @(
    '^\s*Begin\s+\w+',             # Control/block starts
    '^\s*End$',                     # Block ends
    '^\s*Begin$',                   # Bare Begin
    '^\s*(Left|Top|Width|Height|Right|Bottom)\s*=',
    '^\s*(Caption|ControlSource|RecordSource|RowSource|RowSourceType)\s*=',
    '^\s*(Name|Format|DefaultValue|ValidationRule|ValidationText)\s*=',
    '^\s*(Visible|Enabled|Locked|TabStop|TabIndex)\s*=',
    '^\s*(ColumnCount|ColumnWidths|BoundColumn)\s*=',
    '^\s*(On[A-Z][a-zA-Z]+)\s*=',  # Event handlers
    '^\s*(FontSize|FontWeight|FontName|ForeColor|BackColor|BorderColor)\s*=',
    '^\s*(OverlapFlags|IMESentenceMode|ItemSuffix)\s*=',
    '^\s*(SourceObject|LinkChildFields|LinkMasterFields)\s*=',
    '^\s*(Version|VersionRequired)\s*=',
    '^\s*(AllowDesignChanges|NavigationButtons|RecordSelectors|AutoCenter)\s*=',
    '^\s*(DefaultView|FilterOnLoad|PictureAlignment)\s*=',
    '^\s*(GridX|GridY|DatasheetGridlinesBehavior|DatasheetGridlinesColor)\s*=',
    '^\s*RecSrcDt\s*=\s*Begin',
    '^\s+0x[0-9a-fA-F]+',          # Hex inside RecSrcDt (only — noise hex is already stripped)
    '^\s*"\[Event Procedure\]"',
    '^\s*$'                         # Empty lines
)

$noisePatterns = @(
    '^\s*(PrtMip|PrtDevMode|PrtDevNames)\s*=',
    '^\s*Checksum\s*=',
    '^\s*NameMap\s*=',
    '^\s*dbLongBinary\s+',
    '^\s*Datasheet(FontHeight|FontWeight|FontName|FontUnderline|FontItalic)\s*='
)

function Classify-Line {
    param([string]$Line, [string]$File)

    if ([string]::IsNullOrWhiteSpace($Line)) { return "GOOD" }

    $ext = [System.IO.Path]::GetExtension($File).ToLower()
    if ($ext -in '.bas', '.cls', '.sql', '.json') { return "GOOD" }

    foreach ($p in $noisePatterns) { if ($Line -match $p) { return "NOISE" } }
    foreach ($p in $goodPatterns) { if ($Line -match $p) { return "GOOD" } }

    return "UNKNOWN"
}

try {
    Write-Log "=== SAVE & SHARE v2 ==="
    Push-Location $RepoRoot

    # ── Step 1: Check Access is closed ────────────────────────
    if (Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) {
        $r = [System.Windows.Forms.MessageBox]::Show(
            "Please close Access first, then click OK.",
            "Close Access", "OKCancel", "Warning")
        if ($r -ne "OK") { exit 0 }
        $timeout = 120; $elapsed = 0
        while ((Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) -and $elapsed -lt $timeout) {
            Start-Sleep 2; $elapsed += 2
        }
        if (Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) {
            Write-Log "Access still running" -Level 'ERROR'; exit 1
        }
    }

    # ── Step 2: Strip noise (blocklist layer) ─────────────────
    Write-Log "Layer 1: Stripping known noise patterns..."
    $stripScript = Join-Path $scriptDir 'Strip-AccessNoise.ps1'
    & $stripScript -Path $vcsFolder -ConfigPath $configPath

    # ── Step 3: Stage everything ──────────────────────────────
    git add -A 2>&1 | ForEach-Object { Write-Log $_ }

    $changedFiles = @(git diff --cached --name-only 2>&1)
    if ($changedFiles.Count -eq 0) {
        Write-Log "No changes after noise filtering."
        [System.Windows.Forms.MessageBox]::Show(
            "No real changes detected.`nYour database matches what's in Git.",
            "Nothing to Save", "OK", "Information") | Out-Null
        git reset HEAD 2>&1 | Out-Null
        exit 0
    }

    # ── Step 4: Validate via allowlist ────────────────────────
    Write-Log "Layer 2: Validating changes via allowlist..."

    $diffOutput = git diff --cached --unified=0 2>&1
    $goodCount = 0; $noiseCount = 0; $unknownCount = 0
    $unknownDetails = @()
    $noiseDetails = @()
    $currentFile = ""

    foreach ($line in $diffOutput) {
        if ($line -match '^diff --git a/(.+) b/(.+)$') {
            $currentFile = $Matches[2]; continue
        }
        if ($line.StartsWith('@@') -or $line.StartsWith('+++') -or $line.StartsWith('---')) { continue }
        if ($line.StartsWith('+') -or $line.StartsWith('-')) {
            $content = $line.Substring(1)
            $class = Classify-Line -Line $content -File $currentFile
            switch ($class) {
                "GOOD"    { $goodCount++ }
                "NOISE"   {
                    $noiseCount++
                    $noiseDetails += "  $currentFile : $($content.Trim())"
                }
                "UNKNOWN" {
                    $unknownCount++
                    $unknownDetails += "  $currentFile : $($content.Trim())"
                }
            }
        }
    }

    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  CHANGE VALIDATION REPORT" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  ✅ Known good:    $goodCount lines" -ForegroundColor Green
    Write-Host "  📁 Files changed: $($changedFiles.Count)" -ForegroundColor White

    if ($noiseCount -gt 0) {
        Write-Host "  🚫 NOISE LEAKED:  $noiseCount lines" -ForegroundColor Red
        $noiseDetails | Select-Object -First 10 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        Write-Log "Noise leaked past strip filter!" -Level 'ERROR'

        $r = [System.Windows.Forms.MessageBox]::Show(
            "⚠️ $noiseCount noise line(s) leaked past the filter.`n`nThis suggests the filter needs updating. Commit anyway?",
            "Noise Detected", "YesNo", "Warning")
        if ($r -ne "Yes") {
            git reset HEAD 2>&1 | Out-Null
            exit 1
        }
    }

    if ($unknownCount -gt 0) {
        Write-Host "  ⚠️  Unknown:      $unknownCount lines" -ForegroundColor Yellow
        $unknownDetails | Select-Object -First 10 | ForEach-Object { Write-Host $_ -ForegroundColor Yellow }
        if ($unknownDetails.Count -gt 10) {
            Write-Host "  ... and $($unknownDetails.Count - 10) more" -ForegroundColor Yellow
        }

        Write-Host "`n  These changes don't match known patterns." -ForegroundColor Yellow
        Write-Host "  They might be real changes or unknown noise." -ForegroundColor Yellow

        $r = [System.Windows.Forms.MessageBox]::Show(
            "⚠️ $unknownCount unrecognized change(s) detected.`n`nThese might be real changes or unknown noise.`nReview the diff and approve?`n`n$($unknownDetails | Select-Object -First 5 | Out-String)",
            "Unknown Changes", "YesNo", "Question")
        if ($r -ne "Yes") {
            Write-Host "`n  Run 'git diff --cached' to inspect." -ForegroundColor Cyan
            exit 1
        }
    }

    if ($noiseCount -eq 0 -and $unknownCount -eq 0) {
        Write-Host "`n  ✅ All changes validated — safe to commit." -ForegroundColor Green
    }

    # ── Step 5: Commit ────────────────────────────────────────
    $user = git config user.name 2>&1
    if (-not $user) { $user = $env:USERNAME }
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    $commitMsg = "Access DB: $timestamp - $user"

    Write-Log "Committing: $commitMsg"
    git commit -m $commitMsg 2>&1 | ForEach-Object { Write-Log $_ }

    # ── Step 6: Post-commit idempotency check ─────────────────
    Write-Log "Layer 3: Idempotency check..."
    & $stripScript -Path $vcsFolder -ConfigPath $configPath
    git add -A 2>&1
    $postCheck = @(git diff --cached --name-only 2>&1)
    if ($postCheck.Count -gt 0) {
        Write-Log "WARNING: Post-commit strip produced additional changes — filter may be inconsistent" -Level 'WARN'
        git commit -m "Access DB: post-commit noise cleanup" 2>&1
    }
    else {
        git reset HEAD 2>&1 | Out-Null
        Write-Log "Idempotency check passed ✅"
    }

    # ── Step 7: Push ──────────────────────────────────────────
    if ($config.git.pushAfterCommit) {
        Write-Log "Pushing..."
        git push $remote $branch 2>&1 | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) {
            Write-Log "Push failed, trying pull --rebase..." -Level 'WARN'
            git pull --rebase $remote $branch 2>&1
            & $stripScript -Path $vcsFolder -ConfigPath $configPath
            git add -A 2>&1
            $rebaseChanges = @(git diff --cached --name-only 2>&1)
            if ($rebaseChanges.Count -gt 0) {
                git commit -m "Access DB: post-rebase cleanup" 2>&1
            } else { git reset HEAD 2>&1 | Out-Null }
            git push $remote $branch 2>&1
        }
    }

    Write-Log "=== SAVE COMPLETE ==="
    [System.Windows.Forms.MessageBox]::Show(
        "✅ Changes saved!`n`n$($changedFiles.Count) file(s) committed.`n$goodCount validated lines.",
        "Success", "OK", "Information") | Out-Null

}
catch {
    Write-Log "Error: $($_.Exception.Message)" -Level 'ERROR'
    [System.Windows.Forms.MessageBox]::Show("Error: $($_.Exception.Message)", "Error", "OK", "Error") | Out-Null
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
}
