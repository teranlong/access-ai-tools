<#
.SYNOPSIS
    ONE-CLICK: Export Access changes, strip noise, commit, and push.

.DESCRIPTION
    This is the "Save & Share" entry point. It:
    1. Ensures Access is closed (prompts if still open)
    2. Invokes MSAccessVCS to export .accdb to text source files
    3. Strips all noise from exported files
    4. Shows a summary of real changes
    5. Commits with auto-generated message
    6. Pushes to remote

    The user never touches Git directly.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Add-Type -AssemblyName System.Windows.Forms

# Load configuration
$configPath = Join-Path $scriptDir 'config.json'
if (-not (Test-Path $configPath)) {
    [System.Windows.Forms.MessageBox]::Show(
        "config.json not found.`nExpected at: $configPath",
        "Access Git Workflow - Configuration Missing",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    )
    exit 1
}

$config = Get-Content $configPath -Raw | ConvertFrom-Json

# Resolve paths
$repoRoot = Resolve-Path (Join-Path $scriptDir $config.gitRepoRoot) -ErrorAction Stop
$accessDb = Join-Path $scriptDir $config.accessDbPath
$vcsFolder = Join-Path $scriptDir $config.vcsExportFolder
$branch = $config.branch
$remote = $config.remoteName

# Logging
$logFile = Join-Path $scriptDir "logs\save-$(Get-Date -Format 'yyyy-MM-dd_HHmmss').log"
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
    [System.Windows.Forms.MessageBox]::Show(
        $Message,
        "Access Git Workflow - Error",
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Error
    ) | Out-Null
    exit 1
}

function Show-Info {
    param([string]$Message, [string]$Title = "Access Git Workflow")
    [System.Windows.Forms.MessageBox]::Show(
        $Message, $Title,
        [System.Windows.Forms.MessageBoxButtons]::OK,
        [System.Windows.Forms.MessageBoxIcon]::Information
    ) | Out-Null
}

