@echo off
cd /d "%~dp0"

echo --------------------------------------------------
echo OneStepUpdate Build Script (Minimal Env)
echo --------------------------------------------------

:: 1. Clean old env if exists to ensure fresh start
if exist "env" (
    echo [INFO] Removing existing environment to ensure clean build...
    rmdir /s /q env
)

:: 2. Create Venv
echo [INFO] Creating virtual environment 'env'...
python -m venv env
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create venv. Check python installation.
    pause
    exit /b %errorlevel%
)

:: 3. Activate Venv
echo [INFO] Activating virtual environment...
call env\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate venv.
    pause
    exit /b %errorlevel%
)

:: Double check python path
where python
echo [INFO] Ensure above path is inside 'env'.

:: 4. Install Dependencies
echo [INFO] Installing requirements in virtual environment...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements.
    pause
    exit /b %errorlevel%
)

:: 5. Cleanup Build Artifacts
echo [INFO] Cleaning up previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist OneStepUpdate.spec del OneStepUpdate.spec

:: 6. Build
echo [INFO] Building Executable...
:: --noconsole: No terminal window
:: --onefile: Single .exe
:: --icon: Window/Taskbar icon
:: --add-data: Include icon file in internal resources (critical for runtime icon)
pyinstaller --noconsole --onefile --name "OneStepUpdate" --icon "OneStepUpdate.ico" --add-data "OneStepUpdate.ico;." --add-data "onestepupdate.png;." --collect-all customtkinter OneStepUpdate.py

echo.
echo [SUCCESS] Build complete.
echo Location: %~dp0dist\OneStepUpdate.exe
pause
