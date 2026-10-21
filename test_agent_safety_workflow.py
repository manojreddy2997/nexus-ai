
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

ALLOWED_TOOLS = {"get_order", "check_refund_policy"}


def validate_order_id(order_id):
    if not isinstance(order_id, str):
        return False, "Order ID must be text"

    order_id = order_id.strip().upper()

    if not order_id:
        return False, "Order ID cannot be empty"

    if not order_id.startswith("ORD"):
        return False, "Order ID must start with ORD"

    if not order_id[3:].isdigit():
        return False, "Order ID must end with digits"

    return True, order_id


def get_order(order_id):
    order = ORDERS.get(order_id)

    if order is None:
        return {
            "success": False,
            "error": "Order not found",
        }

    return {
        "success": True,
        "data": order,
    }


def check_refund_policy(order_status):
    if order_status not in {"Delayed", "Delivered"}:
        return {
            "success": False,
            "error": "Unrecognized order status",
        }

    return {
        "success": True,
        "data": {
            "review_required": True,
            "automatic_refund": False,
            "status_checked": order_status,
        },
    }


def run_workflow(tool_name, order_id):
    if tool_name not in ALLOWED_TOOLS:
        return {
            "success": False,
            "error": "Tool not allowed",
        }

    if tool_name != "get_order":
        return {
            "success": False,
            "error": "Workflow must start with get_order",
        }

    valid, result = validate_order_id(order_id)

    if not valid:
        return {
            "success": False,
            "error": result,
        }

    order_result = get_order(result)

    if not order_result["success"]:
        return {
            "success": False,
            "step": "order_lookup",
            "error": order_result["error"],
        }

    order = order_result["data"]
    policy_result = check_refund_policy(order["status"])

    if not policy_result["success"]:
        return {
            "success": False,
            "step": "refund_policy",
            "error": policy_result["error"],
        }

    return {
        "success": True,
        "order": order,
        "policy": policy_result["data"],
    }


if __name__ == "__main__":
    print("TEST 1: Valid order")
    print(run_workflow("get_order", " ord1002 "))

    print("\nTEST 2: Missing order")
    print(run_workflow("get_order", "ORD9999"))

    print("\nTEST 3: Invalid order ID")
    print(run_workflow("get_order", "ABC1002"))

    print("\nTEST 4: Unapproved tool")
    print(run_workflow("delete_all_orders", "ORD1002"))
