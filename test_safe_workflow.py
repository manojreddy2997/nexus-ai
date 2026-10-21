
import json

ORDERS = {
    "ORD1002": {
        "order_id": "ORD1002",
        "item": "Mechanical Keyboard",
        "status": "Delayed",
    }
}


def get_order(order_id):
    order = ORDERS.get(order_id.strip().upper())

    if order is None:
        return {
            "success": False,
            "data": None,
            "error": "Order not found",
        }

    return {
        "success": True,
        "data": order,
        "error": None,
    }


def check_refund_policy(order_status):
    print(f"POLICY TOOL CALLED with status: {order_status}")

    return {
        "review_required": True,
        "automatic_refund": False,
        "next_step": (
            "Support review required"
            if order_status == "Delayed"
            else "Check the applicable return policy"
        ),
    }


def run_safe_workflow(order_id):
    print(f"\nLooking up {order_id}...")
    order_result = get_order(order_id)

    if not order_result["success"]:
        return {
            "success": False,
            "message": order_result["error"],
            "policy": None,
        }

    order = order_result["data"]
    policy = check_refund_policy(order["status"])

    return {
        "success": True,
        "message": "Order found and policy checked",
        "order": order,
        "policy": policy,
    }


print("=== TEST 1: Existing order ===")
print(json.dumps(run_safe_workflow("ORD1002"), indent=2))

print("\n=== TEST 2: Missing order ===")
print(json.dumps(run_safe_workflow("ORD9999"), indent=2))
