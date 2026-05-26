from tick_engine import TickEngine

class Backtester:
    def __init__(self, ticks):
        """
        ticks = historical list of price values
        e.g. [1234.56, 1234.57, ...]
        """
        self.ticks = ticks

    def run(self):
        engine = TickEngine()

        results = []

        for price in self.ticks:
            tick = {"quote": price}

            engine.process_tick(tick)

            signal = engine.generate_signal()
            regime = engine.market_regime()

            # simulate outcome using next tick (simple proxy)
            results.append({
                "price": price,
                "signal": signal["signal"],
                "confidence": signal["confidence"],
                "regime": regime["regime"]
            })

        return results
class BacktestReport:
    def __init__(self, results):
        self.results = results

    def evaluate(self):
        wins = 0
        losses = 0
        trades = 0

        for i in range(len(self.results) - 1):
            current = self.results[i]
            next_price = self.results[i + 1]["price"]

            signal = current["signal"]

            if signal == "NO_TRADE":
                continue

            trades += 1

            # simplified directional evaluation
            if signal == "OVER":
                if next_price > current["price"]:
                    wins += 1
                else:
                    losses += 1

            elif signal == "UNDER":
                if next_price < current["price"]:
                    wins += 1
                else:
                    losses += 1

        accuracy = wins / trades if trades > 0 else 0

        return {
            "total_trades": trades,
            "wins": wins,
            "losses": losses,
            "accuracy": round(accuracy, 3)
        }