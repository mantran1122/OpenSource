"""Test ProcessManager and ProcessTableModel."""
import pytest
from lintask.core.process_mgr import ProcessManager
from lintask.models.process_info import ProcessInfo
from lintask.models.process_model import ProcessTableModel, ProcessFilterProxyModel


def test_process_manager_scan():
    mgr = ProcessManager()
    procs = mgr.scan_processes()
    assert len(procs) > 0

    first_proc = procs[0]
    assert isinstance(first_proc, ProcessInfo)
    assert first_proc.pid > 0
    assert isinstance(first_proc.name, str)
    assert first_proc.cpu_percent >= 0.0


def test_process_table_model():
    model = ProcessTableModel()
    test_data = [
        ProcessInfo(
            pid=1001,
            name="chrome",
            status="running",
            cpu_percent=12.5,
            memory_bytes=1024 * 1024 * 500,
            memory_percent=5.0,
            disk_read_bytes_sec=1024,
            disk_write_bytes_sec=2048,
            user="user1",
            nice=0,
            num_threads=15,
            cmdline="/usr/bin/chrome",
            exe="/usr/bin/chrome",
        ),
        ProcessInfo(
            pid=1002,
            name="code",
            status="sleeping",
            cpu_percent=2.1,
            memory_bytes=1024 * 1024 * 250,
            memory_percent=2.5,
            disk_read_bytes_sec=0,
            disk_write_bytes_sec=0,
            user="user1",
            nice=0,
            num_threads=8,
            cmdline="code .",
            exe="/usr/bin/code",
        ),
    ]

    model.update_processes(test_data)
    assert model.rowCount() == 2
    assert model.columnCount() == 8


def test_process_proxy_filter():
    model = ProcessTableModel()
    proxy = ProcessFilterProxyModel()
    proxy.setSourceModel(model)

    test_data = [
        ProcessInfo(
            pid=1001,
            name="firefox",
            status="running",
            cpu_percent=10.0,
            memory_bytes=500000,
            memory_percent=1.0,
            disk_read_bytes_sec=0,
            disk_write_bytes_sec=0,
            user="mantran",
            nice=0,
            num_threads=4,
            cmdline="",
            exe="",
        ),
        ProcessInfo(
            pid=2002,
            name="spotify",
            status="running",
            cpu_percent=1.0,
            memory_bytes=200000,
            memory_percent=0.5,
            disk_read_bytes_sec=0,
            disk_write_bytes_sec=0,
            user="root",
            nice=0,
            num_threads=2,
            cmdline="",
            exe="",
        ),
    ]

    model.update_processes(test_data)
    assert proxy.rowCount() == 2

    # Filter by name
    proxy.set_filter_query("fire")
    assert proxy.rowCount() == 1

    # Filter by user
    proxy.set_filter_query("root")
    assert proxy.rowCount() == 1

    # Filter by PID
    proxy.set_filter_query("2002")
    assert proxy.rowCount() == 1

