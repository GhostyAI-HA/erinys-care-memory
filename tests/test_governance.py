import unittest

from app.governance import (
    DEFAULT_REQUEST,
    all_memories,
    build_governed_prompt,
    govern_memories,
    selected_memories,
    status_counts,
)


class GovernanceTest(unittest.TestCase):
    def test_private_identifiers_are_blocked_from_governed_prompt(self):
        decisions = govern_memories(all_memories())
        prompt = build_governed_prompt(DEFAULT_REQUEST, decisions)

        self.assertNotIn("SYNTH-INSURANCE-9001", prompt)
        self.assertNotIn("SYNTH-PORTAL-4420", prompt)
        self.assertNotIn("SYNTH-DOOR-1122", prompt)
        self.assertTrue(all(memory.id not in {"m008", "m013", "m014"} for memory in selected_memories(decisions)))

    def test_governance_has_all_four_decision_states(self):
        counts = status_counts(govern_memories(all_memories()))

        self.assertGreaterEqual(counts["selected"], 8)
        self.assertGreaterEqual(counts["blocked"], 4)
        self.assertGreaterEqual(counts["demoted"], 1)
        self.assertGreaterEqual(counts["conflicted"], 1)


if __name__ == "__main__":
    unittest.main()
