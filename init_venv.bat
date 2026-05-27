@echo off

echo Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe ou introuvable dans le PATH
    pause
    exit /b 1
)

set VENV_DIR=venv

echo.
echo Creation de l'environnement virtuel...

if not exist "%VENV_DIR%" (
    python -m venv %VENV_DIR%
    echo Environnement virtuel cree
) else (
    echo Environnement virtuel deja existant
)

echo.
echo Activation de l'environnement virtuel...
call %VENV_DIR%\Scripts\activate.bat

echo.
echo Mise a jour de pip...
python -m pip install --upgrade pip

echo.
echo Environnement pret

cmd /k