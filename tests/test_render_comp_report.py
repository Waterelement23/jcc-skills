import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "jcc-meta-researcher" / "scripts" / "render_comp_report.py"
SAMPLE = ROOT / "jcc-meta-researcher" / "assets" / "sample_woodling_corki.json"


class VisualReportRendererTest(unittest.TestCase):
    def render_sample(self) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "report.html"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--input", str(SAMPLE), "--output", str(output)],
                cwd=ROOT,
                check=True,
                text=True,
                capture_output=True,
            )
            return output.read_text(encoding="utf-8")

    def test_visual_report_contains_approved_layout_sections(self):
        html = self.render_sample()

        self.assertIn("木灵飞机", html)
        self.assertIn("后期成型 · 8人口", html)
        self.assertIn("推荐海克斯", html)
        self.assertIn("推荐星神", html)
        self.assertIn("优先装备", html)
        self.assertNotIn("复制阵容码", html)
        self.assertNotIn(">前期<", html)
        self.assertNotIn(">中期<", html)

    def test_visual_report_uses_current_season_square_avatars_and_real_item_icons(self):
        html = self.render_sample()

        self.assertIn("raw.communitydragon.org", html)
        self.assertIn("tft17_corki_square.tft_set17.png", html.lower())
        self.assertNotIn("img/champion/Corki.png", html)
        self.assertNotIn("splash_centered", html)
        self.assertIn("TFT_Item_LastWhisper.png", html)
        self.assertIn("TFT_Item_Deathblade.png", html)
        self.assertIn("Willbreaker_TFT_item.png", html)
        self.assertNotIn("item-fallback", html)

    def test_visual_report_keeps_unit_names_off_board_but_accessible(self):
        html = self.render_sample()

        self.assertNotIn("unit-name", html)
        self.assertIn('title="库奇 ★★★：轻语 / 杀人剑 / 破防者"', html)
        self.assertIn('alt="库奇"', html)
        self.assertIn('alt="轻语"', html)

    def test_visual_report_radar_labels_are_embedded_in_chart(self):
        html = self.render_sample()

        for label in ["成型难度", "成型战力", "经济要求", "装备要求", "运营难度", "抗同行", "烂分能力", "吃鸡上限"]:
            self.assertIn(label, html)
        self.assertIn("radar-chart", html)
        self.assertNotIn("score-list", html)

    def test_sample_data_is_valid_json(self):
        data = json.loads(SAMPLE.read_text(encoding="utf-8"))

        self.assertEqual(data["name"], "木灵飞机")
        self.assertEqual(len(data["board"]["rows"]), 4)
        self.assertEqual(len(data["ratings"]), 8)


if __name__ == "__main__":
    unittest.main()
