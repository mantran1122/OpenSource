"""Test formatters utility."""
from lintask.utils.formatters import (
    format_bytes,
    format_speed,
    format_uptime,
    format_freq,
    format_percent,
)


def test_format_bytes():
    assert format_bytes(0) == "0.0 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024 * 1.5) == "1.5 MB"
    assert format_bytes(1024 * 1024 * 1024 * 4) == "4.0 GB"


def test_format_speed():
    assert format_speed(1024 * 500) == "500.0 KB/s"
    assert format_speed(1024 * 1024 * 12.5) == "12.5 MB/s"


def test_format_uptime():
    assert format_uptime(45) == "00:00:45"
    assert format_uptime(3665) == "01:01:05"
    assert format_uptime(90000) == "1:01:00:00"


def test_format_freq():
    assert format_freq(800) == "800 MHz"
    assert format_freq(3200) == "3.20 GHz"
    assert format_freq(0) == "-- GHz"


def test_format_percent():
    assert format_percent(15.42) == "15.4%"
    assert format_percent(100.0) == "100.0%"

