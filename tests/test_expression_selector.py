import unittest

from voice_agent.expression.selector import ExpressionSelector


class _BadLLM:
    async def generate(self, _messages):
        return "not_a_known_expression"


class ExpressionSelectorTests(unittest.IsolatedAsyncioTestCase):
    async def test_falls_back_when_llm_returns_unknown_expression(self):
        selector = ExpressionSelector(
            llm=_BadLLM(),
            available_expressions=["neutral", "happy", "sad", "say_hallo"],
            choose_with_llm=True,
        )

        expression = await selector.select("你好", "speech")

        self.assertEqual(expression, "say_hallo")

    async def test_can_disable_llm_selection_and_use_rules(self):
        selector = ExpressionSelector(
            llm=_BadLLM(),
            available_expressions=["neutral", "happy", "sad"],
            choose_with_llm=False,
        )

        expression = await selector.select("任务处理完成。", "speech")

        self.assertEqual(expression, "happy")


if __name__ == "__main__":
    unittest.main()
