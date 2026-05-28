import asyncio
import json
import websockets

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

MARKETS = [
    "R_10",
    "R_25",
    "R_50",
    "R_75",
    "R_100"
]


async def stream_deriv_ticks(engines):

    while True:

        try:

            print("Connecting to Deriv WS...")

            async with websockets.connect(DERIV_WS) as websocket:

                print("Deriv multi-market stream started")

                # subscribe
                for symbol in MARKETS:

                    payload = {
                        "ticks": symbol,
                        "subscribe": 1
                    }

                    await websocket.send(json.dumps(payload))

                    print(f"Subscribed -> {symbol}")

                # receive loop
                while True:

                    response = await websocket.recv()

                    data = json.loads(response)

                    # DEBUG
                    print("RAW:", data)

                    if "tick" not in data:
                        continue

                    tick = data["tick"]

                    symbol = tick.get("symbol")
                    quote = tick.get("quote")

                    if not symbol:
                        continue

                    if quote is None:
                        continue

                    print(f"TICK -> {symbol} : {quote}")

                    if symbol in engines:

                        try:

                            result = engines[symbol].process({
                                "quote": float(quote),
                                "symbol": symbol
                            })

                            print("ENGINE OUTPUT:", result)

                        except Exception as e:

                            print("Tick processing error:", e)

        except Exception as e:

            print("WebSocket Error:", e)

            await asyncio.sleep(5)