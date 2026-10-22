
import json
import re

import ollama

from tool_executor import execute_tool


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

MODEL = "llama3.2:3b"
MAX_TOOL_ROUNDS = 5

client = ollama.Client()


# --------------------------------------------------
# 2. DEFINE APPROVED TOOLS FOR OLLAMA
# --------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": (
                "Look up an order using its ID, "
                "such as ORD1002."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The customer's order ID",
                    }
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_refund_policy",
            "description": (
                "Check sample refund guidance using the "
                "actual order status returned by get_order."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_status": {
                        "type": "string",
                        "description": "The actual order status",
                    }
                },
                "required": ["order_status"],
            },
        },
    },
]


# --------------------------------------------------
# 3. EXTRACT AN ORDER ID
# --------------------------------------------------

def extract_order_id(user_input: str):
    """Extract IDs such as ORD1002 or ORD-1002."""

    match = re.search(
        r"\bORD[\s-]*\d+\b",
        user_input,
        re.IGNORECASE,
    )

    if not match:
        return None

    return re.sub(
        r"[\s-]+",
        "",
        match.group(0).upper(),
    )


# --------------------------------------------------
# 4. CONTROLLED REFUND WORKFLOW
# --------------------------------------------------

def handle_refund_request(user_input: str, order_id: str):
    """
    Look up the order and provide sample refund guidance.
    This workflow never approves or processes a refund.
    """

    print("\n--- Tool round 1: Order lookup ---")

    order_result = execute_tool(
        "get_order",
        {"order_id": order_id},
    )

    print("Requested tool: get_order")
    print("Tool result:", json.dumps(order_result, indent=2))

    if not order_result.get("success"):
        print("\nAgent: I couldn't retrieve that order.")
        print(
            order_result.get(
                "error",
                "Please check the order ID and try again.",
            )
        )
        return

    order_data = order_result["data"]
    actual_status = order_data["status"]

    print("\n--- Tool round 2: Refund policy ---")

    policy_result = execute_tool(
        "check_refund_policy",
        {"order_status": actual_status},
    )

    print("Requested tool: check_refund_policy")
    print("Tool result:", json.dumps(policy_result, indent=2))

    if not policy_result.get("success"):
        print(
            "\nAgent: I retrieved the order, but "
            "could not complete the policy check."
        )
        return

    # Format the response directly from verified tool results.
    # Do not ask the LLM to generate refund guidance.

    order_id_result = order_data.get("order_id", order_id)
    item = order_data.get("item", "Unknown item")
    status = order_data.get("status", "Unknown")

    policy = policy_result.get(
        "policy",
        "Refund eligibility requires further review.",
    )

    next_step = policy_result.get(
        "next_step",
        "Contact support for further guidance.",
    )

    print("\n--- Final response ---")

    print(
        f"\nAgent: Order {order_id_result} "
        f"({item}) is currently {status}.\n\n"
        f"Sample refund guidance: {policy}\n\n"
        f"Suggested next step: {next_step}\n\n"
        "This is sample guidance, not an official "
        "retailer policy. No refund has been approved "
        "or processed."
    )


# --------------------------------------------------
# 5. GENERAL TOOL-CALLING AGENT
# --------------------------------------------------

def handle_order_status(order_id: str):
    """Return an order-status response from verified tool data."""

    print("\n--- Order status lookup ---")

    result = execute_tool(
        "get_order",
        {"order_id": order_id},
    )

    print("Requested tool: get_order")
    print("Tool result:", json.dumps(result, indent=2))

    if not result.get("success"):
        error = result.get("error", "Order lookup failed.")
        print(f"\nAgent: I couldn't retrieve order {order_id}.")
        print(f"Reason: {error}")
        return

    order = result["data"]
    verified_id = order.get("order_id", order_id)
    item = order.get("item", "Unknown item")
    status = order.get("status", "Unknown")

    print("\n--- Final response ---")
    print(
        f"\nAgent: Order {verified_id} "
        f"({item}) is currently {status}."
    )

