@echo off
REM Build script for Windows executable
REM This script creates a standalone .exe for WATCHDOG
REM Usage: build_windows.bat

echo ==========================================
echo WATCHDOG Windows Application Builder
echo ==========================================

REM Check if virtual environment exists
if not exist "watchdog_env" (
    echo Error: Virtual environment not found. Please create it first:
    echo   python -m venv watchdog_env
    echo   watchdog_env\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call watchdog_env\Scripts\activate.bat

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Create build directory
if not exist "build" mkdir build

echo Building Windows executable...

REM Build the application
python -m PyInstaller --onedir ^
    --windowed ^
    --name "Watchdog" ^
    --add-data "src;src" ^
    --add-data "models;models" ^
    --add-data "data;data" ^
    --add-data "src\ui\assets;assets" ^
    --hidden-import=scapy.all ^
    --hidden-import=sklearn.ensemble ^
    --hidden-import=sklearn.utils ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtGui ^
    --hidden-import=PyQt6.QtWidgets ^
    --distpath=dist ^
    --workpath=build ^
    src\ui\pyqt_dashboard.py

echo ==========================================
echo Build completed successfully!
echo ==========================================
echo Application location: dist\Watchdog
echo.
echo To run the application:
echo   dist\Watchdog\Watchdog.exe
echo.
echo Note: Run as Administrator for packet capture functionality.
