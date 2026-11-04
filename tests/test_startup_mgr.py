"""Test StartupManager autostart handling."""
import os
import tempfile
import pytest
from lintask.core.startup_mgr import StartupManager
from lintask.models.startup_item import StartupItem


def test_startup_manager_lifecycle():
    with tempfile.TemporaryDirectory() as temp_dir:
        mgr = StartupManager()
        mgr.USER_AUTOSTART_DIR = temp_dir
        mgr.SYSTEM_AUTOSTART_DIR = os.path.join(temp_dir, "empty_sys")

        # 1. Add item
        success, msg = mgr.add_startup_item("Test App", "/usr/bin/test-app --arg", "A test app")
        assert success is True
        assert os.path.exists(os.path.join(temp_dir, "test_app.desktop"))

        # 2. Scan items
        items = mgr.scan_startup_items()
        assert len(items) == 1
        item = items[0]
        assert item.name == "Test App"
        assert item.command == "/usr/bin/test-app --arg"
        assert item.enabled is True

        # 3. Toggle disabled
        success, msg = mgr.set_enabled(item, False)
        assert success is True
        items = mgr.scan_startup_items()
        assert items[0].enabled is False

        # 4. Toggle re-enabled
        success, msg = mgr.set_enabled(item, True)
        assert success is True
        items = mgr.scan_startup_items()
        assert items[0].enabled is True

        # 5. Delete item
        success, msg = mgr.delete_startup_item(item)
        assert success is True
        items = mgr.scan_startup_items()
        assert len(items) == 0
