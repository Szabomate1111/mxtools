$REPO_USER  = "Szabomate1111"
$REPO_ZIP   = "https://github.com/$REPO_USER/mxtools/archive/refs/heads/main.zip"
$INSTALL_DIR = "$env:LOCALAPPDATA\mxtools"
$BIN_DIR     = "$env:LOCALAPPDATA\mxtools\bin"

function Write-Step { param($m) Write-Host "  -> $m" -ForegroundColor Cyan }
function Write-Ok   { param($m) Write-Host "  OK $m" -ForegroundColor Green }
function Write-Warn { param($m) Write-Host "  !  $m" -ForegroundColor Yellow }
function Write-Fail { param($m) Write-Host "  X  $m" -ForegroundColor Red; exit 1 }

Write-Host @"
 __  __      _              _
|  \/  |    | |            | |
| \  / |_  _| |_ ___   ___ | |___
| |\/| \ \/ / __/ _ \ / _ \| / __|
| |  | |>  <| || (_) | (_) | \__ \
|_|  |_/_/\_\__\___/ \___/|_|___/
"@ -ForegroundColor Cyan
Write-Host "  Installer - mxtools`n"

Write-Step "Looking for Python..."
$PY = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3\.(\d+)") {
            if ([int]$Matches[1] -ge 8) { $PY = $cmd; Write-Ok "Python: $ver"; break }
        }
    } catch {}
}
if (-not $PY) {
    Write-Fail "Python 3.8+ not found. Download it at: https://www.python.org/downloads/"
}

Write-Step "Checking pip..."
$null = & $PY -m pip --version 2>&1
if ($LASTEXITCODE -ne 0) { Write-Fail "pip not available. Run: $PY -m ensurepip" }
Write-Ok "pip available"

Write-Step "Downloading mxtools..."
$tmpZip = "$env:TEMP\mxtools_install.zip"
$tmpDir = "$env:TEMP\mxtools_extract"
try {
    Invoke-WebRequest -Uri $REPO_ZIP -OutFile $tmpZip -UseBasicParsing
} catch {
    Write-Fail "Download failed: $_"
}

if (Test-Path $tmpDir) { Remove-Item $tmpDir -Recurse -Force }
Expand-Archive -Path $tmpZip -DestinationPath $tmpDir -Force
$extracted = (Get-ChildItem $tmpDir -Directory | Select-Object -First 1).FullName

if (Test-Path $INSTALL_DIR) { Remove-Item $INSTALL_DIR -Recurse -Force }
New-Item -ItemType Directory -Force -Path $BIN_DIR | Out-Null
Copy-Item -Path "$extracted\*" -Destination $INSTALL_DIR -Recurse -Force
Write-Ok "Files copied to: $INSTALL_DIR"

$bat = "@echo off`r`nset PYTHONPATH=$INSTALL_DIR`r`n$PY -m mxtools %*"
Set-Content -Path "$BIN_DIR\mxtools.bat" -Value $bat -Encoding ASCII
Write-Ok "Launcher: $BIN_DIR\mxtools.bat"

Write-Step "Updating PATH..."
$userPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($userPath -notlike "*$BIN_DIR*") {
    [System.Environment]::SetEnvironmentVariable("PATH", "$BIN_DIR;$userPath", "User")
    Write-Ok "PATH updated: $BIN_DIR"
} else {
    Write-Ok "PATH already contains this directory"
}

Remove-Item $tmpZip -Force -ErrorAction SilentlyContinue
Remove-Item $tmpDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "  mxtools installed!" -ForegroundColor Green
Write-Host ""
Write-Host "  Run: " -NoNewline; Write-Host "mxtools" -ForegroundColor Cyan
Write-Host "  Open a new terminal and it will work." -ForegroundColor Yellow
Write-Host ""
