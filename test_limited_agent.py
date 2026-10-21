
import json
import ollama

MAX_TOOL_CALLS = 3

# Simulated order database
ORDERS = {
    "ORD1002": {
        "order_id": "ORD1002",
        "item": "Mechanical Keyboard",
        "status": "Delayed",
    },
    "ORD1003": {
        "order_id": "ORD1003",
        "item": "Wireless Mouse",
        "status": "Delivered",
    },
}


# Approved Python tool
def get_order(order_id):
    if not isinstance(order_id, str):
        return {"success": False, "error": "Order ID must be text"}

    order_id = order_id.strip().upper()

    if not order_id.startswith("ORD") or not order_id[3:].isdigit():
        return {"success": False, "error": "Invalid order ID"}

    order = ORDERS.get(order_id)

    if order is None:
        return {"success": False, "error": "Order not found"}

    return {"success": True, "data": order}


# Tell the LLM which tool is available
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
                        "description": "Order ID, such as ORD1002",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "You are an order assistant. "
            "Use get_order to answer order questions. "
            "Use only returned tool results. "
            "Never invent order details or claim a refund was processed."
        ),
    },
    {
        "role": "user",
        "content": "Check the status of order ORD9999.",
    },
]

tool_call_count = 0

while True:
    print("\nAsking Ollama for its next response...")

    response = ollama.chat(
        model="llama3.2:3b",
        messages=messages,
        tools=tools,
    )

    # No tool request means the model has produced a final response.
    if not response.message.tool_calls:
        print("\nFINAL ANSWER:")
        print(response.message.content)
        break

    # Stop before executing any request beyond the limit.
    if tool_call_count >= MAX_TOOL_CALLS:
        print("\nSTOP: Maximum tool-call limit reached.")
        print("No additional tool request was executed.")
        break

    # Keep the assistant's tool-call message in the conversation.
    messages.append(response.message)

    stop_workflow = False

    for call in response.message.tool_calls:
        if tool_call_count >= MAX_TOOL_CALLS:
            print("\nSTOP: Maximum tool-call limit reached.")
            stop_workflow = True
            break

        tool_name = call.function.name
        arguments = call.function.arguments

        print(f"\nTool request {tool_call_count + 1}")
        print("Tool:", tool_name)
        print("Arguments:", arguments)

        # Enforce the allowlist and validate arguments.
        if tool_name != "get_order":
            result = {
                "success": False,
                "error": "Tool not allowed",
            }
        elif set(arguments.keys()) != {"order_id"}:
            result = {
                "success": False,
                "error": "Invalid tool arguments",
            }
        else:
            try:
                result = get_order(arguments["order_id"])
            except Exception:
                result = {
                    "success": False,
                    "error": "Tool execution failed",
                }

        tool_call_count += 1

        print("Tool result:", result)

        # Return the result to the model.
        messages.append({
            "role": "tool",
            "name": tool_name,
            "content": json.dumps(result),
        })

    if stop_workflow:
        break

print(f"\nTotal tool calls executed: {tool_call_count}")
