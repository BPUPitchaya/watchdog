#!/bin/bash

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PYTHON_CMD="python3"
    SUDO_CMD="sudo"
else
    PYTHON_CMD="./watchdog_env/bin/python"
    SUDO_CMD="sudo"
fi

echo "Starting Ollama (if installed)..."
if command -v ollama &> /dev/null; then
    ollama serve &
    sleep 5
else
    echo "Ollama not found - skipping AI features"
fi

echo "Starting sniffer..."
sudo $PYTHON_CMD src/network/basic_sniffer.py start &
sleep 2

echo "Starting dashboard..."
$PYTHON_CMD src/ui/pyqt_dashboard.py &
sleep 2

echo "Running Nmap scan (if installed)..."
if command -v nmap &> /dev/null; then
    sudo nmap -sS localhost
else
    echo "nmap not found - skipping network scan"
fi
echo "All done."
