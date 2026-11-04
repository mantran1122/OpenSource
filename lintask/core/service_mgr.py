"""Manager for scanning, querying and controlling Linux systemd services."""
import os
import shutil
import subprocess
from typing import List, Tuple, Optional
from ..models.service_item import ServiceItem


def _get_systemctl_prefix() -> List[str]:
    """Detect how to call systemctl (native host vs flatpak container)."""
    # 1. Direct systemctl in PATH
    if shutil.which("systemctl"):
        return ["systemctl"]

    # 2. Common system paths
    for p in ["/bin/systemctl", "/usr/bin/systemctl", "/usr/sbin/systemctl"]:
        if os.path.exists(p):
            return [p]

    # 3. Inside Flatpak / Bubblewrap container
    if shutil.which("flatpak-spawn"):
        return ["flatpak-spawn", "--host", "systemctl"]

    return ["systemctl"]


class ServiceManager:
    """Interacts with systemd to list, start, stop, restart, enable and disable services."""

    def __init__(self):
        self._prefix = _get_systemctl_prefix()

    def scan_services(self) -> List[ServiceItem]:
        """Fetch all systemd services and parse their states."""
        cmd = self._prefix + ["list-units", "--type=service", "--all", "--no-pager", "--no-legend"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if res.returncode != 0:
                print(f"[ServiceManager] systemctl returned {res.returncode}: {res.stderr}")
                return []

            services: List[ServiceItem] = []
            for raw_line in res.stdout.splitlines():
                line = raw_line.strip()
                if not line:
                    continue

                # Strip bullet symbol (●) used by systemd for failed services
                if line.startswith("●") or line.startswith("*"):
                    line = line.lstrip("●* ").strip()

                parts = line.split(None, 4)
                if len(parts) >= 4:
                    unit_name = parts[0]
                    # Only keep .service units
                    if not unit_name.endswith(".service"):
                        continue

                    load_state = parts[1]
                    active_state = parts[2]
                    sub_state = parts[3]
                    description = parts[4] if len(parts) > 4 else ""

                    services.append(
                        ServiceItem(
                            name=unit_name,
                            load_state=load_state,
                            active_state=active_state,
                            sub_state=sub_state,
                            description=description,
                        )
                    )

            # Sort alphabetically by service name
            return sorted(services, key=lambda s: s.name.lower())
        except Exception as e:
            print(f"[ServiceManager Error]: {e}")
            return []

    def _execute_service_action(self, action: str, service_name: str) -> Tuple[bool, str]:
        """Run systemctl action with fallback to pkexec on permission failure."""
        cmd = self._prefix + [action, service_name]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
            if res.returncode == 0:
                return True, f"Successfully executed '{action}' on {service_name}."

            err_msg = res.stderr.strip()
            # If authentication / permission failed, try pkexec for graphical auth prompt
            if "Authentication required" in err_msg or "Interactive authentication required" in err_msg or "Access denied" in err_msg:
                pkexec_cmd = ["pkexec", "systemctl", action, service_name]
                if "flatpak-spawn" in self._prefix:
                    pkexec_cmd = ["flatpak-spawn", "--host", "pkexec", "systemctl", action, service_name]

                try:
                    pk_res = subprocess.run(pkexec_cmd, capture_output=True, text=True, timeout=20)
                    if pk_res.returncode == 0:
                        return True, f"Successfully executed '{action}' on {service_name}."
                    return False, pk_res.stderr.strip() or f"Failed to {action} {service_name} (Auth cancelled)."
                except Exception as pke:
                    return False, f"Permission error: {pke}"

            return False, err_msg or f"Failed to {action} {service_name}."
        except Exception as e:
            return False, f"Error: {e}"

    def start_service(self, service_name: str) -> Tuple[bool, str]:
        """Start an inactive service."""
        return self._execute_service_action("start", service_name)

    def stop_service(self, service_name: str) -> Tuple[bool, str]:
        """Stop an active service."""
        return self._execute_service_action("stop", service_name)

    def restart_service(self, service_name: str) -> Tuple[bool, str]:
        """Restart a service."""
        return self._execute_service_action("restart", service_name)

    def enable_service(self, service_name: str) -> Tuple[bool, str]:
        """Enable a service to launch at boot."""
        return self._execute_service_action("enable", service_name)

    def disable_service(self, service_name: str) -> Tuple[bool, str]:
        """Disable a service from launching at boot."""
        return self._execute_service_action("disable", service_name)

