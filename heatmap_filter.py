class HeatmapFilter:
    def __init__(self,
                 min_confidence=0.60,
                 min_occurrences=5):

        self.min_confidence = min_confidence
        self.min_occurrences = min_occurrences

    def validate(self,
                 heatmap_data,
                 volatility,
                 pattern):

        vol_data = heatmap_data.get(volatility, {})

        if pattern not in vol_data:
            return None

        digit_probs = vol_data[pattern]

        best_digit = None
        best_prob = 0

        for digit, prob in digit_probs.items():

            if prob > best_prob:
                best_digit = digit
                best_prob = prob

        if best_prob >= self.min_confidence:
            return {
                "valid": True,
                "digit": best_digit,
                "confidence": best_prob
            }

        return {
            "valid": False,
            "digit": best_digit,
            "confidence": best_prob
        }