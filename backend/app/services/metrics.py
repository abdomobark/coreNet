from typing import Dict, Tuple
import threading

_lock = threading.Lock()
_counters: Dict[str, float] = {}
_gauges: Dict[str, float] = {}

def inc(name: str, value: float = 1.0) -> None:
    with _lock:
        _counters[name] = _counters.get(name, 0.0) + value

def set_gauge(name: str, value: float) -> None:
    with _lock:
        _gauges[name] = float(value)

def scrape() -> str:
    # Very small subset of Prometheus text format
    lines = []
    with _lock:
        for k, v in _counters.items():
            lines.append(f"# TYPE {k} counter")
            lines.append(f"{k} {v}")
        for k, v in _gauges.items():
            lines.append(f"# TYPE {k} gauge")
            lines.append(f"{k} {v}")
    return "\n".join(lines) + "\n"
