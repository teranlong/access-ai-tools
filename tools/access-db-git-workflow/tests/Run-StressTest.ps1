<#
.SYNOPSIS
    Stress test for the Access Database Git Workflow noise filter.

.DESCRIPTION
    Simulates multiple "sessions" of Access VCS export where:
    - Real changes are made (new controls, modified properties, new code)
    - Noise is injected (different printer settings, checksums, NameMaps per session)

    Validates that after stripping, ONLY the real changes appear in diffs.

    This simulates the exact problem: two developers open Access on different machines,
    Access regenerates printer blobs/checksums/NameMaps, but only their actual edits
    should survive the filter.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$workflowDir = Split-Path -Parent $scriptDir
$stripScript = Join-Path $workflowDir 'Strip-AccessNoise.ps1'
$configPath = Join-Path $workflowDir 'config.json'

# Create a temp working directory to simulate git operations
$testRoot = Join-Path $env:TEMP "access-workflow-stress-test-$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null

$passCount = 0
$failCount = 0
$testResults = @()

function Write-TestResult {
    param([string]$Name, [bool]$Passed, [string]$Details = "")
    $icon = if ($Passed) { "✅" } else { "❌" }
    $color = if ($Passed) { "Green" } else { "Red" }
    Write-Host "  $icon $Name" -ForegroundColor $color
    if ($Details) { Write-Host "     $Details" -ForegroundColor Gray }
    if ($Passed) { $script:passCount++ } else { $script:failCount++ }
    $script:testResults += @{ Name = $Name; Passed = $Passed; Details = $Details }
}

# ================================================================
# SETUP: Create "baseline" source (already cleaned)
# ================================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " ACCESS DB GIT WORKFLOW - STRESS TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$originalSourceDir = Join-Path $scriptDir "sample-source"
$baselineDir = Join-Path $testRoot "baseline"
Copy-Item $originalSourceDir $baselineDir -Recurse

Write-Host "Step 1: Establishing clean baseline..." -ForegroundColor Yellow
& $stripScript -Path $baselineDir -ConfigPath $configPath
$baselineHashes = @{}
Get-ChildItem $baselineDir -Recurse -File | ForEach-Object {
    $baselineHashes[$_.Name] = (Get-FileHash $_.FullName).Hash
}

Write-Host "`n--- Baseline established ($($baselineHashes.Count) files) ---`n" -ForegroundColor Gray

# ================================================================
# TEST 1: Pure noise injection (no real changes)
# Different printer, different checksum, different NameMap
# After stripping: files should be IDENTICAL to baseline
# ================================================================
Write-Host "TEST 1: Pure noise - different machine exports same DB" -ForegroundColor Yellow
Write-Host "  Scenario: User opens DB on a different PC (different printer)" -ForegroundColor Gray

$test1Dir = Join-Path $testRoot "test1-pure-noise"
Copy-Item $originalSourceDir $test1Dir -Recurse

# Inject different printer noise into Customer form
$custForm = Join-Path $test1Dir "forms\frmCustomerEntry.txt"
$content = Get-Content $custForm -Raw

# Replace with different printer blob (simulating different machine)
$content = $content -replace '(?s)(PrtMip = Begin\r?\n).*?(End)', @'
PrtMip = Begin
        0xb1160000b1160000b1160000b11600000000000000000000000000000000
        0x1111111111111111111111111111111111111111111111111111111111111111
        0x2222222222222222222222222222222222222222222222222222222222222222
        0x333333333333333333333333
    End
'@

$content = $content -replace '(?s)(PrtDevMode = Begin\r?\n).*?(End)', @'
PrtDevMode = Begin
        0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
        0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB
        0x43006100
    End
'@

$content = $content -replace '(?s)(PrtDevNames = Begin\r?\n).*?(End)', @'
PrtDevNames = Begin
        0x0800180038000100000000004800500020004f006600660069006300650000
        0x4a006500740020005000720069006e007400650072000000000000000000
    End
'@

# Different checksum
$content = $content -replace 'Checksum =.*', 'Checksum =5555555555'

# Different NameMap
$content = $content -replace '(?s)(NameMap = Begin\r?\n).*?(End)', @'
NameMap = Begin
        0xDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD
        0xEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
        0xFFFFFFFFFFFF
    End
