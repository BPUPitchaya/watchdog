#!/bin/bash

# Build script for macOS application bundle
# This script creates a standalone .app bundle for WATCHDOG
# Usage: ./build_macos.sh

echo "=========================================="
echo "WATCHDOG macOS Application Builder"
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "watchdog_env" ]; then
    echo "Error: Virtual environment not found. Please create it first:"
    echo "  python3 -m venv watchdog_env"
    echo "  source watchdog_env/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment without triggering logger
echo "Activating virtual environment..."
export PATH="$PWD/watchdog_env/bin:$PATH"
export PYTHONPATH="$PWD/watchdog_env/lib/python3.14/site-packages:$PYTHONPATH"

# Check if PyInstaller is installed
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Create build directory
mkdir -p build

echo "Building macOS application bundle..."

# Build the application
python -m PyInstaller --onedir \
    --windowed \
    --name "Watchdog" \
    --add-data "src:src" \
    --add-data "models:models" \
    --add-data "data:data" \
    --add-data "src/ui/assets:assets" \
    --hidden-import=scapy.all \
    --hidden-import=sklearn.ensemble \
    --hidden-import=sklearn.utils \
    --hidden-import=PyQt6.QtCore \
    --hidden-import=PyQt6.QtGui \
    --hidden-import=PyQt6.QtWidgets \
    --osx-bundle-identifier=com.watchdog.security \
    --distpath=dist \
    --workpath=build \
    --icon=src/ui/assets/logo.png \
    --codesign-identity=- \
    src/ui/pyqt_dashboard.py

echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="
echo "Application location: dist/Watchdog.app"
echo ""
echo "Re-signing app bundle for macOS compatibility..."
codesign --force --deep --sign - dist/Watchdog.app
echo "Removing quarantine attributes..."
xattr -cr dist/Watchdog.app
echo ""
echo "To run the application:"
echo "  open dist/Watchdog.app"
echo ""
echo "Or run directly:"
echo "  ./dist/Watchdog.app/Contents/MacOS/Watchdog"
echo ""
echo "For layout-only mode (no packet capture):"
echo "  ./dist/Watchdog.app/Contents/MacOS/Watchdog --layout-only"
