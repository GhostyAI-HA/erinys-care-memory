import os
import tempfile
import unittest

from app import governance


class RuntimeMemoryPersistenceTest(unittest.TestCase):
    """Covers the README/deploy claim: save -> rerun (answer changes) -> reset."""

    def setUp(self):
        self._tmp = tempfile.mkdtemp()
        self._prev = os.environ.get("ERINYS_APP_DATA_DIR")
        os.environ["ERINYS_APP_DATA_DIR"] = self._tmp
        governance.reset_runtime_memories()

    def tearDown(self):
        if self._prev is None:
            os.environ.pop("ERINYS_APP_DATA_DIR", None)
        else:
            os.environ["ERINYS_APP_DATA_DIR"] = self._prev

    def test_saved_memory_persists_is_selected_then_resets(self):
        saved = governance.save_runtime_memory(
            "Ask reception to arrange wheelchair assistance at the north entrance."
        )

        # Persists across a fresh read (simulates reload).
        reloaded_ids = [m.id for m in governance.load_runtime_memories()]
        self.assertIn(saved.id, reloaded_ids)

        # A saved runtime memory is selected, so the governed answer changes.
        decisions = governance.govern_memories(governance.all_memories())
        selected_ids = [m.id for m in governance.selected_memories(decisions)]
        self.assertIn(saved.id, selected_ids)

        # Reset clears it.
        governance.reset_runtime_memories()
        self.assertEqual(governance.load_runtime_memories(), [])


if __name__ == "__main__":
    unittest.main()
