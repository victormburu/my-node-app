# pattern_research.py

from collections import defaultdict, Counter

def pattern_backtest(data, volatility_fn):
    results = {
        "low": defaultdict(list),
        "mid": defaultdict(list),
        "high": defaultdict(list)
    }

    window = 3

    for i in range(window, len(data)):
        a, b, c = data[i-3], data[i-2], data[i-1]

        vol = volatility_fn(data[:i])
        pattern = (a, b)

        results[vol][pattern].append(c)

    prob_map = {}

    for vol, patterns in results.items():
        prob_map[vol] = {}

        for pattern, outcomes in patterns.items():
            count = Counter(outcomes)
            total = sum(count.values())

            prob_map[vol][pattern] = {
                k: v / total for k, v in count.items()
            }

    return prob_map
