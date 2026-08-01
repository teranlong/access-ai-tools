<#
.SYNOPSIS
    Initialize a new Access Database project with the v3 Git workflow.

.DESCRIPTION
    Sets up a local folder with everything needed for Access DB collaboration via Git:
    - Copies workflow scripts
    - Creates config.json with project-specific paths
    - Sets up .gitignore and .gitattributes
    - Creates desktop shortcuts (Start Working / Save & Share)
    - Initializes git repo (if not already one)

.PARAMETER ProjectPath
    Path to the Access DB project folder. Creates it if it doesn't exist.

.PARAMETER AccessDbName
    Name of the .accdb file (e.g., "MyDatabase.accdb")

.PARAMETER GitRemote
    Optional remote URL to add as origin.

.PARAMETER SourceFolder
    Name of the VCS export folder. Default: "source"

.EXAMPLE
    .\Setup-Project.ps1 -ProjectPath "C:\Projects\MyAccessApp" -AccessDbName "MyApp.accdb"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$ProjectPath,

    [Parameter(Mandatory)]
    [string]$AccessDbName,

    [Parameter()]
    [string]$GitRemote,

    [Parameter()]
    [string]$SourceFolder = "source"
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  ACCESS DB GIT WORKFLOW — PROJECT SETUP" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

# ── Create project folder ─────────────────────────────────────
if (-not (Test-Path $ProjectPath)) {
    New-Item -ItemType Directory -Path $ProjectPath -Force | Out-Null
    Write-Host "  Created: $ProjectPath" -ForegroundColor Green
}
$ProjectPath = [System.IO.Path]::GetFullPath($ProjectPath)

# ── Create workflow subfolder ─────────────────────────────────
$workflowDir = Join-Path $ProjectPath 'workflow'
if (-not (Test-Path $workflowDir)) {
    New-Item -ItemType Directory -Path $workflowDir -Force | Out-Null
}

# Copy core scripts
$scriptsToCopy = @(
    'Start-AccessWork-v3.ps1',
    'Save-AccessWork-v3.ps1',
    'Strip-AccessNoise.ps1'
)
foreach ($script in $scriptsToCopy) {
    $src = Join-Path $scriptDir $script
    $dst = Join-Path $workflowDir $script
    if (Test-Path $src) {
        Copy-Item $src $dst -Force
        Write-Host "  Copied: workflow\$script" -ForegroundColor Gray
    }
}

# ── Create config.json ────────────────────────────────────────
$config = @{
    accessDbPath = $AccessDbName
    vcsExportFolder = $SourceFolder
    gitRepoRoot = "."
    branch = "main"
    remoteName = "origin"
    noiseFilter = @{
        stripPrinterSettings = $true
        stripNameMap = $true
        stripChecksums = $true
        stripGuids = $false
        stripSummaryInfo = $true
        stripDatasheetFont = $true
        customPatterns = @()
    }
    git = @{
        autoStash = $true
        pullRebase = $true
        commitMessageTemplate = "Access DB: {timestamp} - {user}"
        pushAfterCommit = $true
    }
}
$configJson = $config | ConvertTo-Json -Depth 4
$configPath = Join-Path $workflowDir 'config.json'
[System.IO.File]::WriteAllText($configPath, $configJson, [System.Text.UTF8Encoding]::new($false))
Write-Host "  Created: workflow\config.json" -ForegroundColor Green

# ── Create .gitignore ─────────────────────────────────────────
$gitignoreContent = @"
# Access Database Git Workflow
.noise-baseline/
*.accdb
*.laccdb
*.mdw
*.ldb

# Workflow logs
workflow/logs/

# Windows
Thumbs.db
desktop.ini

