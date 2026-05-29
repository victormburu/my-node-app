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

        # store raw prices
        self.prices = deque(maxlen=1000)

        # store LAST DIGITS ONLY
        self.digits = deque(maxlen=1000)

    # =========================================
    # MAIN PROCESSOR
    # =========================================
    def process(self, tick):

        try:

            # -------------------------
            # PRICE
            # -------------------------
            price = float(tick["quote"])

            self.prices.append(price)

            # -------------------------
            # LAST DIGIT
            # -------------------------
            digit = int(str(price)[-1])

            self.digits.append(digit)

            if len(self.digits) < 3:
                return None

            # -------------------------
            # VOLATILITY
            # -------------------------
            vol_state = self.vol.update(price)

            # -------------------------
            # DIGIT PATTERN
            # -------------------------
            pattern = (
                self.digits[-3],
                self.digits[-2]
            )

            # teach engine
            self.pattern.update(digit, vol_state)

            # probability map
            prob = self.pattern.get_probability(
                pattern,
                vol_state
            )

            # -------------------------
            # HEATMAP UPDATE
            # -------------------------
            self.heatmap.update(
                vol_state,
                pattern,
                digit
            )

            heatmap_data = self.heatmap.build_heatmap()

            # -------------------------
            # FILTER VALIDATION
            # -------------------------
            filtered = self.filter.validate(
                heatmap_data,
                vol_state,
                pattern
            )

            # -------------------------
            # DEFAULT SIGNAL
            # -------------------------
            signal = {
                "signal": False,
                "digit": None,
                "confidence": 0
            }

            entry = {
                "score": 0,
                "quality": "LOW"
            }

            # -------------------------
            # SIGNAL GENERATION
            # -------------------------
            if filtered and filtered.get("valid"):

                signal = {
                    "signal": True,
                    "digit": int(filtered["digit"]),
                    "confidence": float(
                        filtered.get("confidence", 0)
                    )
                }

                entry = self.scorer.score(
                    signal,
                    prob,
                    vol_state
                )

            # -------------------------
            # ENTRY FILTER
            # -------------------------
            auto_entry_valid = (
                signal["signal"]
                and entry["score"] >= 45
            )

            if not auto_entry_valid:

                signal["signal"] = False

            # -------------------------
            # PERFORMANCE TRACKING
            # -------------------------
            if signal["signal"]:

                self.performance.record(
                    pattern,
                    vol_state,
                    signal["digit"],
                    digit
                )

            # -------------------------
            # TIMING MODEL
            # -------------------------
            self.timing.update(entry["score"])

            timing = self.timing.estimate_delay()

            # -------------------------
            # DIGIT FREQUENCIES
            # -------------------------
            frequencies = {}

            for i in range(10):

                value = prob.get(i, 0)

                frequencies[i] = round(
                    value * 100,
                    2
                )

            # -------------------------
            # OUTPUT
            # -------------------------
            output = {

                "price": price,

                "digit": digit,

                "volatility": vol_state,

                "pattern": pattern,

                "probability": prob,

                "frequencies": frequencies,

                "signal": signal,

                "entry": entry,

                "timing": timing
            }

            self.latest_output = output
            self.latest = output

            return output

        except Exception as e:

            print("Tick processing error:", e)

            return None

    # =========================================
    # ANALYTICS
    # =========================================
    def analytics(self):

        if not self.latest_output:

            return {
                "status": "waiting_for_ticks"
            }

        return self.latest_output

    # =========================================
    # SIGNAL STATUS
    # =========================================
    def generate_signal(self):

        return {
            "status": "running"
        }

    # =========================================
    # REPLAY MODE
    # =========================================
    def step(self):

        tick = self.mode_manager.next_tick()

        if tick is None:
            return None

        return self.process(tick)