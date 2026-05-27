class SignalEngine:
    def __init__(self, threshold=0.60):
        self.threshold = threshold

    def evaluate(self, prob_map):
        if not prob_map:
            return None

        best_digit = max(prob_map, key=prob_map.get)
        confidence = prob_map[best_digit]

        if confidence >= self.threshold:
            return {
                "signal": True,
                "digit": best_digit,
                "confidence": confidence
            }

        return {
            "signal": False,
            "digit": best_digit,
            "confidence": confidence
        }