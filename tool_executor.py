
from order_tools import ORDERS, get_order


def check_refund_policy(order_status: str) -> dict:
    """Return sample refund guidance without approving a refund."""

    if not isinstance(order_status, str):
        return {
            "success": False,
            "error": "Order status must be text",
        }

    status = order_status.strip().lower()

    if not status:
        return {
            "success": False,
            "error": "Order status cannot be empty",
        }

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
    """Execute approved tools after validating names and argument values."""

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

        return get_order(order_id)

    if tool_name == "check_refund_policy":
        order_status = arguments["order_status"]

        if not isinstance(order_status, str):
            return {
                "success": False,
                "error": "Order status must be text",
            }

        if not order_status.strip():
            return {
                "success": False,
                "error": "Order status cannot be empty",
            }

        known_statuses = {
            order["status"].strip().casefold()
            for order in ORDERS.values()
            if isinstance(order.get("status"), str)
        }

        if order_status.strip().casefold() not in known_statuses:
            return {
                "success": False,
                "error": "Order status does not match a known order status",
            }

        return check_refund_policy(order_status)

    return {
        "success": False,
        "error": "Tool not allowed",
    }
