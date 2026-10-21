
ORDERS = {
    "ORD1002": {
        "order_id": "ORD1002",
        "status": "Delayed",
    }
}


def get_order(order_id):
    order = ORDERS.get(order_id)

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
    allowed_statuses = {"Delayed", "Delivered"}

    if order_status not in allowed_statuses:
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
        "error": None,
    }


def run_workflow(order_id):
    # Step 1: Retrieve the order.
    order_result = get_order(order_id)

    if not order_result["success"]:
        return {
            "success": False,
            "step": "order_lookup",
            "error": order_result["error"],
        }

    # Step 2: Use the status returned by the order tool.
    verified_status = order_result["data"]["status"]

    # Step 3: Check the policy using that status.
    policy_result = check_refund_policy(verified_status)

    if not policy_result["success"]:
        return {
            "success": False,
            "step": "refund_policy",
            "error": policy_result["error"],
        }

    return {
        "success": True,
        "order": order_result["data"],
        "policy": policy_result["data"],
    }


print("TEST 1: Known order")
print(run_workflow("ORD1002"))

print("\nTEST 2: Missing order")
print(run_workflow("ORD9999"))

print("\nTEST 3: Unknown status rejected")
print(check_refund_policy("RefundApproved"))
