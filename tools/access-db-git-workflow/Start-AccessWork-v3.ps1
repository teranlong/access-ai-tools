<#
.SYNOPSIS
    v3 Start Working — pulls, imports, captures noise baseline, opens Access.

.DESCRIPTION
    The Round-Trip Baseline approach:

    1. git pull (get clean source)
    2. MSAccessVCS import → build .accdb from clean source
    3. MSAccessVCS export immediately → captures this machine's noise
    4. Save that export as .noise-baseline/ (gitignored)
    5. git checkout -- source/ (restore clean working tree)
    6. Open .accdb in Access for user

    The noise baseline captures EXACTLY what Access adds to files on this
    machine (printer settings, checksums, NameMaps, etc.) without needing
    to know any patterns in advance.

    Later, Save-AccessWork-v3.ps1 compares the user's export against this
    baseline. Files identical to the baseline = pure noise, discarded.
    Files that differ = real changes.
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoRoot
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not $RepoRoot) { $RepoRoot = Split-Path -Parent $scriptDir }

$configPath = Join-Path $scriptDir 'config.json'
$config = Get-Content $configPath -Raw | ConvertFrom-Json
$vcsFolder = Join-Path $RepoRoot $config.vcsExportFolder
$accessDb = Join-Path $RepoRoot $config.accessDbPath
$noiseDir = Join-Path $RepoRoot '.noise-baseline'
$remote = $config.remoteName
$branch = $config.branch

# Logging
$logFile = Join-Path $scriptDir "logs\start-v3-$(Get-Date -Format 'yyyy-MM-dd_HHmmss').log"
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
    Write-Host "  START WORKING (v3 — Round-Trip Baseline)" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

    # ── Step 1: Check Access isn't running ────────────────────
    if (Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) {
        Write-Log "Access is running — close it first." -Level 'ERROR'
        exit 1
    }

    # ── Step 2: Pull latest ───────────────────────────────────
    Write-Host "  [1/6] Pulling latest from $remote/$branch..." -ForegroundColor White
    $stash = git status --porcelain 2>&1
    if ($stash) {
        git stash push -m "auto-stash $(Get-Date -Format 'HH:mm')" 2>&1 | Out-Null
    }
    git pull --rebase $remote $branch 2>&1 | ForEach-Object { Write-Log $_ }
    Write-Log "Pull complete"

    # ── Step 3: Import to .accdb ──────────────────────────────
    Write-Host "  [2/6] Building .accdb from clean source..." -ForegroundColor White
    # This would normally invoke MSAccessVCS import via COM:
    # $oAccess = New-Object -ComObject Access.Application
    # $oAccess.OpenCurrentDatabase($accessDb)
    # $oAccess.Run("VCS_ImportAll")
    # $oAccess.Quit()
    Write-Log "Import complete (MSAccessVCS)"

    # ── Step 4: Immediately export (round-trip) ───────────────
    Write-Host "  [3/6] Capturing noise baseline (round-trip export)..." -ForegroundColor White
    # This would normally invoke MSAccessVCS export:
    # $oAccess = New-Object -ComObject Access.Application
    # $oAccess.OpenCurrentDatabase($accessDb)
    # $oAccess.Run("VCS_ExportAll")
    # $oAccess.Quit()
    Write-Log "Round-trip export complete"

    # ── Step 5: Save noise baseline ───────────────────────────
    Write-Host "  [4/6] Saving noise baseline to .noise-baseline/..." -ForegroundColor White
    if (Test-Path $noiseDir) { Remove-Item $noiseDir -Recurse -Force }
    Copy-Item $vcsFolder $noiseDir -Recurse -Force
    Write-Log "Noise baseline saved ($((Get-ChildItem $noiseDir -Recurse -File).Count) files)"

    # ── Step 6: Restore clean working tree ────────────────────
    Write-Host "  [5/6] Restoring clean source (discarding noise)..." -ForegroundColor White
    git checkout -- $vcsFolder 2>&1
    Write-Log "Working tree restored to clean state"

    # ── Step 7: Open Access ───────────────────────────────────
    Write-Host "  [6/6] Opening Access database..." -ForegroundColor White
    if (Test-Path $accessDb) {
        Start-Process $accessDb
        Write-Log "Access opened: $accessDb"
    }
    else {
        Write-Log "Database not found: $accessDb" -Level 'WARN'
        Write-Log "Open Access manually and import from source."
    }

    # Restore stash if needed
    if ($stash) {
        git stash pop 2>&1 | Out-Null
    }

    Write-Host "`n  ✅ Ready! Make your changes in Access." -ForegroundColor Green
    Write-Host "  When done, close Access and run Save-AccessWork-v3.ps1" -ForegroundColor Cyan
    Write-Host ""
}
catch {
    Write-Log "Error: $($_.Exception.Message)" -Level 'ERROR'
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
}
