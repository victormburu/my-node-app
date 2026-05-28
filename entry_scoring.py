class EntryScoring:

    def score(self, signal, heatmap, volatility):

        if not signal or not signal.get("signal"):
            return {
                "score": 0,
                "quality": "LOW"
            }

        confidence = signal.get("confidence", 0)

        # heatmap strength (max probability digit)
        max_prob = 0
        if heatmap:
            flat = [v for d in heatmap.values()]
            if flat:
                max_prob = max(flat)

        # volatility weighting
        vol_weight = {
            "low": 1.2,
            "mid": 1.0,
            "high": 0.8
        }.get(volatility, 1.0)

        score = (confidence * 70 + max_prob * 30) * vol_weight

        if score >= 75:
            quality = "HIGH"
        elif score >= 45:
            quality = "MEDIUM"
        else:
            quality = "LOW"

        return {
            "score": round(score, 2),
            "quality": quality
        }