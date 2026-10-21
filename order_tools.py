
"""Validated order lookup tools for Nexus AI."""

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


def get_order(order_id: str) -> dict:
    """Look up an order after validating its ID."""

    if not isinstance(order_id, str):
        return {
            "success": False,
            "error": "Order ID must be text",
        }

    order_id = order_id.strip().upper()

    if not order_id.startswith("ORD") or not order_id[3:].isdigit():
        return {
            "success": False,
            "error": "Invalid order ID",
        }

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
