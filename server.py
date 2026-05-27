from fastapi import FastAPI, WebSocket
from tick_engine import TickEngine
import asyncio
from ws_client import stream_deriv_ticks
from fastapi.responses import FileResponse
import os

app = FastAPI()
streamer = None
ENGINES = {
    "R_10": TickEngine(),
    "R_25": TickEngine(),
    "R_50": TickEngine(),
    "R_75": TickEngine(),
    "R_100": TickEngine()
}

# ----------------------------
# STEP 6: BASIC HEALTH CHECK
# ----------------------------
@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"status": "ok", "message": "Tick engine live"}

# ----------------------------
# STEP 6: RECEIVE TICK DATA
# ----------------------------
@app.post("/tick")
def receive_tick(tick: dict):
    """
    Example payload:
    { "quote": 1234.56 }
    """

    result = ENGINES.process_tick(tick)

    if result is None:
        return {"error": "invalid tick"}

    return {
        "latest": result,
        "signal": ENGINES.generate_signal()
    }

# ----------------------------
# STEP 6: ANALYTICS DASHBOARD
# ----------------------------
@app.get("/analytics/{symbol}")
def analytics(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    return engine.analytics()
# ----------------------------
# STEP 6: SIGNAL ONLY
# ----------------------------
@app.get("/signal/{symbol}")
def signal(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    return engine.generate_signal()

@app.websocket("/stream")
async def stream(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = ENGINES.analytics()
        signal = ENGINES.generate_signal()

        await websocket.send_json({
            "analytics": data,
            "signal": signal
        })
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(stream_deriv_ticks(ENGINES))


@app.get("/dashboard")
def dashboard():
    return FileResponse("static/index.html")