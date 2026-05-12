$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

if (-not (Test-Path ".venv")) {
    Write-Host "Ambiente virtual nao encontrado. Rode primeiro: .\scripts\install-windows.ps1"
    exit 1
}

New-Item -ItemType Directory -Force -Path "data" | Out-Null

$env:HOST = "0.0.0.0"
$env:PORT = "8000"
$env:RELOAD = "false"

Write-Host "CestaControl iniciado."
Write-Host "Neste PC: http://127.0.0.1:8000"
Write-Host "Outros PCs: use um dos enderecos abaixo:"

$Addresses = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
    Select-Object -ExpandProperty IPAddress

foreach ($Address in $Addresses) {
    Write-Host "http://$Address`:8000"
}

Write-Host "Para parar, pressione Ctrl+C nesta janela."
Write-Host ""

.\.venv\Scripts\python.exe run.py
