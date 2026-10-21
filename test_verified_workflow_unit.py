
import unittest

from test_verified_workflow import (
    get_order,
    check_refund_policy,
    run_workflow,
)


class TestVerifiedWorkflow(unittest.TestCase):

    def test_known_order_is_found(self):
        result = get_order("ORD1002")

        self.assertTrue(result["success"])
        self.assertEqual(
            result["data"]["status"],
            "Delayed",
        )

    def test_missing_order_is_rejected(self):
        result = get_order("ORD9999")

        self.assertFalse(result["success"])
        self.assertEqual(
            result["error"],
            "Order not found",
        )

    def test_unknown_status_is_rejected(self):
        result = check_refund_policy("RefundApproved")

        self.assertFalse(result["success"])

    def test_workflow_uses_verified_status(self):
        result = run_workflow("ORD1002")

        self.assertTrue(result["success"])
        self.assertEqual(
            result["policy"]["status_checked"],
            "Delayed",
        )

    def test_missing_order_stops_workflow(self):
        result = run_workflow("ORD9999")

        self.assertFalse(result["success"])
        self.assertEqual(result["step"], "order_lookup")


if __name__ == "__main__":
    unittest.main(verbosity=2)
