
from tool_executor import execute_tool


def test_unapproved_tool_is_rejected():
    result = execute_tool(
        "delete_all_orders",
        {},
    )

    assert result == {
        "success": False,
        "error": "Tool not allowed",
    }


def test_unexpected_arguments_are_rejected():
    result = execute_tool(
        "get_order",
        {
            "order_id": "ORD1002",
            "admin": True,
        },
    )

    assert result == {
        "success": False,
        "error": "Invalid tool arguments",
    }


def test_missing_arguments_are_rejected():
    result = execute_tool("get_order", {})

    assert result == {
        "success": False,
        "error": "Invalid tool arguments",
    }


def test_valid_order_lookup_still_works():
    result = execute_tool(
        "get_order",
        {"order_id": "ORD1002"},
    )

    assert result["success"] is True
    assert result["data"]["order_id"] == "ORD1002"
    assert result["data"]["status"] == "Delayed"
def test_none_arguments_are_rejected():
    result = execute_tool("get_order", None)

    assert result == {
        "success": False,
        "error": "Invalid tool arguments",
    }


def test_list_arguments_are_rejected():
    result = execute_tool("get_order", ["ORD1002"])

    assert result == {
        "success": False,
        "error": "Invalid tool arguments",
    }
def test_invalid_order_id_is_rejected():
    result = execute_tool(
        "get_order",
        {"order_id": "INVALID123"},
    )

    assert result == {
        "success": False,
        "error": "Invalid order ID",
    }


def test_unknown_order_id_is_rejected():
    result = execute_tool(
        "get_order",
        {"order_id": "ORD9999"},
    )

    assert result == {
        "success": False,
        "error": "Order not found",
    }
def test_numeric_order_id_is_rejected():
    result = execute_tool(
        "get_order",
        {"order_id": 12345},
    )

    assert result == {
        "success": False,
        "error": "Order ID must be text",
    }


def test_none_order_id_is_rejected():
    result = execute_tool(
        "get_order",
        {"order_id": None},
    )

    assert result == {
        "success": False,
        "error": "Order ID must be text",
    }
def test_none_tool_name_is_rejected():
    result = execute_tool(None, {})

    assert result == {
        "success": False,
        "error": "Tool not allowed",
    }


def test_list_tool_name_is_rejected():
    result = execute_tool(["get_order"], {})

    assert result == {
        "success": False,
        "error": "Tool not allowed",
    }