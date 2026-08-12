import re

GREETINGS = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
OUT_OF_SCOPE = ["stock", "crypto", "bitcoin", "ethereum", "nft", "real estate", "gold", "silver"]

def is_greeting(message: str) -> bool:
    message = message.lower().strip()
    return (
        any(re.search(rf'\b{re.escape(g)}\b', message) for g in GREETINGS)
        and len(message.split()) <= 4
    )

def is_out_of_scope(message: str) -> bool:
    message = message.lower().strip()
    return any(re.search(rf'\b{re.escape(o)}\b', message) for o in OUT_OF_SCOPE)