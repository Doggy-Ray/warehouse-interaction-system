param([int]$Port=0)
$ErrorActionPreference='Stop'
$ProjectRoot=Split-Path -Parent $PSScriptRoot
$Config=Get-Content -LiteralPath (Join-Path $ProjectRoot 'config\paths.json') -Raw | ConvertFrom-Json
if ($Port -eq 0) {$Port=$Config.port}
$PidPath=Join-Path $ProjectRoot 'server.pid'
try {
 $Existing=Invoke-RestMethod "http://127.0.0.1:$Port/api/health" -TimeoutSec 2
 if ($Existing.application -eq 'warehouse-lab') {Write-Host "应用已运行：http://127.0.0.1:$Port"; exit 0}
} catch {}
$Busy=Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($Busy) {throw "端口 $Port 已占用。可执行 .\scripts\start.ps1 -Port 8766。"}
$Python=(Get-Command python -ErrorAction Stop).Source
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'
$ServerPath=Join-Path $ProjectRoot 'backend\server.py'
$Process=Start-Process -FilePath $Python -ArgumentList @('-B',('"'+$ServerPath+'"'),'--port',"$Port") -WorkingDirectory $ProjectRoot -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $ProjectRoot 'server.log') -RedirectStandardError (Join-Path $ProjectRoot 'server-error.log')
@{pid=$Process.Id;port=$Port;script=$ServerPath;started=(Get-Date).ToString('o')} | ConvertTo-Json | Set-Content -LiteralPath $PidPath -Encoding utf8
for ($Attempt=0;$Attempt -lt 120;$Attempt++) {
 Start-Sleep -Milliseconds 500
 if ($Process.HasExited) {throw ('应用启动失败，请查看 server-error.log；退出码 '+$Process.ExitCode)}
 try {$Health=Invoke-RestMethod "http://127.0.0.1:$Port/api/health" -TimeoutSec 1; if ($Health.pid -eq $Process.Id) {Write-Host "已启动：http://127.0.0.1:$Port / PID $($Process.Id)";exit 0}} catch {}
}
Write-Host '仍在核对上游哈希，请查看 server.log；未强制终止进程。'