# Office temp files
~`$*
"@
$gitignorePath = Join-Path $ProjectPath '.gitignore'
[System.IO.File]::WriteAllText($gitignorePath, $gitignoreContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "  Created: .gitignore" -ForegroundColor Green

# ── Create .gitattributes ─────────────────────────────────────
$gitattributesContent = @"
# Treat Access VCS exports as text for proper diff/merge
$SourceFolder/**/*.txt text eol=crlf
$SourceFolder/**/*.bas text eol=crlf
$SourceFolder/**/*.cls text eol=crlf
$SourceFolder/**/*.sql text eol=crlf

# Keep binary files as binary
*.accdb binary
*.accde binary
"@
$gitattributesPath = Join-Path $ProjectPath '.gitattributes'
[System.IO.File]::WriteAllText($gitattributesPath, $gitattributesContent, [System.Text.UTF8Encoding]::new($false))
Write-Host "  Created: .gitattributes" -ForegroundColor Green

# ── Create source folder ──────────────────────────────────────
$sourceDir = Join-Path $ProjectPath $SourceFolder
if (-not (Test-Path $sourceDir)) {
    New-Item -ItemType Directory -Path $sourceDir -Force | Out-Null
    # Create placeholder so git tracks the folder
    [System.IO.File]::WriteAllText((Join-Path $sourceDir '.gitkeep'), "", [System.Text.UTF8Encoding]::new($false))
    Write-Host "  Created: $SourceFolder\" -ForegroundColor Green
}

# ── Initialize git repo ───────────────────────────────────────
Push-Location $ProjectPath
if (-not (Test-Path '.git')) {
    git init --quiet 2>&1 | Out-Null
    git add -A 2>&1 | Out-Null
    git commit -m "Initialize Access DB Git workflow" --quiet 2>&1 | Out-Null
    Write-Host "  Git repo initialized and committed" -ForegroundColor Green
}

if ($GitRemote) {
    $existing = git remote 2>&1
    if ($existing -notcontains 'origin') {
        git remote add origin $GitRemote 2>&1 | Out-Null
        Write-Host "  Remote added: $GitRemote" -ForegroundColor Green
    }
}
Pop-Location

# ── Create desktop shortcuts ──────────────────────────────────
Write-Host "`n  Creating desktop shortcuts..." -ForegroundColor White

$desktop = [System.Environment]::GetFolderPath('Desktop')
$projectName = Split-Path $ProjectPath -Leaf
$shell = New-Object -ComObject WScript.Shell

# START shortcut
$startLnk = $shell.CreateShortcut("$desktop\▶ START - $projectName.lnk")
$startLnk.TargetPath = "powershell.exe"
$startLnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$workflowDir\Start-AccessWork-v3.ps1`" -RepoRoot `"$ProjectPath`""
$startLnk.WorkingDirectory = $ProjectPath
$startLnk.Description = "Pull latest and open Access DB for editing"
$startLnk.IconLocation = "shell32.dll,175"
$startLnk.Save()
Write-Host "  Created: ▶ START - $projectName" -ForegroundColor Green

# SAVE shortcut
$saveLnk = $shell.CreateShortcut("$desktop\💾 SAVE - $projectName.lnk")
$saveLnk.TargetPath = "powershell.exe"
$saveLnk.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$workflowDir\Save-AccessWork-v3.ps1`" -RepoRoot `"$ProjectPath`""
$saveLnk.WorkingDirectory = $ProjectPath
$saveLnk.Description = "Export from Access, filter noise, commit and push"
$saveLnk.IconLocation = "shell32.dll,258"
$saveLnk.Save()
Write-Host "  Created: 💾 SAVE - $projectName" -ForegroundColor Green

# ── Summary ───────────────────────────────────────────────────
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  ✅ SETUP COMPLETE" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
Write-Host "  Project: $ProjectPath" -ForegroundColor White
Write-Host "  Database: $AccessDbName" -ForegroundColor White
Write-Host ""
Write-Host "  WORKFLOW:" -ForegroundColor Yellow
Write-Host "    1. Double-click '▶ START' on your desktop" -ForegroundColor White
Write-Host "    2. Work in Access (make your changes)" -ForegroundColor White
Write-Host "    3. Close Access" -ForegroundColor White
Write-Host "    4. Double-click '💾 SAVE' on your desktop" -ForegroundColor White
Write-Host ""
Write-Host "  That's it! Git noise is handled automatically." -ForegroundColor Gray
Write-Host ""
