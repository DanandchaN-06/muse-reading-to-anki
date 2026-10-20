import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/muse-reading"
SCRIPT = SKILL / "scripts/muse.py"
spec = importlib.util.spec_from_file_location("muse", SCRIPT)
muse = importlib.util.module_from_spec(spec)
spec.loader.exec_module(muse)


class MuseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def json(self, name, data):
        path = self.folder / name
        muse.write_json(path, data)
        return path

    def run_cli(self, *args, ok=True):
        result = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPT), *map(str, args)], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        return result

    def test_diff_normalization_preserves_phrases(self):
        target = self.folder / "target.txt"
        exclude = self.folder / "exclude.txt"
        target.write_text("Worldly\nworldly\nDON’T\ntake  off\nCuriosity\n", encoding="utf-8")
        exclude.write_text("don't\nTAKE OFF\n", encoding="utf-8")
        output = self.folder / "diff.json"
        self.run_cli("vocab", "--target", target, "--exclude", exclude, "--out", output)
        result = muse.read_json(output)
        self.assertEqual(result["words"], ["curiosity", "worldly"])
        self.assertEqual(result["target"]["entries"], 5)
        self.assertEqual(result["target"]["unique_normalized"], 4)

    def test_supplied_wordlists_reproduce_1174(self):
        raw = SKILL / "assets/wordlists/raw"
        target, _ = muse.words_file(raw / "cet6.txt")
        cet4, _ = muse.words_file(raw / "cet4.txt")
        gaokao, _ = muse.words_file(raw / "gaokao.txt")
        self.assertEqual(len(target - (cet4 | gaokao)), 1174)
        self.assertEqual(sorted(target - (cet4 | gaokao)), muse.read_json(raw.parent / "cet6-exclusive.json")["words"])

    def test_reader_custom_length_and_html_escaping(self):
        sentence = "Alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar."
        data = {"title": "<script>alert(1)</script>", "paragraphs": [sentence],
                "vocab": {w.lower(): {"pos": "n.", "zh": "<img src=x onerror=alert(1)>", "ex": sentence} for w in muse.WORD.findall(sentence)}}
        source = self.json("article.json", data)
        dest = self.folder / "reader.html"
        self.run_cli("reader", "--article", source, "--out", dest, ok=False)
        self.run_cli("reader", "--article", source, "--out", dest, "--min-words", 10, "--max-words", 30)
        rendered = dest.read_text(encoding="utf-8")
        self.assertNotIn("<script>alert(1)</script>", rendered)
        self.assertNotIn("<img src=x onerror=alert(1)>", rendered)
        self.assertIn("\\u003cimg", rendered)
        data["source_url"] = "javascript:alert(1)"
        self.json("article.json", data)
        self.run_cli("reader", "--article", source, "--out", dest, "--demo", ok=False)

    def test_cards_original_sentence_dedupe_and_highlight(self):
        data = muse.read_json(SKILL / "assets/examples/cards.json")
        data["cards"].append({**data["cards"][0], "Word": "WORLDLY"})
        source = self.json("cards.json", data)
        output = self.folder / "cards"
        article = SKILL / "assets/examples/article.json"
        self.run_cli("cards", "--input", source, "--article", article, "--out-dir", output)
        notes = muse.read_json(output / "notes.json")
        report = muse.read_json(output / "report.json")
        self.assertEqual(len(notes), 2)
        self.assertEqual(report["skipped_duplicates"], ["WORLDLY"])
        self.assertIn("<b>worldly</b>", notes[0]["fields"]["Example"])
        self.assertIn("muse::date::2026-10-20", notes[0]["tags"])
        self.assertEqual(report["network_actions"], 0)
        data["cards"][0]["Example"] = "A fabricated worldly sentence."
        self.json("cards.json", data)
        self.run_cli("cards", "--input", source, "--article", article, "--out-dir", output, ok=False)
        data["cards"][0]["ExampleOrigin"] = "ai_supplement"
        self.json("cards.json", data)
        self.run_cli("cards", "--input", source, "--article", article, "--out-dir", output)
        self.assertIn("muse::ai_supplement", muse.read_json(output / "notes.json")[0]["tags"])


if __name__ == "__main__":
    unittest.main()
