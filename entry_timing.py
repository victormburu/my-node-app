import time
from collections import deque

class EntryTimingModel:

    def __init__(self):

        self.history = deque(maxlen=30)

        self.decay_threshold = 45

    def update(self, signal_score):

        self.history.append({
            "time": time.time(),
            "score": signal_score
        })

    def estimate_delay(self):

        if len(self.history) < 5:
            return {
                "ready": False,
                "delay_seconds": None,
                "confidence_peak": 0,
                "state": "COLLECTING"
            }

        latest = self.history[-1]["score"]

        peak = max(x["score"] for x in self.history)

        # signal still growing
        if latest >= peak * 0.9:

            return {
                "ready": True,
                "delay_seconds": 0,
                "confidence_peak": peak,
                "state": "ENTRY READY"
            }

        # signal decaying
        decay = peak - latest

        delay_seconds = round(decay / 4, 1)

        return {
            "ready": False,
            "delay_seconds": delay_seconds,
            "confidence_peak": peak,
            "state": "WAITING RE-ENTRY"
        }