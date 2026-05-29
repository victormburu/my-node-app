from collections import defaultdict, Counter

class PatternEngine:
    def __init__(self, window_size=1000):

        self.window_size = window_size

        # store DIGITS only (IMPORTANT FIX)
        self.ticks = []

        self.db = {
            "low": defaultdict(list),
            "mid": defaultdict(list),
            "high": defaultdict(list),
        }

    # ------------------------
    # SAFE DIGIT EXTRACTION
    # ------------------------
    def _to_digit(self, value):
        return int(str(float(value))[-1])

    # ------------------------
    # UPDATE MODEL
    # ------------------------
    def update(self, tick, vol_state):

        digit = self._to_digit(tick)

        self.ticks.append(digit)

        if len(self.ticks) > self.window_size:
            self.ticks.pop(0)

        if len(self.ticks) < 3:
            return

        a = int(str(self.ticks[-3])[-1])
        b = int(str(self.ticks[-2])[-1])
        c = int(str(self.ticks[-1])[-1])

        pattern = (a, b)
        self.db[vol_state][pattern].append(c)

    # ------------------------
    # PROBABILITY MODEL
    # ------------------------
    def get_probability(self, pattern, vol_state):

        if vol_state not in self.db:
            return {}

        data = self.db[vol_state].get(pattern, [])

        if not data:
            return {}

        count = Counter(data)
        total = sum(count.values())

        return {digit: freq / total for digit, freq in count.items()}