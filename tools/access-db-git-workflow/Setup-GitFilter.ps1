<#
.SYNOPSIS
    Sets up the git clean filter for automatic noise stripping.

.DESCRIPTION
    Configures git to automatically run Strip-AccessNoise.ps1 on every
    `git add` for Access VCS source files. This is the zero-effort layer:
    noise is stripped before content enters the git index.

    Run this once per clone.
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$RepoRoot = "."
)

$ErrorActionPreference = 'Stop'

Push-Location $RepoRoot

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$stripScript = Join-Path $scriptDir 'Strip-AccessNoise.ps1'

# Make the path relative to repo root for portability
$repoRootFull = (git rev-parse --show-toplevel 2>&1).Replace('/', '\')
$relativePath = $stripScript.Replace($repoRootFull + '\', '').Replace('\', '/')

Write-Host "Setting up git clean filter..." -ForegroundColor Cyan
Write-Host "  Script: $relativePath" -ForegroundColor Gray

# Configure the filter
git config filter.accessvcs.clean "powershell -NoProfile -ExecutionPolicy Bypass -File `"$relativePath`" -Stdin"
git config filter.accessvcs.smudge "cat"
git config filter.accessvcs.required true

Write-Host "  ✅ filter.accessvcs.clean configured" -ForegroundColor Green
Write-Host "  ✅ filter.accessvcs.smudge = cat (passthrough)" -ForegroundColor Green
Write-Host "  ✅ filter.accessvcs.required = true (fail on error)" -ForegroundColor Green

# Check .gitattributes has the filter rules
$gitattributes = Join-Path $repoRootFull '.gitattributes'
$hasFilter = $false
if (Test-Path $gitattributes) {
    $content = Get-Content $gitattributes -Raw
    $hasFilter = $content -match 'filter=accessvcs'
}

if (-not $hasFilter) {
    Write-Host "`n  Adding filter rules to .gitattributes..." -ForegroundColor Cyan
    $filterRules = @"

# =========================================================
# ACCESS VCS CLEAN FILTER — strips noise on git add
# =========================================================
source/**/*.txt filter=accessvcs
source/**/*.cls filter=accessvcs
source/**/*.frm filter=accessvcs
"@
    Add-Content -Path $gitattributes -Value $filterRules
    Write-Host "  ✅ .gitattributes updated" -ForegroundColor Green
}
else {
    Write-Host "  ℹ️  .gitattributes already has filter=accessvcs rules" -ForegroundColor Gray
}

Pop-Location

Write-Host "`n✅ Git clean filter is active." -ForegroundColor Green
Write-Host "   Noise will be stripped automatically on every 'git add'." -ForegroundColor Cyan
Write-Host "   No manual steps needed." -ForegroundColor Cyan
