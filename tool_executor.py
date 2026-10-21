
from order_tools import get_order


ALLOWED_TOOLS = {
    "get_order": {"order_id"},
}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute only approved tools with the expected arguments."""

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

    return {
        "success": False,
        "error": "Tool not allowed",
    }
