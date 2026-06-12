# DEVELOPER GUIDE

This guide is for contributors who want to understand, modify, or extend WATCHDOG.

## Project Overview

WATCHDOG is a local-only network security monitoring system that uses machine learning to detect threats in real-time. It runs on macOS, Windows, and Linux.

### Key Principles
- **Local-only**: All data stays on the user's computer. No cloud processing.
- **Privacy-first**: User data is never transmitted externally.
- **Cross-platform**: Works on macOS, Windows, and Linux.
- **Real-time**: Monitors network traffic and detects threats instantly.

## Architecture

### Core Components

#### 1. Network Monitoring
- **Location**: `src/network/`
- **Key Files**:
  - `basic_sniffer.py` - Core packet capture using Scapy
  - `sniffer_service.py` - Service wrapper for continuous monitoring
- **Functionality**: Captures network packets in real-time using libpcap

#### 2. Machine Learning
- **Location**: `src/ml/`
- **Key Files**:
  - `feature_extractor.py` - Extracts NSL-KDD features from packets
  - `models/random_forest_model.pkl` - Trained Random Forest classifier
- **Functionality**: Analyzes packet patterns to detect threats

#### 3. Firewall Management
- **Location**: `src/firewall_manager.py`
- **Functionality**: Blocks malicious IPs at system level
- **Platform Support**:
  - macOS: pfctl
  - Windows: Windows Firewall
  - Linux: iptables/nftables

#### 4. User Interface
- **Location**: `src/ui/`
- **Key Files**:
  - `pyqt_dashboard.py` - Main application window
  - `onboarding_wizard.py` - First-time setup wizard
  - `user_settings.py` - Settings management
  - `pages/` - Individual UI pages
  - `widgets/` - Reusable UI components
- **Framework**: PyQt6

#### 5. AI Integration
- **Location**: `src/ai/`
- **Key Files**:
  - `ollama_installer.py` - Ollama AI backend setup
  - `ollama_client.py` - AI client for threat analysis
- **Functionality**: Optional AI-powered threat analysis

## Development Setup

### Prerequisites
- Python 3.10+
- Git
- Virtual environment tool (venv or conda)

### Setup Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd Watchdog
```

2. **Create virtual environment**
```bash
python3 -m venv watchdog_env
source watchdog_env/bin/activate  # On Windows: watchdog_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
# Development mode (with console output)
python3 src/ui/pyqt_dashboard.py

# Or with sudo for network monitoring
sudo python3 src/ui/pyqt_dashboard.py
```

## Code Structure

### Directory Layout
```
Watchdog/
├── src/
│   ├── ai/              # AI integration
│   ├── firewall_manager.py
│   ├── ml/              # Machine learning
│   ├── network/         # Network monitoring
│   └── ui/              # User interface
├── models/              # ML model files
├── tests/               # Automated tests
├── setup_mac.py         # macOS build config
├── build_windows.py     # Windows build config
├── setup.py             # Linux build config
└── requirements.txt     # Python dependencies
```

### Key Classes

#### FeatureExtractor
- **Purpose**: Extracts NSL-KDD features from network packets
- **Methods**:
  - `extract_packet_features(packet_data)` - Extract features from a single packet
  - `get_selected_features(features_dict)` - Return selected features for ML model
- **Usage**: Called by ML prediction pipeline for each packet

#### BasicSniffer
- **Purpose**: Captures network packets using Scapy
- **Methods**:
  - `start_sniffing(packet_count=0)` - Start packet capture
  - `stop_sniffing()` - Stop packet capture
  - `get_captured_packets()` - Retrieve captured packets
- **Usage**: Runs in separate thread to avoid blocking UI

#### FirewallManager
- **Purpose**: Manages system firewall rules
- **Methods**:
  - `block_ip(ip_address)` - Block an IP address
  - `unblock_ip(ip_address)` - Unblock an IP address
  - `get_blocked_ips()` - Get list of blocked IPs
  - `clear_all_blocked_ips()` - Remove all blocked IPs from firewall
- **Usage**: Called when threat is detected or for bulk IP management

#### WatchdogDashboard
- **Purpose**: Main application window and controller
- **Key Responsibilities**:
  - UI initialization and navigation
  - Packet sniffer management
  - ML prediction coordination
  - Firewall integration
  - Settings management

## Development Workflow

### Making Changes

1. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Edit the relevant files
   - Follow existing code style
   - Add comments for complex logic

3. **Test your changes**
```bash
# Run automated tests
python3 tests/test_core.py

