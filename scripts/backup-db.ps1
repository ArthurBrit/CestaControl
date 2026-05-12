$ErrorActionPreference = "Stop"

$ProjectDir = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectDir

$DbPath = Join-Path $ProjectDir "data\cestacontrol.db"
$BackupDir = Join-Path $ProjectDir "backups"

if (-not (Test-Path $DbPath)) {
    Write-Host "Banco nao encontrado em $DbPath"
    exit 1
}

New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupPath = Join-Path $BackupDir "cestacontrol-$Timestamp.db"

if (Test-Path ".venv\Scripts\python.exe") {
    .\.venv\Scripts\python.exe -c "import sqlite3, sys; src, dst = sys.argv[1], sys.argv[2]; source = sqlite3.connect(src); target = sqlite3.connect(dst); source.backup(target); target.close(); source.close()" $DbPath $BackupPath
} else {
    Copy-Item $DbPath $BackupPath
}

Write-Host "Backup criado em:"
Write-Host $BackupPath
