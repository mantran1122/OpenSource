"""Dataclasses representing system metrics snapshots."""
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CPUMetrics:
    overall_percent: float = 0.0
    core_percents: List[float] = field(default_factory=list)
    current_freq_mhz: float = 0.0
    total_physical_cores: int = 1
    total_logical_cores: int = 1
    uptime_seconds: float = 0.0
    process_count: int = 0
    thread_count: int = 0
    cpu_model_name: str = "Processor"


@dataclass
class MemoryMetrics:
    total: int = 0
    available: int = 0
    used: int = 0
    free: int = 0
    percent: float = 0.0
    cached: int = 0
    buffers: int = 0
    swap_total: int = 0
    swap_used: int = 0
    swap_percent: float = 0.0


@dataclass
class DiskPartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total: int
    used: int
    free: int
    percent: float


@dataclass
class DiskMetrics:
    read_bytes_sec: float = 0.0
    write_bytes_sec: float = 0.0
    partitions: List[DiskPartitionInfo] = field(default_factory=list)


@dataclass
class NetworkMetrics:
    bytes_sent_sec: float = 0.0
    bytes_recv_sec: float = 0.0
    primary_interface: str = "eth0"
    interfaces: Dict[str, dict] = field(default_factory=dict)


@dataclass
class SystemSnapshot:
    timestamp: float
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    network: NetworkMetrics

