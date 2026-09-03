import json
import tempfile
import unittest
from pathlib import Path

from voice_agent.config import load_app_config


class ConfigTests(unittest.TestCase):
    def test_tuning_config_overrides_base_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            base_path = root / "duplex_config.json"
            tuning_path = root / "tuning_config.jsonc"
            base_path.write_text(
                json.dumps(
                    {
                        "pvad": {"activation_threshold": 0.3},
                        "eot": {"threshold": 0.4},
                        "llm": {"provider": "fake"},
                    }
                ),
                encoding="utf-8",
            )
            tuning_path.write_text(
                """
                {
                  // This comment should be ignored by the JSONC loader.
                  "pvad": {
                    "activation_threshold": 0.6,
                    "min_speech_seconds": 0.3
                  },
                  "eot": {
                    "threshold": 0.8
                  }
                }
                """,
                encoding="utf-8",
            )

            config = load_app_config(base_path, tuning_path)

        self.assertEqual(config.pvad.activation_threshold, 0.6)
        self.assertEqual(config.pvad.min_speech_seconds, 0.3)
        self.assertEqual(config.eot.threshold, 0.8)
        self.assertEqual(config.llm.provider, "fake")
        self.assertEqual(config.research.embedding_model, "text-embedding-v4")

    def test_jsonc_loader_keeps_url_strings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            base_path = root / "duplex_config.jsonc"
            base_path.write_text(
                """
                {
                  "llm": {
                    "base_url": "https://example.com/compatible-mode/v1"
                  },
                  /*
                   block comments are also allowed
                  */
                  "pvad": {
                    "min_speech_seconds": 0.25
                  }
                }
                """,
                encoding="utf-8",
            )

            config = load_app_config(base_path, None)

        self.assertEqual(config.llm.base_url, "https://example.com/compatible-mode/v1")
        self.assertEqual(config.pvad.min_speech_seconds, 0.25)

    def test_expression_config_loads_from_tuning_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            tuning_path = root / "tuning_config.jsonc"
            tuning_path.write_text(
                """
                {
                  "expression": {
                    "enabled": false,
                    "video_dir": "expression_video",
                    "default_expression": "neutral",
                    "display_width": 800,
                    "display_height": 460,
                    "keep_aspect_ratio": true,
                    "choose_with_llm": false
                  }
                }
                """,
                encoding="utf-8",
            )

            config = load_app_config(tuning_path=tuning_path)

        self.assertFalse(config.expression.enabled)
        self.assertEqual(config.expression.video_dir, "expression_video")
        self.assertEqual(config.expression.default_expression, "neutral")
        self.assertEqual(config.expression.display_width, 800)
        self.assertEqual(config.expression.display_height, 460)
        self.assertTrue(config.expression.keep_aspect_ratio)
        self.assertFalse(config.expression.choose_with_llm)


if __name__ == "__main__":
    unittest.main()
