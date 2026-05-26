param(
    [switch]$ClientOnly,
    [switch]$ServerOnly,
    [switch]$Clean
)

function Write-Header  { param($msg) Write-Host "======================================" -ForegroundColor Cyan; Write-Host "  $msg" -ForegroundColor Cyan; Write-Host "======================================" -ForegroundColor Cyan }
function Write-Step    { param($msg) Write-Host "  >> $msg" -ForegroundColor Yellow }
function Write-Success { param($msg) Write-Host "  [OK] $msg" -ForegroundColor Green }
function Write-Fail    { param($msg) Write-Host "  [FAIL] $msg" -ForegroundColor Red }

$Root         = Split-Path -Parent $MyInvocation.MyCommand.Path
$ClientDir    = Join-Path $Root "client"
$ServerDir    = Join-Path $Root "server"
$SharedDir    = Join-Path $Root "shared"
$DistDir      = Join-Path $Root "dist"
$BuildDir     = Join-Path $Root "build"
$ClientMain   = Join-Path $ClientDir "main.py"
$ServerMain   = Join-Path $ServerDir "main.py"
$ClientAssets = Join-Path $ClientDir "assets"
$PythonExe    = Join-Path $Root ".venv\Scripts\python.exe"

Write-Header "BUILD - Ursina Game"

if (-not (Test-Path $PythonExe)) {
    Write-Fail "Python venv non trouvé: $PythonExe"
    exit 1
}

$pyVersion = & $PythonExe --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fail "Python introuvable."; exit 1 }
Write-Success "Python: $pyVersion"

& $PythonExe -m pip show nuitka 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Step "Installation de Nuitka..."
    & $PythonExe -m pip install nuitka zstandard
    if ($LASTEXITCODE -ne 0) { Write-Fail "Echec installation Nuitka."; exit 1 }
}
Write-Success "Nuitka OK"

if ($Clean) {
    if (Test-Path $DistDir)  { Remove-Item $DistDir  -Recurse -Force }
    if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
    Write-Success "Nettoyage termine."
}

function Build-Exe {
    param([string]$Name, [string]$MainScript, [string]$SourceDir, [string]$AssetsDir)

    Write-Header "Build : $Name.exe"

    if (-not (Test-Path $MainScript)) { Write-Fail "main.py introuvable : $MainScript"; return $false }

    # Prepare output directory
    if (-not (Test-Path $DistDir)) { New-Item -ItemType Directory -Path $DistDir | Out-Null }

    $nuitkaArgs = @(
        "--output-dir=$DistDir",
        "--remove-output",
        "--follow-imports",
        "--include-package=ursina",
        "--include-package=panda3d",
        "--include-package=shared",
        "--include-package=client",
        "--include-package=server",
        "--include-data-dir=$(Split-Path -Parent $MainScript)/assets=assets",
        "--include-data-dir=$SharedDir=shared"
    )

    # Add Windows-specific options
    if ($Name -eq "client") {
        $nuitkaArgs += "--windows-console-mode=hide"
    }

    # Include Ursina assets
    $ursinaAssets = & $PythonExe -c "import ursina,os; print(os.path.join(os.path.dirname(ursina.__file__),'assets'))" 2>$null
    if ($ursinaAssets -and (Test-Path $ursinaAssets)) {
        $nuitkaArgs += "--include-data-dir=$ursinaAssets=ursina/assets"
        Write-Success "Ursina assets: $ursinaAssets"
    }

    $nuitkaArgs += $MainScript

    Push-Location $Root
    Write-Step "Compilation Nuitka..."
    & $PythonExe -m nuitka $nuitkaArgs
    $exitCode = $LASTEXITCODE
    Pop-Location

    $exePath = Join-Path $DistDir "$Name.exe"
    # Check in subdirectory if onefile wasn't used
    if (-not (Test-Path $exePath)) {
        $exePath = Join-Path $DistDir "$Name" "$Name.exe"
    }
    if ($exitCode -eq 0 -and (Test-Path $exePath)) {
        Write-Success "$Name.exe genere avec succes !"
        return $true
    }
    Write-Fail "Echec build $Name.exe"
    return $false
}

$results = @{}
if (-not $ServerOnly) { $results["client"] = Build-Exe -Name "client" -MainScript $ClientMain -SourceDir $ClientDir -AssetsDir $ClientAssets }
if (-not $ClientOnly) { $results["server"] = Build-Exe -Name "server" -MainScript $ServerMain -SourceDir $ServerDir -AssetsDir "" }

Write-Header "Resume"
foreach ($key in $results.Keys) {
    if ($results[$key]) { Write-Success "$key.exe : OK" } else { Write-Fail "$key.exe : ECHEC" }
}
Write-Host "Executables dans : $DistDir" -ForegroundColor Cyan
