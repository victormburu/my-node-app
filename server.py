# server.py
import asyncio
import uvicorn
from fastapi import FastAPI

from ws_client import stream_ticks
from tick_engine import (
    TICKS,
    digit_counts,
    digit_probability,
    over_under,
    signal_engine,
    matches_differs,
)

app = FastAPI()


# =========================
# START BACKGROUND STREAM
# =========================
@app.on_event("startup")
async def startup():
    asyncio.create_task(stream_ticks())


# =========================
# WIX DASHBOARD API
# =========================
@app.get("/api/dashboard")
def dashboard():

    if len(TICKS) < 50:
        return {
            "ready": False,
            "message": "Collecting ticks..."
        }

    return {
        "ready": True,
        "tick_count": len(TICKS),

        "digit_probability": digit_probability(),

        "over_under_analysis": over_under(5),

        "matches_differs_analysis": matches_differs(7),

        "signal_engine": signal_engine(),
    }


# =========================
# HEALTH CHECK
# =========================
@app.get("/")
def home():
    return {"status": "Deriv Engine Running"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=3000, reload=True)