'@

# Add DatasheetFont noise
$content = $content -replace '(DatasheetFontHeight =)\d+', 'DatasheetFontHeight =13'
$content = $content -replace '(DatasheetFontWeight =)\d+', 'DatasheetFontWeight =700'

Set-Content $custForm -Value $content -NoNewline

# Strip noise
& $stripScript -Path $test1Dir -ConfigPath $configPath

# Compare
$test1Clean = $true
Get-ChildItem $test1Dir -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName).Hash
    if ($baselineHashes[$_.Name] -and $hash -ne $baselineHashes[$_.Name]) {
        $test1Clean = $false
        Write-Host "    DIFF in $($_.Name)" -ForegroundColor Red
    }
}
Write-TestResult "Pure noise injection produces zero diff" $test1Clean

# ================================================================
# TEST 2: Real change + noise (add a new button to form)
# After stripping: only the new button should differ
# ================================================================
Write-Host "`nTEST 2: Real change + noise - user adds a button on different PC" -ForegroundColor Yellow

$test2Dir = Join-Path $testRoot "test2-real-change-plus-noise"
Copy-Item $originalSourceDir $test2Dir -Recurse

$custForm2 = Join-Path $test2Dir "forms\frmCustomerEntry.txt"
$content2 = Get-Content $custForm2 -Raw

# Inject noise (different printer, checksum, NameMap)
$content2 = $content2 -replace 'Checksum =.*', 'Checksum =-9999999'
$content2 = $content2 -replace '(?s)(PrtMip = Begin\r?\n).*?(End)', @'
PrtMip = Begin
        0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC
    End
'@
$content2 = $content2 -replace '(DatasheetFontHeight =)\d+', 'DatasheetFontHeight =9'

# REAL CHANGE: Add a new "Cancel" button after the Save button
$newButton = @"
        Begin CommandButton
            OverlapFlags =85
            Left =2700
            Top =3600
            Width =2000
            Height =450
            TabIndex =4
            Name ="cmdCancel"
            Caption ="Cancel"
            OnClick ="[Event Procedure]"
        End
"@

# Insert the new button by finding the cmdSave End block and appending after it
$lines2 = $content2 -split "`r?`n"
$insertAfter = -1
$inCmdSave = $false
for ($i = 0; $i -lt $lines2.Count; $i++) {
    if ($lines2[$i] -match 'Name ="cmdSave"') { $inCmdSave = $true }
    if ($inCmdSave -and $lines2[$i] -match '^\s+End\s*$') {
        $insertAfter = $i
        break
    }
}
if ($insertAfter -gt 0) {
    $lines2 = $lines2[0..$insertAfter] + $newButton.Split("`n") + $lines2[($insertAfter+1)..($lines2.Count-1)]
}
$content2 = $lines2 -join "`r`n"

Set-Content $custForm2 -Value $content2 -NoNewline

# Strip noise
& $stripScript -Path $test2Dir -ConfigPath $configPath

# The customer form SHOULD differ (we added a button), but ONLY by the button
$custFormBaseline = Join-Path $baselineDir "forms\frmCustomerEntry.txt"
$baseContent = Get-Content $custFormBaseline
$newContent = Get-Content $custForm2

$diffLines = Compare-Object $baseContent $newContent
$hasCmdCancel = $diffLines | Where-Object { $_.InputObject -match 'cmdCancel|Cancel' }
$hasNoise = $diffLines | Where-Object { $_.InputObject -match 'PrtMip|PrtDevMode|Checksum|NameMap|DatasheetFont' }

Write-TestResult "Real change (new button) is preserved" ($null -ne $hasCmdCancel -and ($hasCmdCancel | Measure-Object).Count -gt 0)
Write-TestResult "Noise is stripped despite real changes present" ($null -eq $hasNoise -or ($hasNoise | Measure-Object).Count -eq 0) "Noise lines in diff: $(($hasNoise | Measure-Object).Count)"

# ================================================================
# TEST 3: Module change + form noise (no form changes)
# After stripping: only module should differ, forms should be clean
# ================================================================
Write-Host "`nTEST 3: Module edit + form noise only - user edits code, form auto-regenerates" -ForegroundColor Yellow

