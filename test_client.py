import websocket
import json
import time
import httpx


def test(message, ws):
    print(f"\n{'='*60}")
    print(f"📤 User: {message}")
    print('='*60)
    ws.send(json.dumps({"message": message}))

    while True:
        try:
            raw = ws.recv()
            if not raw:
                continue
            result = json.loads(raw)
            if result.get("status") == "thinking":
                print("🤔 Agent thinking...")
            elif result.get("status") == "done":
                print(f"⚡ Fast path: {result['is_fast_path']}")
                print(f"🔧 Tool calls made: {result['tool_calls_made']}")
                print(f"\n🤖 Response:\n{result['response']}")
                break
            else:
                print(f"📨 Other: {result}")
        except json.JSONDecodeError:
            continue
    time.sleep(1)

# Single persistent connection
ws = websocket.WebSocket()
ws.connect("ws://localhost:8000/ws")
print("✅ Connected to Forex Agent\n")

# Test 1 — Greeting (fast path)
test("Hello!", ws)

# Test 2 — Out of scope (fast path)
test("What is the price of Bitcoin?", ws)

# Test 3 — Live price fetch
test("What is the current EUR/USD price?", ws)

# Test 4 — Price history + trend
test("Show me the recent price history for GBP/USD", ws)

# Test 5 — Market sentiment
#test("What is the market sentiment for USD/JPY?", ws)

# Test 6 — Full analysis with multiple tools
#test("Give me a full analysis of AUD/USD including price, sentiment and trading strategy", ws)

# Test 7 — Brief response style
#test("Give me a quick summary of USD/CHF", ws)

# Test 8 — Conversation memory
#test("Based on everything we discussed, which pair looks most promising?", ws)

ws.close()
print("\n✅ All tests complete!")