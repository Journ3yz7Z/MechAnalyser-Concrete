param([string]$Python = 'python', [string]$DistPath = 'dist', [string]$WorkPath = 'build')
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & $Python -m PyInstaller --noconfirm --clean --distpath $DistPath --workpath $WorkPath MechAnalyser-Concrete.spec
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller build failed' }
    $target = Join-Path $DistPath 'MechAnalyser-Concrete'
    Copy-Item -LiteralPath LICENSE,SOURCE_NOTICE.md,README.md,CHANGELOG.md -Destination $target
    Copy-Item -LiteralPath THIRD_PARTY_NOTICES -Destination $target -Recurse
} finally { Pop-Location }
