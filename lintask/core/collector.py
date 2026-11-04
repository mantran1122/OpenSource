"""Background worker thread collecting system metrics using psutil."""
import time
import os
import psutil
from PyQt6.QtCore import QThread, pyqtSignal

from ..models.metrics import (
    CPUMetrics,
    MemoryMetrics,
    DiskPartitionInfo,
    DiskMetrics,
    NetworkMetrics,
    SystemSnapshot,
)
from .process_mgr import ProcessManager


def _get_cpu_model_name() -> str:
    """Extract CPU model name from /proc/cpuinfo on Linux."""
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("model name"):
                        return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return "Generic Processor"


class MetricsCollector(QThread):
    """Worker thread running in the background to sample OS metrics without blocking GUI."""

    snapshot_ready = pyqtSignal(SystemSnapshot)
    processes_ready = pyqtSignal(list)

    def __init__(self, interval_sec: float = 1.0, parent=None):
        super().__init__(parent)
        self.interval_sec = interval_sec
        self._running = True
        self.process_mgr = ProcessManager()

        # Cache static hardware info
        self._cpu_model = _get_cpu_model_name()
        self._physical_cores = psutil.cpu_count(logical=False) or 1
        self._logical_cores = psutil.cpu_count(logical=True) or 1
        self._boot_time = psutil.boot_time()

        # Initialize initial counters for differential calculation
        self._prev_time = time.time()
        self._prev_disk_io = psutil.disk_io_counters()
        self._prev_net_io = psutil.net_io_counters()

        # Prime psutil CPU percent
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(percpu=True)

    def run(self):
        """Main loop executed in background thread."""
        while self._running:
            start_loop = time.time()
            try:
                snapshot = self._collect_snapshot()
                if self._running:
                    self.snapshot_ready.emit(snapshot)

                procs = self.process_mgr.scan_processes()
                if self._running:
                    self.processes_ready.emit(procs)
            except Exception as e:
                # Catch any unexpected OS exception to ensure thread stability
                print(f"[MetricsCollector Error]: {e}")

            # Sleep remaining time of the interval
            elapsed = time.time() - start_loop
            sleep_duration = max(0.1, self.interval_sec - elapsed)
            
            # Subdivide sleep to respond quickly to stop requests
            steps = int(sleep_duration / 0.1)
            for _ in range(steps):
                if not self._running:
                    break
                time.sleep(0.1)

    def stop(self):
        """Gracefully stop the collector thread."""
        self._running = False
        self.wait(1500)

    def _collect_snapshot(self) -> SystemSnapshot:
        now = time.time()
        time_delta = max(0.001, now - self._prev_time)
        self._prev_time = now

        # 1. CPU Metrics
        overall_cpu = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(percpu=True)
        freq_info = psutil.cpu_freq()
        current_freq = freq_info.current if freq_info else 0.0

        uptime = now - self._boot_time
        
        # Approximate process/thread counts
        pids = psutil.pids()
        proc_count = len(pids)
        thread_count = 0
        try:
            # Sample threads from running processes
            for p in psutil.process_iter(['num_threads']):
                thread_count += p.info.get('num_threads') or 1
        except Exception:
            thread_count = proc_count * 2

        cpu_metrics = CPUMetrics(
            overall_percent=overall_cpu,
            core_percents=per_core,
            current_freq_mhz=current_freq,
            total_physical_cores=self._physical_cores,
            total_logical_cores=self._logical_cores,
            uptime_seconds=uptime,
            process_count=proc_count,
            thread_count=thread_count,
            cpu_model_name=self._cpu_model,
        )

        # 2. Memory Metrics
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        mem_metrics = MemoryMetrics(
            total=vm.total,
            available=vm.available,
            used=vm.used,
            free=vm.free,
            percent=vm.percent,
            cached=getattr(vm, "cached", 0),
            buffers=getattr(vm, "buffers", 0),
            swap_total=sm.total,
            swap_used=sm.used,
            swap_percent=sm.percent,
        )

        # 3. Disk Metrics (I/O speed + Partitions)
        curr_disk_io = psutil.disk_io_counters()
        read_speed = 0.0
        write_speed = 0.0
        if curr_disk_io and self._prev_disk_io:
            read_speed = (curr_disk_io.read_bytes - self._prev_disk_io.read_bytes) / time_delta
            write_speed = (curr_disk_io.write_bytes - self._prev_disk_io.write_bytes) / time_delta
        self._prev_disk_io = curr_disk_io

        partitions_list = []
        try:
            for part in psutil.disk_partitions(all=False):
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    partitions_list.append(
                        DiskPartitionInfo(
                            device=part.device,
                            mountpoint=part.mountpoint,
                            fstype=part.fstype,
                            total=usage.total,
                            used=usage.used,
                            free=usage.free,
                            percent=usage.percent,
                        )
                    )
                except (PermissionError, OSError):
                    continue
        except Exception:
            pass

        disk_metrics = DiskMetrics(
            read_bytes_sec=max(0.0, read_speed),
            write_bytes_sec=max(0.0, write_speed),
            partitions=partitions_list,
        )

        # 4. Network Metrics (Throughput)
        curr_net_io = psutil.net_io_counters()
        sent_speed = 0.0
        recv_speed = 0.0
        if curr_net_io and self._prev_net_io:
            sent_speed = (curr_net_io.bytes_sent - self._prev_net_io.bytes_sent) / time_delta
            recv_speed = (curr_net_io.bytes_recv - self._prev_net_io.bytes_recv) / time_delta
        self._prev_net_io = curr_net_io

        net_metrics = NetworkMetrics(
            bytes_sent_sec=max(0.0, sent_speed),
            bytes_recv_sec=max(0.0, recv_speed),
        )

        return SystemSnapshot(
            timestamp=now,
            cpu=cpu_metrics,
            memory=mem_metrics,
            disk=disk_metrics,
            network=net_metrics,
        )

