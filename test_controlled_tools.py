
def get_order(order_id):
    return {
        "order_id": order_id,
        "status": "Delayed",
    }


def check_refund_policy(order_status):
    return {
        "order_status": order_status,
        "automatic_refund": False,
    }


def validate_order_id(order_id):
    if not isinstance(order_id, str):
        return False, "Order ID must be text"

    normalized_id = order_id.strip().upper()

    if not normalized_id:
        return False, "Order ID cannot be empty"

    if not normalized_id.startswith("ORD"):
        return False, "Order ID must start with ORD"

    if not normalized_id[3:].isdigit():
        return False, "Order ID must contain digits after ORD"

    return True, normalized_id


AVAILABLE_TOOLS = {
    "get_order": get_order,
    "check_refund_policy": check_refund_policy,
}


def execute_tool(tool_name, arguments):
    # 1. Check tool permission.
    if tool_name not in AVAILABLE_TOOLS:
        return {
            "success": False,
            "error": "Tool not allowed",
        }

    # 2. Check argument structure.
    if not isinstance(arguments, dict):
        return {
            "success": False,
            "error": "Arguments must be a dictionary",
        }

    # 3. Validate the order ID before calling get_order.
    if tool_name == "get_order":
        if set(arguments.keys()) != {"order_id"}:
            return {
                "success": False,
                "error": "Expected only the order_id argument",
            }

        valid, result = validate_order_id(arguments["order_id"])

        if not valid:
            return {
                "success": False,
                "error": result,
            }

        arguments = {"order_id": result}

    # 4. Execute the approved function safely.
    try:
        data = AVAILABLE_TOOLS[tool_name](**arguments)
        return {
            "success": True,
            "data": data,
            "error": None,
        }

    except (TypeError, ValueError) as error:
        return {
            "success": False,
            "error": f"Tool execution failed: {error}",
        }


print("TEST 1: Valid order")
print(execute_tool("get_order", {"order_id": " ord1002 "}))

print("\nTEST 2: Empty order ID")
print(execute_tool("get_order", {"order_id": "  "}))

print("\nTEST 3: Unapproved tool")
print(execute_tool("delete_all_orders", {}))

print("\nTEST 4: Unexpected argument")
print(execute_tool(
    "get_order",
    {"order_id": "ORD1002", "admin": True},
))
