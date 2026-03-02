# Watchdog - Network Security Monitoring System

An AI-powered network intrusion detection and prevention system built with Python, Flet, Scapy, and machine learning.

## Project Overview

Watchdog is a comprehensive network security solution that monitors network traffic in real-time, detects potential threats using machine learning, and provides automated threat response capabilities. The system features a modern web-based interface and an AI assistant for intelligent log analysis.

## Features

- **Real-time Network Monitoring**: Continuous packet capture and analysis using Scapy
- **Machine Learning Detection**: Random Forest classifier trained on NSL-KDD dataset
- **Modern UI Interface**: Flet-based web dashboard with real-time visualizations
- **AI Assistant**: Llama 3 integration for intelligent log analysis and explanation
- **Automated Response**: Firewall automation for threat mitigation
- **Cross-platform**: Works on macOS, Linux, and Windows

## Technology Stack

- **Frontend**: Flet (Python-based UI framework)
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
   source watchdog_env/bin/activate  # On Windows: watchdog_env\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama** (for AI assistant):
   - Download from https://ollama.ai/
   - Pull Llama 3 model: `ollama pull llama3`

## Usage

### Running the Application

1. **Activate virtual environment**:
   ```bash
   source watchdog_env/bin/activate
   ```

2. **Run the main application**:
   ```bash
   python main.py
   ```

3. **Run individual components**:
   ```bash
   # Run basic Flet UI
   python src/ui/hello_world.py
   
   # Run basic packet sniffer
   python src/network/basic_sniffer.py
   ```

### Basic Operations

1. **Start Network Monitoring**: Click "Start Sniffing" in the UI
2. **View Captured Packets**: Real-time display in the packet list
3. **Stop Monitoring**: Click "Stop Sniffing" to halt packet capture
4. **View Statistics**: Packet count and status displayed in real-time

## Project Structure

```
watchdog/
├── README.md                 # Project documentation
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore file
├── main.py                  # Main application entry point
├── src/                     # Source code directory
│   ├── __init__.py
│   ├── ui/                  # Flet UI components
│   │   ├── __init__.py
│   │   └── hello_world.py
│   ├── network/             # Network monitoring components
│   │   ├── __init__.py
│   │   └── basic_sniffer.py
│   ├── ml/                  # Machine learning components
│   │   └── __init__.py
│   └── utils/               # Utility functions
│       └── __init__.py
├── tests/                   # Test files
├── docs/                    # Documentation
└── watchdog_env/            # Virtual environment
```

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
   - Run with administrator privileges: `sudo python main.py`
   - Ensure user has necessary network permissions

2. **Virtual Environment Issues**:
   - Ensure virtual environment is activated
   - Recreate environment if needed: `python3 -m venv watchdog_env`

3. **Dependency Conflicts**:
   - Update pip: `pip install --upgrade pip`
   - Check for conflicts: `pip check`

4. **Ollama Not Found**:
   - Ensure Ollama is installed and in PATH
   - Restart terminal after installation

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
