#!/bin/bash

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    PYTHON_CMD="python3"
    SUDO_CMD="sudo"
else
    PYTHON_CMD="python"
    SUDO_CMD=""
fi

echo "Starting Ollama..."
ollama serve &
sleep 5

echo "Starting sniffer..."
$SUDO_CMD $PYTHON_CMD src/network/basic_sniffer.py start &
sleep 2

echo "Starting dashboard..."
$PYTHON_CMD src/ui/pyqt_dashboard.py &
sleep 2

echo "Running Nmap scan..."
$SUDO_CMD nmap -sS localhost
echo "All done."
