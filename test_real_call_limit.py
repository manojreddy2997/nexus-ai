
MAX_TOOL_CALLS = 3


def execute_tool(tool_name):
    if tool_name != "get_order":
        return {"success": False, "error": "Tool not allowed"}

    return {"success": True, "data": {"status": "Delayed"}}


def run_agent(requested_calls):
    calls_executed = 0

    for tool_name in requested_calls:
        if calls_executed >= MAX_TOOL_CALLS:
            print("STOP: Maximum tool-call limit reached.")
            break

        result = execute_tool(tool_name)
        calls_executed += 1

        print(f"Call {calls_executed}: {tool_name}")
        print("Result:", result)
    else:
        print("All requested calls completed.")

    print("Total calls executed:", calls_executed)


print("TEST 1: Two requests")
run_agent(["get_order", "get_order"])

print("\nTEST 2: Five requests")
run_agent([
    "get_order",
    "get_order",
    "get_order",
    "get_order",
    "get_order",
])
