import json
from collections import deque, Counter

try:
    import websockets
except ImportError:
    websockets = None

# =========================================
# DERIV WS
# =========================================

DERIV_WS = "wss://api.derivws.com/trading/v1/options/ws/public"

# =========================================
# STORAGE
# =========================================

last_1000_ticks = deque(maxlen=1000)

market_data = {}

# =========================================
# PRICE CHANGE ANALYSIS
# =========================================

def calculate_change(old, new):
    if not old:
        return 0
    return ((new - old) / old) * 100


def build_market_analytics():

    stats = []

    for symbol, data in market_data.items():

        change = calculate_change(data["old"], data["new"])

        stats.append({
            "index_name": symbol,
            "change_percent": round(change, 2)
        })

    # sort strongest movers
    stats.sort(
        key=lambda x: abs(x["change_percent"]),
        reverse=True
    )

    return {
        "market_statistics": stats[:10],
        "live_analytics": stats[:4]
    }

# =========================================
# DIGIT EXTRACTION
# =========================================

def extract_digits():

    digits = []

    for price in last_1000_ticks:
        try:
            digit = int(str(price)[-1])
            digits.append(digit)
        except:
            pass

    return digits

# =========================================
# OVER / UNDER ANALYSIS
# =========================================

def over_under_analysis():

    digits = extract_digits()

    total = len(digits)

    if total == 0:
        return {}

    over = sum(1 for d in digits if d >= 5)
    under = sum(1 for d in digits if d <= 4)

    return {
        "type": "OVER_UNDER",
        "total_ticks": total,
        "over_count": over,
        "under_count": under,
        "over_percent": round((over / total) * 100, 2),
        "under_percent": round((under / total) * 100, 2),
        "bias": "OVER" if over > under else "UNDER"
    }

# =========================================
# MATCHES / DIFFERS ANALYSIS
# =========================================

def matches_differs_analysis(target_digit=7):

    digits = extract_digits()

    total = len(digits)

    if total == 0:
        return {}

    counts = Counter(digits)

    match_count = counts.get(target_digit, 0)

    differ_count = total - match_count

    return {
        "type": "MATCH_DIFFERS",
        "target_digit": target_digit,
        "match_count": match_count,
        "differ_count": differ_count,
        "match_percent": round((match_count / total) * 100, 2),
        "differ_percent": round((differ_count / total) * 100, 2),
        "bias": "MATCH" if match_count > differ_count else "DIFFER"
    }

# =========================================
# SIGNAL ENGINE
# =========================================

def generate_signal():

    ou = over_under_analysis()
    md = matches_differs_analysis()

    signal_score = 0

    # OVER UNDER
    if ou.get("over_percent", 0) > 55:
        signal_score += 1

    if ou.get("under_percent", 0) > 55:
        signal_score -= 1

    # MATCH DIFFER
    if md.get("match_percent", 0) > 12:
        signal_score += 1

    if md.get("differ_percent", 0) > 88:
        signal_score -= 1

    # FINAL SIGNAL
    if signal_score >= 2:
        signal = "STRONG OVER BIAS"

    elif signal_score == 1:
        signal = "WEAK OVER BIAS"

    elif signal_score == -1:
        signal = "WEAK UNDER BIAS"

    else:
        signal = "NEUTRAL"

    return {
        "signal": signal,
        "score": signal_score
    }

# =========================================
# STREAM TICKS
# =========================================

async def stream_ticks():

    async with websockets.connect(DERIV_WS) as ws:

        symbols = [
            "R_10",
            "R_25",
            "R_50",
            "R_75",
            "R_100"
        ]

        # subscribe
        for s in symbols:
            await ws.send(json.dumps({
                "ticks": s,
                "subscribe": 1
            }))

        while True:

            msg = await ws.recv()

            data = json.loads(msg)

            if "tick" in data:

                symbol = data["tick"]["symbol"]

                price = float(data["tick"]["quote"])

                # store rolling prices
                last_1000_ticks.append(price)

                # market analytics
                if symbol not in market_data:

                    market_data[symbol] = {
                        "old": price,
                        "new": price
                    }

                else:

                    market_data[symbol]["old"] = market_data[symbol]["new"]

                    market_data[symbol]["new"] = price