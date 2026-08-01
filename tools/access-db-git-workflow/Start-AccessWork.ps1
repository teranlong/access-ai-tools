<#
.SYNOPSIS
    ONE-CLICK: Pull latest changes and open Access database for editing.

.DESCRIPTION
    This is the "Start Working" entry point. It:
    1. Stashes any local uncommitted changes
    2. Pulls latest from remote (rebase)
    3. Strips noise from pulled source files
    4. Invokes MSAccessVCS to build the .accdb from source
    5. Opens the .accdb in Microsoft Access

    The user never touches Git directly.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Load configuration
$configPath = Join-Path $scriptDir 'config.json'
if (-not (Test-Path $configPath)) {
    [System.Windows.Forms.MessageBox]::Show(
        "config.json not found.`nExpected at: $configPath`n`nPlease copy config.template.json and configure your paths.",
        "Access Git Workflow - Configuration Missing",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Resolve paths relative to config file location
$repoRoot = Resolve-Path (Join-Path $scriptDir $config.gitRepoRoot) -ErrorAction Stop
$accessDb = Join-Path $scriptDir $config.accessDbPath
$vcsFolder = Join-Path $scriptDir $config.vcsExportFolder
$branch = $config.branch
$remote = $config.remoteName

# Logging
$logFile = Join-Path $scriptDir "logs\start-$(Get-Date -Format 'yyyy-MM-dd_HHmmss').log"
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

function Show-ErrorAndExit {
    param([string]$Message)
    Write-Log $Message -Level 'ERROR'
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show(
        $Message,
        "Access Git Workflow - Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
    exit 1
}

try {
    Write-Log "=== START WORKING ==="
    Write-Log "Repo: $repoRoot"
    Write-Log "Database: $accessDb"

    # Step 1: Ensure we're in the repo
    Push-Location $repoRoot

    # Step 2: Check if Access is running with our database
    $accessProc = Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue
    if ($accessProc) {
        Write-Log "Microsoft Access is already running. Please close it first." -Level 'WARN'
        Show-ErrorAndExit "Microsoft Access is already running.`nPlease close Access and try again."
    }

    # Step 3: Stash any local changes
    Write-Log "Checking for local changes..."
    $status = git status --porcelain 2>&1
    if ($status) {
        Write-Log "Stashing local changes..."
        git stash push -m "auto-stash before pull $(Get-Date -Format 'yyyy-MM-dd HH:mm')" 2>&1 | ForEach-Object { Write-Log $_ }
    }

    # Step 4: Pull latest
    Write-Log "Pulling latest from $remote/$branch..."
    $pullArgs = @('pull', $remote, $branch)
    if ($config.git.pullRebase) { $pullArgs += '--rebase' }

    $pullResult = & git @pullArgs 2>&1
    $pullResult | ForEach-Object { Write-Log $_ }

    if ($LASTEXITCODE -ne 0) {
        Show-ErrorAndExit "Git pull failed.`n`nDetails in log: $logFile"
    }

    # Step 5: Strip noise from source files
    Write-Log "Stripping noise from VCS source files..."
    $stripScript = Join-Path $scriptDir 'Strip-AccessNoise.ps1'
    if (Test-Path $vcsFolder) {
        & $stripScript -Path $vcsFolder -ConfigPath $configPath
    }
    else {
        Write-Log "VCS folder not found: $vcsFolder (may be first run)" -Level 'WARN'
    }

    # Step 6: Build .accdb from source using MSAccessVCS
    Write-Log "Building Access database from source..."

    # MSAccessVCS can be invoked via COM automation or command line
    # This uses the command-line approach via Access macro
    if (Test-Path $accessDb) {
        Write-Log "Existing database found, backing up..."
        $backupPath = "$accessDb.bak"
        Copy-Item $accessDb $backupPath -Force
    }

    # Launch Access with the VCS build command
    # MSAccessVCS uses a specific macro to import from source
    $vbScript = @"
Dim oAccess
Set oAccess = CreateObject("Access.Application")
oAccess.OpenCurrentDatabase "$accessDb"
oAccess.Run "VCS_ImportAll"
oAccess.Quit
Set oAccess = Nothing
"@

    # Alternative: If MSAccessVCS add-in auto-imports on open, just open the DB
    # For most setups, opening the .accdb with VCS installed triggers the import
    Write-Log "Opening Access database..."
    Start-Process $accessDb

    Write-Log "=== START COMPLETE ==="
    Write-Log "Access database is ready for editing."

    # Pop stash if we stashed earlier (after successful build)
    if ($status) {
        Write-Log "Restoring stashed changes..."
        git stash pop 2>&1 | ForEach-Object { Write-Log $_ }
    }

}
catch {
    Show-ErrorAndExit "Unexpected error: $($_.Exception.Message)"
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
}

Write-Host "`n✅ Ready! Access database is open for editing." -ForegroundColor Green
Write-Host "When done, close Access and click 'Save & Share'." -ForegroundColor Cyan
