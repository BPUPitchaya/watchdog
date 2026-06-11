#!/bin/bash
# Format script for Watchdog project
# Run this script to auto-format code

echo "=========================================="
echo "WATCHDOG Code Formatter"
echo "=========================================="
echo ""

# Activate virtual environment
source watchdog_env/bin/activate

echo "1. Running Ruff auto-fix..."
ruff check --fix src tests

echo ""
echo "2. Running Black formatter..."
black src tests

echo ""
echo "=========================================="
echo "Formatting complete!"
echo "=========================================="
