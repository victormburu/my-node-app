import asyncio
import json
import websockets

DERIV_WS = "wss://ws.derivws.com/websockets/v3?app_id=1089"

MARKETS = ["R_10", "R_25", "R_50", "R_75", "R_100"]


async def stream_deriv_ticks(engines):

    while True:
        try:
            async with websockets.connect(DERIV_WS) as websocket:

                print("Deriv multi-market stream started")
                print("Connecting to Deriv WS...")

                # =========================
                # SUBSCRIBE MARKETS SAFELY
                # =========================
                for i, symbol in enumerate(MARKETS):

                    await websocket.send(json.dumps({
                        "ticks": symbol,
                        "subscribe": 1,
                        "req_id": i + 1
                    }))

                # =========================
                # MAIN LISTENER LOOP
                # =========================
                while True:
                    response = await websocket.recv()

                    try:
                        data = json.loads(response)
                    except:
                        continue

                    # only process tick messages
                    if "tick" not in data:
                        continue

                    tick = data["tick"]

                    symbol = tick.get("symbol")
                    quote = tick.get("quote")

                    # safety guard
                    if symbol not in engines:
                        continue

                    if quote is None:
                        continue

                    try:
                        price = float(quote)

                        engines[symbol].process({
                            "quote": price,
                            "symbol": symbol
                        })

                    except Exception as e:
                        print("Tick processing error:", e)
                        continue

        except Exception as e:
            print("❌ WebSocket crash:", repr(e))
            await asyncio.sleep(5)