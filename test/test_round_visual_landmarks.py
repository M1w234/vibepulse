#!/usr/bin/env python3
"""Raster contracts for the 466x466 circular VibePulse profile."""

from __future__ import annotations

import math
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
WHITE = (255, 255, 255)
CLAUDE = (217, 119, 87)
MUTED = (146, 152, 162)
DIM = (92, 104, 123)
RED = (229, 72, 77)


class RoundVisualLandmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="vibepulse-round-raster-")
        cls.capture_dir = Path(cls.temp.name)
        subprocess.run(
            [
                "cmake", "-S", "sim", "-B", "sim/build-round",
                "-G", "Ninja", "-DTORGET_SIM_PROFILE=round-1.75c",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        subprocess.run(
            ["cmake", "--build", "sim/build-round"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        subprocess.run(
            [str(ROOT / "sim/build-round/torget-sim"),
             "--vibepulse-static-qa"],
            cwd=ROOT,
            env={
                **os.environ,
                "SDL_VIDEODRIVER": "dummy",
                "TORGET_CAPTURE_DIR": str(cls.capture_dir),
            },
            check=True,
            text=True,
            capture_output=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def image(self, stem):
        path = self.capture_dir / f"torget-{stem}.bmp"
        self.assertTrue(path.is_file(), f"missing round capture: {path.name}")
        image = Image.open(path).convert("RGB")
        self.assertEqual(image.size, (466, 466))
        return image

    @staticmethod
    def count(image, box, color):
        return sum(pixel == color
                   for pixel in image.crop(box).get_flattened_data())

    def test_quota_hero_keeps_ink_away_from_the_round_edge(self):
        image = self.image("vibepulse-claude-fable")
        points = [
            (x, y)
            for y in range(126, 286)
            for x in range(466)
            if image.getpixel((x, y)) == WHITE
        ]
        self.assertGreater(len(points), 10_000)
        self.assertGreaterEqual(min(x for x, _ in points), 60)
        self.assertLessEqual(max(x for x, _ in points), 406)
        # Independent geometric proof: the hero ink has at least 12px radial
        # clearance, so clipping cannot masquerade as a valid bounding box.
        self.assertTrue(all(math.hypot(x - 233, y - 233) <= 221
                            for x, y in points))

    def test_question_card_has_three_separate_text_bands(self):
        image = self.image("vibepulse-needs-you-question")
        self.assertGreater(self.count(image, (50, 176, 416, 192), CLAUDE), 40)
        self.assertGreater(self.count(image, (50, 193, 416, 217), WHITE), 300)
        self.assertGreater(self.count(image, (50, 217, 416, 234), MUTED), 100)

    def test_question_actions_fit_the_contracting_bottom_chord(self):
        image = self.image("vibepulse-needs-you-question")
        # The filled primary target is the approved 90px tall.
        primary = [image.getpixel((60, y)) == CLAUDE
                   for y in range(220, 350)]
        best = run = 0
        for active in primary:
            run = run + 1 if active else 0
            best = max(best, run)
        self.assertGreaterEqual(best, 90)
        # The secondary target ends before the last narrow 34px of the circle,
        # and the removed terminal footer cannot reoccupy that unsafe band.
        self.assertGreater(self.count(image, (126, 342, 340, 432), DIM), 500)
        self.assertEqual(self.count(image, (0, 433, 466, 450), DIM), 0)

    def test_approval_secondary_labels_are_readable_inside_their_targets(self):
        image = self.image("vibepulse-needs-you-approval")
        self.assertGreater(self.count(image, (140, 375, 218, 412), RED), 35)
        self.assertGreater(self.count(image, (245, 375, 331, 412), MUTED), 45)

    def test_private_handoff_is_inside_the_circle(self):
        image = self.image("vibepulse-needs-you-private")
        self.assertGreater(self.count(image, (90, 390, 376, 420), DIM), 120)
        self.assertEqual(self.count(image, (0, 425, 466, 450), DIM), 0)

    def test_all_key_states_respect_the_physical_circle(self):
        for stem in (
            "vibepulse-claude-fable",
            "vibepulse-needs-you-question",
            "vibepulse-needs-you-question-long",
            "vibepulse-needs-you-approval",
            "vibepulse-needs-you-private",
            "vibepulse-needs-you-payoff",
        ):
            with self.subTest(stem=stem):
                image = self.image(stem)
                for y in range(466):
                    for x in range(466):
                        if math.hypot(x - 233, y - 233) > 234.5:
                            self.assertEqual(image.getpixel((x, y)), (0, 0, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
