from volatility_engine import VolatilityEngine
from performance_tracker import PerformanceTracker
from entry_timing import EntryTimingModel
from heatmap_filter import HeatmapFilter
from heatmap_engine import HeatmapEngine
from pattern_engine import PatternEngine
from entry_scoring import EntryScoring
from signal_engine import SignalEngine
from mode_manager import ModeManager
from collections import deque

class TickEngine:
    def __init__(self):
        self.vol = VolatilityEngine()
        self.timing = EntryTimingModel()
        self.performance = PerformanceTracker()
        self.pattern = PatternEngine()
        self.filter = HeatmapFilter()
        self.scorer = EntryScoring()
        self.signal = SignalEngine()
        self.mode_manager = ModeManager()
        self.latest_output = {}
        self.latest = None
        self.heatmap = HeatmapEngine()

        # store ONLY numeric prices
        self.prices = deque(maxlen=1000)

    # ----------------------------
    # MAIN PROCESSOR (LIVE + REPLAY)
    # ----------------------------
    def process(self, tick):

        price = float(tick["quote"])
        self.prices.append(price)

        if len(self.prices) < 3:
            return None

        # =========================
        # VOLATILITY
        # =========================
        vol_state = self.vol.update(price)

        # =========================
        # PATTERN (CONSISTENT)
        # =========================
        pattern = (self.prices[-3], self.prices[-2], self.prices[-1])

        self.pattern.update(price, vol_state)

        prob = self.pattern.get_probability(
            (self.prices[-2], self.prices[-1]),
            vol_state
        )
        
        # =========================
        # HEATMAP FIRST (IMPORTANT FIX)
        # =========================
        next_digit = int(str(price)[-1])

        self.heatmap.update(
            vol_state,
            (self.prices[-2], self.prices[-1]),
            next_digit
        )

        heatmap_data = self.heatmap.build_heatmap()
        

        filtered = self.filter.validate(
            heatmap_data,
            vol_state,
            (self.prices[-2], self.prices[-1])
        )
        
        # =========================
        # SIGNAL GENERATION
        # =========================
        if filtered and filtered["valid"] and entry["score"] >=45:
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
        entry = self.scorer.score(signal, heatmap_data, vol_state)
        # =========================
        # PERFORMANCE TRACKING (SAFE)
        # =========================
        predicted_digit = signal["digit"]
        actual_digit = next_digit

        if predicted_digit is not None:
            self.performance.record(
                pattern,
                vol_state,
                predicted_digit,
                actual_digit
            )
        
        self.timing.update(entry["score"])
        timing = self.timing.estimate_delay()
        # =========================
        # STORE STATE
        # =========================
        output = {
            "price": price,
            "volatility": vol_state,
            "pattern": pattern,
            "probability": prob,
            "signal": signal,
            "entry": entry,
            "timing": timing
        }

        self.latest_output = output
        self.latest = output

        return output
        
    def analytics(self):

        if not self.latest_output:
            return {
                "status": "waiting_for_ticks"
            }

        return self.latest_output

    def generate_signal(self):
        return {
            "status": "running"
        }
    # ----------------------------
    # REPLAY STEP (IMPORTANT ADDITION)
    # ----------------------------
    def step(self):
        tick = self.mode_manager.next_tick()

        if tick is None:
            return None

        return self.process(tick)