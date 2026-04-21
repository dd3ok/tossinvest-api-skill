import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationPromptTests(unittest.TestCase):
    def test_prompts_do_not_depend_on_dollar_skill_selectors(self):
        checked_paths = [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "eval-prompts.md",
        ]
        for path in checked_paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, re.escape("$tas"))
                self.assertNotRegex(text, re.escape("$twa"))
                self.assertNotRegex(text, re.escape("$tossinvest-web-api"))

    def test_skill_keeps_descriptive_canonical_name(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("\nname: tossinvest-web-api\n", frontmatter)
        self.assertNotIn("\nname: twa\n", frontmatter)

    def test_readme_describes_natural_language_routing(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("TossInvest/토스증권을 언급한 자연어 요청", text)
        self.assertNotIn("description과 맞으면", text)

    def test_docs_do_not_name_third_party_trading_tools(self):
        forbidden_terms = ["tossinvest" + "-cli", "toss" + "ctl"]
        checked_paths = [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "references" / "safety-rules.md",
            ROOT / "references" / "api-catalog.md",
            ROOT / "SECURITY.md",
        ]
        for path in checked_paths:
            text = path.read_text(encoding="utf-8").lower()
            for term in forbidden_terms:
                with self.subTest(path=path.relative_to(ROOT), term=term):
                    self.assertNotIn(term, text)

    def test_readme_uses_project_native_safety_wording(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("공개 주식/시장 페이지", text)
        self.assertIn("막힌 요청", text)
        self.assertIn("현재 공개 웹 페이지", text)
        self.assertIn("서비스 보호", text)
        self.assertNotIn("rate limit", text.lower())
        self.assertNotRegex(text.lower(), r"403|429|anti-bot|fan-out|polling loop")

    def test_technical_safety_docs_warn_about_rate_limits_and_aggressive_polling(self):
        checked_paths = [
            ROOT / "SKILL.md",
            ROOT / "references" / "safety-rules.md",
            ROOT / "SECURITY.md",
        ]
        for path in checked_paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8").lower()
                self.assertIn("rate limit", text)
                self.assertRegex(text, r"429|403")
                self.assertRegex(text, r"polling|반복 호출")

    def test_skill_frontmatter_uses_standard_compatibility_field(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"\ndescription: Use when ")
        self.assertIn("\ncompatibility:", frontmatter)
        self.assertNotIn("metadata:\n  compatibility:", frontmatter)

    def test_gitignore_covers_python_build_and_local_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in [".venv/", "build/", "dist/", "*.egg-info/", ".coverage", "htmlcov/"]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
