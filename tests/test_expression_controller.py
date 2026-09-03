import tempfile
import unittest
from pathlib import Path

from voice_agent.config import ExpressionConfig
from voice_agent.expression.controller import ExpressionVideoController


class ExpressionVideoControllerTests(unittest.TestCase):
    def test_scans_expression_videos_by_filename(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            video_dir = root / "expression_video"
            video_dir.mkdir()
            (video_dir / "neutral.mp4").write_bytes(b"")
            (video_dir / "say-hallo.mp4").write_bytes(b"")
            (video_dir / "ignore.txt").write_text("ignore", encoding="utf-8")

            controller = ExpressionVideoController(
                ExpressionConfig(video_dir=str(video_dir), default_expression="neutral")
            )

        self.assertEqual(controller.available_expressions, ["neutral", "say_hallo"])
        self.assertEqual(controller.normalize_expression("say hallo"), "say_hallo")
        self.assertEqual(controller.normalize_expression("missing"), "neutral")


if __name__ == "__main__":
    unittest.main()
