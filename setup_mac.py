"""
py2app configuration for macOS .app bundle
Creates a standalone macOS application
"""

from setuptools import setup
import py2app
import sys
import os

APP = ['src/ui/pyqt_dashboard.py']
DATA_FILES = [
    'models/',
    'src/ui/assets/',
    'packet_data.json',
]

OPTIONS = {
    'py2app': {
        'argv_emulation': False,
        'iconfile': 'src/ui/assets/icon.icns' if os.path.exists('src/ui/assets/icon.icns') else None,
        'plist': {
            'CFBundleName': 'WATCHDOG AI Dashboard',
            'CFBundleDisplayName': 'WATCHDOG',
            'CFBundleGetInfoString': 'Network Security Monitoring System',
            'CFBundleIdentifier': 'com.watchdog.dashboard',
            'CFBundleVersion': '2.0',
            'CFBundleShortVersionString': '2.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSUIElement': False,
        },
        'packages': [
            'PyQt6',
            'scapy',
            'sklearn',
            'pandas',
            'numpy',
            'joblib',
            'psutil',
        ],
        'includes': [
            'src.ml.feature_extractor',
            'src.network.basic_sniffer',
            'src.firewall_manager',
            'src.ai.ollama_installer',
            'src.ui.onboarding_wizard',
            'src.ui.user_settings',
            'src.ui.error_handler',
            'src.ui.system_tray',
            'src.ui.notification_manager',
        ],
        'excludes': [
            'matplotlib',
            'scipy',
            'IPython',
        ],
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
