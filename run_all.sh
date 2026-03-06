#!/bin/bash
echo "Starting Ollama..."
ollama serve &
sleep 5
echo "Starting sniffer..."
sudo python3 src/network/basic_sniffer.py start &
sleep 2
echo "Starting dashboard..."
python3 src/ui/pyqt_dashboard.py &
sleep 2
echo "Running Nmap scan..."
sudo nmap -sS localhost
echo "All done."
