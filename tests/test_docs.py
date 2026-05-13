import json
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

    def test_readme_has_safe_search_phrases(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("비공식 토스증권 API", text)
        self.assertIn("TossInvest API", text)
        self.assertIn("Agent Skill", text)
        self.assertIn("공개 웹 페이지", text)
        self.assertIn("공식 API", text)

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

    def test_project_slug_uses_singular_skill_name(self):
        forbidden_terms = [
            "tossinvest-api-" + "skills",
            "tossinvest-api-" + "skills-skill",
            "TossInvest API " + "Skills",
        ]
        checked_paths = [
            ROOT / "README.md",
            ROOT / "SECURITY.md",
            ROOT / "scripts" / "tossinvest_api.py",
        ]
        for path in checked_paths:
            text = path.read_text(encoding="utf-8")
            for term in forbidden_terms:
                with self.subTest(path=path.relative_to(ROOT), term=term):
                    self.assertNotIn(term, text)

    def test_readme_uses_project_native_safety_wording(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("공개 주식/시장 페이지", text)
        self.assertEqual(text.count("read-only"), 1)
        self.assertIn("공개 페이지에서 확인 가능한 read-only 주식/시장 정보 조회", text)
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
        self.assertIn("public read-only stock and market data", frontmatter)
        self.assertIn("\ncompatibility:", frontmatter)
        self.assertNotIn("metadata:\n  compatibility:", frontmatter)

    def test_skill_body_has_positive_when_to_use_guidance(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## When To Use\n", text)
        self.assertLess(text.index("## When To Use"), text.index("## When Not To Use"))
        section = text.split("## When To Use", 1)[1].split("## When Not To Use", 1)[0]
        self.assertIn("public TossInvest", section)
        self.assertIn("quotes", section)
        self.assertIn("read-only browser endpoint", section)

    def test_endpoint_drift_guidance_is_explicit_and_routed(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Lookup Failures\n", skill_text)
        self.assertIn("HTTP 400/404", skill_text)
        self.assertIn("endpoint-drift signal", skill_text)
        self.assertIn("stop using the stale path", skill_text)
        self.assertIn("references/capture-workflow.md", skill_text)
        self.assertIn("Known Observed Pages", skill_text)
        self.assertIn("Do not infer replacement paths", skill_text)

        catalog_text = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        observed_pages = catalog_text.split("## Known Observed Pages", 1)[1]
        self.assertIn("endpoint drift or lookup failures", observed_pages)
        self.assertIn("capture-workflow.md", observed_pages)
        self.assertIn("Do not guess a replacement endpoint", observed_pages)

    def test_openai_skill_metadata_is_localized_and_distributable(self):
        text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "토스증권 Web API"', text)
        self.assertIn("토스증권 공개 주식/시장 데이터", text)
        self.assertIn("A005930", text)
        self.assertIn("조회해줘", text)

        license_text = (ROOT / "LICENSE.txt").read_text(encoding="utf-8")
        self.assertEqual(license_text, (ROOT / "LICENSE").read_text(encoding="utf-8"))

    def test_cookbook_documents_page_level_api_smoke_check(self):
        text = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        self.assertIn("Page API Smoke Checks", text)
        self.assertIn("scripts/page_api_check.py --code A005930", text)
        self.assertIn("order,analytics,news,transaction-status", text)
        self.assertIn("does not call order placement", text)

    def test_eval_prompts_cover_core_script_routes(self):
        text = (ROOT / "references" / "eval-prompts.md").read_text(encoding="utf-8")
        for expected in [
            "scripts/quote.py --code A005930 --ticks 5",
            "scripts/financials.py --code A005930 --kind comprehensive",
            "scripts/page_api_check.py --code A005930",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_cookbook_documents_us_product_source_code_caution(self):
        checked_paths = [
            ROOT / "SKILL.md",
            ROOT / "README.md",
            ROOT / "GEMINI.md",
            ROOT / "references" / "script-cookbook.md",
            ROOT / "references" / "api-catalog.md",
        ]
        for path in checked_paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("US20100311002", text)
                self.assertIn("display ticker", text.lower())
        api_catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        self.assertIn("SPY", api_catalog)
        self.assertIn("HTTP 400", api_catalog)

    def test_gemini_extension_metadata_is_distributable(self):
        config = json.loads((ROOT / "gemini-extension.json").read_text(encoding="utf-8"))
        self.assertEqual(config["name"], "tossinvest-web-api")
        self.assertEqual(config["contextFileName"], "GEMINI.md")
        self.assertRegex(config["version"], r"^\d+\.\d+\.\d+$")

        text = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertIn("TossInvest", text)
        self.assertIn("scripts/stock_chart.py", text)
        self.assertIn("SPX.CBI", text)

    def test_gitignore_covers_python_build_and_local_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in [".venv/", "build/", "dist/", "*.egg-info/", ".coverage", "htmlcov/"]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
