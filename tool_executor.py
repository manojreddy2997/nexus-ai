from order_tools import get_order


def check_refund_policy(order_status: str) -> dict:
    """Return sample refund guidance without approving a refund."""

    if not isinstance(order_status, str):
        return {
            "success": False,
            "error": "Order status must be text",
        }

    status = order_status.strip().lower()

    if status == "delivered":
        return {
            "success": True,
            "policy": "Delivered orders may qualify for a refund review.",
            "next_step": "Check the return window and applicable conditions.",
            "automatic_refund": False,
        }

    if status == "delayed":
        return {
            "success": True,
            "policy": "Delayed orders require a support review.",
            "next_step": "Review the delivery delay and applicable policy.",
            "automatic_refund": False,
        }

    return {
        "success": True,
        "policy": "Eligibility cannot be determined from this status alone.",
        "next_step": "Ask support to review the order.",
        "automatic_refund": False,
    }


ALLOWED_TOOLS = {
    "get_order": {"order_id"},
    "check_refund_policy": {"order_status"},
}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute only approved tools with exactly the expected arguments."""

    if not isinstance(tool_name, str) or tool_name not in ALLOWED_TOOLS:
        return {
            "success": False,
            "error": "Tool not allowed",
        }

    if not isinstance(arguments, dict):
        return {
            "success": False,
            "error": "Invalid tool arguments",
        }

    expected_arguments = ALLOWED_TOOLS[tool_name]

    if set(arguments.keys()) != expected_arguments:
        return {
            "success": False,
            "error": "Invalid tool arguments",
        }

    if tool_name == "get_order":
        return get_order(arguments["order_id"])

    if tool_name == "check_refund_policy":
        return check_refund_policy(arguments["order_status"])

    return {
        "success": False,
        "error": "Tool not allowed",
    }
