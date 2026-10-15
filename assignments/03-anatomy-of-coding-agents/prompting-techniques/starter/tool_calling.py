"""Tool calling — order lookup.

Task: the model must decide to call the `get_order_status` tool with the order id it
finds in the user's message, then use the returned status in a short reply.

Fill in YOUR_SYSTEM_PROMPT and the tool schema TODO.
Run:  python tool_calling.py
"""
from ollama import chat

MODEL = "llama3.1:8b"

FAKE_DB = {
    "4412": "shipped, arriving Friday",
    "9001": "processing",
}


def get_order_status(order_id: str) -> str:
    return FAKE_DB.get(order_id, "not found")


# The description makes lookup mandatory for order-status questions and prevents guessed statuses.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Look up the current status for a specific order. Use this whenever a customer asks about an order's status; do not guess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID exactly as provided by the customer."},
                },
                "required": ["order_id"],
            },
        },
    }
]

# Tell the model to ground its answer in the function result, not its prior knowledge.
YOUR_SYSTEM_PROMPT = """When a customer asks for an order's status, extract the order ID and call get_order_status before replying. Use the returned status in a brief, helpful response. Never invent or assume an order status. If the customer did not provide an order ID, ask them for it instead of calling the tool."""


def run() -> bool:
    message = "Hi, can you check on order 4412 for me?"
    resp = chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": YOUR_SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ],
        tools=TOOLS,
        options={"temperature": 0.0},
    )
    calls = resp.message.tool_calls or []
    if not calls:
        print("[FAIL] model did not call the tool")
        return False
    call = calls[0]
    order_id = str(call.function.arguments.get("order_id"))
    ok = order_id == "4412"
    print(f"[{'PASS' if ok else 'FAIL'}] tool called with order_id={order_id!r}")
    if ok:
        print("tool result:", get_order_status(order_id))
    return ok


if __name__ == "__main__":
    run()
