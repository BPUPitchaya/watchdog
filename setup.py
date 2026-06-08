#!/usr/bin/env python3
"""
Automated Setup Script for WATCHDOG AI Dashboard
Handles all installation steps automatically for non-technical users
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class SetupWizard:
    """Automated setup wizard for WATCHDOG installation"""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "watchdog_env"
        
    def print_header(self):
        """Print setup header"""
        print("=" * 60)
        print("WATCHDOG AI Dashboard - Automated Setup")
        print("=" * 60)
        print(f"System: {self.system}")
        print(f"Python: {self.python_version.major}.{self.python_version.minor}.{self.python_version.micro}")
        print("=" * 60)
        print()
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("Checking Python version...")
        if self.python_version.major < 3 or (self.python_version.major == 3 and self.python_version.minor < 8):
            print("❌ Python 3.8 or higher is required")
            print(f"   Current version: {self.python_version.major}.{self.python_version.minor}")
            return False
        print("✓ Python version compatible")
        return True
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        print("Creating virtual environment...")
        if self.venv_path.exists():
            print("✓ Virtual environment already exists")
            return True
        
        try:
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)], 
                          check=True, capture_output=True)
            print("✓ Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get path to virtual environment Python"""
        if self.system == "Windows":
            return self.venv_path / "Scripts" / "python.exe"
        else:
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get path to virtual environment pip"""
        if self.system == "Windows":
            return self.venv_path / "Scripts" / "pip.exe"
        else:
            return self.venv_path / "bin" / "pip"
    
    def upgrade_pip(self):
        """Upgrade pip in virtual environment"""
        print("Upgrading pip...")
        try:
            subprocess.run([str(self.get_venv_pip()), "install", "--upgrade", "pip"],
                          check=True, capture_output=True)
            print("✓ Pip upgraded")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to upgrade pip: {e}")
            return False
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("Installing dependencies...")
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print("❌ requirements.txt not found")
            return False
        
        try:
            subprocess.run([str(self.get_venv_pip()), "install", "-r", str(requirements_file)],
                          check=True, capture_output=True)
            print("✓ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def check_system_requirements(self):
        """Check system-specific requirements"""
        print("Checking system requirements...")
        
        if self.system == "Darwin":  # macOS
            print("✓ macOS detected")
            print("  Note: Network monitoring requires administrator privileges")
            print("  You will be prompted for permissions when running the application")
        elif self.system == "Windows":
            print("✓ Windows detected")
            print("  Note: Network monitoring requires administrator privileges")
            print("  Run as Administrator when launching the application")
        elif self.system == "Linux":
            print("✓ Linux detected")
            print("  Note: Network monitoring requires sudo privileges")
            print("  Run with sudo when launching the application")
        else:
            print(f"⚠ Unknown system: {self.system}")
        
        return True
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for easy access"""
        print("Creating desktop shortcut...")
        
        if self.system == "Darwin":
            # macOS - create a simple launch script
            launch_script = self.project_root / "launch_watchdog.sh"
            with open(launch_script, 'w') as f:
                f.write(f"""#!/bin/bash
cd "{self.project_root}"
"{self.get_venv_python()}" src/ui/pyqt_dashboard.py
""")
            os.chmod(launch_script, 0o755)
            print("✓ Launch script created: launch_watchdog.sh")
            
        elif self.system == "Windows":
            # Windows - create batch file
            launch_script = self.project_root / "launch_watchdog.bat"
            with open(launch_script, 'w') as f:
                f.write(f"""@echo off
cd /d "{self.project_root}"
"{self.get_venv_python()}" src/ui/pyqt_dashboard.py
""")
            print("✓ Launch script created: launch_watchdog.bat")
            
        elif self.system == "Linux":
            # Linux - create launch script
            launch_script = self.project_root / "launch_watchdog.sh"
            with open(launch_script, 'w') as f:
                f.write(f"""#!/bin/bash
cd "{self.project_root}"
"{self.get_venv_python()}" src/ui/pyqt_dashboard.py
""")
            os.chmod(launch_script, 0o755)
            print("✓ Launch script created: launch_watchdog.sh")
        
        return True
    
    def create_quick_start_guide(self):
        """Create quick start guide"""
        print("Creating quick start guide...")
        
        guide_content = """# WATCHDOG AI Dashboard - Quick Start Guide

## How to Launch

### macOS:
```bash
./launch_watchdog.sh
```

### Windows:
Double-click `launch_watchdog.bat`

### Linux:
```bash
./launch_watchdog.sh
```

## First Time Setup

1. Launch the application using the launch script
2. You'll see a splash screen (5 seconds)
3. Accept the Terms & Conditions
4. Complete the onboarding wizard (first time only)
5. Start monitoring your network!

## Permissions

The application requires administrator privileges for network monitoring:
- **macOS**: You'll be prompted for your password
- **Windows**: Run as Administrator
- **Linux**: Use sudo

## Features

- Real-time network packet monitoring
- AI-powered threat detection
- System tray icon for background monitoring
- Desktop notifications for security alerts
- Local-only - no cloud sync or data transmission

## Troubleshooting

If you encounter issues:
1. Make sure you're running with administrator privileges
2. Check that all dependencies are installed
3. Try deleting the `local_settings.json` file to reset settings

## Support

For issues or questions, please refer to the main README.md file.
"""
        
        guide_file = self.project_root / "QUICK_START.md"
        with open(guide_file, 'w') as f:
            f.write(guide_content)
        
        print("✓ Quick start guide created: QUICK_START.md")
        return True
    
    def run_setup(self):
        """Run complete setup process"""
        self.print_header()
        
        steps = [
            ("Python Version Check", self.check_python_version),
            ("System Requirements Check", self.check_system_requirements),
            ("Virtual Environment Creation", self.create_virtual_environment),
            ("Pip Upgrade", self.upgrade_pip),
            ("Dependency Installation", self.install_dependencies),
            ("Desktop Shortcut Creation", self.create_desktop_shortcut),
            ("Quick Start Guide Creation", self.create_quick_start_guide),
        ]
        
        failed_steps = []
        for step_name, step_func in steps:
            try:
                if not step_func():
                    failed_steps.append(step_name)
            except Exception as e:
                print(f"❌ {step_name} failed with error: {e}")
                failed_steps.append(step_name)
        
        print()
        print("=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        
        if failed_steps:
            print(f"⚠ {len(failed_steps)} step(s) failed:")
            for step in failed_steps:
                print(f"  - {step}")
            print()
            print("Please resolve the issues above and run setup again.")
            return False
        else:
            print("✓ All steps completed successfully!")
            print()
            print("To launch WATCHDOG:")
            if self.system == "Windows":
                print("  Double-click: launch_watchdog.bat")
            else:
                print("  Run: ./launch_watchdog.sh")
            print()
            print("For more information, see QUICK_START.md")
            return True


def main():
    """Main entry point"""
    wizard = SetupWizard()
    success = wizard.run_setup()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
