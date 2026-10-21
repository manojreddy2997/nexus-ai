
def validate_order_id(order_id):
    if not isinstance(order_id, str):
        return False, "Order ID must be text"

    normalized_id = order_id.strip().upper()

    if not normalized_id:
        return False, "Order ID cannot be empty"

    if not normalized_id.startswith("ORD"):
        return False, "Order ID must start with ORD"

    digits = normalized_id[3:]

    if not digits.isdigit():
        return False, "Order ID must contain digits after ORD"

    return True, normalized_id


# Test 1: Valid ID
print("TEST 1:", validate_order_id("ORD1002"))

# Test 2: Empty ID
print("TEST 2:", validate_order_id("   "))

# Test 3: Invalid format
print("TEST 3:", validate_order_id("ABC1002"))

# Test 4: Non-text input
print("TEST 4:", validate_order_id(None))
