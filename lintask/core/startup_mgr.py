"""Manager for scanning, parsing, enabling, disabling, and creating Linux autostart items."""
import os
import re
from typing import List, Tuple, Dict, Optional
from ..models.startup_item import StartupItem


def _parse_desktop_file(file_path: str) -> Dict[str, str]:
    """Parse key-value pairs inside [Desktop Entry] section of a .desktop file."""
    data = {}
    in_entry = False
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line == "[Desktop Entry]":
                    in_entry = True
                    continue
                elif line.startswith("[") and line.endswith("]"):
                    in_entry = False
                    continue

                if in_entry and "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    data[key.strip()] = val.strip()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return data


def _write_desktop_file(file_path: str, fields: Dict[str, str]):
    """Update or create a .desktop file with given fields."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    existing_lines = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                existing_lines = f.readlines()
        except Exception:
            existing_lines = []

    if not existing_lines:
        existing_lines = ["[Desktop Entry]\n", "Type=Application\n"]

    # Update or append keys
    updated_lines = []
    keys_handled = set()
    in_entry = False

    for line in existing_lines:
        stripped = line.strip()
        if stripped == "[Desktop Entry]":
            in_entry = True
            updated_lines.append(line)
            continue
        elif stripped.startswith("[") and stripped.endswith("]"):
            # Before leaving [Desktop Entry], write remaining keys
            if in_entry:
                for k, v in fields.items():
                    if k not in keys_handled:
                        updated_lines.append(f"{k}={v}\n")
                        keys_handled.add(k)
            in_entry = False
            updated_lines.append(line)
            continue

        if in_entry and "=" in stripped and not stripped.startswith("#"):
            k = stripped.split("=", 1)[0].strip()
            if k in fields:
                updated_lines.append(f"{k}={fields[k]}\n")
                keys_handled.add(k)
                continue

        updated_lines.append(line)

    if in_entry:
        for k, v in fields.items():
            if k not in keys_handled:
                updated_lines.append(f"{k}={v}\n")
                keys_handled.add(k)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)


class StartupManager:
    """Discovers and configures XDG Autostart applications."""

    USER_AUTOSTART_DIR = os.path.expanduser("~/.config/autostart")
    SYSTEM_AUTOSTART_DIR = "/etc/xdg/autostart"

    def __init__(self):
        os.makedirs(self.USER_AUTOSTART_DIR, exist_ok=True)

    def scan_startup_items(self) -> List[StartupItem]:
        """Scan both user and system autostart directories, resolving overrides."""
        items_by_filename: Dict[str, StartupItem] = {}

        # 1. System Autostart
        if os.path.exists(self.SYSTEM_AUTOSTART_DIR):
            try:
                for fname in os.listdir(self.SYSTEM_AUTOSTART_DIR):
                    if not fname.endswith(".desktop"):
                        continue
                    full_path = os.path.join(self.SYSTEM_AUTOSTART_DIR, fname)
                    data = _parse_desktop_file(full_path)
                    if not data:
                        continue

                    hidden = data.get("Hidden", "").lower() == "true"
                    gnome_disabled = data.get("X-GNOME-Autostart-enabled", "").lower() == "false"
                    enabled = not (hidden or gnome_disabled)

                    name = data.get("Name") or os.path.splitext(fname)[0]
                    command = data.get("Exec") or ""
                    comment = data.get("Comment") or ""
                    icon = data.get("Icon") or ""

                    items_by_filename[fname] = StartupItem(
                        file_name=fname,
                        name=name,
                        command=command,
                        comment=comment,
                        icon=icon,
                        is_system=True,
                        enabled=enabled,
                        file_path=full_path,
                    )
            except Exception as e:
                print(f"Error scanning system autostart: {e}")

        # 2. User Autostart (overrides system entries if same filename)
        if os.path.exists(self.USER_AUTOSTART_DIR):
            try:
                for fname in os.listdir(self.USER_AUTOSTART_DIR):
                    if not fname.endswith(".desktop"):
                        continue
                    full_path = os.path.join(self.USER_AUTOSTART_DIR, fname)
                    data = _parse_desktop_file(full_path)
                    if not data:
                        continue

                    hidden = data.get("Hidden", "").lower() == "true"
                    gnome_disabled = data.get("X-GNOME-Autostart-enabled", "").lower() == "false"
                    enabled = not (hidden or gnome_disabled)

                    # If this overrides a system item, inherit details if user file only contains override flags
                    name = data.get("Name") or (items_by_filename[fname].name if fname in items_by_filename else os.path.splitext(fname)[0])
                    command = data.get("Exec") or (items_by_filename[fname].command if fname in items_by_filename else "")
                    comment = data.get("Comment") or (items_by_filename[fname].comment if fname in items_by_filename else "")
                    icon = data.get("Icon") or (items_by_filename[fname].icon if fname in items_by_filename else "")

                    is_sys = fname in items_by_filename

                    items_by_filename[fname] = StartupItem(
                        file_name=fname,
                        name=name,
                        command=command,
                        comment=comment,
                        icon=icon,
                        is_system=is_sys,
                        enabled=enabled,
                        file_path=full_path,
                    )
            except Exception as e:
                print(f"Error scanning user autostart: {e}")

        # Sort alphabetically by app name
        return sorted(items_by_filename.values(), key=lambda x: x.name.lower())

    def set_enabled(self, item: StartupItem, enabled: bool) -> Tuple[bool, str]:
        """Enable or disable a startup item."""
        user_path = os.path.join(self.USER_AUTOSTART_DIR, item.file_name)
        val_str = "true" if enabled else "false"
        hidden_str = "false" if enabled else "true"

        try:
            # If it's a system item that hasn't been copied to user dir yet
            if item.is_system and not os.path.exists(user_path):
                # Copy system desktop file to user autostart dir
                sys_path = os.path.join(self.SYSTEM_AUTOSTART_DIR, item.file_name)
                with open(sys_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                with open(user_path, "w", encoding="utf-8") as f:
                    f.write(content)

            # Update flags in user autostart
            _write_desktop_file(
                user_path,
                {
                    "Hidden": hidden_str,
                    "X-GNOME-Autostart-enabled": val_str,
                },
            )

            state_label = "enabled" if enabled else "disabled"
            return True, f"'{item.name}' has been {state_label}."
        except Exception as e:
            return False, f"Failed to update '{item.name}': {e}"

    def add_startup_item(self, name: str, command: str, comment: str = "") -> Tuple[bool, str]:
        """Create a new user autostart .desktop item."""
        if not name.strip() or not command.strip():
            return False, "Name and Command cannot be empty."

        slug = re.sub(r"[^a-zA-Z0-9_-]", "_", name.lower().strip())
        fname = f"{slug}.desktop"
        user_path = os.path.join(self.USER_AUTOSTART_DIR, fname)

        try:
            fields = {
                "Type": "Application",
                "Name": name.strip(),
                "Exec": command.strip(),
                "Comment": comment.strip(),
                "Hidden": "false",
                "X-GNOME-Autostart-enabled": "true",
                "Terminal": "false",
            }
            _write_desktop_file(user_path, fields)
            return True, f"Added '{name}' to startup apps."
        except Exception as e:
            return False, f"Failed to create startup app: {e}"

    def delete_startup_item(self, item: StartupItem) -> Tuple[bool, str]:
        """Remove startup item or reset system override."""
        user_path = os.path.join(self.USER_AUTOSTART_DIR, item.file_name)
        try:
            if os.path.exists(user_path):
                os.remove(user_path)
                return True, f"Removed '{item.name}'."
            elif item.is_system:
                return False, "Cannot delete system-wide startup app. Use the toggle switch to disable it instead."
            return False, "File does not exist."
        except Exception as e:
            return False, f"Error deleting item: {e}"

