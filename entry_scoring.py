class EntryScoring:

    def score(self, signal, heatmap, volatility):

        if not signal or not signal.get("signal"):
            return {
                "score": 0,
                "quality": "LOW"
            }

        confidence = signal.get("confidence", 0)

        # -------------------------
        # FIXED HEATMAP FLATTENING
        # -------------------------
        max_prob = 0
        if heatmap:
            flat = [
                prob
                for pattern in heatmap.values()
                for prob in pattern.values()
            ]
            if flat:
                max_prob = max(flat)

        # -------------------------
        # VOLATILITY WEIGHTING
        # -------------------------
        vol_weight = {
            "low": 1.2,
            "mid": 1.0,
            "high": 0.8
        }.get(volatility, 1.0)

        # -------------------------
        # STABLE SCORE (0–100)
        # -------------------------
        score = (confidence * 0.7 + max_prob * 0.3) * 100 * vol_weight

        # -------------------------
        # QUALITY LABEL
        # -------------------------
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