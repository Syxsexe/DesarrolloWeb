# Arranca backend y frontend, cada uno en su propia ventana.
# Requiere haber ejecutado antes setup.ps1.
#
#   Backend  (Django)  -> http://127.0.0.1:8000
#   Frontend (Angular) -> http://localhost:4200  (reenvía /api al backend)

$Raiz = $PSScriptRoot
$venvPython = Join-Path $Raiz 'Django\.venv\Scripts\python.exe'

if (-not (Test-Path $venvPython) -or -not (Test-Path (Join-Path $Raiz 'frontend\node_modules'))) {
    Write-Host 'Falta instalar dependencias. Ejecuta primero setup.bat (o setup.ps1).' -ForegroundColor Yellow
    exit 1
}

# Las ventanas nuevas heredan el PATH de esta; se relee del registro por si
# Node se instaló (con setup.ps1) después de abrir la terminal actual.
$env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
            [Environment]::GetEnvironmentVariable('Path', 'User')

Start-Process powershell -WorkingDirectory (Join-Path $Raiz 'Django') -ArgumentList @(
    '-NoExit', '-Command', "`$Host.UI.RawUI.WindowTitle = 'Backend :8000'; & '$venvPython' manage.py runserver 127.0.0.1:8000"
)
Start-Process powershell -WorkingDirectory (Join-Path $Raiz 'frontend') -ArgumentList @(
    '-NoExit', '-Command', "`$Host.UI.RawUI.WindowTitle = 'Frontend :4200'; npm start -- --port 4200 --open"
)

Write-Host 'Backend en http://127.0.0.1:8000 y frontend en http://localhost:4200 (se abrirá el navegador al compilar).'
Write-Host 'Para pararlos, cierra sus ventanas.'