$test3Dir = Join-Path $testRoot "test3-module-change-form-noise"
Copy-Item $originalSourceDir $test3Dir -Recurse

# Add noise to BOTH forms (simulates Access re-exporting everything)
foreach ($formFile in (Get-ChildItem (Join-Path $test3Dir "forms") -Filter "*.txt")) {
    $fc = Get-Content $formFile.FullName -Raw
    $fc = $fc -replace 'Checksum =.*', 'Checksum =1111111'
    $fc = $fc -replace '(?s)(PrtDevMode = Begin\r?\n).*?(End)', @'
PrtDevMode = Begin
        0x4444444444444444444444444444444444444444444444444444444444444444
        0x5555555555555555555555555555555555555555555555555555555555555555
    End
'@
    $fc = $fc -replace '(DatasheetFontWeight =)\d+', 'DatasheetFontWeight =300'
    Set-Content $formFile.FullName -Value $fc -NoNewline
}

# REAL CHANGE: Add a new function to the module
$modFile = Join-Path $test3Dir "modules\modUtilities.bas"
$modContent = Get-Content $modFile -Raw
$newFunction = @'


Public Function CalculateDiscount(ByVal dblTotal As Double, ByVal intPercent As Integer) As Double
    ' Calculate discount amount
    If intPercent < 0 Or intPercent > 100 Then
        CalculateDiscount = 0
    Else
        CalculateDiscount = dblTotal * (intPercent / 100)
    End If
End Function
'@
$modContent += $newFunction
Set-Content $modFile -Value $modContent -NoNewline

# Strip noise
& $stripScript -Path $test3Dir -ConfigPath $configPath

# Check forms are identical to baseline
$formsClean = $true
Get-ChildItem (Join-Path $test3Dir "forms") -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName).Hash
    if ($baselineHashes[$_.Name] -and $hash -ne $baselineHashes[$_.Name]) {
        $formsClean = $false
        Write-Host "    UNEXPECTED form diff: $($_.Name)" -ForegroundColor Red
    }
}

# Check module DID change
$modHash = (Get-FileHash $modFile).Hash
$modChanged = $modHash -ne $baselineHashes["modUtilities.bas"]

Write-TestResult "Forms remain clean (noise only, no real changes)" $formsClean
Write-TestResult "Module change (new function) is preserved" $modChanged

# ================================================================
# TEST 4: Two users, same form, different real changes + different noise
# Simulates the merge scenario
# ================================================================
Write-Host "`nTEST 4: Two users edit same form - both add controls" -ForegroundColor Yellow
Write-Host "  Scenario: User A adds a field, User B adds a button, both on different PCs" -ForegroundColor Gray

# User A's version
$test4aDir = Join-Path $testRoot "test4-userA"
Copy-Item $originalSourceDir $test4aDir -Recurse

$orderFormA = Join-Path $test4aDir "forms\frmOrderManagement.txt"
$contentA = Get-Content $orderFormA -Raw

# User A's noise
$contentA = $contentA -replace 'Checksum =.*', 'Checksum =77777777'
$contentA = $contentA -replace '(?s)(PrtMip = Begin\r?\n).*?(End)', @'
PrtMip = Begin
        0xAAAA0000AAAA0000AAAA0000AAAA00000000000000000000000000000000
    End
'@
$contentA = $contentA -replace '(DatasheetFontHeight =)\d+', 'DatasheetFontHeight =14'

# User A's REAL CHANGE: Add a status textbox after cmdDeleteOrder
$statusField = @"
        Begin TextBox
            OverlapFlags =85
            IMESentenceMode =3
            Left =5500
            Top =2800
            Width =3000
            Height =360
            TabIndex =7
            Name ="txtStatus"
            ControlSource ="Status"
            Begin
                Begin Label
                    OverlapFlags =85
                    Left =5500
                    Top =2560
                    Width =1800
                    Height =240
                    Name ="lblStatus"
                    Caption ="Order Status:"
                End
            End
        End
