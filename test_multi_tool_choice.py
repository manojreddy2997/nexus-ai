
import ollama

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Find an order's item and delivery status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"}
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_policy",
            "description": "Check refund policy using an order's status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_status": {"type": "string"}
                },
                "required": ["order_status"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_ticket",
            "description": (
                "Request creation of a support ticket for an order issue. "
                "This is a simulated tool."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string"},
                    "issue": {"type": "string"}
                },
                "required": ["order_id", "issue"]
            }
        }
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "You are a customer-support assistant. "
            "Choose the most appropriate available tool for the user's request. "
            "Do not invent order information."
        )
    },
    {
        "role": "user",
        "content": "Check the delivery status of order ORD1002."
    }
]

response = ollama.chat(
    model="llama3.2:3b",
    messages=messages,
    tools=tools
)

if response.message.tool_calls:
    for call in response.message.tool_calls:
        print("Selected tool:", call.function.name)
        print("Arguments:", call.function.arguments)
else:
    print("No tool call returned.")
    print("Response:", response.message.content)
