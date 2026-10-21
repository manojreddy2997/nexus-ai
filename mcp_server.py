
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Customer Support Tools")

# Simulated data for learning only.
ORDERS = {
    "ORD1002": {"status": "Delayed"},
    "ORD1003": {"status": "Delivered"},
}


@mcp.tool()
def get_order(order_id: str) -> dict:
    """Look up a simulated order by its ID."""
    order = ORDERS.get(order_id)

    if order is None:
        return {
            "success": False,
            "error": "Order not found",
        }

    return {
        "success": True,
        "order_id": order_id,
        "status": order["status"],
    }


if __name__ == "__main__":
    mcp.run()
