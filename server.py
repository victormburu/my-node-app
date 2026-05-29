from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import FileResponse
import asyncio
from tick_buffer import TickBuffer
from tick_engine import TickEngine
from ws_client import stream_deriv_ticks

app = FastAPI()
buffer = TickBuffer()
ENGINES = {
    "R_10": TickEngine(),
    "R_25": TickEngine(),
    "R_50": TickEngine(),
    "R_75": TickEngine(),
    "R_100": TickEngine()
}

stream_task = None


# ----------------------------
# Helper
# ----------------------------
def get_engine(symbol: str):
    return ENGINES.get(symbol)


# ----------------------------
# HEALTH
# ----------------------------
@app.get("/")
@app.head("/")
def home():
    return {"status": "ok", "message": "Tick engine live"}


# ----------------------------
# TICK INPUT
# ----------------------------
@app.post("/tick/{symbol}")
def receive_tick(symbol: str, tick: dict):
    engine = get_engine(symbol)
    if not engine:
        return {"error": "invalid symbol"}

    try:
        result = engine.process_tick(tick)
    except Exception as e:
        return {"error": f"processing failed: {str(e)}"}

    if not result:
        return {"error": "invalid tick"}

    return {
        "latest": result,
        "signal": result.get("signal")
    }


# ----------------------------
# ANALYTICS
# ----------------------------
@app.get("/analytics/{symbol}")
def analytics(symbol: str):
    engine = get_engine(symbol)
    if not engine:
        return {"error": "invalid symbol"}

    return engine.latest or {"status": "waiting"}


# ----------------------------
# SIGNAL
# ----------------------------
@app.get("/signal/{symbol}")
def signal(symbol: str):
    engine = get_engine(symbol)
    if not engine:
        return {"signal": False, "status": "no_data"}

    latest = engine.latest or {}
    return {"signal": latest.get("signal", False)}


# ----------------------------
# WEBSOCKET STREAM
# ----------------------------
@app.websocket("/stream/{symbol}")
async def stream(websocket: WebSocket, symbol: str):
    await websocket.accept()

    engine = get_engine(symbol)
    if not engine:
        await websocket.send_json({"error": "invalid symbol"})
        await websocket.close()
        return

    try:
        while True:
            analytics = engine.analytics()
            await websocket.send_json({
                "symbol": symbol,
                "analytics": analytics
            })
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        print(f"🔌 Client disconnected: {symbol}")


# ----------------------------
# STARTUP STREAM
# ----------------------------
@app.on_event("startup")
async def startup_event():
    print("🚀 Booting system...")

    async def runner():
        while True:
            try:
                await stream_deriv_ticks(ENGINES)
            except Exception as e:
                print("🔁 stream error:", e)
                await asyncio.sleep(3)

    asyncio.create_task(runner())

# ----------------------------
# DASHBOARD
# ----------------------------
@app.get("/dashboard")
def dashboard():
    return FileResponse("static/index.html")


# ----------------------------
# REPLAY
# ----------------------------
@app.get("/replay/load/{symbol}")
def load_replay(symbol: str):

    engine = ENGINES.get(symbol)
    if not engine:
        return {"error": "invalid symbol"}

    ticks = buffer.get_ticks(symbol)

    engine.set_replay(ticks)

    return {
        "status": "replay loaded from buffer",
        "count": len(ticks)
    }

# ----------------------------
# HEATMAP
# ----------------------------
@app.get("/heatmap/{symbol}")
def get_heatmap(symbol: str):
    engine = get_engine(symbol)
    if not engine:
        return {"error": "invalid symbol"}

    return engine.heatmap.build_heatmap()

@app.post("/tick/{symbol}")
def receive_tick(symbol: str, tick: dict):
    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    # 💾 store tick
    buffer.add_tick(symbol, tick)

    result = engine.process_tick(tick)

    if not result:
        return {"error": "invalid tick"}

    return {
        "latest": result,
        "signal": result.get("signal")
    }
# ----------------------------
# PERFORMANCE
# ----------------------------
@app.get("/performance/{symbol}")
def performance(symbol: str):
    engine = get_engine(symbol)
    if not engine:
        return {"error": "invalid symbol"}

    return engine.performance.report()