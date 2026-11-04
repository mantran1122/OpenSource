"""Helpers for registering LinTask into Linux application launcher menus."""
import os
import sys

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESKTOP_ENTRY_DIR = os.path.expanduser("~/.local/share/applications")
DESKTOP_ENTRY_PATH = os.path.join(DESKTOP_ENTRY_DIR, "lintask.desktop")
ICON_PATH = os.path.join(APP_DIR, "assets", "icons", "lintask.svg")
RUN_SCRIPT = os.path.join(APP_DIR, "run.py")


def is_shortcut_installed() -> bool:
    """Check if lintask.desktop already exists in user applications directory."""
    return os.path.exists(DESKTOP_ENTRY_PATH)


def install_shortcut() -> tuple[bool, str]:
    """Create or update ~/.local/share/applications/lintask.desktop."""
    try:
        os.makedirs(DESKTOP_ENTRY_DIR, exist_ok=True)
        
        # Point to python run.py
        exec_cmd = f"python3 {RUN_SCRIPT}"
        # If virtualenv python exists, point directly to it
        venv_py = os.path.join(APP_DIR, ".venv", "bin", "python3")
        if os.path.exists(venv_py):
            exec_cmd = f"{venv_py} {RUN_SCRIPT}"

        content = f"""[Desktop Entry]
Type=Application
Name=LinTask Manager
GenericName=Task Manager
Comment=Modern Windows-style Task Manager for Linux
Exec={exec_cmd}
Icon={ICON_PATH}
Terminal=false
Categories=System;Monitor;
Keywords=task;manager;system;process;performance;monitor;
StartupNotify=true
"""
        with open(DESKTOP_ENTRY_PATH, "w", encoding="utf-8") as f:
            f.write(content)

        return True, "LinTask Manager shortcut added to application menu."
    except Exception as e:
        return False, f"Failed to install desktop shortcut: {e}"


def remove_shortcut() -> tuple[bool, str]:
    """Remove ~/.local/share/applications/lintask.desktop."""
    try:
        if os.path.exists(DESKTOP_ENTRY_PATH):
            os.remove(DESKTOP_ENTRY_PATH)
            return True, "LinTask Manager removed from application menu."
        return False, "Shortcut was not found."
    except Exception as e:
        return False, f"Failed to remove shortcut: {e}"

