from collections import defaultdict, Counter

class PatternEngine:
    def __init__(self, window_size=1000):
        self.window_size = window_size
        self.ticks = []

        # structure:
        # {volatility: {pattern: Counter(next_digits)}}
        self.db = {
            "low": defaultdict(list),
            "mid": defaultdict(list),
            "high": defaultdict(list),
        }

    def update(self, tick, vol_state):
        self.ticks.append(tick)

        if len(self.ticks) < 3:
            return

        # keep rolling window
        if len(self.ticks) > self.window_size:
            self.ticks.pop(0)

        # build 2-step patterns
        a, b, c = self.ticks[-3], self.ticks[-2], self.ticks[-1]
        pattern = (a, b)

        self.db[vol_state][pattern].append(c)

    def get_probability(self, pattern, vol_state):
        data = self.db[vol_state].get(pattern, [])
        if not data:
            return {}

        count = Counter(data)
        total = sum(count.values())

        return {k: v/total for k, v in count.items()}