# Changelog

All notable changes to Watchdog AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-06-11

### Added

#### Core Features
- **AI-Powered Network Intrusion Detection System**
  - Real-time network packet capture and analysis
  - Machine learning-based threat detection using Random Forest classifier
  - Explainable AI (XAI) with Ollama integration for threat analysis
  - Automated firewall mitigation for detected threats

#### User Interface
- **Modern PyQt6 Dashboard**
  - Dark-themed, professional UI design
  - Six main pages: Live Sentinel, Forensic Vault, Autonomous Shield, AI Mentor, Network Topology, Threat Encyclopedia
  - Real-time traffic visualization with live packet stream
  - Risk analysis gauge with threat level indicators
  - System health monitoring (CPU, RAM, network status)
  - Onboarding wizard for first-time users
  - Settings management with theme customization

#### Network Analysis
- **Network Topology Discovery**
  - Automatic device discovery on local network
  - Visual network topology map with device classification
  - Device type detection (PC/Server, Mobile, IoT, Unknown)
  - MAC address-based device identification

#### AI Integration
- **Ollama Integration**
  - Local LLM integration for threat explanation
  - Automatic Ollama installation and setup
  - AI Mentor for security guidance and recommendations
  - Technical analysis and general query modes

#### Security Features
- **Firewall Management**
  - macOS pfctl-based IP blocking
  - Automated threat mitigation with configurable timeouts
  - Temporary and permanent blocking options
  - Block history and management

#### Data Management
- **Forensic Vault**
  - Incident logging and storage
  - Packet capture history
  - Threat analysis records
  - Export functionality for incident reports

#### Testing & Quality
- **Comprehensive Test Suite**
  - Unit tests for core functionality
  - Integration tests for UI components
  - Performance benchmarks
  - Accuracy testing for ML model
  - Test coverage reporting

- **Code Quality Tools**
  - Ruff linter for code quality checks
  - Black formatter for consistent code style
  - pytest for testing framework
  - pytest-cov for coverage reporting

#### Documentation
- **Project Documentation**
  - Comprehensive README with setup instructions
  - Branch organization documentation
  - API documentation for key modules
  - User guide for features and settings

#### Cross-Platform Support
- **Build Scripts**
  - macOS application bundling with PyInstaller
  - Windows executable packaging
  - Automated build scripts for both platforms
  - Code signing for macOS applications

### Improved

#### Performance
- Optimized packet capture with background threading
- Efficient ML model inference with configurable sampling rate
- Reduced memory footprint for long-running sessions
- Improved UI responsiveness with worker threads

#### User Experience
- Streamlined onboarding process
- Better error messages with user-friendly explanations
- Improved notification system for alerts
- Enhanced settings management with persistence

#### Code Quality
- Added comprehensive error handling across all modules
- Centralized logging configuration
- Improved code organization with clear module boundaries
- Better separation of concerns in UI components

### Fixed

#### Bug Fixes
- Fixed resource path resolution for bundled applications
- Corrected ML model loading in production builds
- Fixed file permission issues for logs and settings
- Resolved dialog display issues in GUI launches
- Fixed undefined variable errors in various modules
- Corrected import statements and dependencies

#### Platform-Specific Fixes
- macOS: Fixed quarantine attribute handling
- macOS: Improved code signing for app bundles
- macOS: Fixed working directory issues for GUI launches
- Windows: Improved firewall command execution

### Security

- **Data Privacy**
  - Zero cloud transmission - all processing happens locally
  - No telemetry or data sent to external servers
  - User data sovereignty with local storage only

- **Permission Handling**
  - Administrator privilege detection
  - Permission request dialog for sensitive operations
  - Clear user consent for network monitoring

### Technical Details

#### Dependencies
- PyQt6 >= 6.0.0
- scapy >= 2.4.5
- scikit-learn >= 1.0.0
- pandas >= 1.3.0
- numpy >= 1.21.0
- psutil >= 5.8.0
- joblib >= 1.0.0
- matplotlib >= 3.4.0

#### Development Tools
- Python 3.8+
- Virtual environment support
- Automated testing with pytest
- Code quality tools (ruff, black)

### Known Limitations

- macOS app launch from Spotlight requires manual bypass due to Gatekeeper
- Works perfectly when launched from command line
- Some advanced firewall features require macOS-specific pfctl
- Ollama requires separate installation (automated installer provided)

### Migration Guide

#### From Development to Production
1. Run `./build_macos.sh` or `build_windows.bat` to create distributable
2. For macOS: Sign and remove quarantine attributes
3. Copy to `/Applications/` (macOS) or Program Files (Windows)
4. Launch from command line for best compatibility

#### Settings Migration
- Settings automatically migrate to user directories on first run
- `~/Library/Application Support/Watchdog/` on macOS
- `%APPDATA%/Watchdog/` on Windows

---

## [Unreleased]

### Planned Features
- Windows firewall integration
- Additional ML model options (XGBoost, Neural Networks)
- Cloud-based threat intelligence integration (optional)
- Mobile app companion
- Advanced reporting and analytics dashboard
- Custom alert rules and thresholds
- Integration with SIEM systems

---

[1.0.0]: https://github.com/yourusername/watchdog/releases/tag/v1.0.0
