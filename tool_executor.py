
"""Validated tool execution for Nexus AI."""

from order_tools import get_order


def check_refund_policy(order_status: str) -> dict:
    """Return sample refund guidance without approving a refund."""

    if not isinstance(order_status, str) or not order_status.strip():
        return {
            "success": False,
            "error": "A valid order status is required",
        }

    status = order_status.strip().casefold()

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
    "check_refund_policy": {"order_id"},
}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute approved tools using validated, trusted order records."""

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

    if set(arguments.keys()) != ALLOWED_TOOLS[tool_name]:
        return {
            "success": False,
            "error": "Invalid tool arguments",
        }

    order_id = arguments["order_id"]

    if not isinstance(order_id, str):
        return {
            "success": False,
            "error": "Order ID must be text",
        }

    if not order_id.strip():
        return {
            "success": False,
            "error": "Order ID cannot be empty",
        }

    order_result = get_order(order_id)

    if not order_result.get("success"):
        return order_result

    if tool_name == "get_order":
        return order_result

    order_data = order_result.get("data")

    if not isinstance(order_data, dict):
        return {
            "success": False,
            "error": "Invalid order record",
        }

    actual_status = order_data.get("status")

    if not isinstance(actual_status, str) or not actual_status.strip():
        return {
            "success": False,
            "error": "Order record has no valid status",
        }

    return check_refund_policy(actual_status)
