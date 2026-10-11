param([string]$Workspace = "", [string]$AlignmentConfig = "")
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
uv sync --locked
if ($LASTEXITCODE -ne 0) { throw 'Python dependency sync failed.' }
npm --prefix frontend ci
if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency install failed.' }
npm --prefix frontend run build
if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
$launchArguments = @('run', 'taketwo-web')
if ($Workspace) { $launchArguments += @('--workspace', $Workspace) }
if ($AlignmentConfig) { $launchArguments += @('--alignment-config', $AlignmentConfig) }
uv @launchArguments
