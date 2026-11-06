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

# 2. Make run script executable
chmod +x run.py

# 3. Setup Virtual Environment (User space - no root/password needed)
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/python3" ]; then
    echo "Creating virtual environment in .venv..."
    if ! python3 -m venv .venv 2>/dev/null; then
        echo ""
        echo "[!] Không thể tạo môi trường ảo Python (.venv)."
        echo "[!] Trên Ubuntu / Debian / Zorin OS / Linux Mint, vui lòng chạy lệnh sau:"
        echo "    sudo apt update && sudo apt install -y python3-venv python3-pip"
        echo "Sau đó chạy lại: ./install.sh"
        exit 1
    fi
fi

# 4. Install Requirements
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Desktop and Taskbar Integration (User space - no root/password needed)
echo ""
echo "Registering LinTask Manager to your Linux Application Menu & Taskbar..."
python3 -c "from lintask.utils.desktop_integration import install_shortcut; success, msg = install_shortcut(); print('-> ' + msg)"

echo ""
echo "=== Setup Complete! ==="
echo "You can now launch LinTask Manager by:"
echo " 1. Clicking 'Theo dõi hệ thống' or 'LinTask Manager' on your taskbar right-click menu"
echo " 2. Clicking the LinTask Manager icon pinned on your taskbar"
echo " 3. Running: python3 run.py"
