from collections import deque, defaultdict

TICKS = deque(maxlen=1000)

digit_counts = defaultdict(int)

# =========================
# ADD TICK
# =========================
def add_tick(price: float):
    last_digit = int(str(price)[-1])

    TICKS.append(price)
    digit_counts[last_digit] += 1


# =========================
# DIGIT PROBABILITY MODEL
# =========================
def digit_probability():
    total = sum(digit_counts.values()) or 1

    return {
        str(d): round((c / total) * 100, 2)
        for d, c in digit_counts.items()
    }


# =========================
# MATCHES / DIFFERS ENGINE
# =========================
def matches_differs(target_digit: int):
    total = sum(digit_counts.values()) or 1

    match = digit_counts.get(target_digit, 0)

    match_pct = (match / total) * 100
    differ_pct = 100 - match_pct

    return {
        "type": "MATCH_DIFFERS",
        "target_digit": target_digit,
        "match_percent": round(match_pct, 2),
        "differ_percent": round(differ_pct, 2),
        "bias": "MATCH" if match_pct > 12 else "DIFFER"
    }


# =========================
# OVER / UNDER ENGINE
# =========================
def over_under(barrier: int = 5):
    total = sum(digit_counts.values()) or 1

    over = sum(c for d, c in digit_counts.items() if int(d) > barrier)
    under = total - over

    return {
        "type": "OVER_UNDER",
        "barrier": barrier,
        "over_percent": round((over / total) * 100, 2),
        "under_percent": round((under / total) * 100, 2),
        "bias": "OVER" if over > under else "UNDER"
    }


# =========================
# SIGNAL ENGINE (BLUEPRINT STYLE)
# =========================
def signal_engine():
    probs = digit_probability()

    if not probs:
        return {"signal": "NO DATA", "score": 0}

    hot = max(probs, key=probs.get)
    cold = min(probs, key=probs.get)

    return {
        "hot_digit": int(hot),
        "cold_digit": int(cold),
        "signal": f"DIGIT {hot} HOT / DIGIT {cold} COLD",
        "score": int(float(probs[hot]) - float(probs[cold]))
    }