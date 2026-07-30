import websocket
import json
import time

def test(message, ws):
    print(f"\n{'='*60}")
    print(f"📤 User: {message}")
    print('='*60)
    ws.send(json.dumps({"message": message}))

    tool_calls = 0
    streaming_started = False
    full_response = ""

    while True:
        try:
            raw = ws.recv()
            if not raw:
                continue
            result = json.loads(raw)
            msg_type = result.get("type")

            if msg_type == "thinking":
                print("🤔 Agent thinking...")

            elif msg_type == "tool_call":
                print(f"🔧 Tool called: {result['tool']}")

            elif msg_type == "token":
                token = result.get("token", "")
                if not streaming_started:
                    print("🤖 Response (streaming):")
                    streaming_started = True
                print(token, end="", flush=True)
                full_response += token

            elif msg_type == "done":
                tool_calls = result.get("tool_calls_made", 0)
                is_fast_path = result.get("is_fast_path", False)
                if not streaming_started:
                    # Fast path — no streaming, just print response
                    print(f"🤖 Response:\n{result.get('response', '')}")
                else:
                    # Streaming finished — print newline
                    print()
                print(f"\n⚡ Fast path: {is_fast_path}")
                print(f"🔧 Total tool calls: {tool_calls}")
                break

            elif msg_type == "error":
                print(f"❌ Error: {result.get('response')}")
                break

        except json.JSONDecodeError:
            continue

    time.sleep(1)


# Single persistent connection
ws = websocket.WebSocket()
ws.connect("ws://localhost:8000/ws?user_id=test-user-123")
print("✅ Connected to Forex Agent\n")

test("Hello!", ws)
test("What is the price of Bitcoin?", ws)
test("What is the current EUR/INR price?", ws)
test("Show me the recent price history for GBP/USD", ws)
test("What is the market sentiment for USD/JPY?", ws)
test("Give me a full analysis of AUD/USD including price, sentiment and trading strategy", ws)
test("Give me a quick summary of USD/CHF", ws)
test("Based on everything we discussed, which pair looks most promising?", ws)

ws.close()
print("\n✅ All tests complete!")