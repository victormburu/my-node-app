import asyncio
import json
import websockets

DERIV_URL = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

class DerivStream:
    def __init__(self, engine, symbol="R_100"):
        self.engine = engine
        self.symbol = symbol

    async def connect(self):
        while True:
            try:
                async with websockets.connect(DERIV_URL) as ws:

                    # subscribe to ticks
                    await ws.send(json.dumps({
                        "ticks": self.symbol,
                        "subscribe": 1
                    }))

                    print("Connected to Deriv stream...")

                    while True:
                        msg = await ws.recv()
                        data = json.loads(msg)

                        if "tick" in data:
                            self.engine.process_tick(data["tick"])

            except Exception as e:
                print("WebSocket error:", e)
                print("Reconnecting in 3 seconds...")
                await asyncio.sleep(3)