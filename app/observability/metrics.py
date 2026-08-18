from collections import deque
import statistics
class Metrics:
    def __init__(self): self.values=deque(maxlen=1000)
    def record(self, response): self.values.append(response.latency_ms.total)
    def snapshot(self):
        v=sorted(self.values)
        percentile=lambda p: v[min(len(v)-1, max(0, int((len(v)-1)*p)))] if v else 0
        return {"query_count":len(v),"p50_ms":percentile(.5),"p70_ms":percentile(.7),"p100_ms":max(v, default=0),"mean_ms":statistics.mean(v) if v else 0}
metrics=Metrics()
