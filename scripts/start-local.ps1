param([string]$Workspace = "", [string]$AlignmentConfig = "", [switch]$Setup, [ValidateRange(1,65535)][int]$Port = 8765)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'Install uv and Python 3.11, then run this script with -Setup. See docs/windows-setup.md.' }
if ($Setup) {
    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { throw 'Install Node.js 24 with npm before setup.' }
    uv sync --locked
    if ($LASTEXITCODE -ne 0) { throw 'Python dependency sync failed.' }
    npm --prefix frontend ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency install failed.' }
    npm --prefix frontend run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} elseif (-not (Test-Path -LiteralPath '.venv/Scripts/python.exe') -or -not (Test-Path -LiteralPath 'frontend/dist/index.html')) {
    throw 'First-time setup required: run .\scripts\start-local.ps1 -Setup.'
}
$launchArguments = @('run', '--locked', '--no-sync', 'taketwo-web', '--port', "$Port")
if ($Workspace) { $launchArguments += @('--workspace', $Workspace) }
if ($AlignmentConfig) { $launchArguments += @('--alignment-config', $AlignmentConfig) }
Write-Output "Open http://127.0.0.1:$Port. Stop with Ctrl+C. Recordings stay local."
uv @launchArguments
if ($LASTEXITCODE -ne 0) { throw 'TakeTwo could not start. Review the prerequisite or port message above.' }
