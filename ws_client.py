# ws_client.py
import asyncio
import json
try:
    import websockets
except ImportError as exc:
    raise ImportError(
        "Missing dependency 'websockets'. Install it with: pip install websockets"
    ) from exc

try:
    from tick_engine import add_tick
except ImportError:
    from .tick_engine import add_tick

DERIV_WS = "wss://api.derivws.com/trading/v1/options/ws/public"


SYMBOLS = ["R_10", "R_25", "R_50", "R_75", "R_100"]


async def stream_ticks():
    while True:
        try:
            async with websockets.connect(DERIV_WS) as ws:

                for s in SYMBOLS:
                    await ws.send(json.dumps({
                        "ticks": s,
                        "subscribe": 1
                    }))

                print("Connected to Deriv WebSocket")

                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)

                    if "tick" in data:
                        price = float(data["tick"]["quote"])
                        add_tick(price)

        except Exception as e:
            print("WS Error:", e)
            print("Reconnecting in 3s...")
            await asyncio.sleep(3)