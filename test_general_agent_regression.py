
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import agent


def make_tool_call(name, arguments):
    """Create a mock Ollama tool call."""
    return SimpleNamespace(
        function=SimpleNamespace(
            name=name,
            arguments=arguments,
        )
    )


def make_response(content="", tool_calls=None):
    """Create a mock Ollama chat response."""
    message = SimpleNamespace(
        role="assistant",
        content=content,
        tool_calls=tool_calls or [],
    )
    return SimpleNamespace(message=message)


class TestGeneralAgentRegression(unittest.TestCase):

    @patch("builtins.print")
    def test_known_order_uses_tool_result(self, mock_print):
        tool_call = make_tool_call(
            "get_order",
            {"order_id": "ORD1002"},
        )
        tool_response = make_response(tool_calls=[tool_call])
        final_response = make_response(
            content="The Mechanical Keyboard order is delayed."
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
            agent.run_general_agent("Explain my order ORD1002.")

        execute.assert_called_once_with(
            "get_order",
            {"order_id": "ORD1002"},
        )

    @patch("builtins.print")
    def test_missing_order_error_is_returned_to_model(self, mock_print):
        tool_call = make_tool_call(
            "get_order",
            {"order_id": "ORD9999"},
        )
        tool_response = make_response(tool_calls=[tool_call])
        final_response = make_response(
            content="I could not find that order."
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
            ),
        ):
            agent.run_general_agent("Look up order ORD9999.")

        self.assertEqual(chat.call_count, 2)

        messages = chat.call_args_list[1].kwargs["messages"]
        self.assertTrue(
            any(
                getattr(message, "role", None) == "tool"
                or (
                    isinstance(message, dict)
                    and message.get("role") == "tool"
                )
                for message in messages
            )
        )


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
        self.assertIn("ORD9999", output)
        self.assertIn("Order not found", output)


    @patch("builtins.print")
    def test_refund_request_routes_to_refund_handler(self, mock_print):
        with (
            patch.object(agent, "handle_refund_request") as handler,
            patch.object(agent.client, "chat") as chat,
        ):
            agent.run_agent("I want a refund for order ORD1002")

        handler.assert_called_once_with(
            "I want a refund for order ORD1002",
            "ORD1002",
        )
        chat.assert_not_called()

    @patch("builtins.print")
    def test_status_request_bypasses_llm(self, mock_print):
        with (
            patch.object(agent, "handle_order_status") as handler,
            patch.object(agent.client, "chat") as chat,
        ):
            agent.run_agent("Track order ORD1002")

        handler.assert_called_once()
        chat.assert_not_called()


    @patch("builtins.print")
    def test_refund_without_order_id_requests_order_id(self, mock_print):
        with (
            patch.object(agent, "handle_refund_request") as handler,
            patch.object(agent.client, "chat") as chat,
        ):
            agent.run_agent("I want a refund")

        handler.assert_not_called()
        chat.assert_not_called()

        output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("ORD1002", output)





    @patch("builtins.print")
    def test_general_question_uses_llm_agent(self, mock_print):
        with (
            patch.object(agent, "run_general_agent") as general_agent,
        ):
            agent.run_agent("Explain how AI assistants work.")

        general_agent.assert_called_once_with(
            "Explain how AI assistants work."
        )

    @patch("builtins.print")
    def test_tool_exception_is_returned_as_safe_error(self, mock_print):
        tool_call = make_tool_call(
            "get_order",
            {"order_id": "ORD1002"},
        )
        tool_response = make_response(tool_calls=[tool_call])
        final_response = make_response(
            content="Sorry, I couldn't retrieve the order."
        )

        with (
            patch.object(
                agent.client,
                "chat",
                side_effect=[tool_response, final_response],
            ) as chat,
            patch(
                "agent.execute_tool",
                side_effect=ConnectionError(
                    "Sensitive internal database details"
                ),
            ) as execute,
        ):
            agent.run_general_agent("Explain my order.")

        execute.assert_called_once_with(
            "get_order",
            {"order_id": "ORD1002"},
        )
        self.assertEqual(chat.call_count, 2)

        messages = chat.call_args_list[1].kwargs["messages"]

        # Ollama messages may be dictionaries or objects.
        tool_contents = []

        for message in messages:
            if isinstance(message, dict):
                role = message.get("role")
                content = message.get("content")
            else:
                role = getattr(message, "role", None)
                content = getattr(message, "content", None)

            if role == "tool" and isinstance(content, str):
                tool_contents.append(content)

        self.assertTrue(
            any(
                json.loads(content).get("error")
                == "Tool execution failed"
                for content in tool_contents
            ),
            f"Expected a safe tool error in messages: {messages!r}",
        )

        self.assertNotIn(
            "Sensitive internal database details",
            repr(messages),
        )

    @patch("builtins.print")
    def test_ollama_exception_is_handled_safely(self, mock_print):
        with patch.object(
            agent.client,
            "chat",
            side_effect=ConnectionError(
                "Sensitive internal connection details"
            ),
        ):
            agent.run_general_agent("Explain AI agents.")

        output = " ".join(
            str(call) for call in mock_print.call_args_list
        )

        self.assertNotIn(
            "Sensitive internal connection details",
            output,
        )

    @patch("builtins.print")
    def test_tool_round_limit_stops_repeated_tool_calls(self, mock_print):
        tool_call = make_tool_call(
            "get_order",
            {"order_id": "ORD1002"},
        )
        repeated_tool_response = make_response(
            tool_calls=[tool_call]
        )

        with (
            patch.object(
                agent.client,
                "chat",
                return_value=repeated_tool_response,
            ) as chat,
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
            agent.run_general_agent("Explain my order.")

        self.assertEqual(
            chat.call_count,
            agent.MAX_TOOL_ROUNDS,
        )
        self.assertEqual(
            execute.call_count,
            agent.MAX_TOOL_ROUNDS,
        )

        output = " ".join(
            str(call) for call in mock_print.call_args_list
        )
        self.assertIn("maximum number of tool rounds", output.lower())


if __name__ == "__main__":
    unittest.main()
