import time
from collections import deque

class EntryTimingModel:

    def __init__(self):
        # stores recent signal strengths over time
        self.history = deque(maxlen=50)

        self.last_signal_time = None

    def update(self, signal_score):

        now = time.time()

        self.history.append({
            "time": now,
            "score": signal_score
        })

        self.last_signal_time = now

    def estimate_delay(self):

        if len(self.history) < 10:
            return {
                "ready": False,
                "delay_seconds": None,
                "confidence_peak": None
            }

        scores = list(self.history)

        # find best future-like peak proxy (local max behavior)
        peak_index = max(range(len(scores)), key=lambda i: scores[i]["score"])

        peak_time = scores[peak_index]["time"]
        current_time = scores[-1]["time"]

        delay = peak_time - current_time

        return {
            "ready": delay <= 0,
            "delay_seconds": max(0, round(delay, 2)),
            "confidence_peak": scores[peak_index]["score"]
        }