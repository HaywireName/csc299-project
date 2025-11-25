@echo off
REM PKMS Task Manager Installation Script for Windows
REM This script sets up the environment and installs all dependencies

echo ================================
echo PKMS Task Manager Installation
echo ================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%
echo.

REM Check if version is 3.9+
python -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"
if %errorlevel% neq 0 (
    echo Error: Python 3.9 or higher is required
    echo Current version: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
if exist venv\ (
    echo Virtual environment already exists
) else (
    python -m venv venv
    echo Virtual environment created
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo Pip upgraded
echo.

REM Install dependencies
echo Installing dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    echo Dependencies installed
) else (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)
echo.

REM Create data directories
echo Creating data directories...
if not exist data\docs\pdfs mkdir data\docs\pdfs
if not exist data\docs\docx mkdir data\docs\docx
if not exist data\docs\txt mkdir data\docs\txt
if not exist data\doc_cache mkdir data\doc_cache
if not exist data\backups mkdir data\backups
if not exist exports mkdir exports
echo Data directories created
echo.

REM Check for API key
echo Checking for OpenAI API key...
if "%OPENAI_API_KEY%"=="" (
    echo Warning: OpenAI API key not found
    echo.
    echo To use AI features, you need to set your OpenAI API key:
    echo.
    echo   For current session ^(PowerShell^):
    echo     $env:OPENAI_API_KEY="sk-your-key-here"
    echo.
    echo   For current session ^(Command Prompt^):
    echo     set OPENAI_API_KEY=sk-your-key-here
    echo.
    echo   For permanent setup ^(System Environment Variables^):
    echo     1. Open System Properties ^> Environment Variables
    echo     2. Add new User Variable: OPENAI_API_KEY
    echo     3. Value: sk-your-key-here
    echo     4. Restart your terminal
    echo.
    echo Get your API key at: https://platform.openai.com/api-keys
) else (
    echo OpenAI API key found
)
echo.

echo ================================
echo Installation Complete!
echo ================================
echo.
echo Next steps:
echo.
echo 1. Activate the virtual environment ^(if not already active^):
echo    venv\Scripts\activate
echo.
echo 2. Set your OpenAI API key ^(if not already set^):
echo    PowerShell: $env:OPENAI_API_KEY="sk-your-key-here"
echo    CMD:        set OPENAI_API_KEY=sk-your-key-here
echo.
echo 3. Run the application:
echo    python main.py
echo.
echo For help, see:
echo   - README.md for overview
echo   - USER_GUIDE.md for tutorials
echo   - COMMANDS.md for command reference
echo.
echo Happy organizing! 🚀
echo.
pause
