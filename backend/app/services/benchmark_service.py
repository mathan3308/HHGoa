import numpy as np
from typing import List, Dict, Any

class BenchmarkService:
    """Latency analytics calculator for P50, P70, P100 metrics."""
    _instance = None
    records: List[Dict[str, Any]] = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BenchmarkService, cls).__new__(cls)
            cls._instance.records = []
        return cls._instance

    def add_record(self, record: Dict[str, Any]) -> None:
        self.records.append(record)

    def get_summary(self) -> Dict[str, Any]:
        if not self.records:
            return {"status": "no_data", "count": 0}

        rag_latencies = [r["latency"]["total_rag_ms"] for r in self.records if "latency" in r]
        e2e_latencies = [r["latency"]["total_end_to_end_ms"] for r in self.records if "latency" in r]

        if not rag_latencies:
            return {"status": "no_data", "count": 0}

        return {
            "query_count": len(self.records),
            "rag_latency": {
                "p50": float(np.percentile(rag_latencies, 50)),
                "p70": float(np.percentile(rag_latencies, 70)),
                "p100": float(np.max(rag_latencies)),
                "mean": float(np.mean(rag_latencies)),
                "min": float(np.min(rag_latencies)),
                "max": float(np.max(rag_latencies))
            },
            "end_to_end_latency": {
                "p50": float(np.percentile(e2e_latencies, 50)),
                "p70": float(np.percentile(e2e_latencies, 70)),
                "p100": float(np.max(e2e_latencies)),
                "mean": float(np.mean(e2e_latencies)),
                "min": float(np.min(e2e_latencies)),
                "max": float(np.max(e2e_latencies))
            }
        }
