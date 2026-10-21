
def safe_execute(tool_function, *args):
    try:
        result = tool_function(*args)

        return {
            "success": True,
            "data": result,
            "error": None,
        }

    except Exception:
        # Do not expose internal exception details to the user.
        return {
            "success": False,
            "data": None,
            "error": "Tool execution failed",
        }


def working_tool(order_id):
    return {
        "order_id": order_id,
        "status": "Delayed",
    }


def failing_tool(order_id):
    raise ConnectionError("Simulated database connection failure")


print("TEST 1: Working tool")
print(safe_execute(working_tool, "ORD1002"))

print("\nTEST 2: Failing tool")
print(safe_execute(failing_tool, "ORD1002"))
