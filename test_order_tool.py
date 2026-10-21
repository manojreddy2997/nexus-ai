
import json


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


def success_result(data):
    return {
        "success": True,
        "data": data,
        "error": None,
    }


def error_result(message):
    return {
        "success": False,
        "data": None,
        "error": message,
    }


def get_order(order_id: str) -> dict:
    # Normalize the ID to avoid case and whitespace problems.
    normalized_id = order_id.strip().upper()

    # Look up the order in our sample database.
    order = ORDERS.get(normalized_id)

    # Return a consistent error if the order does not exist.
    if order is None:
        return error_result("Order not found")

    # Return the order details when the lookup succeeds.
    return success_result(order)


# Test 1: Existing order.
print("TEST 1: Existing order")
print(json.dumps(get_order("ORD1002"), indent=2))

# Test 2: Unknown order.
print("\nTEST 2: Missing order")
print(json.dumps(get_order("ORD9999"), indent=2))

# Test 3: Lowercase ID with extra spaces.
print("\nTEST 3: Normalize order ID")
print(json.dumps(get_order("  ord1003  "), indent=2))
