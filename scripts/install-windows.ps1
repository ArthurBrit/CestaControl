$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

New-Item -ItemType Directory -Force -Path "data" | Out-Null
New-Item -ItemType Directory -Force -Path "backups" | Out-Null

if (-not (Test-Path ".venv")) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        py -3 -m venv .venv
    } else {
        python -m venv .venv
    }
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    $Secret = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
    (Get-Content ".env") -replace "^SECRET_KEY=.*", "SECRET_KEY=$Secret" | Set-Content ".env"
    Write-Host "Arquivo .env criado. Edite ADMIN_USERNAME e ADMIN_PASSWORD antes de usar em producao."
}

Write-Host ""
Write-Host "Instalacao concluida."
Write-Host "Para iniciar o sistema, execute: .\scripts\start-server.ps1"
