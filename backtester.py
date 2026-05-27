from tick_engine import TickEngine

class Backtester:
    def __init__(self, ticks):
        self.ticks = ticks

    def run(self):
        engine = TickEngine()
        results = []

        for i, price in enumerate(self.ticks):
            tick = {"quote": price}

            output = engine.process_tick(tick)

            if not output:
                continue

            results.append({
                "index": i,
                "price": price,
                "signal": output["signal"],
                "confidence": output["confidence"],
                "regime": output["volatility"]
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

        return {
            "total_trades": trades,
            "wins": wins,
            "losses": losses,
            "accuracy": round(wins / trades, 3) if trades else 0
        }
        
