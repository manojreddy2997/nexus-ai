
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
def test_empty_order_id_is_rejected():
    result = execute_tool(
        "get_order",
        {"order_id": ""},
    )

    assert result == {
        "success": False,
        "error": "Order ID cannot be empty",
    }


def test_whitespace_order_id_is_rejected():
    result = execute_tool(
        "get_order",
        {"order_id": "   "},
    )

    assert result == {
        "success": False,
        "error": "Order ID cannot be empty",
    }


def test_empty_order_id_for_refund_policy_is_rejected():
    result = execute_tool(
        "check_refund_policy",
        {"order_id": ""},
    )

    assert result == {
        "success": False,
        "error": "Order ID cannot be empty",
    }


def test_non_text_order_id_for_refund_policy_is_rejected():
    result = execute_tool(
        "check_refund_policy",
        {"order_id": None},
    )

    assert result == {
        "success": False,
        "error": "Order ID must be text",
    }


def test_unknown_order_for_refund_policy_is_rejected():
    result = execute_tool(
        "check_refund_policy",
        {"order_id": "ORD9999"},
    )

    assert result == {
        "success": False,
        "error": "Order not found",
    }


def test_refund_policy_uses_status_for_requested_order():
    delayed = execute_tool(
        "check_refund_policy",
        {"order_id": "ORD1002"},
    )

    delivered = execute_tool(
        "check_refund_policy",
        {"order_id": "ORD1003"},
    )

    assert delayed["success"] is True
    assert delayed["policy"] == (
        "Delayed orders require a support review."
    )

    assert delivered["success"] is True
    assert delivered["policy"] == (
        "Delivered orders may qualify for a refund review."
    )

    assert delayed["automatic_refund"] is False
    assert delivered["automatic_refund"] is False


def test_caller_cannot_override_order_status():
    result = execute_tool(
        "check_refund_policy",
        {
            "order_id": "ORD1002",
            "order_status": "Delivered",
        },
    )

    assert result == {
        "success": False,
        "error": "Invalid tool arguments",
    }


def test_old_status_argument_is_rejected():
    result = execute_tool(
        "check_refund_policy",
        {"order_status": "Delivered"},
    )

    assert result == {
        "success": False,
        "error": "Invalid tool arguments",
    }