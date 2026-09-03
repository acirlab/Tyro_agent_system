import unittest

from voice_agent.infrastructure.event_bus import EventBus


class EventBusTests(unittest.IsolatedAsyncioTestCase):
    async def test_event_bus_routes_named_and_wildcard_events(self):
        bus = EventBus()
        named = bus.subscribe("ToolStarted")
        wildcard = bus.subscribe("*")

        await bus.publish("ToolStarted", tool_name="web_search")

        self.assertEqual((await named.get()).payload["tool_name"], "web_search")
        self.assertEqual((await wildcard.get()).type, "ToolStarted")


if __name__ == "__main__":
    unittest.main()
