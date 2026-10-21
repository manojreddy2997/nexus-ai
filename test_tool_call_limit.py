
MAX_TOOL_CALLS = 3


def run_agent_simulation(requested_calls):
    tool_calls_made = 0

    for tool_name in requested_calls:
        if tool_calls_made >= MAX_TOOL_CALLS:
            print("STOP: Maximum tool-call limit reached.")
            return

        print(f"Executing approved tool: {tool_name}")
        tool_calls_made += 1

    print(f"Finished. Tool calls made: {tool_calls_made}")


print("TEST 1: Two tool requests")
run_agent_simulation(["get_order", "check_refund_policy"])

print("\nTEST 2: Five tool requests")
run_agent_simulation([
    "get_order",
    "check_refund_policy",
    "get_order",
    "check_refund_policy",
    "get_order"
])