"@
# Insert after cmdDeleteOrder's End block
$linesA = $contentA -split "`r?`n"
$insertA = -1
$inDeleteBtn = $false
for ($i = 0; $i -lt $linesA.Count; $i++) {
    if ($linesA[$i] -match 'Name ="cmdDeleteOrder"') { $inDeleteBtn = $true }
    if ($inDeleteBtn -and $linesA[$i] -match '^\s+End\s*$') {
        $insertA = $i
        break
    }
}
if ($insertA -gt 0) {
    $linesA = $linesA[0..$insertA] + $statusField.Split("`n") + $linesA[($insertA+1)..($linesA.Count-1)]
}
$contentA = $linesA -join "`r`n"
Set-Content $orderFormA -Value $contentA -NoNewline

# User B's version
$test4bDir = Join-Path $testRoot "test4-userB"
Copy-Item $originalSourceDir $test4bDir -Recurse

$orderFormB = Join-Path $test4bDir "forms\frmOrderManagement.txt"
$contentB = Get-Content $orderFormB -Raw

# User B's noise (DIFFERENT printer, checksum, etc.)
$contentB = $contentB -replace 'Checksum =.*', 'Checksum =-33333333'
$contentB = $contentB -replace '(?s)(PrtDevNames = Begin\r?\n).*?(End)', @'
PrtDevNames = Begin
        0x0800180038000100000000004200720069007400680065007200000000
        0x44004300500020004c003300380030000000000000000000000000
    End
'@
$contentB = $contentB -replace '(?s)(NameMap = Begin\r?\n).*?(End)', @'
NameMap = Begin
        0x1111111111111111111111111111111111111111111111111111111111111111
        0x2222222222222222222222222222222222222222222222222222222222222222
    End
'@
$contentB = $contentB -replace '(DatasheetFontWeight =)\d+', 'DatasheetFontWeight =800'

# User B's REAL CHANGE: Add a Print button after cmdDeleteOrder
$printButton = @"
        Begin CommandButton
            OverlapFlags =85
            Left =5100
            Top =8000
            Width =2000
            Height =450
            TabIndex =8
            Name ="cmdPrintOrder"
            Caption ="Print Order"
            OnClick ="[Event Procedure]"
        End
"@
# Insert after cmdDeleteOrder's End block
$linesB = $contentB -split "`r?`n"
$insertB = -1
$inDeleteBtnB = $false
for ($i = 0; $i -lt $linesB.Count; $i++) {
    if ($linesB[$i] -match 'Name ="cmdDeleteOrder"') { $inDeleteBtnB = $true }
    if ($inDeleteBtnB -and $linesB[$i] -match '^\s+End\s*$') {
        $insertB = $i
        break
    }
}
if ($insertB -gt 0) {
    $linesB = $linesB[0..$insertB] + $printButton.Split("`n") + $linesB[($insertB+1)..($linesB.Count-1)]
}
$contentB = $linesB -join "`r`n"
Set-Content $orderFormB -Value $contentB -NoNewline

# Strip both
& $stripScript -Path $test4aDir -ConfigPath $configPath
& $stripScript -Path $test4bDir -ConfigPath $configPath

# Verify User A: has txtStatus, no noise
$cleanA = Get-Content $orderFormA
$aHasStatus = ($cleanA | Where-Object { $_ -match 'txtStatus' }).Count -gt 0
$aHasNoise = ($cleanA | Where-Object { $_ -match 'PrtMip|PrtDevMode|PrtDevNames|Checksum|NameMap|DatasheetFontHeight|DatasheetFontWeight' }).Count -gt 0

# Verify User B: has cmdPrintOrder, no noise
$cleanB = Get-Content $orderFormB
$bHasPrint = ($cleanB | Where-Object { $_ -match 'cmdPrintOrder' }).Count -gt 0
$bHasNoise = ($cleanB | Where-Object { $_ -match 'PrtMip|PrtDevMode|PrtDevNames|Checksum|NameMap|DatasheetFontHeight|DatasheetFontWeight' }).Count -gt 0

Write-TestResult "User A: real change (txtStatus) preserved" $aHasStatus
Write-TestResult "User A: all noise stripped" (-not $aHasNoise) "Noise lines: $(($cleanA | Where-Object { $_ -match 'PrtMip|Checksum|NameMap' }).Count)"
Write-TestResult "User B: real change (cmdPrintOrder) preserved" $bHasPrint
Write-TestResult "User B: all noise stripped" (-not $bHasNoise)

