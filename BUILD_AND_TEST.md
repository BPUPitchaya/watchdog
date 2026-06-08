# BUILD AND TESTING GUIDE

This guide explains how to build and test WATCHDOG on different operating systems.

## Prerequisites

### Common Requirements
- Python 3.10 or higher
- pip package manager
- Administrator/root privileges (for network monitoring)

### Platform-Specific Requirements
- **macOS**: Xcode Command Line Tools, py2app
- **Windows**: PyInstaller, Visual C++ Redistributable
- **Linux**: PyQt6 development packages, gcc

## Platform Build Instructions

### macOS

#### 1. Install Dependencies
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Create virtual environment
python3 -m venv watchdog_env
source watchdog_env/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install py2app
```

#### 2. Build .app Bundle
```bash
python3 setup_mac.py py2app
```

#### 3. Test the Application
```bash
# Run the built app
open "dist/WATCHDOG AI Dashboard.app"

# Or run with sudo for network monitoring
sudo open "dist/WATCHDOG AI Dashboard.app"
```

#### 4. Verify Functionality
- [ ] Application launches successfully
- [ ] Onboarding wizard appears for first-time users
- [ ] Network monitoring starts after setup
- [ ] Firewall blocking works
- [ ] ML threat detection functions
- [ ] UI displays correctly

### Windows

#### 1. Install Dependencies
```cmd
# Create virtual environment
python -m venv watchdog_env
watchdog_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install pyinstaller
```

#### 2. Build .exe
```cmd
pyinstaller build_windows.py
```

#### 3. Test the Application
```cmd
# Run the built executable
dist\WATCHDOG\WATCHDOG.exe

# Or run as Administrator for network monitoring
# Right-click -> Run as Administrator
```

#### 4. Verify Functionality
- [ ] Application launches successfully
- [ ] Onboarding wizard appears for first-time users
- [ ] Network monitoring starts after setup
- [ ] Firewall blocking works
- [ ] ML threat detection functions
- [ ] UI displays correctly

### Linux

#### 1. Install Dependencies
```bash
# Install system packages
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
sudo apt-get install python3-pyqt6 python3-scapy
sudo apt-get install build-essential

# Create virtual environment
python3 -m venv watchdog_env
source watchdog_env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Build Application
```bash
# Use setup.py for Linux
python3 setup.py install
```

#### 3. Test the Application
```bash
# Run with sudo for network monitoring
sudo python3 src/ui/pyqt_dashboard.py
```

#### 4. Verify Functionality
- [ ] Application launches successfully
- [ ] Onboarding wizard appears for first-time users
- [ ] Network monitoring starts after setup
- [ ] Firewall blocking works (iptables/nftables)
- [ ] ML threat detection functions
- [ ] UI displays correctly

## Cross-Platform Testing Checklist

### Core Functionality
- [ ] Application starts on all platforms
- [ ] Onboarding wizard works correctly
- [ ] Settings persistence (local_settings.json)
- [ ] Network packet capture
- [ ] ML threat detection
- [ ] Firewall IP blocking
- [ ] UI responsiveness

### Platform-Specific Testing

#### macOS
- [ ] .app bundle launches from Finder
- [ ] System tray icon appears
- [ ] pfctl firewall integration
- [ ] Network permissions dialog
- [ ] Dark mode support

#### Windows
- [ ] .exe launches from Explorer
- [ ] System tray icon appears
- [ ] Windows Firewall integration
- [ ] Network permissions (UAC)
- [ ] DPI scaling

#### Linux
- [ ] Application launches from terminal
- [ ] System tray icon appears (if supported)
- [ ] iptables/nftables integration
- [ ] Network permissions (sudo)
- [ ] Desktop environment compatibility

## Known Issues and Solutions

### macOS
**Issue**: "QBasicTimer can only be used with threads started with QThread"
- **Solution**: This is a warning, not an error. Application should still work.

**Issue**: Network permissions denied
- **Solution**: Run with sudo or add network monitoring permission in System Preferences

### Windows
**Issue**: Missing Visual C++ Redistributable
- **Solution**: Install from https://aka.ms/vs/17/release/vc_redist.x64.exe

**Issue**: Firewall blocking application
- **Solution**: Allow WATCHDOG through Windows Firewall when prompted

### Linux
**Issue**: Missing PyQt6 packages
- **Solution**: Install via package manager: `sudo apt-get install python3-pyqt6`

**Issue**: libpcap permissions
- **Solution**: Run with sudo or add user to pcap group

## Performance Testing

### High Network Load Test
1. Generate high network traffic (e.g., using iperf)
2. Monitor CPU and memory usage
3. Verify application remains responsive
4. Check for packet drops

### Expected Performance
- CPU usage: < 30% under normal load
- Memory usage: < 500MB
- Packet capture rate: > 1000 packets/second
- UI responsiveness: < 100ms latency

## Release Preparation

### Version Management
1. Update version numbers in:
   - `setup_mac.py` (CFBundleVersion)
   - `build_windows.py` (if version info added)
   - `README.md` (version reference)

### Pre-Release Checklist
- [ ] All platform builds completed
- [ ] Cross-platform testing passed
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Release notes prepared

### Distribution
- **macOS**: Distribute .app bundle (dmg optional)
- **Windows**: Distribute .exe or installer
- **Linux**: Distribute source with setup instructions

## Troubleshooting

### Build Failures
- Ensure all dependencies are installed
- Check Python version compatibility
- Verify virtual environment is activated
- Review build logs for specific errors

### Runtime Errors
- Check ML model file exists: `models/random_forest_model.pkl`
- Verify network permissions
- Check firewall configuration
- Review application logs

### Platform-Specific Issues
- **macOS**: Check macOS version compatibility
- **Windows**: Verify Windows version (10/11)
- **Linux**: Check distribution compatibility (Ubuntu/Debian/Fedora)

## Support

For issues or questions:
1. Check this guide first
2. Review USER_GUIDE.md
3. Check README.md
4. Review error logs in console output
