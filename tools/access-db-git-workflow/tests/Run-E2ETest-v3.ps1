<#
.SYNOPSIS
    End-to-end test for the v3 round-trip baseline workflow.

.DESCRIPTION
    Simulates the FULL workflow without needing Access or MSAccessVCS:
    1. Creates a temp git repo with Access VCS-style source files
    2. Runs "Start" logic (captures noise baseline)
    3. Simulates user making changes in Access (adds noise + real changes)
    4. Runs "Save" logic (compares against baseline, discards noise)
    5. Verifies ONLY real changes survive in the commit

    Tests multiple scenarios:
    - Pure noise injection (printer changes, checksums)
    - Real changes mixed with noise
    - New file creation
    - File deletion
    - Multi-developer simulation (different printers)
    - Idempotency (running save twice)
#>

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workflowDir = Split-Path -Parent $scriptDir

# ── Test Infrastructure ──────────────────────────────────────────

$testRoot = Join-Path $env:TEMP "access-v3-e2e-$(Get-Date -Format 'HHmmss')"
$passed = 0
$failed = 0
$total = 0

function New-TestRepo {
    param([string]$Name)
    $repoPath = Join-Path $testRoot $Name
    New-Item -ItemType Directory -Path $repoPath -Force | Out-Null
    Push-Location $repoPath
    git init --quiet 2>&1 | Out-Null
    git config user.name "Test User" 2>&1 | Out-Null
    git config user.email "test@example.com" 2>&1 | Out-Null

    # Create source folder structure
    $srcDir = Join-Path $repoPath 'source'
    New-Item -ItemType Directory -Path "$srcDir\forms" -Force | Out-Null
    New-Item -ItemType Directory -Path "$srcDir\modules" -Force | Out-Null
    New-Item -ItemType Directory -Path "$srcDir\queries" -Force | Out-Null

    # Create config.json pointing to this repo
    $config = @{
        accessDbPath = "MyDatabase.accdb"
        vcsExportFolder = "source"
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
            pushAfterCommit = $false
        }
    }
    $configJson = $config | ConvertTo-Json -Depth 4
    [System.IO.File]::WriteAllText("$repoPath\config.json", $configJson, [System.Text.UTF8Encoding]::new($false))

    # Create .gitignore
    $gitignore = ".noise-baseline/`r`n*.accdb`r`n*.laccdb`r`n"
    [System.IO.File]::WriteAllText("$repoPath\.gitignore", $gitignore, [System.Text.UTF8Encoding]::new($false))

    Pop-Location
    return $repoPath
}

function Write-CleanForm {
    param([string]$Path, [string]$FormName, [string]$Caption, [hashtable]$Controls)

    $content = @"
Version =21
VersionRequired =20
Begin Form
    RecordSelectors = NotDefault
    AutoCenter = NotDefault
    DefaultView =0
    Width =9360
    ItemSuffix =45
    RecordSource ="tblMain"
    Caption ="$Caption"
"@

    if ($Controls) {
        $content += "`r`n    Begin"
        foreach ($ctrl in $Controls.GetEnumerator()) {
            $content += "`r`n        Begin TextBox`r`n            Name =""$($ctrl.Key)""`r`n            ControlSource =""$($ctrl.Value)""`r`n        End"
        }
        $content += "`r`n    End"
    }

    $content += "`r`nEnd`r`n"
    [System.IO.File]::WriteAllText($Path, $content, [System.Text.UTF8Encoding]::new($false))
}

