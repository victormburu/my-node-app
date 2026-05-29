import json
import os
from threading import Lock

BUFFER_FILE = "tick_buffer.json"
lock = Lock()


class TickBuffer:
    def __init__(self):
        self.data = self._load()

    # ----------------------------
    # LOAD BUFFER
    # ----------------------------
    def _load(self):
        if not os.path.exists(BUFFER_FILE):
            return {}

        try:
            with open(BUFFER_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}

    # ----------------------------
    # SAVE BUFFER
    # ----------------------------
    def _save(self):
        with lock:
            with open(BUFFER_FILE, "w") as f:
                json.dump(self.data, f, indent=2)

    # ----------------------------
    # ADD TICK
    # ----------------------------
    def add_tick(self, symbol: str, tick: dict, max_size: int = 1000):
        if symbol not in self.data:
            self.data[symbol] = []

        self.data[symbol].append(tick)

        # keep buffer bounded
        if len(self.data[symbol]) > max_size:
            self.data[symbol] = self.data[symbol][-max_size:]

        self._save()

    # ----------------------------
    # GET TICKS
    # ----------------------------
    def get_ticks(self, symbol: str):
        return self.data.get(symbol, [])

    # ----------------------------
    # CLEAR BUFFER
    # ----------------------------
    def clear(self, symbol: str):
        self.data[symbol] = []
        self._save()