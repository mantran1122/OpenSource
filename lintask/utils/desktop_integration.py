"""Helpers for registering LinTask into Linux application launcher menus and taskbars."""
import os
import sys
import shutil
import ast
import subprocess

APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DESKTOP_ENTRY_DIR = os.path.expanduser("~/.local/share/applications")
DESKTOP_ENTRY_PATH = os.path.join(DESKTOP_ENTRY_DIR, "lintask.desktop")
ICON_PATH = os.path.join(APP_DIR, "assets", "icons", "lintask.svg")
RUN_SCRIPT = os.path.join(APP_DIR, "run.py")
LOCAL_BIN_DIR = os.path.expanduser("~/.local/bin")
LOCAL_ICON_DIR = os.path.expanduser("~/.local/share/icons/hicolor/scalable/apps")


def _run_cmd(cmd: list[str], timeout: int = 5) -> tuple[int, str]:
    """Execute command, handling Flatpak sandbox escaping when necessary."""
    prefix = []
    if os.path.exists("/.flatpak-info") and shutil.which("flatpak-spawn"):
        prefix = ["flatpak-spawn", "--host"]
    try:
        res = subprocess.run(
            prefix + cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return res.returncode, res.stdout.strip()
    except Exception as e:
        return -1, str(e)


def is_shortcut_installed() -> bool:
    """Check if lintask.desktop already exists in user applications directory."""
    return os.path.exists(DESKTOP_ENTRY_PATH)


def _install_icons():
    """Copy scalable SVG icon to XDG icon theme directory."""
    try:
        os.makedirs(LOCAL_ICON_DIR, exist_ok=True)
        dest_icon = os.path.join(LOCAL_ICON_DIR, "lintask.svg")
        if os.path.exists(ICON_PATH) and not os.path.exists(dest_icon):
            shutil.copy2(ICON_PATH, dest_icon)
            _run_cmd(["gtk-update-icon-cache", "-f", "-t", os.path.expanduser("~/.local/share/icons/hicolor")])
    except Exception:
        pass


def _parse_gvariant_str_list(raw: str) -> list[str]:
    """Parse GVariant string array representation (e.g. @as [] or ['a', 'b'])."""
    try:
        clean = raw.removeprefix("@as ").strip()
        if clean.startswith("[") and clean.endswith("]"):
            val = ast.literal_eval(clean)
            if isinstance(val, list):
                return [str(x) for x in val]
    except Exception:
        pass
    return []


def _pin_to_gnome_favorites():
    """Pin LinTask Manager to GNOME Shell favorite apps (taskbar / dock)."""
    try:
        code, out = _run_cmd(["gsettings", "get", "org.gnome.shell", "favorite-apps"])
        if code == 0:
            favorites = _parse_gvariant_str_list(out)
            if "lintask.desktop" not in favorites:
                favorites.append("lintask.desktop")
                _run_cmd(["gsettings", "set", "org.gnome.shell", "favorite-apps", str(favorites)])
    except Exception:
        pass


def _unpin_from_gnome_favorites():
    """Remove LinTask Manager from GNOME Shell favorite apps."""
    try:
        code, out = _run_cmd(["gsettings", "get", "org.gnome.shell", "favorite-apps"])
        if code == 0:
            favorites = _parse_gvariant_str_list(out)
            if "lintask.desktop" in favorites:
                favorites = [f for f in favorites if f != "lintask.desktop"]
                _run_cmd(["gsettings", "set", "org.gnome.shell", "favorite-apps", str(favorites)])
    except Exception:
        pass


def _integrate_zorin_taskbar():
    """Add LinTask Manager entry directly to Zorin OS taskbar right-click context menu."""
    try:
        code, cmd_out = _run_cmd(["gsettings", "get", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-commands"])
        if code == 0:
            commands = _parse_gvariant_str_list(cmd_out)
            code2, title_out = _run_cmd(["gsettings", "get", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-titles"])
            titles = _parse_gvariant_str_list(title_out) if code2 == 0 else []
            
            # Clean up length mismatches if any
            min_len = min(len(commands), len(titles))
            commands = commands[:min_len]
            titles = titles[:min_len]

            if RUN_SCRIPT not in commands:
                commands.append(RUN_SCRIPT)
                titles.append("LinTask Manager")
                _run_cmd(["gsettings", "set", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-commands", str(commands)])
                _run_cmd(["gsettings", "set", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-titles", str(titles)])
    except Exception:
        pass


def _remove_from_zorin_taskbar():
    """Remove LinTask Manager entry from Zorin OS taskbar right-click context menu."""
    try:
        code, cmd_out = _run_cmd(["gsettings", "get", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-commands"])
        if code == 0:
            commands = _parse_gvariant_str_list(cmd_out)
            code2, title_out = _run_cmd(["gsettings", "get", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-titles"])
            titles = _parse_gvariant_str_list(title_out) if code2 == 0 else []

            new_cmds, new_titles = [], []
            for c, t in zip(commands, titles):
                if c != RUN_SCRIPT and "lintask" not in c.lower():
                    new_cmds.append(c)
                    new_titles.append(t)
            
            _run_cmd(["gsettings", "set", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-commands", str(new_cmds)])
            _run_cmd(["gsettings", "set", "org.gnome.shell.extensions.zorin-taskbar", "panel-context-menu-titles", str(new_titles)])
    except Exception:
        pass


def _install_system_monitor_overrides():
    """
    Ensure clicks on 'System Monitor' ('Theo dõi hệ thống') launch LinTask Manager.
    1. Overrides user desktop files for gnome-system-monitor and org.gnome.SystemMonitor.
    2. Installs ~/.local/bin/gnome-system-monitor wrapper.
    3. Attempts to install /usr/local/bin/gnome-system-monitor for global taskbar override.
    """
    wrapper_content = f"""#!/bin/bash
exec "{RUN_SCRIPT}" "$@"
"""
    # 1. ~/.local/bin wrapper
    try:
        os.makedirs(LOCAL_BIN_DIR, exist_ok=True)
        local_wrapper = os.path.join(LOCAL_BIN_DIR, "gnome-system-monitor")
        with open(local_wrapper, "w", encoding="utf-8") as f:
            f.write(wrapper_content)
        os.chmod(local_wrapper, 0o755)
    except Exception:
        pass

    # 2. User desktop entry overrides
    override_desktop_content = f"""[Desktop Entry]
Type=Application
Name=Theo dõi hệ thống (LinTask)
GenericName=Task Manager
Comment=Modern Windows-style Task Manager for Linux
Exec={RUN_SCRIPT}
Icon=lintask
Terminal=false
Categories=System;Monitor;
Keywords=task;manager;system;process;performance;monitor;
StartupNotify=true
X-GNOME-Utilities-Folder=System
"""
    for entry_name in ["gnome-system-monitor.desktop", "org.gnome.SystemMonitor.desktop"]:
        try:
            target = os.path.join(DESKTOP_ENTRY_DIR, entry_name)
            with open(target, "w", encoding="utf-8") as f:
                f.write(override_desktop_content)
        except Exception:
            pass

    # 3. Global /usr/local/bin wrapper (highest priority in GNOME Shell PATH)
    usr_local_wrapper = "/usr/local/bin/gnome-system-monitor"
    try:
        # If writable directly
        if os.access("/usr/local/bin", os.W_OK):
            with open(usr_local_wrapper, "w", encoding="utf-8") as f:
                f.write(wrapper_content)
            os.chmod(usr_local_wrapper, 0o755)
        else:
            # Try pkexec or passwordless sudo
            script = f'cat << "EOF" > {usr_local_wrapper}\n{wrapper_content}EOF\nchmod +x {usr_local_wrapper}'
            _run_cmd(["pkexec", "bash", "-c", script])
    except Exception:
        pass


def _remove_system_monitor_overrides():
    """Remove system monitor overrides."""
    for entry_name in ["gnome-system-monitor.desktop", "org.gnome.SystemMonitor.desktop"]:
        try:
            target = os.path.join(DESKTOP_ENTRY_DIR, entry_name)
            if os.path.exists(target):
                os.remove(target)
        except Exception:
            pass

    try:
        local_wrapper = os.path.join(LOCAL_BIN_DIR, "gnome-system-monitor")
        if os.path.exists(local_wrapper):
            os.remove(local_wrapper)
    except Exception:
        pass

    usr_local_wrapper = "/usr/local/bin/gnome-system-monitor"
    try:
        if os.path.exists(usr_local_wrapper):
            if os.access("/usr/local/bin", os.W_OK):
                os.remove(usr_local_wrapper)
            else:
                _run_cmd(["pkexec", "rm", "-f", usr_local_wrapper])
    except Exception:
        pass


def install_shortcut() -> tuple[bool, str]:
    """Create or update LinTask integration across application menus, docks, and taskbars."""
    try:
        os.makedirs(DESKTOP_ENTRY_DIR, exist_ok=True)

        content = f"""[Desktop Entry]
Type=Application
Name=LinTask Manager
GenericName=Task Manager
Comment=Modern Windows-style Task Manager for Linux
Exec={RUN_SCRIPT}
Icon=lintask
Terminal=false
Categories=System;Monitor;
Keywords=task;manager;system;process;performance;monitor;
StartupNotify=true
"""
        with open(DESKTOP_ENTRY_PATH, "w", encoding="utf-8") as f:
            f.write(content)

        # Ensure run.py is executable
        try:
            os.chmod(RUN_SCRIPT, 0o755)
        except Exception:
            pass

        # Install icons and desktop databases
        _install_icons()
        _run_cmd(["update-desktop-database", DESKTOP_ENTRY_DIR])

        # Integrate with GNOME taskbar, favorites, and Zorin context menus
        _pin_to_gnome_favorites()
        _integrate_zorin_taskbar()
        _install_system_monitor_overrides()

        return True, "LinTask Manager shortcut and taskbar integrations configured successfully."
    except Exception as e:
        return False, f"Failed to install desktop shortcut: {e}"


def remove_shortcut() -> tuple[bool, str]:
    """Remove LinTask Manager from application menus, dock favorites, and taskbars."""
    try:
        if os.path.exists(DESKTOP_ENTRY_PATH):
            os.remove(DESKTOP_ENTRY_PATH)

        _unpin_from_gnome_favorites()
        _remove_from_zorin_taskbar()
        _remove_system_monitor_overrides()
        _run_cmd(["update-desktop-database", DESKTOP_ENTRY_DIR])

        return True, "LinTask Manager removed from system shortcuts and taskbars."
    except Exception as e:
        return False, f"Failed to remove shortcut: {e}"
