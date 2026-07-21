import websocket
import json
import time

def chat(ws, message):
    ws.send(json.dumps({"message": message}))
    while True:
        raw = ws.recv()
        if not raw:
            continue
        result = json.loads(raw)
        if result.get("status") == "done":
            print(f"🤖 {result['response']}...")
            return
        elif result.get("status") == "thinking":
            print("🤔 thinking...")

print("=" * 60)
print("SESSION 1 — First connection")
print("=" * 60)
ws1 = websocket.WebSocket()
ws1.connect("ws://localhost:8000/ws?user_id=test-user-123")

# Get the thread_id from server logs — we'll use a fixed one for testing
# For now just chat and then reconnect
chat(ws1, "What is the current EUR/USD price?")
chat(ws1, "What is the GBP/USD sentiment?")

print("\n⚡ Disconnecting...\n")
ws1.close()
time.sleep(2)

print("=" * 60)
print("SESSION 2 — Reconnecting (NEW connection, no history in memory)")
print("=" * 60)
ws2 = websocket.WebSocket()
ws2.connect("ws://localhost:8000/ws?user_id=test-user-123")

# This question refers to previous session context
# Without checkpointing it would fail
# With checkpointing it should remember EUR/USD and GBP/USD
chat(ws2, "Based on what we just discussed, which pair looks better?")

ws2.close()
print("\n✅ Checkpoint test complete!")
print("If the last response referenced EUR/USD and GBP/USD — checkpointing works!")
print("If it said it has no context — checkpointing is not working yet.")