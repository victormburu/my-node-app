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

                # -----------------------------------
                # SUBSCRIBE TO ALL MARKETS
                # -----------------------------------
                for symbol in MARKETS:

                    payload = {
                        "ticks": symbol,
                        "subscribe": 1
                    }

                    await websocket.send(json.dumps(payload))

                    print(f"Subscribed -> {symbol}")

                print("Deriv multi-market stream started")

                # -----------------------------------
                # RECEIVE LOOP
                # -----------------------------------
                while True:

                    response = await websocket.recv()

                    data = json.loads(response)

                    # DEBUG
                    print("RAW:", data)

                    # -----------------------------------
                    # ENSURE TICK MESSAGE
                    # -----------------------------------
                    if data.get("msg_type") != "tick":
                        continue

                    tick = data.get("tick")

                    if not tick:
                        continue

                    symbol = tick.get("symbol")
                    quote = tick.get("quote")

                    if symbol is None or quote is None:
                        continue

                    print(f"TICK -> {symbol} : {quote}")

                    # -----------------------------------
                    # ENGINE PROCESSING
                    # -----------------------------------
                    engine = engines.get(symbol)

                    if not engine:
                        print(f"No engine found for {symbol}")
                        continue

                    try:

                        output = engine.process({
                            "quote": float(quote),
                            "symbol": symbol
                        })

                        print("Processed:", output)

                    except Exception as e:
                        print("Tick processing error:", str(e))

        except Exception as e:

            print("WebSocket Error:", str(e))

            await asyncio.sleep(5)