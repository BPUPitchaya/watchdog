#!/bin/bash
echo "Stopping sniffer..."
pkill -f "python3 src/network/basic_sniffer.py"
echo "Stopping dashboard..."
pkill -f "python3 src/ui/pyqt_dashboard.py"
echo "All stopped."


/.stop_all.shpython3 src/ui/pyqt_dashboard.py --layout-only
