# Prepara el proyecto en un PC nuevo (Windows).
#
# Uso (desde la raíz del repo):
#     powershell -ExecutionPolicy Bypass -File setup.ps1
# o doble clic en setup.bat.
#
# Es idempotente: se puede volver a ejecutar sin romper nada, solo instala
# lo que falte y aplica las migraciones pendientes.

$ErrorActionPreference = 'Stop'
$Raiz = $PSScriptRoot
$DirDjango = Join-Path $Raiz 'Django'
$DirFront = Join-Path $Raiz 'frontend'

function Paso($texto) { Write-Host "`n==> $texto" -ForegroundColor Cyan }

# Tras instalar algo con winget, la sesión actual no ve el PATH nuevo hasta
# que se abre otra terminal; se relee del registro para seguir sin reiniciar.
function Actualizar-Path {
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' +
                [Environment]::GetEnvironmentVariable('Path', 'User')
}

# Por si algo se instaló después de abrir la terminal desde la que se lanza.
Actualizar-Path

function Instalar-ConWinget($id) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw "No se encontró winget. Instala $id a mano y vuelve a ejecutar este script."
    }
    winget install -e --id $id --accept-source-agreements --accept-package-agreements --silent
    Actualizar-Path
}

# Devuelve la versión de Python como [version], o $null si el comando no es
# un Python real (en Windows 'python' puede ser el acceso directo a la Store).
function Version-Python($cmd, $argsExtra) {
    try {
        $v = & $cmd @argsExtra -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
        if ($LASTEXITCODE -eq 0 -and $v) { return [version]$v }
    } catch {}
    return $null
}

# --- Python (Django 6 exige 3.12 o superior) --------------------------------
Paso 'Comprobando Python'
$PythonMin = [version]'3.12'

function Buscar-Python {
    foreach ($c in @(@('py', @('-3')), @('python', @()))) {
        if (Get-Command $c[0] -ErrorAction SilentlyContinue) {
            $v = Version-Python $c[0] $c[1]
            if ($v -and $v -ge $PythonMin) { return ,$c }
        }
    }
    return $null
}

$python = Buscar-Python
if (-not $python) {
    Write-Host "No hay Python >= $PythonMin. Instalándolo con winget..."
    Instalar-ConWinget 'Python.Python.3.13'
    $python = Buscar-Python
    if (-not $python) { throw 'Python se instaló pero no aparece en el PATH. Abre otra terminal y vuelve a ejecutar el script.' }
}
Write-Host "Python $(Version-Python $python[0] $python[1]) OK"

# --- Node.js (Angular 22 exige 22 o superior) -------------------------------
Paso 'Comprobando Node.js'
$NodeMin = 22

function Version-Node {
    if (-not (Get-Command node -ErrorAction SilentlyContinue)) { return 0 }
    return [int]((node -v).TrimStart('v').Split('.')[0])
}

if ((Version-Node) -lt $NodeMin) {
    Write-Host "No hay Node.js >= $NodeMin. Instalando la versión LTS con winget..."
    Instalar-ConWinget 'OpenJS.NodeJS.LTS'
    if ((Version-Node) -lt $NodeMin) { throw 'Node.js se instaló pero no aparece en el PATH. Abre otra terminal y vuelve a ejecutar el script.' }
}
Write-Host "Node.js $(node -v) OK"

# --- Backend ----------------------------------------------------------------
Paso 'Backend: entorno virtual y dependencias'
$venvPython = Join-Path $DirDjango '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    & $python[0] @($python[1]) -m venv (Join-Path $DirDjango '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'No se pudo crear el entorno virtual.' }
}
& $venvPython -m pip install --disable-pip-version-check -q -r (Join-Path $DirDjango 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Falló pip install.' }

Paso 'Backend: migraciones'
Push-Location $DirDjango
try {
    & $venvPython manage.py migrate
    if ($LASTEXITCODE -ne 0) { throw 'Fallaron las migraciones.' }

    # db.sqlite3 no se versiona, así que en un PC nuevo no hay usuarios.
    # 'shell' de Django 6 imprime antes un aviso de autoimportación; solo
    # interesa la última línea.
    $hayAdmin = & $venvPython manage.py shell -c "from django.contrib.auth.models import User; print(User.objects.filter(is_superuser=True).exists())" |
        Select-Object -Last 1
    if ($hayAdmin -ne 'True') {
        Paso 'Backend: crear superusuario (para el login del frontend y el /admin/)'
        & $venvPython manage.py createsuperuser
    }
} finally {
    Pop-Location
}

# --- Frontend ---------------------------------------------------------------
Paso 'Frontend: dependencias de npm'
Push-Location $DirFront
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw 'Falló npm ci.' }
} finally {
    Pop-Location
}

Write-Host "`nTodo listo. Para arrancar los dos servidores: iniciar.bat (o iniciar.ps1)" -ForegroundColor Green
