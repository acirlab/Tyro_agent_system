import unittest

from PIL import Image

from voice_agent.expression.controller import _TkAvVideoWindow


class ExpressionControllerRenderTests(unittest.TestCase):
    def test_fit_frame_uses_fixed_canvas_size(self):
        window = _TkAvVideoWindow(
            title="test",
            display_size=(640, 368),
            keep_aspect_ratio=True,
        )
        image = Image.new("RGB", (1024, 600), "white")

        fitted = window._fit_frame(image, Image)

        self.assertEqual(fitted.size, (640, 368))

    def test_fit_frame_can_stretch_to_fixed_size(self):
        window = _TkAvVideoWindow(
            title="test",
            display_size=(640, 368),
            keep_aspect_ratio=False,
        )
        image = Image.new("RGB", (1024, 600), "white")

        fitted = window._fit_frame(image, Image)

        self.assertEqual(fitted.size, (640, 368))


if __name__ == "__main__":
    unittest.main()
