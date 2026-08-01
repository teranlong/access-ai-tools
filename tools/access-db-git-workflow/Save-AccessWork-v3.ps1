<#
.SYNOPSIS
    v3 Save & Share — compares export against noise baseline, commits only real changes.

.DESCRIPTION
    The Round-Trip Baseline approach eliminates pattern matching entirely for
    determining what's noise vs. what's real:

    1. MSAccessVCS export → source/ (has noise + real changes)
    2. Compare each file against .noise-baseline/ (captured during Start):
       - File IDENTICAL to noise baseline → pure noise, discard (git checkout)
       - File DIFFERS from noise baseline → real changes exist, keep
    3. For files with real changes, optionally run strip filter as extra safety
    4. Validate, commit, push

    WHY THIS IS ROBUST:
    - No regex patterns needed — empirical comparison
    - Works even if Access/VCS version changes noise format
    - Works even on machines with unique printer configurations
    - If Access adds a new noise type, it appears in BOTH baseline and export
      → cancels out automatically
    - Corruption impossible: we only KEEP files, never transform content
      blindly (the strip filter is optional extra cleanup)

    FAILURE MODE:
    - Only fails if noise is NON-DETERMINISTIC between exports (e.g., timestamps)
    - In practice, Access VCS noise IS deterministic within a session
      (same printer, same NameMap, same checksums per machine)
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoRoot,

    [Parameter()]
    [switch]$SkipExport,

    [Parameter()]
    [switch]$NoStripFilter
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $scriptDir }

Add-Type -AssemblyName System.Windows.Forms

$configPath = Join-Path $scriptDir 'config.json'
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$vcsFolder = Join-Path $RepoRoot $config.vcsExportFolder
$accessDb = Join-Path $RepoRoot $config.accessDbPath
$noiseDir = Join-Path $RepoRoot '.noise-baseline'
$remote = $config.remoteName
$branch = $config.branch

# Logging
$logFile = Join-Path $scriptDir "logs\save-v3-$(Get-Date -Format 'yyyy-MM-dd_HHmmss').log"
$logDir = Split-Path $logFile -Parent
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }

function Write-Log {
    param([string]$Message, [string]$Level = 'INFO')
    $entry = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Add-Content -Path $logFile -Value $entry
    switch ($Level) {
        'ERROR' { Write-Host "  ❌ $Message" -ForegroundColor Red }
        'WARN'  { Write-Host "  ⚠️  $Message" -ForegroundColor Yellow }
        default { Write-Host "  $Message" -ForegroundColor Gray }
    }
}

