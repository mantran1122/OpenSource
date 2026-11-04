"""Data structure representing a single running process."""
from dataclasses import dataclass


@dataclass
class ProcessInfo:
    pid: int
    name: str
    status: str
    cpu_percent: float
    memory_bytes: int
    memory_percent: float
    disk_read_bytes_sec: float
    disk_write_bytes_sec: float
    user: str
    nice: int
    num_threads: int
    cmdline: str
    exe: str

