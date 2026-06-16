#!/bin/bash
# Lint script for Watchdog project
# Run this script to check code quality

echo "=========================================="
echo "WATCHDOG Code Quality Check"
echo "=========================================="
echo ""

# Activate virtual environment
source watchdog_env/bin/activate

echo "1. Running Ruff linter..."
ruff check src tests
LINT_EXIT=$?

echo ""
echo "2. Running Black formatter check..."
black --check src tests
FORMAT_EXIT=$?

echo ""
echo "=========================================="
echo "Results:"
echo "=========================================="
if [ $LINT_EXIT -eq 0 ]; then
    echo "Ruff: No linting issues found"
else
    echo "Ruff: Linting issues found (run 'ruff check --fix src tests' to auto-fix)"
fi

if [ $FORMAT_EXIT -eq 0 ]; then
    echo "Black: Code is properly formatted"
else
    echo "Black: Code needs formatting (run 'black src tests' to fix)"
fi

echo ""
echo "To auto-fix issues, run:"
echo "  ruff check --fix src tests"
echo "  black src tests"
