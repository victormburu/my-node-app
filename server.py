from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import asyncio

from tick_engine import TickEngine
from ws_client import stream_deriv_ticks

app = FastAPI()

streamer = None

# ----------------------------
# ENGINE REGISTRY
# ----------------------------
ENGINES = {
    "R_10": TickEngine(),
    "R_25": TickEngine(),
    "R_50": TickEngine(),
    "R_75": TickEngine(),
    "R_100": TickEngine()
}

# ----------------------------
# HEALTH CHECK
# ----------------------------
@app.api_route("/", methods=["GET", "HEAD"])
def home():
    return {"status": "ok", "message": "Tick engine live"}

@app.post("/tick/{symbol}")
def receive_tick(symbol: str, tick: dict):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    result = engine.process_tick(tick)

    if result is None:
        return {"error": "invalid tick"}

    return {
        "latest": result,
        "signal": result.get("signal")
    }
    
@app.get("/analytics/{symbol}")
def analytics(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    return engine.analytics()

@app.get("/signal/{symbol}")
def signal(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    return engine.generate_signal()

@app.websocket("/stream/{symbol}")
async def stream(websocket: WebSocket, symbol: str):

    await websocket.accept()

    engine = ENGINES.get(symbol)

    if not engine:
        await websocket.send_json({"error": "invalid symbol"})
        return

    while True:
        data = engine.analytics()
        signal = engine.generate_signal()

        await websocket.send_json({
            "symbol": symbol,
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

@app.post("/replay/load/{symbol}")
def load_replay(symbol: str, ticks: list):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    engine.mode_manager.set_replay(ticks)

    return {"status": "replay loaded"}

@app.get("/replay/step/{symbol}")
def replay_step(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    tick = engine.mode_manager.next_tick()

    if not tick:
        return {"done": True}

    output = engine.process_tick(tick)

    return {
        "tick": tick,
        "output": output,
        "mode": "replay"
    }
    
@app.get("/heatmap/{symbol}")
def get_heatmap(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    return engine.heatmap.build_heatmap()

@app.get("/performance/{symbol}")
def performance(symbol: str):

    engine = ENGINES.get(symbol)

    if not engine:
        return {"error": "invalid symbol"}

    return engine.performance.report()