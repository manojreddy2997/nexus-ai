
import asyncio
import json
import sys
from pathlib import Path

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

MODEL = "llama3.2:3b"
MAX_TOOL_CALLS = 3

# Only these tools are permitted.
ALLOWED_TOOLS = {"get_order"}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order",
            "description": "Look up a simulated order by its exact order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID, for example ORD1002",
                    }
                },
                "required": ["order_id"],
            },
        },
    }
]


async def main():
    server_file = Path(__file__).with_name("mcp_server.py")

    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server_file)],
    )

    print("Starting local MCP-powered agent...")
    print("Type 'exit' to quit.\n")

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            available = await session.list_tools()
            available_names = {tool.name for tool in available.tools}

            if "get_order" not in available_names:
                raise RuntimeError("MCP server does not expose get_order")

            while True:
                question = input("You: ").strip()

                if question.lower() in {"exit", "quit"}:
                    break

                if not question:
                    continue

                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are a customer-support assistant. "
                            "Use get_order when the user asks to check an order. "
                            "Never invent order details. Report only information "
                            "supported by the tool result. This tool only looks "
                            "up orders; it cannot approve or process refunds."
                        ),
                    },
                    {"role": "user", "content": question},
                ]

                try:
                    for _ in range(MAX_TOOL_CALLS):
                        response = await asyncio.to_thread(
                            ollama.chat,
                            model=MODEL,
                            messages=messages,
                            tools=TOOLS,
                        )

                        message = response.message
                        messages.append(message)

                        calls = message.tool_calls or []

                        if not calls:
                            print(f"Agent: {message.content}\n")
                            break

                        for call in calls:
                            name = call.function.name
                            args = call.function.arguments

                            # Validate tool name and arguments.
                            if name not in ALLOWED_TOOLS:
                                result = {
                                    "success": False,
                                    "error": "Tool not approved",
                                }
                            elif not isinstance(args, dict) or set(args) != {
                                "order_id"
                            } or not isinstance(args["order_id"], str):
                                result = {
                                    "success": False,
                                    "error": "Invalid tool arguments",
                                }
                            else:
                                result_obj = await session.call_tool(
                                    name,
                                    args,
                                )

                                result = {
                                    "is_error": result_obj.isError,
                                    "content": [
                                        item.text
                                        for item in result_obj.content
                                        if hasattr(item, "text")
                                    ],
                                }

                            messages.append(
                                {
                                    "role": "tool",
                                    "name": name,
                                    "content": json.dumps(result),
                                }
                            )
                    else:
                        print(
                            "Agent: I couldn't finish within the tool-call "
                            "limit. Please try again.\n"
                        )

                except Exception as exc:
                    # Do not print credentials or internal exception details.
                    print(
                        "Agent: The request failed. Check that Ollama and "
                        "the MCP server are available.\n"
                    )
                    print(f"Diagnostic: {type(exc).__name__}\n")


if __name__ == "__main__":
    asyncio.run(main())
