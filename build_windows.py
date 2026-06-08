"""
PyInstaller configuration for Windows .exe
Creates a standalone Windows executable
"""

from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import sys
import os

# Main application script
main_script = 'src/ui/pyqt_dashboard.py'

# Data files to include
datas = [
    ('models/', 'models'),
    ('src/ui/assets/', 'src/ui/assets'),
    ('packet_data.json', '.'),
]

# Hidden imports
hiddenimports = [
    'PyQt6',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets',
    'scapy',
    'scapy.all',
    'sklearn',
    'pandas',
    'numpy',
    'joblib',
    'psutil',
    'src.ml.feature_extractor',
    'src.network.basic_sniffer',
    'src.firewall_manager',
    'src.ai.ollama_installer',
    'src.ui.onboarding_wizard',
    'src.ui.user_settings',
    'src.ui.error_handler',
    'src.ui.system_tray',
    'src.ui.notification_manager',
]

# Excluded modules
excludes = [
    'matplotlib',
    'scipy',
    'IPython',
    'jupyter',
    'notebook',
]

# Build configuration
a = Analysis(
    [main_script],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WATCHDOG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/ui/assets/icon.ico' if os.path.exists('src/ui/assets/icon.ico') else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WATCHDOG',
)

# Build one-file executable
exe_onefile = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WATCHDOG',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/ui/assets/icon.ico' if os.path.exists('src/ui/assets/icon.ico') else None,
)
