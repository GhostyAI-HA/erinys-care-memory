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
        # Token estimate is derived from the actual prompt lengths, so the
        # governed prompt must be genuinely smaller than the raw one.
        self.assertGreater(body["token_reduction_percent"], 0)
        by_mode = {run["mode"]: run["prompt_tokens_estimate"] for run in body["runs"]}
        self.assertLess(by_mode["erinys_qwen"], by_mode["raw_memory"])

    def test_benchmark_exposes_prompt_private_id_proof(self):
        body = benchmark_payload("Draft the care plan.", use_live_qwen=False)
        by_mode = {run["mode"]: run for run in body["runs"]}

        self.assertEqual(by_mode["no_memory"]["prompt_private_ids"], [])
        self.assertGreaterEqual(len(by_mode["raw_memory"]["prompt_private_ids"]), 3)
        self.assertEqual(by_mode["erinys_qwen"]["prompt_private_ids"], [])


if __name__ == "__main__":
    unittest.main()
