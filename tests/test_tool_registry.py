import unittest

from voice_agent.bootstrap import build_tool_registry


class ToolRegistryTests(unittest.TestCase):
    def test_default_tools_registered(self):
        registry = build_tool_registry()

        self.assertEqual(registry.get("academic_research").name, "academic_research")
        self.assertEqual(registry.get("fake_long_task").name, "fake_long_task")
        self.assertEqual(registry.get("web_search").name, "web_search")

        with self.assertRaises(KeyError):
            registry.get("missing")


if __name__ == "__main__":
    unittest.main()
