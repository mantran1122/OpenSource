"""String and numeric formatters for metrics display."""

def format_bytes(num_bytes: float, decimals: int = 1) -> str:
    """Format bytes into human readable string (B, KB, MB, GB, TB)."""
    if num_bytes is None or num_bytes < 0:
        return "0.0 B"
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:.{decimals}f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.{decimals}f} EB"


def format_speed(bytes_per_sec: float, decimals: int = 1) -> str:
    """Format network or disk speed (e.g. 1.2 MB/s, 450 KB/s)."""
    return f"{format_bytes(bytes_per_sec, decimals)}/s"


def format_uptime(seconds: float) -> str:
    """Format uptime seconds into 'D:HH:MM:SS' format similar to Windows Task Manager."""
    if seconds is None or seconds < 0:
        return "00:00:00"
    
    sec = int(seconds)
    days, sec = divmod(sec, 86400)
    hours, sec = divmod(sec, 3600)
    minutes, sec = divmod(sec, 60)
    
    if days > 0:
        return f"{days}:{hours:02d}:{minutes:02d}:{sec:02d}"
    return f"{hours:02d}:{minutes:02d}:{sec:02d}"


def format_freq(mhz: float) -> str:
    """Format frequency in MHz or GHz."""
    if mhz is None or mhz <= 0:
        return "-- GHz"
    if mhz >= 1000.0:
        return f"{mhz / 1000.0:.2f} GHz"
    return f"{int(mhz)} MHz"


def format_percent(val: float, decimals: int = 1) -> str:
    """Format percentage value."""
    if val is None or val < 0:
        return "0%"
    return f"{val:.{decimals}f}%"

