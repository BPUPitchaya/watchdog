#!/bin/bash
echo "Stopping sniffer..."
sudo pkill -f "basic_sniffer.py"
echo "Stopping dashboard..."
pkill -f "pyqt_dashboard.py"
echo "All stopped."
