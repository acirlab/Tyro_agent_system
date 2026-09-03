import unittest

from voice_agent.conversation.controller import ConversationController, Intent
from voice_agent.skills.registry import build_default_skill_registry


class _Agent:
    current_task = None

    class skill_registry:
        @staticmethod
        async def match(_text):
            class Skill:
                name = "web_research"

            return Skill()


class _RealSkillAgent:
    current_task = None
    skill_registry = build_default_skill_registry()


class ConversationControllerTests(unittest.IsolatedAsyncioTestCase):
    async def test_classifies_task_controls(self):
        controller = ConversationController(_Agent(), speech_scheduler=None)

        self.assertEqual((await controller.classify_intent("先停一下")).intent, Intent.PAUSE_TASK)
        self.assertEqual((await controller.classify_intent("继续")).intent, Intent.RESUME_TASK)
        self.assertEqual((await controller.classify_intent("取消任务")).intent, Intent.CANCEL_TASK)
        self.assertEqual((await controller.classify_intent("进度怎么样了")).intent, Intent.ASK_PROGRESS)


    async def test_classifies_web_research_start(self):
        controller = ConversationController(_Agent(), speech_scheduler=None)

        result = await controller.classify_intent("帮我查三款手机的区别")

        self.assertEqual(result.intent, Intent.START_TASK)
        self.assertEqual(result.skill_name, "web_research")

    async def test_classifies_academic_research_start(self):
        controller = ConversationController(_RealSkillAgent(), speech_scheduler=None)

        result = await controller.classify_intent("帮我调研科研 agent 的综述论文")

        self.assertEqual(result.intent, Intent.START_TASK)
        self.assertEqual(result.skill_name, "academic_research")


if __name__ == "__main__":
    unittest.main()
