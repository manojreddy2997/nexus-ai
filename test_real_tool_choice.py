
import ollama

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
            "When the user asks about an order, call get_order. "
            "Do not invent order details."
        )
    },
    {
        "role": "user",
        "content": "Check the status of order ORD1002."
    }
]

print("Asking the local LLM to choose a tool...\n")

response = ollama.chat(
    model="llama3.2:3b",
    messages=messages,
    tools=tools
)

tool_calls = response.message.tool_calls

if tool_calls:
    for call in tool_calls:
        print("Tool selected:", call.function.name)
        print("Arguments:", call.function.arguments)
else:
    print("No tool call was returned.")
    print("LLM response:", response.message.content)
