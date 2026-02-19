@echo off
:: ============================================================
:: setup_venv.bat — Create and populate the conversion pipeline venv
::
:: Run once from the skill directory:
::     cd .agents\skills\access-migration-catalog
::     setup_venv.bat
:: ============================================================

setlocal

set VENV_DIR=%~dp0.venv

echo.
echo  Access Migration — AI-Compatible Converter Setup
echo  =================================================
echo  Skill dir : %~dp0
echo  Venv      : %VENV_DIR%
echo.

:: Check for Python
where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found on PATH. Install Python 3.10+ and retry.
    exit /b 1
)
python --version

:: Create venv if it doesn't exist
if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo.
    echo  Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo  ERROR: Failed to create virtual environment.
        exit /b 1
    )
) else (
    echo  Venv already exists — skipping creation.
)

:: Activate and install
echo.
echo  Installing / upgrading dependencies from requirements.txt...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip --quiet
pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo.
    echo  ERROR: pip install failed. Check requirements.txt and your network.
    exit /b 1
)

echo.
echo  ============================================================
echo   Setup complete!
echo.
echo   To activate the environment in a new shell:
echo     call "%VENV_DIR%\Scripts\activate.bat"
echo.
echo   To run the converter:
echo     python convert_to_ai_compatible.py "path\to\SampleProject"
echo  ============================================================
echo.

endlocal
