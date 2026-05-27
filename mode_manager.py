class ModeManager:
    def __init__(self):
        self.mode = "live"
        self.replay_data = []
        self.index = 0

    def set_live(self):
        self.mode = "live"

    def set_replay(self, data):
        self.mode = "replay"
        self.replay_data = data
        self.index = 0

    def next_tick(self):
        if self.mode == "replay":
            if self.index >= len(self.replay_data):
                return None
            tick = self.replay_data[self.index]
            self.index += 1
            return tick