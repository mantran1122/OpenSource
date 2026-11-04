#!/usr/bin/env bash
# LinTask Manager - Git Setup Script
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== LinTask Manager Setup ==="

# 1. Check Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    python3 -m venv .venv
fi

# 3. Install Requirements
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Desktop Shortcut Integration
echo ""
echo "Registering LinTask Manager to your Linux Application Menu..."
python3 -c "from lintask.utils.desktop_integration import install_shortcut; success, msg = install_shortcut(); print('-> ' + msg)"

echo ""
echo "=== Setup Complete! ==="
echo "You can now launch LinTask Manager from your application menu, or run:"
echo "    python3 run.py"

