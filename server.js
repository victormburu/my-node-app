require("dotenv").config();
const express = require("express");
const WebSocket = require("ws");

const app = express();
const PORT = process.env.PORT || 3000;

// ==========================
// CONFIG
// ==========================
const DERIV_WS =
    "wss://api.derivws.com/trading/v1/options/ws/demo?otp=" + process.env.DERIV_OTP;

// Track latest prices
const marketData = new Map(); // { symbol -> { oldPrice, newPrice } }

// Final computed stats cache
let analyticsCache = {
    market_statistics: [],
    live_analytics: [],
};

// ==========================
// HELPERS
// ==========================
function calculateChange(oldPrice, newPrice) {
    if (!oldPrice) return 0;
    return ((newPrice - oldPrice) / oldPrice) * 100;
}

// pick top movers
function buildAnalytics() {
    const stats = [];

    for (const [symbol, data] of marketData.entries()) {
        const change = calculateChange(data.oldPrice, data.newPrice);

        stats.push({
            index_name: symbol,
            change_percent: parseFloat(change.toFixed(2)),
        });
    }

    // sort by absolute movement
    stats.sort((a, b) =>
        Math.abs(b.change_percent) - Math.abs(a.change_percent)
    );

    const top10 = stats.slice(0, 10).map((item, i) => ({
        rank: i + 1,
        ...item,
    }));

    const liveAnalytics = stats.slice(0, 4).map((item) => ({
        name: `Live: ${item.index_name}`,
        change_percent: item.change_percent,
    }));

    analyticsCache = {
        market_statistics: top10,
        live_analytics: liveAnalytics,
    };
}

// ==========================
// DERIV WEBSOCKET
// ==========================
let ws;

function connect() {
    ws = new WebSocket(DERIV_WS);

    ws.on("open", () => {
        console.log("Connected to Deriv WebSocket");

        // Subscribe to synthetic indices (example symbols)
        const symbols = [
            "R_10",
            "R_25",
            "R_50",
            "R_75",
            "R_100",
        ];

        symbols.forEach((symbol) => {
            ws.send(
                JSON.stringify({
                    ticks: symbol,
                    subscribe: 1,
                })
            );
        });
    });

    ws.on("message", (msg) => {
        try {
            const data = JSON.parse(msg);

            if (data.tick) {
                const symbol = data.tick.symbol;
                const price = parseFloat(data.tick.quote);

                if (!marketData.has(symbol)) {
                    marketData.set(symbol, {
                        oldPrice: price,
                        newPrice: price,
                    });
                } else {
                    const existing = marketData.get(symbol);

                    marketData.set(symbol, {
                        oldPrice: existing.newPrice,
                        newPrice: price,
                    });
                }

                buildAnalytics();
            }
        } catch (err) {
            console.error("Parse error:", err.message);
        }
    });

    ws.on("close", () => {
        console.log("WebSocket closed. Reconnecting...");
        setTimeout(connect, 3000);
    });

    ws.on("error", (err) => {
        console.error("WebSocket error:", err.message);
        ws.close();
    });
}

// start connection
connect();

// ==========================
// API ENDPOINT
// ==========================
app.get("/api/trading-stats", (req, res) => {
    res.json(analyticsCache);
});

// health check
app.get("/", (req, res) => {
    res.send("Deriv Analytics Service Running");
});

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});