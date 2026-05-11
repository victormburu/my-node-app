from fastapi import FastAPI
import asyncio

try:
    import uvicorn
except ImportError:
    uvicorn = None

from tick_engine import (
    stream_ticks,
    last_1000_ticks,
    build_market_analytics,
    over_under_analysis,
    matches_differs_analysis,
    generate_signal
)

app = FastAPI()

# =========================================
# START BACKGROUND STREAM
# =========================================

@app.on_event("startup")
async def startup_event():

    asyncio.create_task(stream_ticks())

# =========================================
# ROOT
# =========================================

@app.get("/")
def root():

    return {
        "message": "Deriv Analytics Engine Running"
    }

# =========================================
# DASHBOARD API
# =========================================

@app.get("/api/dashboard")
def dashboard():

    market = build_market_analytics()

    over_under = over_under_analysis()

    matches_differs = matches_differs_analysis(
        target_digit=7
    )

    signal = generate_signal()

    return {

        "ready": True,

        "tick_count": len(last_1000_ticks),

        # =================================
        # MARKET ANALYTICS
        # =================================
        "market_statistics": market["market_statistics"],

        "live_analytics": market["live_analytics"],

        # =================================
        # OVER / UNDER
        # =================================
        "over_under_analysis": over_under,

        # =================================
        # MATCH / DIFFER
        # =================================
        "matches_differs_analysis": matches_differs,

        # =================================
        # SIGNAL ENGINE
        # =================================
        "signal_engine": signal
    }

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=3000,
        reload=True
    )