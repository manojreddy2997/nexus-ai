
import json

tool_request = {
    "tool_name": "get_order",
    "arguments": {
        "order_id": "ORD1002"
    }
}

print("LLM tool request:")
print(json.dumps(tool_request, indent=2))

print("\nRequested tool:", tool_request["tool_name"])
print("Arguments:", tool_request["arguments"])