def run_general_agent(user_input: str):
    """
    Let Ollama request approved tools.

    Python validates and executes every tool request.
    The verified results are returned to Ollama.
    """

    messages = [
                 {
            "role": "system",
            "content": (
                "You are Nexus AI, a careful customer-support assistant. "
                "Use approved tools when you need order information. "
                "Treat successful tool results as the only source of "
                "facts about orders. Never invent order details, "
                "shipping information, or delivery dates. "
                "For requests involving multiple orders, look up each "
                "requested order with get_order and compare only the "
                "facts returned by those lookups. "
                "Use check_refund_policy only when the user explicitly "
                "asks about refund policy, refund eligibility, or "
                "refund guidance. Its order_status argument must be "
                "the actual status string returned by get_order, "
                "never a comparison, explanation, or guessed value. "
                "Do not call the refund-policy tool just to compare "
                "orders or report their statuses. "
                "If a tool returns an error, explain it clearly. "
                "If order information is unavailable, say so. "
                "Never claim a refund was approved or processed. "
                "Refund guidance is sample guidance, not an official "
                "retailer policy. Keep answers concise and factual."
            ),
        },
        {
            "role": "user",
            "content": user_input,
        },
    ]

    for round_number in range(1, MAX_TOOL_ROUNDS + 1):
        try:
            response = client.chat(
                model=MODEL,
                messages=messages,
                tools=tools,
            )
        except Exception:
            print(
                "\nAgent: I couldn't communicate with the "
                "local language model. Check that Ollama "
                "is running and the model is available."
            )
            return

        tool_calls = response.message.tool_calls

        # No tool calls means the model has finished.
        if not tool_calls:
            print("\nAgent:", response.message.content)
            return

        print(f"\n--- Tool round {round_number} ---")

        # Preserve the assistant's tool-call message.
        messages.append(response.message)

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print("Requested tool:", tool_name)
            print("Arguments:", arguments)

            # All tool requests must pass through the executor.
            try:
                if not isinstance(arguments, dict):
                    tool_result = {
                        "success": False,
                        "error": "Invalid tool arguments",
                    }
                else:
                    tool_result = execute_tool(
                        tool_name,
                        arguments,
                    )
            except Exception:
                tool_result = {
                    "success": False,
                    "error": "Tool execution failed",
                }

            print(
                "Tool result:",
                json.dumps(tool_result, indent=2),
            )

            # Send the result back so the model can continue.
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(tool_result),
                }
            )

    print(
        "\nAgent: I reached the maximum number of tool "
        "rounds. Please try a simpler request."
    )


# --------------------------------------------------
# 6. MAIN AGENT ENTRY POINT
# --------------------------------------------------



def run_agent(user_input: str):
    """Route user input to the appropriate workflow."""

    user_input = user_input.strip()

    if not user_input:
        print("Agent: Please enter a message.")
        return

    order_ids = re.findall(
        r"\bORD[\s-]*\d+\b",
        user_input,
        re.IGNORECASE,
    )

    order_ids = [
        re.sub(r"[\s-]+", "", order_id.upper())
        for order_id in order_ids
    ]

    order_id = order_ids[0] if order_ids else None
    lower_input = user_input.lower()

    # Refund requests take priority over ordinary status requests.
    if "refund" in lower_input:
        if order_id is None:
            print(
                "Agent: Please provide an order ID, "
                "such as ORD1002."
            )
            return

        handle_refund_request(user_input, order_id)
        return

    # Handle simple status questions for exactly one order.
    status_keywords = ("status", "where is", "track")

    if len(order_ids) == 1 and any(
        keyword in lower_input for keyword in status_keywords
    ):
        handle_order_status(order_id)
        return

    # Multi-order and other requests use the LLM tool-calling path.
    run_general_agent(user_input)


# --------------------------------------------------
# 7. RUN THE PROGRAM
# --------------------------------------------------

if __name__ == "__main__":
    print("=" * 50)
    print("       NEXUS AI - TOOL-CALLING AGENT")
    print("=" * 50)
    print("Model:", MODEL)
    print("Type 'exit' to quit.")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if user_input.lower() in {"exit", "quit"}:
                print("Agent: Goodbye!")
                break

            run_agent(user_input)

        except KeyboardInterrupt:
            print("\nAgent: Goodbye!")
            break
