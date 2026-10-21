
import json
import ollama

# Simulated order database
ORDERS = {
    "ORD1002": {
        "order_id": "ORD1002",
        "item": "Mechanical Keyboard",
        "status": "Delayed"
    },
    "ORD1003": {
        "order_id": "ORD1003",
        "item": "Wireless Mouse",
        "status": "Delivered"
    }
}


# Python tool: validates and looks up an order
def get_order(order_id: str) -> dict:
    if not isinstance(order_id, str):
        return {"success": False, "error": "Order ID must be text"}

    order_id = order_id.strip().upper()

    if not order_id.startswith("ORD") or not order_id[3:].isdigit():
        return {"success": False, "error": "Invalid order ID"}

    order = ORDERS.get(order_id)

    if order is None:
        return {"success": False, "error": "Order not found"}

    return {"success": True, "data": order}


# Tell Ollama which tool it may request
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Look up an order using its order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID, such as ORD1002"
                    }
                },
                "required": ["order_id"]
            }
        }
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "You are an order assistant. "
            "Use get_order for order questions. "
            "Base your answer only on the tool result. "
            "If the lookup fails, say the order could not be verified. "
            "Never claim that a refund was processed."
        )
    },
    {
        "role": "user",
        "content": "Check the status of order ORD9999."
    }
]

print("STEP 1: Asking the LLM to choose a tool...")

response = ollama.chat(
    model="llama3.2:3b",
    messages=messages,
    tools=tools
)

# Give the model a chance to finish if it doesn't request a tool.
if not response.message.tool_calls:
    print("The model did not request a tool.")
    print("Model response:", response.message.content)
    raise SystemExit(0)

# Execute the requested tool through our controlled Python code.
for call in response.message.tool_calls:
    tool_name = call.function.name
    arguments = call.function.arguments

    print("Selected tool:", tool_name)
    print("Arguments:", arguments)

    # Only execute tools explicitly approved by this program.
    if tool_name != "get_order":
        tool_result = {
            "success": False,
            "error": "Tool not allowed"
        }
    elif set(arguments.keys()) != {"order_id"}:
        tool_result = {
            "success": False,
            "error": "Invalid tool arguments"
        }
    else:
        tool_result = get_order(arguments["order_id"])

    print("\nSTEP 2: Python tool result:")
    print(json.dumps(tool_result, indent=2))

    # Send the tool request and its result back to the LLM.
    messages.append(response.message)

    messages.append({
        "role": "tool",
        "name": tool_name,
        "content": json.dumps(tool_result)
    })

    print("\nSTEP 3: Asking the LLM for its final answer...")

    final_response = ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        tools=tools
    )

    print("\nFINAL ANSWER:")
    print(final_response.message.content)
