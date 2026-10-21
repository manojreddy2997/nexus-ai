
import json


def handle_order_result(result):
    # Stop if the order lookup failed.
    if not result["success"]:
        return {
            "action": "stop",
            "message": result["error"],
            "order": None,
        }

    # Use order details only after a successful lookup.
    order = result["data"]

    return {
        "action": "check_refund_policy",
        "message": "Order found. Check the policy using its actual status.",
        "order": order,
    }


# Test 1: A valid order was found.
valid_result = {
    "success": True,
    "data": {
        "order_id": "ORD1002",
        "item": "Mechanical Keyboard",
        "status": "Delayed",
    },
    "error": None,
}

# Test 2: The order does not exist.
missing_result = {
    "success": False,
    "data": None,
    "error": "Order not found",
}

for name, result in [
    ("VALID ORDER", valid_result),
    ("MISSING ORDER", missing_result),
]:
    print(f"\n--- {name} ---")
    decision = handle_order_result(result)
    print(json.dumps(decision, indent=2))
