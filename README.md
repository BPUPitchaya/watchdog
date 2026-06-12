# Watchdog - Network Security Monitoring System

An AI-powered network intrusion detection and prevention system built with Python, PyQt6, Scapy, and machine learning.

## Project Overview

Watchdog is a comprehensive network security solution that monitors network traffic in real-time, detects potential threats using machine learning, and provides automated threat response capabilities. The system features a modern web-based interface and an AI assistant for intelligent log analysis.

## Features

- **Real-time Network Monitoring**: Continuous packet capture and analysis using Scapy
- **Machine Learning Detection**: Random Forest classifier trained on NSL-KDD dataset
- **Modern UI Interface**: PyQt6-based desktop dashboard with real-time visualizations
- **AI Assistant**: Llama 3 integration for intelligent log analysis and explanation
- **Automated Response**: Firewall automation for threat mitigation
- **Cross-platform**: Works on macOS, Linux, and Windows
- **Threat Simulation**: Interactive attack simulation with plain English explanations
- **Progress Tracking**: Real-time statistics and progress indicators for simulations
- **Quick Start Guide**: Built-in onboarding for new users
- **Pause/Resume**: Full control over simulation execution

## Technology Stack

- **Frontend**: PyQt6 (Python-based GUI framework)
- **Network Monitoring**: Scapy for packet capture and analysis
- **Machine Learning**: Scikit-learn Random Forest classifier
- **AI Assistant**: Ollama with Llama 3 model
- **Dataset**: NSL-KDD for network intrusion detection
- **Version Control**: Git for collaboration and code management

## Installation

### Prerequisites

- Python 3.9 or higher
- Git
- Administrator/root privileges (for packet capture)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BPUPitchaya/watchdog.git
   cd watchdog
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv watchdog_env
   source watchdog_env/bin/activate  # macOS/Linux
   # On Windows: watchdog_env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install system dependencies**:

   **macOS**:
   ```bash
   # Install Homebrew if not already installed
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   
   # Install nmap and libpcap (for packet capture)
   brew install nmap libpcap
   ```

   **Linux (Ubuntu/Debian)**:
   ```bash
   sudo apt update
   sudo apt install nmap libpcap-dev python3-dev
   ```

   **Linux (CentOS/RHEL)**:
   ```bash
   sudo yum install nmap libpcap-devel python3-devel
   ```

   **Windows**:
   ```powershell
   # Install Npcap (required for Scapy packet capture)
   # Download from https://npcap.com/#download
   # During installation, check "Install Npcap in WinPcap API-compatible Mode"
   
   # Install nmap
   # Download from https://nmap.org/download.html
   # Or use Chocolatey: choco install nmap
   # Or use winget: winget install nmap
   ```

5. **Install Ollama** (for AI assistant):
   
   **Option 1: Auto-Install (Recommended)**
   ```bash
   # Run the auto-installer script
   python src/ai/ollama_installer.py --auto-install
   
   # This will automatically:
   # - Detect if Ollama is installed
   # - Download and install Ollama for your platform
   # - Pull the required AI model
   ```
   
   **Option 2: Manual Installation**
   
   **macOS**:
   ```bash
   # Download from https://ollama.ai/download
   # After installation, pull Llama 3 model
   ollama pull llama3
   ```
   
   **Linux**:
   ```bash
   # Install using curl
   curl -fsSL https://ollama.ai/install.sh | sh
   # Pull Llama 3 model after installation
   ollama pull llama3
   ```
   
   **Windows**:
   ```powershell
   # Download installer from https://ollama.ai/download
   # Run installer and restart terminal
   # Pull Llama 3 model after installation
   ollama pull llama3
   ```

## Usage

### Running the Application

1. **Activate virtual environment**:
   ```bash
   # macOS/Linux
   source watchdog_env/bin/activate
   
   # Windows
   watchdog_env\Scripts\activate
   ```

2. **Run main application**:
   ```bash
   # macOS/Linux: Full features (requires sudo for packet capture)
   sudo python3 src/ui/pyqt_dashboard.py
   
   # Windows: Run as Administrator for packet capture
   # Right-click Command Prompt/PowerShell and select "Run as administrator"
   # Then run: python src/ui/pyqt_dashboard.py
   
   # Development mode (UI only, no packet capture, no sudo needed)
   python src/ui/pyqt_dashboard.py --layout-only
   ```

3. **Run individual components**:
   ```bash
   # macOS/Linux: Basic packet sniffer (requires sudo)
   sudo python3 src/network/basic_sniffer.py
   
   # Windows: Basic packet sniffer (requires Administrator)
   # Right-click Command Prompt/PowerShell and select "Run as administrator"
   # Then run: python src/network/basic_sniffer.py
   
   # macOS/Linux: Network topology scanner (requires sudo)
   sudo python3 src/ui/pages/network_topology_page.py
   
   # Windows: Network topology scanner (requires Administrator)
   # Right-click Command Prompt/PowerShell and select "Run as administrator"
   # Then run: python src/ui/pages/network_topology_page.py
   
   # ML analysis (no sudo needed on any platform)
   python src/ml/dataset_analysis.py
   ```

