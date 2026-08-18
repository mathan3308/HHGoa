import time
from contextlib import contextmanager

class LatencyTimer:
    """High-precision timer for tracking component latency in milliseconds."""
    def __init__(self):
        self.start_time = 0.0
        self.elapsed_ms = 0.0

    def start(self):
        self.start_time = time.perf_counter()
        return self

    def stop(self) -> float:
        self.elapsed_ms = (time.perf_counter() - self.start_time) * 1000.0
        return round(self.elapsed_ms, 2)

@contextmanager
def measure_latency():
    """Context manager yielding elapsed milliseconds upon exit."""
    timer = LatencyTimer()
    timer.start()
    yield timer
    timer.stop()
