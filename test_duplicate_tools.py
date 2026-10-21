
import json


def make_call_key(tool_name, arguments):
    # Sort keys so equivalent dictionaries produce the same key.
    normalized_arguments = json.dumps(
        arguments,
        sort_keys=True,
    )
    return f"{tool_name}:{normalized_arguments}"


def should_execute(tool_name, arguments, completed_calls):
    call_key = make_call_key(tool_name, arguments)

    if call_key in completed_calls:
        return False, "Duplicate tool call detected"

    return True, call_key


completed_calls = set()

# First request: allow it.
allowed, result = should_execute(
    "get_order",
    {"order_id": "ORD1002"},
    completed_calls,
)
print("TEST 1:", allowed, result)

if allowed:
    completed_calls.add(result)

# Same request again: block it.
allowed, result = should_execute(
    "get_order",
    {"order_id": "ORD1002"},
    completed_calls,
)
print("TEST 2:", allowed, result)

# Different order: allow it.
allowed, result = should_execute(
    "get_order",
    {"order_id": "ORD1003"},
    completed_calls,
)
print("TEST 3:", allowed, result)