# ================================================================
# TEST 5: dbLongBinary and SummaryInfo noise
# ================================================================
Write-Host "`nTEST 5: dbLongBinary section changes (DocumentMap/SummaryInfo)" -ForegroundColor Yellow

$test5Dir = Join-Path $testRoot "test5-longbinary"
Copy-Item $originalSourceDir $test5Dir -Recurse

$form5 = Join-Path $test5Dir "forms\frmCustomerEntry.txt"
$content5 = Get-Content $form5 -Raw

# Replace SummaryInfo with different blob (this changes every export)
$content5 = $content5 -replace '(?s)(dbLongBinary "SummaryInfo" = Begin\r?\n).*?(End)', @'
dbLongBinary "SummaryInfo" = Begin
        0xAABBCCDDAABBCCDDAABBCCDDAABBCCDDAABBCCDDAABBCCDDAABBCCDDAABBCCDD
        0x1122334411223344112233441122334411223344112233441122334411223344
        0x5566778855667788556677885566778855667788556677885566778855667788
    End
'@

# Also add a DocumentMap blob
$content5 += @'

dbLongBinary "DocumentMap" = Begin
        0xFFEEDDCCFFEEDDCCFFEEDDCCFFEEDDCCFFEEDDCCFFEEDDCCFFEEDDCC
    End
'@

Set-Content $form5 -Value $content5 -NoNewline

& $stripScript -Path $test5Dir -ConfigPath $configPath

$hash5 = (Get-FileHash $form5).Hash
$test5Clean = $hash5 -eq $baselineHashes["frmCustomerEntry.txt"]
Write-TestResult "dbLongBinary SummaryInfo/DocumentMap changes stripped" $test5Clean

# ================================================================
# TEST 6: Repeated round-trip (export → strip → export → strip → export → strip)
# Verifies idempotency - running strip multiple times gives same result
# ================================================================
Write-Host "`nTEST 6: Idempotency - strip is stable across multiple runs" -ForegroundColor Yellow

$test6Dir = Join-Path $testRoot "test6-idempotent"
Copy-Item $originalSourceDir $test6Dir -Recurse

# Run strip 3 times
& $stripScript -Path $test6Dir -ConfigPath $configPath
$hash_run1 = @{}
Get-ChildItem $test6Dir -Recurse -File | ForEach-Object { $hash_run1[$_.Name] = (Get-FileHash $_.FullName).Hash }

& $stripScript -Path $test6Dir -ConfigPath $configPath
$hash_run2 = @{}
Get-ChildItem $test6Dir -Recurse -File | ForEach-Object { $hash_run2[$_.Name] = (Get-FileHash $_.FullName).Hash }

& $stripScript -Path $test6Dir -ConfigPath $configPath
$hash_run3 = @{}
Get-ChildItem $test6Dir -Recurse -File | ForEach-Object { $hash_run3[$_.Name] = (Get-FileHash $_.FullName).Hash }

$idempotent = $true
foreach ($key in $hash_run1.Keys) {
    if ($hash_run1[$key] -ne $hash_run2[$key] -or $hash_run2[$key] -ne $hash_run3[$key]) {
        $idempotent = $false
        Write-Host "    NOT IDEMPOTENT: $key" -ForegroundColor Red
    }
}
Write-TestResult "Strip is idempotent (3 consecutive runs = same output)" $idempotent

# ================================================================
# SUMMARY
# ================================================================
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " RESULTS: $passCount passed, $failCount failed" -ForegroundColor $(if ($failCount -eq 0) { "Green" } else { "Red" })
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test directory: $testRoot" -ForegroundColor Gray

# Cleanup option
if ($failCount -eq 0) {
    Write-Host "`n All tests passed! The noise filter is working correctly." -ForegroundColor Green
    Write-Host " You can safely collaborate on Access databases via Git." -ForegroundColor Green
}
else {
    Write-Host "`n Some tests failed. Review the output above." -ForegroundColor Red
    Write-Host " Test files preserved at: $testRoot" -ForegroundColor Yellow
}

Write-Host ""
