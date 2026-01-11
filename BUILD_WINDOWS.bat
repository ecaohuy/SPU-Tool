@echo off
echo ============================================
echo SPU Tool V1.0 - Windows Build Script
echo Single EXE Version
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install pandas openpyxl numpy click loguru pydantic pyinstaller

echo.
echo [2/3] Building single-file executable...
pyinstaller --clean SPU_Tool_V1.0.spec

echo.
echo [3/3] Done!

echo.
echo ============================================
echo Build complete!
echo.
echo Single EXE location: dist\SPU_Tool_V1.0.exe
echo.
echo NOTE: First startup may be slow as it extracts
echo       files to a temporary directory.
echo ============================================
pause
