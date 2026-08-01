<#
.SYNOPSIS
    Creates desktop shortcuts for Start Working and Save & Share.

.DESCRIPTION
    Run this once during setup. Creates two desktop shortcuts:
    - "Access - Start Working" (green icon)
    - "Access - Save & Share" (red icon)

    Each shortcut runs the corresponding PowerShell script silently.
#>
[CmdletBinding()]
param(
    [Parameter()]
    [string]$DesktopPath = [Environment]::GetFolderPath('Desktop')
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function New-Shortcut {
    param(
        [string]$Name,
        [string]$TargetScript,
        [string]$Description,
        [string]$IconIndex = "0"
    )

    $shortcutPath = Join-Path $DesktopPath "$Name.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($shortcutPath)

    # Run PowerShell with the script, keep window visible for feedback
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$TargetScript`""
    $shortcut.WorkingDirectory = $scriptDir
    $shortcut.Description = $Description
    $shortcut.WindowStyle = 1  # Normal window

    # Use shell32.dll icons (green=43 for start, red=131 for save)
    $shortcut.IconLocation = "shell32.dll,$IconIndex"

    $shortcut.Save()
    Write-Host "  Created: $shortcutPath" -ForegroundColor Green
}

Write-Host "`nCreating desktop shortcuts..." -ForegroundColor Cyan
Write-Host "  Desktop: $DesktopPath" -ForegroundColor Gray
Write-Host ""

# Start Working shortcut (green folder icon)
New-Shortcut `
    -Name "Access - Start Working" `
    -TargetScript (Join-Path $scriptDir 'Start-AccessWork.ps1') `
    -Description "Pull latest changes and open Access database for editing" `
    -IconIndex "43"

# Save & Share shortcut (upload icon)
New-Shortcut `
    -Name "Access - Save & Share" `
    -TargetScript (Join-Path $scriptDir 'Save-AccessWork.ps1') `
    -Description "Export, strip noise, commit, and push Access database changes" `
    -IconIndex "131"

Write-Host ""
Write-Host "✅ Shortcuts created!" -ForegroundColor Green
Write-Host ""
Write-Host "Usage:" -ForegroundColor Cyan
Write-Host "  1. Double-click 'Access - Start Working' to begin" -ForegroundColor White
Write-Host "  2. Make your changes in Access" -ForegroundColor White
Write-Host "  3. Close Access" -ForegroundColor White
Write-Host "  4. Double-click 'Access - Save & Share' to push changes" -ForegroundColor White
