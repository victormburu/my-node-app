import asyncio
import json
import websockets

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

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

                print("Deriv multi-market stream started")

                # STEP 1: subscribe correctly
                for symbol in MARKETS.values():

                    await websocket.send(json.dumps({
                        "ticks": symbol,
                        "subscribe": 1
                    }))

                # STEP 2: listen loop
                while True:
                    response = await websocket.recv()
                    data = json.loads(response)

                    # safety check
                    if "tick" not in data:
                        continue

                    tick = data["tick"]

                    symbol = tick.get("symbol")
                    quote = tick.get("quote")

                    if not symbol or quote is None:
                        continue

                    if symbol in engines:

                        engines[symbol].process({
                            "quote": float(quote),
                            "symbol": symbol
                        })

        except Exception as e:
            print("WebSocket Error:", e)
            await asyncio.sleep(5)