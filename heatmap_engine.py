from collections import defaultdict, Counter

class HeatmapEngine:
    def __init__(self):
        # structure:
        # vol → pattern → list of next digits
        self.data = {
            "low": defaultdict(list),
            "mid": defaultdict(list),
            "high": defaultdict(list)
        }

    def update(self, vol, pattern, next_digit):
        self.data[vol][pattern].append(next_digit)

    def build_heatmap(self):
        heatmap = {}

        for vol, patterns in self.data.items():
            heatmap[vol] = {}

            for pattern, outcomes in patterns.items():
                count = Counter(outcomes)
                total = sum(count.values())

                heatmap[vol][pattern] = {
                    digit: round(freq / total, 3)
                    for digit, freq in count.items()
                }

        return heatmap