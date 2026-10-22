
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import agent


def make_response(content=None, tool_calls=None):
    """Create a mock Ollama response."""
    message = SimpleNamespace(
        content=content,
        tool_calls=tool_calls or [],
    )
    return SimpleNamespace(message=message)


def make_tool_call(name, arguments):
    """Create a mock tool call."""
    function = SimpleNamespace(
        name=name,
        arguments=arguments,
    )
    return SimpleNamespace(function=function)


class TestGeneralAgentRegression(unittest.TestCase):

    @patch("builtins.print")
    def test_known_order_uses_tool_result(self, mock_print):
        tool_call = make_tool_call(
            "get_order",
            {"order_id": "ORD1002"},
        )

        tool_response = make_response(tool_calls=[tool_call])
        final_response = make_response(
            content="Order ORD1002 is Delayed."
        )

        with (
            patch.object(
                agent.client,
                "chat",
                side_effect=[tool_response, final_response],
            ),
            patch(
                "agent.execute_tool",
                return_value={
                    "success": True,
                    "data": {
                        "order_id": "ORD1002",
                        "item": "Mechanical Keyboard",
                        "status": "Delayed",
                    },
                },
            ) as execute,
        ):
            agent.run_general_agent(
                "What is the status of order ORD1002?"
            )

        execute.assert_called_once_with(
            "get_order",
            {"order_id": "ORD1002"},
        )

        printed_text = " ".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertIn("Delayed", printed_text)

    @patch("builtins.print")
    def test_missing_order_error_is_returned_to_model(
        self,
        mock_print,
    ):
        tool_call = make_tool_call(
            "get_order",
            {"order_id": "ORD9999"},
        )

        tool_response = make_response(tool_calls=[tool_call])
        final_response = make_response(
            content="Order ORD9999 was not found."
        )

        with (
            patch.object(
                agent.client,
                "chat",
                side_effect=[tool_response, final_response],
            ) as chat,
            patch(
                "agent.execute_tool",
                return_value={
                    "success": False,
                    "error": "Order not found",
                },
            ) as execute,
        ):
            agent.run_general_agent(
                "What is the status of order ORD9999?"
            )

        execute.assert_called_once_with(
            "get_order",
            {"order_id": "ORD9999"},
        )

        # Confirm the failed lookup is sent to the model.
        messages = chat.call_args_list[1].kwargs["messages"]
        tool_messages = [
            message
            for message in messages
            if isinstance(message, dict)
            and message.get("role") == "tool"
        ]

        self.assertTrue(tool_messages)

        result = json.loads(tool_messages[-1]["content"])
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Order not found")

        printed_text = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("not found", printed_text.lower())

    @patch("builtins.print")
    def test_order_status_uses_verified_tool_data(self, mock_print):
        with patch(
            "agent.execute_tool",
            return_value={
                "success": True,
                "data": {
                    "order_id": "ORD1002",
                    "item": "Mechanical Keyboard",
                    "status": "Delayed",
                },
            },
        ) as execute:
            agent.handle_order_status("ORD1002")

        execute.assert_called_once_with(
            "get_order",
            {"order_id": "ORD1002"},
        )

        output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("ORD1002", output)
        self.assertIn("Mechanical Keyboard", output)
        self.assertIn("Delayed", output)

    @patch("builtins.print")
    def test_order_status_handles_missing_order(self, mock_print):
        with patch(
            "agent.execute_tool",
            return_value={
                "success": False,
                "error": "Order not found",
            },
        ) as execute:
            agent.handle_order_status("ORD9999")

        execute.assert_called_once_with(
            "get_order",
            {"order_id": "ORD9999"},
        )

        output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("couldn't retrieve", output.lower())
        self.assertIn("Order not found", output)


if __name__ == "__main__":
    unittest.main(verbosity=2)
