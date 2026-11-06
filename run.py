#!/usr/bin/env python3
"""
LinTask Manager - Modern Windows-inspired Task Manager for Linux.
Usage:
    python3 run.py
"""
import sys
import os
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

lib_dir = os.path.join(PROJECT_ROOT, "lintask", "lib")
venv_dir = os.path.join(PROJECT_ROOT, ".venv")
venv_python = os.path.join(venv_dir, "bin", "python3")
requirements_file = os.path.join(PROJECT_ROOT, "requirements.txt")


def _has_dependencies() -> bool:
    """Check if all required runtime libraries are installed in current Python."""
    try:
        import PyQt6
        import qfluentwidgets
        import pyqtgraph
        import psutil
        return True
    except ImportError:
        return False


def _auto_bootstrap_venv():
    """Attempt to create .venv and install requirements if not yet initialized."""
    print("=" * 65)
    print("⚡ [LinTask Manager] Phát hiện lần đầu khởi chạy trên máy mới.")
    print("⚡ Đang tự động thiết lập môi trường ảo .venv và cài đặt thư viện...")
    print("=" * 65)

    # 1. Try creating venv
    venv_res = subprocess.run([sys.executable, "-m", "venv", venv_dir], capture_output=True, text=True)
    if venv_res.returncode != 0:
        print("\n[!] Không thể tự động tạo môi trường ảo Python (.venv).")
        print("[!] Gói 'python3-venv' có thể chưa được cài đặt trên hệ thống.")
        print("\n👉 Cách khắc phục đơn giản nhất:")
        print("   - Trên Ubuntu / Debian / Zorin OS / Linux Mint:")
        print("         sudo apt update && sudo apt install -y python3-venv python3-pip")
        print("         ./install.sh")
        print("   - Trên Fedora / RHEL:")
        print("         sudo dnf install -y python3-pip && ./install.sh")
        print("   - Trên Arch Linux / Manjaro:")
        print("         sudo pacman -S --needed python-pip && ./install.sh\n")
        sys.exit(1)

    # 2. Install requirements into newly created venv
    if os.path.exists(venv_python) and os.path.exists(requirements_file):
        print("⚡ Đang tải các thư viện cần thiết (PyQt6, QFluentWidgets, pyqtgraph)...")
        install_res = subprocess.run([venv_python, "-m", "pip", "install", "-r", requirements_file])
        if install_res.returncode != 0:
            print("\n[!] Cài đặt dependencies không thành công. Vui lòng kiểm tra mạng và chạy: ./install.sh")
            sys.exit(1)
        print("⚡ Cài đặt hoàn tất! Đang khởi chạy LinTask Manager...\n")


# 1. Check if current environment already has all dependencies
if not _has_dependencies():
    # If not inside .venv and .venv exists, prepare to re-exec into it
    if not os.path.exists(venv_python):
        _auto_bootstrap_venv()
    elif os.path.abspath(sys.prefix) == os.path.abspath(venv_dir):
        # We are already inside .venv but dependencies are missing -> install them
        print("⚡ [LinTask] Đang cài đặt bổ sung dependencies vào .venv...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file], check=True)

# 2. Configure LD_LIBRARY_PATH and re-exec with venv python if needed
ld_paths = [p for p in os.environ.get("LD_LIBRARY_PATH", "").split(":") if p]
needs_ld = os.path.isdir(lib_dir) and (lib_dir not in ld_paths)
needs_venv = os.path.exists(venv_python) and (os.path.abspath(sys.prefix) != os.path.abspath(venv_dir))

if needs_ld or needs_venv:
    env = os.environ.copy()
    if needs_ld:
        env["LD_LIBRARY_PATH"] = f"{lib_dir}:{':'.join(ld_paths)}" if ld_paths else lib_dir
    target_py = venv_python if os.path.exists(venv_python) else sys.executable
    os.execve(target_py, [target_py] + sys.argv, env)

from lintask.app import main

if __name__ == "__main__":
    main()
