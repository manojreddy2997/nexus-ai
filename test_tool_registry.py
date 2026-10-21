
import json


def get_order(order_id):
    return {
        "order_id": order_id,
        "status": "Delayed",
    }


def check_refund_policy(order_status):
    return {
        "status_checked": order_status,
        "automatic_refund": False,
    }


# Only these functions are approved for execution.
AVAILABLE_TOOLS = {
    "get_order": get_order,
    "check_refund_policy": check_refund_policy,
}


def execute_tool(tool_name, arguments):
    # Reject tool names that are not in our approved registry.
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "success": False,
            "error": f"Tool not allowed: {tool_name}",
        }

    # Execute only a registered function.
    try:
        result = AVAILABLE_TOOLS[tool_name](**arguments)

        return {
            "success": True,
            "data": result,
            "error": None,
        }

    except (TypeError, ValueError) as error:
        return {
            "success": False,
            "error": f"Invalid tool arguments: {error}",
        }


print("TEST 1: Approved tool")
print(json.dumps(
    execute_tool("get_order", {"order_id": "ORD1002"}),
    indent=2,
))

print("\nTEST 2: Unapproved tool")
print(json.dumps(
    execute_tool("delete_all_orders", {}),
    indent=2,
))

print("\nTEST 3: Invalid arguments")
print(json.dumps(
    execute_tool("get_order", {}),
    indent=2,
))
