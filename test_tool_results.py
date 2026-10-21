
import json


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


# Example 1: An order was found.
order = {
    "order_id": "ORD1002",
    "status": "Delayed",
}

result = success_result(order)
print("SUCCESS RESULT:")
print(json.dumps(result, indent=2))


# Example 2: An order was not found.
result = error_result("Order not found")
print("\nERROR RESULT:")
print(json.dumps(result, indent=2))