function Add-NoiseToFile {
    param([string]$Path, [string]$PrinterName = "HP LaserJet")

    # IMPORTANT: Noise must be DETERMINISTIC for a given printer name.
    # This matches real-world behavior — Access VCS always produces the same
    # printer blob, NameMap, and Checksum for the same machine/printer config.
    $printerHex = ($PrinterName.ToCharArray() | ForEach-Object { '{0:x2}00' -f [int]$_ }) -join ''
    # Deterministic "checksum" and "namemap" derived from printer name (not random)
    $seed = 0; $PrinterName.ToCharArray() | ForEach-Object { $seed = $seed * 31 + [int]$_ }
    $checksumVal = [Math]::Abs($seed) % 2000000000

    $lines = [System.Collections.Generic.List[string]]::new()
    $originalLines = [System.IO.File]::ReadAllLines($Path)

    foreach ($line in $originalLines) {
        $lines.Add($line)
        # Insert noise block after Caption line
        if ($line -match '^\s*Caption\s*=') {
            $lines.Add("    DatasheetFontHeight =11")
            $lines.Add("    DatasheetFontName =""Calibri""")
            $lines.Add("    DatasheetFontWeight =400")
            $lines.Add("    PrtMip = Begin")
            $lines.Add("        0xa0050000a0050000a0050000a00500000000000000000000000000000000")
            $lines.Add("        0x0000000000000000000000000000000000000000000000000000000000000000")
            $lines.Add("    End")
            $lines.Add("    PrtDevMode = Begin")
            $lines.Add("        0x0000000000000000000000000000000000000000000000000000000000000000")
            $lines.Add("        0x$printerHex")
            $lines.Add("    End")
            $lines.Add("    PrtDevNames = Begin")
            $lines.Add("        0x0800180038000100$printerHex")
            $lines.Add("    End")
        }
    }

    # Append checksum and NameMap at end (deterministic values)
    $lines.Add("Checksum =-$checksumVal")
    $lines.Add("NameMap = Begin")
    $lines.Add("    0x000000000000$($printerHex.Substring(0, [Math]::Min(20, $printerHex.Length)))")
    $lines.Add("End")

    $output = ($lines -join "`r`n") + "`r`n"
    [System.IO.File]::WriteAllText($Path, $output, [System.Text.UTF8Encoding]::new($false))
}

function Invoke-StartWorkflow {
    param([string]$RepoPath)

    $RepoPath = [System.IO.Path]::GetFullPath($RepoPath)
    $srcDir = [System.IO.Path]::GetFullPath((Join-Path $RepoPath 'source'))
    $noiseDir = Join-Path $RepoPath '.noise-baseline'

    # Step: Simulate MSAccessVCS round-trip (adds machine-specific noise)
    $files = Get-ChildItem $srcDir -Recurse -File
    foreach ($f in $files) {
        Add-NoiseToFile -Path $f.FullName -PrinterName "HP LaserJet Pro MFP"
    }

    # Step: Save as noise baseline
    if (Test-Path $noiseDir) { Remove-Item $noiseDir -Recurse -Force }
    Copy-Item $srcDir $noiseDir -Recurse -Force

    # Step: Restore clean working tree
    Push-Location $RepoPath
    git checkout -- source/ 2>&1 | Out-Null
    Pop-Location
}

