from collections import defaultdict, Counter


class TickEngine:
    def __init__(self, max_history=1000, window=50):
        self.history = []
        self.max_history = max_history
        self.window = window

        # STEP 4: transition matrix
        self.transitions = defaultdict(list)

    # ---------------------------
    # STEP 2: tick processing
    # ---------------------------
    def process_tick(self, tick):
        price = tick.get("quote")

        if price is None:
            return None

        digit = int(str(price)[-1])
        
        # STEP 4: capture transitions
        if len(self.history) > 0:
            prev = self.history[-1]
            self.transitions[prev].append(digit)

        self.history.append(digit)

        if len(self.history) > self.max_history:
            self.history.pop(0)

        return {
            "price": price,
            "digit": digit
        }
        
    # ---------------------------
    # STEP 3: CORE INTELLIGENCE
    # ---------------------------

    def get_window(self):
        """Use last N digits for analysis"""
        return self.history[-self.window:]

    def digit_frequencies(self):
        """Count occurrence of each digit"""
        window = self.get_window()
        counts = Counter(window)

        return {str(i): counts.get(i, 0) for i in range(10)}

    def digit_probabilities(self):
        """Convert frequencies into probabilities"""
        window = self.get_window()
        total = len(window)

        if total == 0:
            return {str(i): 0 for i in range(10)}

        counts = Counter(window)

        return {
            str(i): round(counts.get(i, 0) / total, 4)
            for i in range(10)
        }
        
    def bias_signal(self):
        """
        Simple market bias idea:
        - low digits (0–4)
        - high digits (5–9)
        """

        window = self.get_window()
        if not window:
            return {"bias": "neutral"}

        low = sum(1 for d in window if d <= 4)
        high = sum(1 for d in window if d >= 5)

        total = len(window)

        low_pct = low / total
        high_pct = high / total

        if high_pct > 0.55:
            bias = "high-digit dominance"
        elif low_pct > 0.55:
            bias = "low-digit dominance"
        else:
            bias = "balanced"

        return {
            "bias": bias,
            "low_pct": round(low_pct, 3),
            "high_pct": round(high_pct, 3)
        }
        
    def detect_streak(self, min_length=3):
        """
        Detect repeating digit streaks like:
        7,7,7 or 3,3,3,3
        """

        if len(self.history) < min_length:
            return None

        streak_digit = self.history[-1]
        streak_len = 1

        for i in range(len(self.history) - 2, -1, -1):
            if self.history[i] == streak_digit:
                streak_len += 1
            else:
                break

        if streak_len >= min_length:
            return {
                "digit": streak_digit,
                "length": streak_len,
                "type": "active_streak"
            }

        return {
            "type": "no_streak"
        }
        
    def transition_probabilities(self):
        """
        Builds a Markov-style probability map:
        digit -> next digit distribution
        """

        model = {}

        for digit in range(10):
            next_digits = self.transitions.get(digit, [])

            if not next_digits:
                model[str(digit)] = {str(i): 0 for i in range(10)}
                continue

            counts = Counter(next_digits)
            total = len(next_digits)

            model[str(digit)] = {
                str(i): round(counts.get(i, 0) / total, 4)
                for i in range(10)
            }

        return model
    
    def predict_next_digit(self):
        """
        Predict next digit based on:
        - last digit transitions
        - fallback to global probabilities
        """

        if len(self.history) == 0:
            return None

        last_digit = self.history[-1]
        transitions = self.transitions.get(last_digit, [])

        # fallback: global behavior
        if not transitions:
            freq = Counter(self.get_window())
            total = sum(freq.values())

            return {
                "method": "global_fallback",
                "prediction": max(freq, key=freq.get),
                "confidence": round(freq[max(freq, key=freq.get)] / total, 3) if total else 0
            }

        counts = Counter(transitions)
        total = len(transitions)

        predicted_digit = max(counts, key=counts.get)

        return {
            "method": "markov_transition",
            "based_on": last_digit,
            "prediction": predicted_digit,
            "confidence": round(counts[predicted_digit] / total, 3)
        }

    
    def analytics(self):
        """Single endpoint for dashboard/API"""
        return {
            "window_size": len(self.get_window()),
            "frequencies": self.digit_frequencies(),
            "probabilities": self.digit_probabilities(),
            "bias": self.bias_signal(),
            
            # STEP 4 additions
            "transition_model": self.transition_probabilities(),
            "prediction": self.predict_next_digit(),
            "streak": self.detect_streak()
        }
        
    
    def generate_signal(self):
        """
        Converts analytics into trade decision logic.
        This is your Over/Under entry engine.
        """

        analytics = self.analytics()

        probs = analytics["probabilities"]
        prediction = analytics["prediction"]
        bias = analytics["bias"]

        # Convert probabilities into usable scores
        high_digits = sum(probs[str(i)] for i in range(5, 10))
        low_digits = sum(probs[str(i)] for i in range(0, 5))

        confidence = 0
        signal = "NO_TRADE"

        # -----------------------------
        # RULE 1: strong bias filter
        # -----------------------------
        if high_digits > 0.58:
            signal = "OVER"
            confidence = high_digits

        elif low_digits > 0.58:
            signal = "UNDER"
            confidence = low_digits

        # -----------------------------
        # RULE 2: prediction alignment
        # -----------------------------
        predicted_digit = prediction.get("prediction") if prediction else None

        if predicted_digit is not None:
            if predicted_digit >= 5 and signal == "OVER":
                confidence += 0.05

            if predicted_digit < 5 and signal == "UNDER":
                confidence += 0.05

        # -----------------------------
        # RULE 3: streak suppression
        # -----------------------------
        streak = analytics.get("streak", {})

        if streak.get("type") == "active_streak":
            # avoid chasing long streaks (common trap in synthetic indices)
            if streak.get("length", 0) >= 4:
                signal = "NO_TRADE"
                confidence = 0

        # -----------------------------
        # RULE 4: final threshold filter
        # -----------------------------
        if confidence < 0.62:
            signal = "NO_TRADE"

        return {
            "signal": signal,
            "confidence": round(confidence, 3),
            "bias": bias,
            "prediction": prediction
        }

    
    