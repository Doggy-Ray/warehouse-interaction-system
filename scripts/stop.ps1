$ErrorActionPreference='Stop'
$ProjectRoot=Split-Path -Parent $PSScriptRoot
$PidPath=Join-Path $ProjectRoot 'server.pid'
if (!(Test-Path -LiteralPath $PidPath)) {Write-Host '没有本项目 PID 记录。';exit 0}
$Record=Get-Content -LiteralPath $PidPath -Raw | ConvertFrom-Json
$Process=Get-Process -Id $Record.pid -ErrorAction SilentlyContinue
if (!$Process) {Remove-Item -LiteralPath $PidPath;Write-Host '本项目进程已退出。';exit 0}
$Health=Invoke-RestMethod "http://127.0.0.1:$($Record.port)/api/health" -TimeoutSec 3
if ($Health.pid -ne $Record.pid -or $Health.application -ne 'warehouse-lab' -or $Health.project -ne $ProjectRoot) {throw '无法确认 PID 属于本项目，拒绝停止。'}
Stop-Process -Id $Record.pid
Remove-Item -LiteralPath $PidPath
Write-Host "已停止本项目 PID $($Record.pid)"
