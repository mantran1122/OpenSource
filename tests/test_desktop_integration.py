"""Test desktop integration helper."""
import os
import tempfile
import pytest
from lintask.utils import desktop_integration


def test_desktop_shortcut_lifecycle():
    with tempfile.TemporaryDirectory() as temp_dir:
        # Patch paths
        desktop_integration.DESKTOP_ENTRY_DIR = temp_dir
        desktop_integration.DESKTOP_ENTRY_PATH = os.path.join(temp_dir, "lintask.desktop")

        assert desktop_integration.is_shortcut_installed() is False

        # Install
        success, msg = desktop_integration.install_shortcut()
        assert success is True
        assert desktop_integration.is_shortcut_installed() is True
        assert os.path.exists(desktop_integration.DESKTOP_ENTRY_PATH)

        # Content check
        with open(desktop_integration.DESKTOP_ENTRY_PATH, "r") as f:
            content = f.read()
            assert "LinTask Manager" in content
            assert "Categories=System;Monitor;" in content

        # Remove
        success, msg = desktop_integration.remove_shortcut()
        assert success is True
        assert desktop_integration.is_shortcut_installed() is False

