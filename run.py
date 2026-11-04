#!/usr/bin/env python3
"""
LinTask Manager - Development Entrypoint.
Usage:
    python3 run.py
"""
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

# Auto-detect and re-exec with project .venv if not currently activated
venv_dir = os.path.join(PROJECT_ROOT, ".venv")
venv_python = os.path.join(venv_dir, "bin", "python3")
if os.path.exists(venv_python) and os.path.abspath(sys.prefix) != os.path.abspath(venv_dir):
    os.execv(venv_python, [venv_python] + sys.argv)

from lintask.app import main

if __name__ == "__main__":
    main()
