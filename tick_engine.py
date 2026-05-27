from volatility_engine import VolatilityEngine
from performance_tracker import PerformanceTracker
from heatmap_filter import HeatmapFilter
from heatmap_engine import HeatmapEngine
from pattern_engine import PatternEngine
from signal_engine import SignalEngine
from mode_manager import ModeManager
from collections import deque

class TickEngine:
    def __init__(self):
        self.vol = VolatilityEngine()
        self.performance = PerformanceTracker()
        self.pattern = PatternEngine()
        self.filter = HeatmapFilter()
        self.signal = SignalEngine()
        self.mode_manager = ModeManager()
        self.heatmap = HeatmapEngine()

        # store ONLY numeric prices
        self.prices = deque(maxlen=1000)

    # ----------------------------
    # MAIN PROCESSOR (LIVE + REPLAY)
    # ----------------------------
    def process(self, tick):
        price = tick["quote"]

        self.prices.append(price)

        vol_state = self.vol.update(price)
        self.pattern.update(price, vol_state)

        if len(self.prices) < 3:
            return None

        # clean numeric pattern (IMPORTANT FIX)
        pattern = (self.prices[-2], self.prices[-1])

        prob = self.pattern.get_probability(pattern, vol_state)

        heatmap_data = self.heatmap.build_heatmap()

        filtered = self.filter.validate(
            heatmap_data,
            vol_state,
            pattern
        )
        if filtered and filtered["valid"]:

            signal = {
                "signal": True,
                "digit": filtered["digit"],
                "confidence": filtered["confidence"]
            }

        else:

            signal = {
                "signal": False,
                "digit": None,
                "confidence": 0
            }
            
        pattern = tuple(self.prices[-2:])

        next_digit = int(str(price)[-1])  # digit extraction (important)

        self.heatmap.update(vol_state, pattern, next_digit)
        predicted_digit = signal["digit"]
        actual_digit = int(str(price)[-1])

        self.performance.record(
            pattern,
            vol_state,
            predicted_digit,
            actual_digit
        )

        return {
            "price": price,
            "volatility": vol_state,
            "pattern": pattern,
            "probability": prob,
            "signal": signal
        }
        
    
    # ----------------------------
    # REPLAY STEP (IMPORTANT ADDITION)
    # ----------------------------
    def step(self):
        tick = self.mode_manager.next_tick()

        if tick is None:
            return None

        return self.process(tick)