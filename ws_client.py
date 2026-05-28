import asyncio
import json
import websockets

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

# Supported markets
MARKETS = {
    "R_10": "R_10",
    "R_25": "R_25",
    "R_50": "R_50",
    "R_75": "R_75",
    "R_100": "R_100"
}
async def stream_deriv_ticks(engines):
    while True:
        try:
            async with websockets.connect(DERIV_WS) as websocket:

                # subscribe all markets
                for symbol in MARKETS.values():
                    await websocket.send(json.dumps({
                        "ticks": symbol,
                        "subscribe": 1
                    }))

                print("Deriv multi-market stream started")
                
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)

                    if "tick" in data:
                        tick = data["tick"]

                        symbol = tick.get("symbol")
                        quote = tick.get("quote")

                        if symbol in engines:
                            engines[symbol].process({
                                "quote": quote
                            })

        except Exception as e:
            print("WebSocket Error:", e)
            await asyncio.sleep(5)