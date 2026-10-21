
import json
import re
import ollama


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

MODEL = "llama3.2:3b"
MAX_TOOL_ROUNDS = 5

client = ollama.Client()


# --------------------------------------------------
# 2. TOOL 1: LOOK UP AN ORDER
# --------------------------------------------------

def get_order(order_id: str) -> dict:
    """
    Look up an order in our sample database.
    """

    orders = {
        "ORD1002": {
            "order_id": "ORD1002",
            "item": "Mechanical Keyboard",
            "status": "Delayed",
        },
        "ORD1003": {
            "order_id": "ORD1003",
            "item": "Wireless Mouse",
            "status": "Delivered",
        },
    }

    normalized_id = order_id.strip().upper()
    normalized_id = re.sub(r"[\s-]+", "", normalized_id)

    if normalized_id in orders:
        return orders[normalized_id]

    return {
        "error": "Order not found",
        "order_id": normalized_id,
    }


# --------------------------------------------------
# 3. TOOL 2: CHECK REFUND POLICY
# --------------------------------------------------

def check_refund_policy(order_status: str) -> dict:
    """
    Return sample policy guidance based on order status.

    This tool does not approve or process refunds.
    """

    status = order_status.strip().lower()

    if status == "delivered":
        return {
            "policy": (
                "Delivered orders may qualify for a refund review."
            ),
            "next_step": (
                "Check the return window and applicable conditions."
            ),
            "automatic_refund": False,
        }

    if status == "delayed":
        return {
            "policy": (
                "Delayed orders require a support review."
            ),
            "next_step": (
                "Review the delivery delay and applicable policy."
            ),
            "automatic_refund": False,
        }

    return {
        "policy": (
            "Eligibility cannot be determined from this status alone."
        ),
        "next_step": (
            "Ask support to review the order."
        ),
        "automatic_refund": False,
    }


# --------------------------------------------------
# 4. DEFINE TOOLS FOR THE LLM
# --------------------------------------------------

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": (
                "Look up an order using its ID, such as ORD1002."
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
                "Check sample refund guidance using the actual "
                "order status returned by get_order."
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


# Connect each advertised tool to its real Python function.
available_functions = {
    "get_order": get_order,
    "check_refund_policy": check_refund_policy,
}


# --------------------------------------------------
# 5. EXTRACT A VALID ORDER ID
# --------------------------------------------------

def extract_order_id(user_input: str):
    """
    Find IDs like ORD1002, ord1002, or ORD-1002.
    Avoid matching the ordinary word 'order'.
    """

    match = re.search(
        r"\bORD[\s-]*\d+\b",
        user_input,
        re.IGNORECASE,
    )

    if not match:
        return None

    order_id = re.sub(
        r"[\s-]+",
        "",
        match.group(0).upper(),
    )

    return order_id


# --------------------------------------------------
# 6. REFUND WORKFLOW
# --------------------------------------------------

def handle_refund_request(user_input: str, order_id: str):
    """
    Explicitly run the order lookup first, then the policy check.
    This prevents the LLM from skipping the policy tool.
    Do not claim that support will contact the customer
    unless a contact tool actually performs that action.
    """

    print("\n--- Tool round 1: Order lookup ---")

    order_result = get_order(order_id)

    print("Requested tool: get_order")
    print("Arguments:", {"order_id": order_id})
    print("DEBUG: Extracted order ID =", repr(order_id))
    print("Tool result:", json.dumps(order_result, indent=2))

    # Stop if the order does not exist.
    if "error" in order_result:
        print("\nAgent: I couldn't find that order.")
        print("Please check the order ID and try again.")
        return

    print("\n--- Tool round 2: Refund policy ---")

    actual_status = order_result["status"]

    policy_result = check_refund_policy(actual_status)

    print("Requested tool: check_refund_policy")
    print("Arguments:", {"order_status": actual_status})
    print("Tool result:", json.dumps(policy_result, indent=2))

    # Give the LLM verified tool results to summarize.
    messages = [
        {
            "role": "system",
            "content": (
                "You are a careful customer-support assistant. "
                "Answer using only the supplied order and policy "
                "results. Explain the order status, policy guidance, "
                "and next step. Do not invent facts. Do not claim "
                "a refund is approved or processed. The supplied "
                "policy is sample guidance, not a real retailer's "
                "official policy. Keep your answer concise."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Customer request: {user_input}\n\n"
                f"Verified order result:\n"
                f"{json.dumps(order_result, indent=2)}\n\n"
                f"Policy tool result:\n"
                f"{json.dumps(policy_result, indent=2)}\n\n"
                "Explain the result to the customer."
            ),
        },
    ]

    print("\n--- Generating final response ---")

    try:
        response = client.chat(
            model=MODEL,
            messages=messages,
        )

        print("\nAgent:", response.message.content)

    except Exception as error:
        print("\nAgent: The order and policy checks completed.")
        print("Order status:", actual_status)
        print("Policy:", policy_result["policy"])
        print("Next step:", policy_result["next_step"])
        print("LLM error:", error)


# --------------------------------------------------
# 7. GENERAL TOOL-CALLING AGENT
# --------------------------------------------------

def run_general_agent(user_input: str):
    """
    Let the LLM request tools, execute them in Python,
    observe their results, and continue until it finishes.
    """

    messages = [
        {
            "role": "system",
            "content": (
                "You are a customer-support AI agent. "
                "Use tools when you need order information. "
                "Never invent order details. If a tool returns "
                "an error, explain it clearly. You may request "
                "multiple tools when needed. Never claim a refund "
                "was approved or processed. Sample refund guidance "
                "is not an official retailer policy."
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

        except Exception as error:
            print("\nAgent error:", error)
            return

        tool_calls = response.message.tool_calls

        # If the LLM does not request another tool, finish.
        if not tool_calls:
            print("\nAgent:", response.message.content)
            return

        print(f"\n--- Tool round {round_number} ---")

        # Preserve the assistant's tool-call message in history.
        messages.append(response.message)

        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print("Requested tool:", tool_name)
            print("Arguments:", arguments)

            function_to_call = available_functions.get(tool_name)

            if function_to_call is None:
                tool_result = {
                    "error": f"Unknown tool: {tool_name}"
                }
            else:
                try:
                    tool_result = function_to_call(**arguments)
                except Exception as error:
                    tool_result = {
                        "error": str(error)
                    }

            print(
                "Tool result:",
                json.dumps(tool_result, indent=2),
            )

            # Send the result back to the LLM.
            messages.append(
                {
                    "role": "tool",
                    "content": json.dumps(tool_result),
                }
            )

    print(
        "\nAgent: I reached the maximum number of tool rounds. "
        "Please try a simpler request."
    )


# --------------------------------------------------
# 8. MAIN AGENT ENTRY POINT
# --------------------------------------------------

def run_agent(user_input: str):
    user_input = user_input.strip()

    if not user_input:
        print("Agent: Please enter a message.")
        return

    # Refund requests follow a controlled, reliable sequence.
    if "refund" in user_input.lower():
        order_id = extract_order_id(user_input)

        if order_id is None:
            print(
                "Agent: Please provide an order ID, "
                "such as ORD1002."
            )
            return

        handle_refund_request(user_input, order_id)
        return

    # Other requests use the general LLM tool-calling loop.
    run_general_agent(user_input)


# --------------------------------------------------
# 9. RUN THE PROGRAM
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