### Basic Operations

1. **Start Network Monitoring**: Click "Start Sniffing" in the UI
2. **View Captured Packets**: Real-time display in the packet list
3. **Stop Monitoring**: Click "Stop Sniffing" to halt packet capture
4. **View Statistics**: Packet count and status displayed in real-time
5. **Threat Simulation**: Navigate to Threat Encyclopedia page to test attack simulations
   - Click "Simulator" on any threat card
   - Review the "What to Expect" modal before starting
   - Watch real-time packet injection with plain English explanations
   - Use Pause/Resume to control simulation flow
   - View progress bar and statistics (packets/sec, threat level)

## Project Structure

```
watchdog/
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── .gitignore                  # Git ignore file
├── main.py                     # Main application entry point
├── integrated_watchdog.py      # Integrated watchdog script
├── run_all.sh                  # Script to run all components
├── stop_all.sh                 # Script to stop all components
├── packet_data.json            # Example packet data
├── source.txt                  # Data source file
├── data/                       # Data directory
├── eda_plots/                  # Exploratory Data Analysis plots
│   ├── correlation_matrix.png
│   ├── dst_bytes_distribution.png
│   └── ... (other plot images)
├── experiments/                # Experimental code and research
│   ├── README.md              # Experiments documentation
│   ├── active/                # Currently active experiments
│   │   └── throughput_test.py # System throughput testing
│   └── archive/               # Archived experiments
├── src/                        # Source code directory
│   ├── __init__.py
│   ├── firewall_manager.py     # Manages firewall rules
│   ├── test_traffic.py         # Script for testing network traffic
│   ├── ai/                     # AI assistant components
│   │   ├── __init__.py
│   │   ├── ollama_client.py    # Client for Ollama/Llama 3 interaction
│   │   ├── prompts.py          # AI prompt definitions
│   │   └── utils.py            # AI related utility functions
│   ├── ml/                     # Machine learning components
│   │   ├── __init__.py
│   │   ├── dataset_analysis.py # Scripts for dataset analysis
│   │   ├── dataset_preparation.py # Data preparation and preprocessing
│   │   ├── feature_extractor.py # Extracts features from network data
│   │   ├── feature_selection.py # Selects relevant features
│   │   ├── integration_testing.py # ML integration tests
│   │   ├── model_training.py   # Trains the ML model
│   │   └── train_with_extractor.py # Training with feature extractor
│   ├── network/                # Network monitoring components
│   │   ├── __init__.py
│   │   ├── basic_sniffer.py    # Basic packet sniffer
│   │   └── sniffer_service.py  # Network sniffing service
│   ├── ui/                     # User Interface components (PyQt/Flet)
│   │   ├── __init__.py
│   │   ├── hello_world.py      # Example UI file
│   │   ├── help_content.py     # Help content for the UI
│   │   ├── modern_dashboard.py # Modern dashboard layout
│   │   ├── pyqt_dashboard.py   # Main PyQt dashboard application
│   │   ├── streamlit_dashboard.py # Streamlit dashboard alternative
│   │   ├── theme.py            # UI theme definitions
│   │   ├── assets/             # UI assets (icons, fonts)
│   │   │   ├── Ai assistant icon.png
│   │   │   ├── dashboard icon.png
│   │   │   └── ... (other UI assets)
│   │   ├── pages/              # UI pages
│   │   │   ├── __init__.py
│   │   │   ├── ai_mentor_page.py # AI mentor page
│   │   │   ├── autonomous_shield_page.py # Autonomous shield features
│   │   │   ├── forensic_vault_page.py # Forensic data vault
│   │   │   ├── live_sentinel_page.py # Live network monitoring
│   │   │   ├── network_topology_page.py # Network topology visualization
│   │   │   ├── placeholder_page.py # Placeholder for future pages
│   │   │   ├── settings_page.py # Application settings
│   │   │   └── threat_encyclopedia_page.py # Threat information database
│   │   └── widgets/            # Reusable UI widgets
│   │       ├── __init__.py
│   │       ├── ai_widget.py    # AI assistant widget
│   │       ├── charts.py       # Charting widgets
│   │       ├── forensic_panel.py # Forensic data display panel
│   │       ├── gauges.py       # Gauge widgets
│   │       ├── help_dialog.py  # Help dialog widget
│   │       ├── network_topology.py # Network topology visualization widget
│   │       └── toast.py        # Notification toast widget
│   └── utils/                  # General utility functions
│       ├── __init__.py
│       └── logger.py           # Centralized logging configuration
├── tests/                      # Test files
│   ├── test_core.py           # Core functionality tests
│   ├── test_performance.py    # Performance tests
│   ├── test_accuracy.py       # ML model accuracy tests
│   └── test_ui.py             # UI component and integration tests
├── docs/                       # Documentation
└── watchdog_env/               # Virtual environment
```