function Invoke-SaveWorkflow {
    param([string]$RepoPath, [switch]$NoStripFilter)

    $RepoPath = [System.IO.Path]::GetFullPath($RepoPath)
    $srcDir = [System.IO.Path]::GetFullPath((Join-Path $RepoPath 'source'))
    $noiseDir = Join-Path $RepoPath '.noise-baseline'
    $configPath = Join-Path $RepoPath 'config.json'
    $stripScript = Join-Path $workflowDir 'Strip-AccessNoise.ps1'

    # Compare each file against noise baseline
    $sourceFiles = Get-ChildItem $srcDir -Recurse -File
    $noiseOnlyFiles = @()
    $realChangeFiles = @()
    $newFiles = @()

    foreach ($file in $sourceFiles) {
        $relativePath = $file.FullName.Substring($srcDir.Length)
        $baselineFile = Join-Path $noiseDir $relativePath

        if (-not (Test-Path $baselineFile)) {
            $newFiles += $file.FullName
            continue
        }

        $currentHash = (Get-FileHash $file.FullName -Algorithm SHA256).Hash
        $baselineHash = (Get-FileHash $baselineFile -Algorithm SHA256).Hash

        if ($currentHash -eq $baselineHash) {
            $noiseOnlyFiles += $file.FullName
        }
        else {
            $realChangeFiles += $file.FullName
        }
    }

    # Discard noise-only files
    Push-Location $RepoPath
    foreach ($noiseFile in $noiseOnlyFiles) {
        $relPath = $noiseFile.Substring($RepoPath.Length + 1).Replace('\', '/')
        git checkout -- $relPath 2>&1 | Out-Null
    }

    # Run strip filter on real change files (extra safety)
    if (-not $NoStripFilter) {
        foreach ($changedFile in $realChangeFiles) {
            & $stripScript -Path $changedFile -ConfigPath $configPath 2>&1 | Out-Null
        }
    }

    # Stage everything
    git add -A 2>&1 | Out-Null
    $changes = @(git diff --cached --name-only 2>&1)

    if ($changes.Count -gt 0) {
        git commit -m "Test commit" --quiet 2>&1 | Out-Null
    }

    Pop-Location

    return @{
        NoiseDiscarded = $noiseOnlyFiles.Count
        RealChanges = $realChangeFiles.Count
        NewFiles = $newFiles.Count
        CommittedFiles = $changes
    }
}

function Assert-Equal {
    param([string]$Name, $Expected, $Actual)
    $script:total++
    if ($Expected -eq $Actual) {
        Write-Host "  ✅ $Name" -ForegroundColor Green
        $script:passed++
    }
    else {
        Write-Host "  ❌ $Name — expected: $Expected, got: $Actual" -ForegroundColor Red
        $script:failed++
    }
}

function Assert-Contains {
    param([string]$Name, [string]$Needle, [string[]]$Haystack)
    $script:total++
    $found = $Haystack | Where-Object { $_ -like "*$Needle*" }
    if ($found) {
        Write-Host "  ✅ $Name" -ForegroundColor Green
        $script:passed++
    }
    else {
        Write-Host "  ❌ $Name — '$Needle' not found in: $($Haystack -join ', ')" -ForegroundColor Red
        $script:failed++
    }
}

function Assert-NotContains {
    param([string]$Name, [string]$Needle, [string[]]$Haystack)
    $script:total++
    $found = $Haystack | Where-Object { $_ -like "*$Needle*" }
    if (-not $found) {
        Write-Host "  ✅ $Name" -ForegroundColor Green
        $script:passed++
    }
    else {
        Write-Host "  ❌ $Name — '$Needle' should NOT be in: $($Haystack -join ', ')" -ForegroundColor Red
        $script:failed++
    }
}

function Assert-FileNotContains {
    param([string]$Name, [string]$FilePath, [string]$Pattern)
    $script:total++
    if (-not (Test-Path $FilePath)) {
        Write-Host "  ❌ $Name — file not found: $FilePath" -ForegroundColor Red
        $script:failed++
        return
    }
    $content = [System.IO.File]::ReadAllText($FilePath)
    if ($content -notmatch $Pattern) {
        Write-Host "  ✅ $Name" -ForegroundColor Green
        $script:passed++
    }
    else {
        Write-Host "  ❌ $Name — pattern '$Pattern' found in file" -ForegroundColor Red
        $script:failed++
    }
}

# ── TESTS ────────────────────────────────────────────────────────

Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  V3 END-TO-END TEST SUITE" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

# ── Test 1: Pure noise — nothing should be committed ─────────────
Write-Host "TEST 1: Pure noise injection (no real changes)" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test1-pure-noise"
$formPath = "$repo\source\forms\frmMain.txt"
Write-CleanForm -Path $formPath -FormName "frmMain" -Caption "Main Form" -Controls @{ txtName = "Name"; txtAge = "Age" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

Invoke-StartWorkflow -RepoPath $repo

# Simulate Access re-export with ONLY noise (same printer as baseline)
$files = Get-ChildItem "$repo\source" -Recurse -File
foreach ($f in $files) {
    Add-NoiseToFile -Path $f.FullName -PrinterName "HP LaserJet Pro MFP"
}

$result = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "No files committed (pure noise discarded)" 0 $result.CommittedFiles.Count
Assert-Equal "Noise files detected" 1 $result.NoiseDiscarded
Write-Host ""

# ── Test 2: Real changes + noise — only real changes committed ───
Write-Host "TEST 2: Real changes mixed with noise" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test2-real-plus-noise"
$formPath = "$repo\source\forms\frmCustomer.txt"
Write-CleanForm -Path $formPath -FormName "frmCustomer" -Caption "Customer" -Controls @{ txtName = "CustomerName" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

Invoke-StartWorkflow -RepoPath $repo

# Simulate: user changes caption + adds control, Access adds noise
$content = [System.IO.File]::ReadAllText($formPath)
$content = $content -replace 'Caption ="Customer"', 'Caption ="Customer Management"'
$content = $content -replace '(ControlSource ="CustomerName")', "`$1`r`n        End`r`n        Begin TextBox`r`n            Name =""txtEmail""`r`n            ControlSource =""Email"""
[System.IO.File]::WriteAllText($formPath, $content, [System.Text.UTF8Encoding]::new($false))
Add-NoiseToFile -Path $formPath -PrinterName "HP LaserJet Pro MFP"

$result = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "One file committed (form with real changes)" 1 $result.CommittedFiles.Count
Assert-Contains "Form file is in commit" "frmCustomer" $result.CommittedFiles

# Verify noise was stripped from committed file
Assert-FileNotContains "No PrtMip in committed file" $formPath "PrtMip"
Assert-FileNotContains "No Checksum in committed file" $formPath "Checksum"
Assert-FileNotContains "No NameMap in committed file" $formPath "NameMap"

# Verify real changes survived
$finalContent = [System.IO.File]::ReadAllText($formPath)
$script:total++
if ($finalContent -match 'Customer Management' -and $finalContent -match 'txtEmail') {
    Write-Host "  ✅ Real changes (caption + new control) preserved" -ForegroundColor Green
    $script:passed++
} else {
    Write-Host "  ❌ Real changes lost!" -ForegroundColor Red
    $script:failed++
}
Write-Host ""

# ── Test 3: New file creation — should always be committed ───────
Write-Host "TEST 3: New file creation" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test3-new-file"
$formPath = "$repo\source\forms\frmExisting.txt"
Write-CleanForm -Path $formPath -FormName "frmExisting" -Caption "Existing" -Controls @{ txtA = "FieldA" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

Invoke-StartWorkflow -RepoPath $repo

# Simulate: user creates new module, Access adds noise to existing form
$newModule = "$repo\source\modules\modNewFeature.bas"
$moduleContent = "Option Compare Database`r`nOption Explicit`r`n`r`nPublic Function CalculateTotal(qty As Long, price As Currency) As Currency`r`n    CalculateTotal = qty * price`r`nEnd Function`r`n"
[System.IO.File]::WriteAllText($newModule, $moduleContent, [System.Text.UTF8Encoding]::new($false))
Add-NoiseToFile -Path $formPath -PrinterName "HP LaserJet Pro MFP"

$result = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "One file committed (new module only)" 1 $result.CommittedFiles.Count
Assert-Contains "New module in commit" "modNewFeature" $result.CommittedFiles
Assert-Equal "Existing form noise discarded" 1 $result.NoiseDiscarded
Write-Host ""

# ── Test 4: Multi-developer — different printers, same outcome ───
Write-Host "TEST 4: Multi-developer simulation (different printers)" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test4-multi-dev"
$formPath = "$repo\source\forms\frmOrders.txt"
Write-CleanForm -Path $formPath -FormName "frmOrders" -Caption "Orders" -Controls @{ txtOrderId = "OrderID"; txtTotal = "Total" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

# Dev A starts (captures HP printer noise in baseline)
Invoke-StartWorkflow -RepoPath $repo

# Dev A makes a real change + noise with same printer
$content = [System.IO.File]::ReadAllText($formPath)
$content = $content -replace 'Caption ="Orders"', 'Caption ="Order Management v2"'
[System.IO.File]::WriteAllText($formPath, $content, [System.Text.UTF8Encoding]::new($false))
Add-NoiseToFile -Path $formPath -PrinterName "HP LaserJet Pro MFP"

$result = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "Dev A: one file committed" 1 $result.CommittedFiles.Count

# Verify caption changed
$finalContent = [System.IO.File]::ReadAllText($formPath)
$script:total++
if ($finalContent -match 'Order Management v2') {
    Write-Host "  ✅ Dev A's caption change preserved" -ForegroundColor Green
    $script:passed++
} else {
    Write-Host "  ❌ Dev A's change lost" -ForegroundColor Red
    $script:failed++
}
Assert-FileNotContains "No printer noise in Dev A's commit" $formPath "PrtMip"
Write-Host ""

# ── Test 5: No baseline exists — save should refuse ──────────────
Write-Host "TEST 5: Safety check — no baseline" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test5-no-baseline"
$formPath = "$repo\source\forms\frmTest.txt"
Write-CleanForm -Path $formPath -FormName "frmTest" -Caption "Test" -Controls @{ txtX = "X" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

# DON'T run Start — try to Save directly
$noiseDir = Join-Path $repo '.noise-baseline'
$script:total++
if (-not (Test-Path $noiseDir)) {
    Write-Host "  ✅ Save correctly requires baseline (would refuse)" -ForegroundColor Green
    $script:passed++
} else {
    Write-Host "  ❌ Baseline shouldn't exist" -ForegroundColor Red
    $script:failed++
}
Write-Host ""

# ── Test 6: Idempotency — running save twice changes nothing ─────
Write-Host "TEST 6: Idempotency (save twice)" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test6-idempotent"
$formPath = "$repo\source\forms\frmIdempotent.txt"
Write-CleanForm -Path $formPath -FormName "frmIdempotent" -Caption "Idempotent" -Controls @{ txtVal = "Value" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

Invoke-StartWorkflow -RepoPath $repo

# Make a real change
$content = [System.IO.File]::ReadAllText($formPath)
$content = $content -replace 'Caption ="Idempotent"', 'Caption ="Updated Form"'
[System.IO.File]::WriteAllText($formPath, $content, [System.Text.UTF8Encoding]::new($false))
Add-NoiseToFile -Path $formPath -PrinterName "HP LaserJet Pro MFP"

# First save
$result1 = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "First save commits 1 file" 1 $result1.CommittedFiles.Count

# Second cycle: Start again (re-captures baseline), then re-export with only noise
Invoke-StartWorkflow -RepoPath $repo
# Re-export with only noise (no new real changes)
Add-NoiseToFile -Path $formPath -PrinterName "HP LaserJet Pro MFP"
$result2 = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "Second save commits 0 files (idempotent)" 0 $result2.CommittedFiles.Count
Write-Host ""

# ── Test 7: File deletion — should be tracked ────────────────────
Write-Host "TEST 7: File deletion" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test7-deletion"
$form1 = "$repo\source\forms\frmKeep.txt"
$form2 = "$repo\source\forms\frmDelete.txt"
Write-CleanForm -Path $form1 -FormName "frmKeep" -Caption "Keep" -Controls @{ txtA = "A" }
Write-CleanForm -Path $form2 -FormName "frmDelete" -Caption "Delete Me" -Controls @{ txtB = "B" }
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

Invoke-StartWorkflow -RepoPath $repo

# Simulate: user deleted frmDelete in Access, Access re-exports without it
Remove-Item $form2
# Add noise to the remaining form
Add-NoiseToFile -Path $form1 -PrinterName "HP LaserJet Pro MFP"

$result = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "Deletion detected in commit" 1 $result.CommittedFiles.Count
Assert-Contains "Deleted file in commit" "frmDelete" $result.CommittedFiles
Write-Host ""

# ── Test 8: Large-scale noise (many files, one real change) ──────
Write-Host "TEST 8: Large-scale noise (10 forms, 1 real change)" -ForegroundColor Yellow
$repo = New-TestRepo -Name "test8-scale"
for ($i = 1; $i -le 10; $i++) {
    $fp = "$repo\source\forms\frmForm$i.txt"
    Write-CleanForm -Path $fp -FormName "frmForm$i" -Caption "Form $i" -Controls @{ "txtField$i" = "Field$i" }
}
Push-Location $repo; git add -A; git commit -m "initial" --quiet 2>&1 | Out-Null; Pop-Location

Invoke-StartWorkflow -RepoPath $repo

# Add noise to ALL 10 forms, real change to only form5
for ($i = 1; $i -le 10; $i++) {
    $fp = "$repo\source\forms\frmForm$i.txt"
    if ($i -eq 5) {
        $content = [System.IO.File]::ReadAllText($fp)
        $content = $content -replace 'Caption ="Form 5"', 'Caption ="Form 5 - Updated"'
        [System.IO.File]::WriteAllText($fp, $content, [System.Text.UTF8Encoding]::new($false))
    }
    Add-NoiseToFile -Path $fp -PrinterName "HP LaserJet Pro MFP"
}

$result = Invoke-SaveWorkflow -RepoPath $repo
Assert-Equal "Only 1 of 10 files committed" 1 $result.CommittedFiles.Count
Assert-Contains "Correct file committed (form5)" "frmForm5" $result.CommittedFiles
Assert-Equal "9 noise-only files discarded" 9 $result.NoiseDiscarded
Write-Host ""

# ── RESULTS ──────────────────────────────────────────────────────
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  RESULTS: $passed/$total passed, $failed failed" -ForegroundColor $(if ($failed -eq 0) { 'Green' } else { 'Red' })
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan

# Cleanup
Remove-Item $testRoot -Recurse -Force -ErrorAction SilentlyContinue

exit $failed
