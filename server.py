from fastapi import FastAPI, WebSocket
from tick_engine import TickEngine
import asyncio
from ws_client import DerivStream
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()
streamer = None
engine = TickEngine()

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

    result = engine.process_tick(tick)

    if result is None:
        return {"error": "invalid tick"}

    return {
        "latest": result,
        "signal": engine.generate_signal()
    }

# ----------------------------
# STEP 6: ANALYTICS DASHBOARD
# ----------------------------
@app.get("/analytics")
def analytics():
    return engine.analytics()

# ----------------------------
# STEP 6: SIGNAL ONLY
# ----------------------------
@app.get("/signal")
def signal():
    return engine.generate_signal()

@app.websocket("/stream")
async def stream(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = engine.analytics()
        signal = engine.generate_signal()

        await websocket.send_json({
            "analytics": data,
            "signal": signal
        })
        
@app.on_event("startup")
async def startup():
    global streamer

    streamer = DerivStream(engine, symbol="R_100")

    asyncio.create_task(streamer.connect())

    print("Deriv live stream started")
    

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/dashboard")
def dashboard():
    return FileResponse("static/index.html")