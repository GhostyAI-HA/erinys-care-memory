import unittest

from app.server import benchmark_payload, health_payload


class ApiPayloadTest(unittest.TestCase):
    def test_health_endpoint_payload(self):
        body = health_payload()
        self.assertTrue(body["ok"])
        self.assertIn("/run/benchmark", body["endpoints"])

    def test_benchmark_payload_uses_demo_fallback_without_key(self):
        body = benchmark_payload("Draft the care plan.", use_live_qwen=False)
        self.assertEqual(len(body["runs"]), 3)
        self.assertGreaterEqual(body["governance_counts"]["blocked"], 4)
        self.assertGreaterEqual(body["token_reduction_percent"], 60)


if __name__ == "__main__":
    unittest.main()