try {
    Write-Log "=== SAVE & SHARE ==="
    Write-Log "Repo: $repoRoot"
    Write-Log "Database: $accessDb"

    # Step 1: Check if Access is still running
    $accessProc = Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue
    if ($accessProc) {
        $result = [System.Windows.Forms.MessageBox]::Show(
            "Microsoft Access is still running.`n`nPlease save your work and close Access, then click OK.",
            "Access Git Workflow - Close Access First",
            [System.Windows.Forms.MessageBoxButtons]::OKCancel,
            [System.Windows.Forms.MessageBoxIcon]::Warning
        )
        if ($result -eq [System.Windows.Forms.DialogResult]::Cancel) {
            Write-Log "User cancelled (Access still open)" -Level 'WARN'
            exit 0
        }

        # Wait for Access to close
        $timeout = 120
        $elapsed = 0
        while ((Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) -and $elapsed -lt $timeout) {
            Start-Sleep -Seconds 2
            $elapsed += 2
        }

        if (Get-Process -Name "MSACCESS" -ErrorAction SilentlyContinue) {
            Show-ErrorAndExit "Access is still running after waiting. Please close it manually and try again."
        }
    }

    Push-Location $repoRoot

    # Step 2: Export from Access using MSAccessVCS
    Write-Log "Exporting Access database to source files..."

    if (-not (Test-Path $accessDb)) {
        Show-ErrorAndExit "Database not found: $accessDb"
    }

    # MSAccessVCS export via COM automation
    # Opens Access, runs the export, then closes
    $exportScript = @"
try {
    `$oAccess = New-Object -ComObject Access.Application
    `$oAccess.OpenCurrentDatabase("$accessDb")
    `$oAccess.Run("VCS_ExportAll")
    `$oAccess.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject(`$oAccess) | Out-Null
} catch {
    Write-Error `$_.Exception.Message
    exit 1
}
"@

    Write-Log "Running MSAccessVCS export..."
    $exportResult = powershell -NoProfile -Command $exportScript 2>&1
    $exportResult | ForEach-Object { Write-Log $_ }

    # If COM automation fails, user may need to export manually
    if ($LASTEXITCODE -ne 0) {
        Write-Log "Automated export failed. Checking if source folder has recent changes..." -Level 'WARN'
        # Allow continuing if source folder exists (user may have exported manually)
        if (-not (Test-Path $vcsFolder)) {
            Show-ErrorAndExit "Export failed and no source folder found.`nPlease export manually from Access using MSAccessVCS, then try again."
        }
    }

    # Step 3: Strip noise from ALL exported files
    Write-Log "Stripping noise from exported files..."
    $stripScript = Join-Path $scriptDir 'Strip-AccessNoise.ps1'
    & $stripScript -Path $vcsFolder -ConfigPath $configPath

    # Step 4: Check what actually changed (after noise removal)
    Write-Log "Checking for real changes..."
    git add -A 2>&1 | ForEach-Object { Write-Log $_ }

    $diffStat = git diff --cached --stat 2>&1
    $changedFiles = git diff --cached --name-only 2>&1

    if (-not $changedFiles) {
        Write-Log "No real changes detected after noise filtering."
        Show-Info "No changes to save.`n`nYour database matches what's already in Git (after filtering noise)."
        git reset HEAD 2>&1 | Out-Null
        Pop-Location
        exit 0
    }

    # Step 5: Show summary and confirm
    $fileCount = ($changedFiles | Measure-Object).Count
    Write-Log "Found $fileCount files with real changes"

    $summaryMsg = "Changes detected in $fileCount file(s):`n`n"
    $changedFiles | Select-Object -First 15 | ForEach-Object {
        $summaryMsg += "  • $_`n"
    }
    if ($fileCount -gt 15) {
        $summaryMsg += "  ... and $($fileCount - 15) more`n"
    }
    $summaryMsg += "`nCommit and push these changes?"

    $confirmResult = [System.Windows.Forms.MessageBox]::Show(
        $summaryMsg,
        "Access Git Workflow - Confirm Save",
        [System.Windows.Forms.MessageBoxButtons]::YesNo,
        [System.Windows.Forms.MessageBoxIcon]::Question
    )

    if ($confirmResult -ne [System.Windows.Forms.DialogResult]::Yes) {
        Write-Log "User cancelled commit" -Level 'WARN'
        git reset HEAD 2>&1 | Out-Null
        Pop-Location
        exit 0
    }

    # Step 6: Commit
    $user = git config user.name 2>&1
    if (-not $user) { $user = $env:USERNAME }
    $timestamp = Get-Date -Format 'yyyy-MM-dd HH:mm'

    $commitMsg = $config.git.commitMessageTemplate -replace '\{timestamp\}', $timestamp -replace '\{user\}', $user
    if (-not $commitMsg) { $commitMsg = "Access DB: $timestamp - $user" }

    Write-Log "Committing: $commitMsg"
    git commit -m $commitMsg 2>&1 | ForEach-Object { Write-Log $_ }

    if ($LASTEXITCODE -ne 0) {
        Show-ErrorAndExit "Git commit failed. Check log: $logFile"
    }

    # Step 7: Push
    if ($config.git.pushAfterCommit) {
        Write-Log "Pushing to $remote/$branch..."
        $pushResult = git push $remote $branch 2>&1
        $pushResult | ForEach-Object { Write-Log $_ }

        if ($LASTEXITCODE -ne 0) {
            # Try pull --rebase then push again
            Write-Log "Push failed, attempting pull --rebase then push..." -Level 'WARN'
            git pull --rebase $remote $branch 2>&1 | ForEach-Object { Write-Log $_ }

            # Re-strip noise after rebase (in case pulled files have noise)
            & $stripScript -Path $vcsFolder -ConfigPath $configPath
            git add -A 2>&1 | Out-Null
            $rebaseChanges = git diff --cached --name-only 2>&1
            if ($rebaseChanges) {
                git commit -m "Access DB: post-rebase noise cleanup" 2>&1 | Out-Null
            }

            git push $remote $branch 2>&1 | ForEach-Object { Write-Log $_ }
            if ($LASTEXITCODE -ne 0) {
                Show-ErrorAndExit "Push failed after retry.`nYou may need to resolve conflicts manually.`n`nLog: $logFile"
            }
        }
    }

    Write-Log "=== SAVE COMPLETE ==="
    Show-Info "Changes saved and shared!`n`n$fileCount file(s) committed and pushed to $remote/$branch."

}
catch {
    Show-ErrorAndExit "Unexpected error: $($_.Exception.Message)`n`nLog: $logFile"
}
finally {
    Pop-Location -ErrorAction SilentlyContinue
}

Write-Host "`n✅ Done! Changes saved and pushed." -ForegroundColor Green
