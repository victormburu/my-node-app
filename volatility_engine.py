from collections import deque

class VolatilityEngine:
    def __init__(self, window=50):
        self.window = window
        self.buffer = deque(maxlen=window)

    def update(self, tick):
        self.buffer.append(tick)
        return self.get_state()

    def get_state(self):
        if len(self.buffer) < 10:
            return "low"

        changes = [
            abs(self.buffer[i] - self.buffer[i-1])
            for i in range(1, len(self.buffer))
        ]

        score = sum(changes) / len(changes)

        if score < 2.0:
            return "low"
        elif score < 4.0:
            return "mid"
        else:
            return "high"