# Run the application
python3 src/ui/pyqt_dashboard.py
```

4. **Commit your changes**
```bash
git add .
git commit -m "Description of your changes"
```

5. **Push and create pull request**
```bash
git push origin feature/your-feature-name
```

### Code Style Guidelines

- **Python**: Follow PEP 8
- **Comments**: Use docstrings for functions and classes
- **Variable names**: Use descriptive, snake_case names
- **Class names**: Use PascalCase
- **Constants**: Use UPPER_CASE

### Testing

#### Running Tests
```bash
# Run all tests
python3 tests/test_core.py

# Run specific test class
python3 -m unittest tests.test_core.TestFeatureExtractor

# Run with verbose output
python3 -m unittest tests.test_core -v
```

#### Writing Tests
- Add tests to `tests/test_core.py`
- Use unittest framework
- Test both success and failure cases
- Mock external dependencies when needed

## Common Tasks

### Adding a New UI Page

1. Create page class in `src/ui/pages/`
2. Inherit from appropriate base class
3. Add navigation button in `pyqt_dashboard.py`
4. Register page in `create_pages()` method

### Modifying ML Features

1. Update `feature_extractor.py` to extract new features
2. Retrain the model with the new features
3. Update `get_selected_features()` to include new features
4. Replace `models/random_forest_model.pkl` with new model

### Adding Platform Support

1. Create platform-specific build script
2. Add firewall integration for the platform
3. Update `BUILD_AND_TEST.md` with build instructions
4. Test on target platform

### Updating Dependencies

1. Update `requirements.txt`
2. Test with new versions
3. Update build scripts if needed
4. Document breaking changes

## Debugging

### Common Issues

#### Network Permissions
- **macOS**: Run with sudo or enable in System Preferences
- **Windows**: Run as Administrator
- **Linux**: Run with sudo or add to pcap group

#### ML Model Not Loading
- Check `models/random_forest_model.pkl` exists
- Verify joblib is installed
- Check file permissions

#### UI Not Responding
- Check if sniffer thread is running
- Verify ML predictions aren't blocking main thread
- Check for long-running operations on main thread

### Debug Mode

Enable debug output by setting environment variable:
```bash
export WATCHDOG_DEBUG=1
python3 src/ui/pyqt_dashboard.py
```

## Performance Considerations

### Packet Capture
- Sniffer runs in separate thread to avoid blocking UI
- ML predictions are cached to avoid recomputation
- Connection tracking has time-based cleanup

### Memory Management
- Packet history is limited (deque with maxlen)
- Old connections are cleaned up periodically
- ML model is loaded once at startup

### UI Responsiveness
- Heavy operations run in worker threads
- UI updates use Qt signals/slots
- Gauge updates are throttled

## Security Considerations

### Local-Only Philosophy
- No data is transmitted to external servers
- All processing happens on user's machine
- Settings stored locally in JSON

### Privilege Management
- Network monitoring requires elevated privileges
- Firewall operations require admin/root
- Permission dialogs guide users through setup

### Data Privacy
- User data never leaves the device
- Settings are encrypted at rest (optional)
- No telemetry or analytics

## Contributing

### Before Contributing
1. Read this guide
2. Set up development environment
3. Run existing tests
4. Review existing code

### Submitting Changes
1. Create pull request
2. Describe changes clearly
3. Include test coverage
4. Update documentation if needed

### Code Review Process
- Changes are reviewed by maintainers
- Feedback will be provided
- Address all review comments
- Tests must pass before merge

## Resources

### Documentation
- `README.md` - Project overview
- `USER_GUIDE.md` - User documentation
- `BUILD_AND_TEST.md` - Build and testing guide
- This file - Developer guide

### External Resources
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [scikit-learn Documentation](https://scikit-learn.org/)
- [NSL-KDD Dataset](https://www.unb.ca/cic/datasets/nsl.html)

## Getting Help

- Check existing documentation
- Review test files for examples
- Look at similar code in the codebase
- Ask questions in pull requests

## License

This project is licensed under the terms specified in the LICENSE file.