## Branch Organization

This project uses a hybrid branch organization approach to balance stability with research experimentation:

### Main Branch (Production)
- **Purpose**: Production-ready, stable code for presentations and deployment
- **Contents**: Full application, comprehensive test suite, production model
- **Status**: Always stable, tested, and ready for use
- **Updates**: Merged from research branch when experiments prove successful

### Primary_Research Branch (Experimental)
- **Purpose**: Active research and development of new features
- **Contents**: Experimental code, performance tests, new algorithms
- **Status**: May be unstable, for research purposes only
- **Workflow**: Successful experiments are merged to main branch

### Experiments Directory
- **experiments/active/**: Currently active experiments being tested
- **experiments/archive/**: Archived experiments (successful merged to main, or discontinued)
- **Workflow**: 
  1. New experiments go in `experiments/active/`
  2. When successful, merge to main branch
  3. Move to `experiments/archive/` with documentation
  4. Failed experiments also go to archive with failure analysis

### Workflow
1. Develop new features in `primary_research` branch or `experiments/active/`
2. Test thoroughly and validate results
3. Merge successful experiments to `main` branch
4. Archive completed experiments with documentation
5. Keep `main` branch always stable and presentation-ready

## Development Phases

### Phase 1: Foundation & Data Intelligence (Weeks 1–3)
- Environment setup and proof of concept
- NSL-KDD dataset analysis and feature selection
- Random Forest model training and evaluation

### Phase 2: Core Detection & Defense System (Weeks 4–6)
- Real-time feature extractor development
- System integration and testing
- Firewall automation implementation

### Phase 3: User Interface & AI Assistant (Weeks 7–9)
- Modern dashboard development
- Red Team/Blue Team testing
- Llama 3 AI assistant integration

### Phase 4: Optimization & Delivery (Weeks 10–12)
- Performance tuning and optimization
- Documentation and reporting
- Final project delivery

## Troubleshooting

### Common Issues

1. **Permission Denied for Packet Capture**:
   ```bash
   # macOS/Linux: Run with sudo
   sudo python3 src/ui/pyqt_dashboard.py
   
   # Windows: Run as Administrator
   # Method 1: Right-click Command Prompt and select "Run as administrator"
   # Method 2: Right-click PowerShell and select "Run as administrator"
   # Method 3: Open Command Prompt as Administrator from Start Menu
   # Then run: python src/ui/pyqt_dashboard.py
   ```

2. **Virtual Environment Issues**:
   ```bash
   # macOS/Linux: Ensure virtual environment is activated
   source watchdog_env/bin/activate
   
   # Windows: Ensure virtual environment is activated
   # Method 1: watchdog_env\Scripts\activate
   # Method 2: watchdog_env\Scripts\activate.bat
   # Method 3: Use Command Prompt with activation script
   
   # Recreate environment if needed
   python3 -m venv watchdog_env
   source watchdog_env/bin/activate  # macOS/Linux
   watchdog_env\Scripts\activate    # Windows
   pip install -r requirements.txt
   ```

3. **Dependency Conflicts**:
   - Update pip: `pip install --upgrade pip`
   - Check for conflicts: `pip check`

4. **Ollama Not Found**:
   - Use auto-installer: `python src/ai/ollama_installer.py --auto-install`
   - Or manually install from https://ollama.ai/download
   - Restart terminal after installation
   - Test with: `ollama list`
   - If Ollama is installed but not running, start the Ollama application/service

5. **Scapy Packet Capture Issues**:
   
   **macOS**:
   - Grant network permissions in System Preferences → Security & Privacy → Privacy → Full Disk Access
   - Ensure libpcap is installed: `brew install libpcap`
   
   **Linux**:
   - Add user to pcap group: `sudo usermod -a -G pcap $USER`
   - Log out and back in for group changes to take effect
   - Install libpcap-dev: `sudo apt install libpcap-dev` (Ubuntu/Debian)
   
   **Windows**:
   - Ensure Npcap is installed with WinPcap compatibility mode
   - Run Npcap installer as Administrator
   - Restart after Npcap installation
   - Check Npcap service is running in Services.msc

### Performance Tips

- Close unnecessary network applications during monitoring
- Use wired connection for better packet capture accuracy
- Monitor system resources during extended use

## Contributing

This is a collaborative project between Pitchaya and Blossom. Please follow the established development workflow:

1. Create feature branches from `develop`
2. Test changes thoroughly before merging
3. Update documentation for new features
4. Follow PEP 8 coding standards

## License

This project is developed for educational purposes as part of a university project.

## Contact

- **Developers**: Pitchaya & Blossom
- **Project**: Network Security Monitoring System
- **Repository**: https://github.com/BPUPitchaya/watchdog.git

## Acknowledgments

- NSL-KDD dataset providers
- Scapy development team
- Flet framework contributors
- Ollama and Llama 3 developers
