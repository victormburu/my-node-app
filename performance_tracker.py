from collections import defaultdict

class PerformanceTracker:
    def __init__(self):
        self.stats = defaultdict(lambda: {
            "wins": 0,
            "losses": 0
        })

    def record(self,
               pattern,
               volatility,
               predicted,
               actual):

        key = f"{pattern}_{volatility}_{predicted}"

        if predicted == actual:
            self.stats[key]["wins"] += 1
        else:
            self.stats[key]["losses"] += 1

    def report(self):
        output = {}

        for key, stat in self.stats.items():

            total = stat["wins"] + stat["losses"]

            accuracy = (
                stat["wins"] / total
                if total > 0 else 0
            )

            output[key] = {
                "wins": stat["wins"],
                "losses": stat["losses"],
                "accuracy": round(accuracy, 3)
            }

        return output