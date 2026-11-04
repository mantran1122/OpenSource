#!/usr/bin/env python3
"""
LinTask Manager - Modern Windows-inspired Task Manager for Linux.
Usage:
    python3 run.py
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Auto-configure bundled libraries (e.g. libxcb-cursor for Qt6 on X11)
lib_dir = os.path.join(PROJECT_ROOT, "lintask", "lib")
ld_paths = [p for p in os.environ.get("LD_LIBRARY_PATH", "").split(":") if p]
needs_ld = os.path.isdir(lib_dir) and (lib_dir not in ld_paths)

# Auto-detect and re-exec with project .venv if not currently active
venv_dir = os.path.join(PROJECT_ROOT, ".venv")
venv_python = os.path.join(venv_dir, "bin", "python3")
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
