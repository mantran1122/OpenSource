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

# 3. Setup Virtual Environment
if [ ! -d ".venv" ] || [ ! -f ".venv/bin/python3" ]; then
    echo "Creating virtual environment in .venv..."
    if ! python3 -m venv .venv 2>/dev/null; then
        echo ""
        echo "[!] Không thể tạo môi trường ảo Python (.venv)."
        echo "[!] Hệ thống của bạn có thể đang thiếu gói 'python3-venv'."
        echo ""
        if command -v apt-get &> /dev/null; then
            echo "-> Đang thử cài đặt python3-venv và python3-pip..."
            if [ "$(id -u)" -eq 0 ]; then
                apt-get update -q && apt-get install -y -q python3-venv python3-pip
            elif command -v pkexec &> /dev/null; then
                pkexec apt-get update -q && pkexec apt-get install -y -q python3-venv python3-pip
            elif command -v sudo &> /dev/null; then
                sudo apt-get update -q && sudo apt-get install -y -q python3-venv python3-pip
            fi
            python3 -m venv .venv
        else
            echo "Vui lòng cài đặt python3-venv / python3-pip cho hệ thống của bạn và chạy lại ./install.sh"
            exit 1
        fi
    fi
fi

# 4. Install Requirements
echo "Installing dependencies..."
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Ensure Qt6 XCB Cursor Compatibility (for Ubuntu 24.04+ / Zorin OS 17+)
if ! ldconfig -p 2>/dev/null | grep -q "libxcb-cursor.so.0"; then
    if [ ! -f "lintask/lib/libxcb-cursor.so.0" ]; then
        echo "Ensuring Qt6 X11 cursor compatibility..."
        if command -v apt-get &> /dev/null && [ "$(id -u)" -eq 0 ]; then
            apt-get install -y -q libxcb-cursor0 2>/dev/null || true
        elif command -v pkexec &> /dev/null; then
            pkexec apt-get install -y -q libxcb-cursor0 2>/dev/null || true
        elif command -v sudo &> /dev/null; then
            sudo apt-get install -y -q libxcb-cursor0 2>/dev/null || true
        fi
    fi
fi

# 6. Desktop and Taskbar Integration
echo ""
echo "Registering LinTask Manager to your Linux Application Menu & Taskbar..."
python3 -c "from lintask.utils.desktop_integration import install_shortcut; success, msg = install_shortcut(); print('-> ' + msg)"

echo ""
echo "=== Setup Complete! ==="
echo "You can now launch LinTask Manager by:"
echo " 1. Clicking 'Theo dõi hệ thống' or 'LinTask Manager' on your taskbar right-click menu"
echo " 2. Clicking the LinTask Manager icon pinned on your taskbar"
echo " 3. Running: python3 run.py"