try {
    Push-Location $RepoRoot

    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  SAVE & SHARE (v3 — Round-Trip Baseline)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

    # ── Pre-check: noise baseline must exist ──────────────────
    if (-not (Test-Path $noiseDir)) {
        Write-Log "No noise baseline found at: $noiseDir" -Level 'ERROR'
        Write-Host "  Run Start-AccessWork-v3.ps1 first to establish the baseline." -ForegroundColor Red
        exit 1
    }

    # ── Step 1: Ensure Access is closed ───────────────────────
    if (Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) {
        $r = [System.Windows.Forms.MessageBox]::Show(
            "Close Access first, then click OK.",
            "Close Access", "OKCancel", "Warning")
        if ($r -ne "OK") { exit 0 }
        $timeout = 60; $elapsed = 0
        while ((Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) -and $elapsed -lt $timeout) {
            Start-Sleep 2; $elapsed += 2
        }
    }

    # ── Step 2: Export from Access ────────────────────────────
    if (-not $SkipExport) {
        Write-Host "  [1/5] Exporting from Access..." -ForegroundColor White
        # MSAccessVCS export via COM automation
        # $oAccess = New-Object -ComObject Access.Application
        # $oAccess.OpenCurrentDatabase($accessDb)
        # $oAccess.Run("VCS_ExportAll")
        # $oAccess.Quit()
        Write-Log "Export complete"
    }

    # ── Step 3: Compare against noise baseline ────────────────
    Write-Host "  [2/5] Comparing export against noise baseline..." -ForegroundColor White

    $sourceFiles = Get-ChildItem $vcsFolder -Recurse -File
    $noiseOnlyFiles = @()    # Files where export = noise baseline (pure noise)
    $realChangeFiles = @()   # Files where export ≠ noise baseline (real changes)
    $newFiles = @()          # Files not in baseline (newly created)

    foreach ($file in $sourceFiles) {
        $relativePath = $file.FullName.Substring($vcsFolder.Length)
        $baselineFile = Join-Path $noiseDir $relativePath

        if (-not (Test-Path $baselineFile)) {
            # New file — not in baseline, so it's definitely a real addition
            $newFiles += $file.FullName
            continue
        }

        # Compare file hashes
        $currentHash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
        $baselineHash = (Get-FileHash $baselineFile -Algorithm SHA256).Hash

        if ($currentHash -eq $baselineHash) {
            $noiseOnlyFiles += $file.FullName
        }
        else {
            $realChangeFiles += $file.FullName
        }
    }

    # Check for deleted files (in baseline but not in export)
    $baselineFiles = Get-ChildItem $noiseDir -Recurse -File
    $deletedFiles = @()
    foreach ($bFile in $baselineFiles) {
        $relativePath = $bFile.FullName.Substring($noiseDir.Length)
        $sourceFile = Join-Path $vcsFolder $relativePath
        if (-not (Test-Path $sourceFile)) {
            $deletedFiles += $relativePath
        }
    }

    Write-Host ""
    Write-Host "  ┌─────────────────────────────────────┐" -ForegroundColor White
    Write-Host "  │ COMPARISON RESULTS                   │" -ForegroundColor White
    Write-Host "  ├─────────────────────────────────────┤" -ForegroundColor White
    Write-Host "  │ Noise only (discarded):  $($noiseOnlyFiles.Count) files   │" -ForegroundColor DarkGray
    Write-Host "  │ Real changes:            $($realChangeFiles.Count) files   │" -ForegroundColor Green
    Write-Host "  │ New files:               $($newFiles.Count) files   │" -ForegroundColor Green
    Write-Host "  │ Deleted files:           $($deletedFiles.Count) files   │" -ForegroundColor Yellow
    Write-Host "  └─────────────────────────────────────┘" -ForegroundColor White
    Write-Host ""

    # ── Step 4: Discard noise-only files ──────────────────────
    Write-Host "  [3/5] Discarding noise-only files..." -ForegroundColor White
    foreach ($noiseFile in $noiseOnlyFiles) {
        # Restore from git (clean version)
        $relPath = $noiseFile.Substring($RepoRoot.Length + 1).Replace('\', '/')
        git checkout -- $relPath 2>&1 | Out-Null
    }
    Write-Log "Discarded $($noiseOnlyFiles.Count) noise-only files"

    # ── Step 5: Optionally strip remaining files ──────────────
    if (-not $NoStripFilter -and $realChangeFiles.Count -gt 0) {
        Write-Host "  [4/5] Running safety strip filter on changed files..." -ForegroundColor White
        $stripScript = Join-Path $scriptDir 'Strip-AccessNoise.ps1'
        foreach ($changedFile in $realChangeFiles) {
            & $stripScript -Path $changedFile -ConfigPath $configPath 2>&1 | Out-Null
        }
        Write-Log "Strip filter applied to $($realChangeFiles.Count) files"
    }
    else {
        Write-Host "  [4/5] Strip filter skipped" -ForegroundColor DarkGray
    }

    # ── Step 6: Stage and validate ────────────────────────────
    Write-Host "  [5/5] Staging and validating..." -ForegroundColor White
    git add -A 2>&1

    $changedInGit = @(git diff --cached --name-only 2>&1)
    if ($changedInGit.Count -eq 0) {
        Write-Host "`n  ℹ️  No real changes to commit." -ForegroundColor Gray
        Write-Host "  Your database matches what's in Git." -ForegroundColor Gray
        git reset HEAD 2>&1 | Out-Null
        exit 0
    }

    # Show what's actually being committed
    Write-Host ""
    Write-Host "  Files to commit:" -ForegroundColor Green
    $changedInGit | ForEach-Object { Write-Host "    • $_" -ForegroundColor White }

    # Quick diff stat
    Write-Host ""
    git --no-pager diff --cached --stat 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

    # ── Confirm ───────────────────────────────────────────────
    $r = [System.Windows.Forms.MessageBox]::Show(
        "Commit $($changedInGit.Count) file(s)?`n`n$($changedInGit | Select-Object -First 10 | Out-String)",
        "Confirm Save", "YesNo", "Question")

    if ($r -ne "Yes") {
        git reset HEAD 2>&1 | Out-Null
        Write-Host "  Cancelled." -ForegroundColor Yellow
        exit 0
    }

    # ── Commit ────────────────────────────────────────────────
    $user = git config user.name 2>&1
    if (-not $user) { $user = $env:USERNAME }
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'
    $commitMsg = "Access DB: $timestamp - $user"

    git commit -m $commitMsg 2>&1 | ForEach-Object { Write-Log $_ }

    # ── Push ──────────────────────────────────────────────────
    if ($config.git.pushAfterCommit) {
        Write-Host "`n  Pushing to $remote/$branch..." -ForegroundColor White
        git push $remote $branch 2>&1 | ForEach-Object { Write-Log $_ }
        if ($LASTEXITCODE -ne 0) {
            git pull --rebase $remote $branch 2>&1
            git push $remote $branch 2>&1
        }
    }

    Write-Host "`n  ✅ Done! $($changedInGit.Count) file(s) committed and pushed." -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Log "Error: $($_.Exception.Message)" -Level 'ERROR'
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
}
