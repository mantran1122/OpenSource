"""Core Process Manager for scanning, inspecting and controlling processes."""
import os
import subprocess
from typing import List, Dict, Tuple, Optional
import psutil

from ..models.process_info import ProcessInfo


class ProcessManager:
    """Manages process lifecycle, inspection, and operations."""

    def __init__(self):
        self._proc_cache: Dict[int, psutil.Process] = {}
        self._num_cores = psutil.cpu_count(logical=True) or 1
        # Prime the cache on init
        self._prime_cache()

    def _prime_cache(self):
        """Initial pass to populate process objects for delta calculation."""
        for p in psutil.process_iter(["pid"]):
            try:
                p.cpu_percent(interval=None)
                self._proc_cache[p.pid] = p
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def scan_processes(self) -> List[ProcessInfo]:
        """Scan and return structured information for all running processes."""
        current_pids = set()
        results: List[ProcessInfo] = []

        for p in psutil.process_iter([
            "pid",
            "name",
            "status",
            "memory_info",
            "memory_percent",
            "username",
            "nice",
            "num_threads",
        ]):
            try:
                pid = p.pid
                current_pids.add(pid)

                # Use cached instance for accurate CPU percent delta
                proc_obj = self._proc_cache.get(pid, p)
                self._proc_cache[pid] = proc_obj

                # Calculate normalized CPU % (0-100% total system, Windows-style)
                raw_cpu = proc_obj.cpu_percent(interval=None)
                normalized_cpu = max(0.0, raw_cpu / self._num_cores)

                mem_info = p.info.get("memory_info")
                mem_rss = mem_info.rss if mem_info else 0
                mem_pct = p.info.get("memory_percent") or 0.0

                # Disk I/O per process
                read_speed = 0.0
                write_speed = 0.0
                try:
                    io_counters = proc_obj.io_counters()
                    if io_counters:
                        read_speed = float(io_counters.read_bytes)
                        write_speed = float(io_counters.write_bytes)
                except (psutil.AccessDenied, AttributeError, psutil.NoSuchProcess):
                    pass

                cmdline = ""
                try:
                    cmdline = " ".join(proc_obj.cmdline() or [])
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                exe_path = ""
                try:
                    exe_path = proc_obj.exe() or ""
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    pass

                info = ProcessInfo(
                    pid=pid,
                    name=p.info.get("name") or "Unknown",
                    status=p.info.get("status") or "running",
                    cpu_percent=round(normalized_cpu, 1),
                    memory_bytes=mem_rss,
                    memory_percent=round(mem_pct, 1),
                    disk_read_bytes_sec=read_speed,
                    disk_write_bytes_sec=write_speed,
                    user=p.info.get("username") or "system",
                    nice=p.info.get("nice") or 0,
                    num_threads=p.info.get("num_threads") or 1,
                    cmdline=cmdline,
                    exe=exe_path,
                )
                results.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Prune dead PIDs from cache
        dead_pids = set(self._proc_cache.keys()) - current_pids
        for dead_pid in dead_pids:
            self._proc_cache.pop(dead_pid, None)

        return results

    def terminate_process(self, pid: int) -> Tuple[bool, str]:
        """Send SIGTERM (graceful shutdown) to a process."""
        try:
            p = psutil.Process(pid)
            name = p.name()
            p.terminate()
            return True, f"Terminated {name} (PID: {pid})"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} no longer exists"
        except psutil.AccessDenied:
            return False, f"Access denied for PID {pid}. Root permissions required."
        except Exception as e:
            return False, str(e)

    def kill_process(self, pid: int) -> Tuple[bool, str]:
        """Send SIGKILL (forced kill) to a process."""
        try:
            p = psutil.Process(pid)
            name = p.name()
            p.kill()
            return True, f"Force killed {name} (PID: {pid})"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} no longer exists"
        except psutil.AccessDenied:
            return False, f"Access denied for PID {pid}. Root permissions required."
        except Exception as e:
            return False, str(e)

    def pause_process(self, pid: int) -> Tuple[bool, str]:
        """Pause (SIGSTOP) a process."""
        try:
            p = psutil.Process(pid)
            p.suspend()
            return True, f"Paused {p.name()} (PID: {pid})"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} no longer exists"
        except psutil.AccessDenied:
            return False, f"Access denied for PID {pid}."
        except Exception as e:
            return False, str(e)

    def resume_process(self, pid: int) -> Tuple[bool, str]:
        """Resume (SIGCONT) a process."""
        try:
            p = psutil.Process(pid)
            p.resume()
            return True, f"Resumed {p.name()} (PID: {pid})"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} no longer exists"
        except psutil.AccessDenied:
            return False, f"Access denied for PID {pid}."
        except Exception as e:
            return False, str(e)

    def set_priority(self, pid: int, nice_value: int) -> Tuple[bool, str]:
        """Adjust process priority (nice value from -20 to 19)."""
        try:
            p = psutil.Process(pid)
            p.nice(nice_value)
            return True, f"Set priority of {p.name()} to {nice_value}"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} no longer exists"
        except psutil.AccessDenied:
            return False, f"Access denied for PID {pid}. Higher priority requires root."
        except Exception as e:
            return False, str(e)

    def open_file_location(self, pid: int) -> Tuple[bool, str]:
        """Open the folder containing the process executable."""
        try:
            p = psutil.Process(pid)
            exe = p.exe()
            if not exe or not os.path.exists(exe):
                return False, f"Executable path for PID {pid} not accessible."
            
            folder = os.path.dirname(exe)
            subprocess.Popen(["xdg-open", folder])
            return True, f"Opened {folder}"
        except Exception as e:
            return False, f"Could not open location: {e}"

