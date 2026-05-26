from tick_engine import TickEngine
engine = TickEngine()

def on_tick(message):
    tick = message["tick"]

    engine.process_tick(tick)

    # STEP 3 OUTPUT
    analytics = engine.analytics()
    signal = engine.generate_signal()
    
    output = {
        "analytics": analytics,
        "signal": signal
    }

    print(output)