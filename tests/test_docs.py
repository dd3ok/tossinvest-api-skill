import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationPromptTests(unittest.TestCase):
    def test_prompts_do_not_depend_on_dollar_skill_selectors(self):
        checked_paths = [
            ROOT / ".github" / "RELEASE_CHECKLIST.md",
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

    def test_readme_install_root_matches_skill_name(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("name: tossinvest-web-api", text)
        self.assertIn("최종 skill root를 `tossinvest-web-api`", text)

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

    def test_docs_do_not_reference_personal_project_details(self):
        forbidden_hashes = {
            "08f65dba38b29733214a82715b4698d02b322983d08b564840acdc1dfb600068",
            "24f0de806060dfed92e061d322773330d9bc67cfef69f17b6641bfda449cb09a",
            "5bf88f4aea2c997524cdc6746f867cb6508fb1e3c6467f8c5e044f9e0cd20b6f",
            "9201ffb5facc764a4ae1aae8f6cb99b73d8b0645085d1a389e42cbddbf51f8a2",
            "d099b4d5fb4911ab2f6f689978b1e1d2b1d0b1e2710ea9b18abaf5b08e36904d",
            "da4b260c37d6cb1c114176c82132dcc91ca19fe0fc75cecf6770c3fabdb399f6",
            "e237cb2a2eb43c0c30c6631fe52dbe6bdc496312368abf2879da3645b2d85b1c",
        }
        checked_paths = [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "GEMINI.md",
            ROOT / "references" / "api-catalog.md",
            ROOT / "references" / "response-notes.md",
            ROOT / "references" / "script-cookbook.md",
            ROOT / "references" / "safety-rules.md",
            ROOT / ".github" / "RELEASE_CHECKLIST.md",
        ]
        for path in checked_paths:
            text = path.read_text(encoding="utf-8").lower()
            tokens = re.findall(r"[a-z0-9_.-]+", text)
            candidates = set(tokens)
            candidates.update(f"{left}_{right}" for left, right in zip(tokens, tokens[1:]))
            candidates.update(f"{left}.{right}" for left, right in zip(tokens, tokens[1:]))
            for candidate in candidates:
                digest = hashlib.sha256(candidate.encode()).hexdigest()
                with self.subTest(path=path.relative_to(ROOT), digest=digest):
                    self.assertNotIn(digest, forbidden_hashes)

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

    def test_skill_frontmatter_uses_validator_compatible_fields(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertRegex(frontmatter, r"\ndescription: Use ")
        description = next(
            line.removeprefix("description: ")
            for line in frontmatter.splitlines()
            if line.startswith("description: ")
        )
        self.assertLessEqual(len(description), 200)
        self.assertIn("public, read-only TossInvest", description)
        for broad_trigger in [
            "AI signals",
            "accounts",
            "credit",
            "investment advice",
            "lending trading",
            "login",
            "short-selling",
            "trading",
            "CFD",
            "VWAP.KRW-*",
        ]:
            with self.subTest(broad_trigger=broad_trigger):
                self.assertNotIn(broad_trigger, frontmatter)
        self.assertNotIn("\ncompatibility:", frontmatter)

    def test_skill_routes_disambiguate_financial_and_signal_labels(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("UI-provided home AI-summary label fields", text)
        self.assertIn("Do not interpret these labels as buy/sell signals", text)
        self.assertIn("public transaction-status page datasets only", text)
        self.assertIn("`scripts/trading_trend.py --type credit`", text)
        self.assertIn("account credit limits", text)
        self.assertIn("margin eligibility", text)
        self.assertIn("leverage decisions", text)

    def test_gemini_context_mirrors_financial_and_signal_guards(self):
        text = (ROOT / "GEMINI.md").read_text(encoding="utf-8")
        self.assertIn("UI-provided home AI-summary label fields", text)
        self.assertIn("not buy/sell signals", text)
        self.assertIn("public transaction-status page datasets only", text)
        self.assertIn("credit|lending-trading|short-selling-trend|cfd", text)
        self.assertIn(
            "not account limits, orderability, leverage decisions, or trading advice", text
        )

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
        self.assertIn("## Known Observed Pages", catalog_text)
        observed_pages = catalog_text.split("## Known Observed Pages", 1)[1]
        self.assertIn("endpoint drift or lookup failures", observed_pages)
        self.assertIn("capture-workflow.md", observed_pages)
        self.assertIn("Do not guess a replacement endpoint", observed_pages)

    def test_openai_skill_metadata_is_localized_and_distributable(self):
        text = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "토스증권 Web API"', text)
        self.assertIn("토스증권 공개 주식·시장·지수·랭킹·스크리너 데이터", text)
        self.assertIn("A005930", text)
        self.assertIn("조회해줘", text)

        license_text = (ROOT / "LICENSE.txt").read_text(encoding="utf-8")
        self.assertEqual(license_text, (ROOT / "LICENSE").read_text(encoding="utf-8"))

    def test_ci_and_release_docs_use_singular_skill_wording(self):
        ci_text = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("name: TossInvest API Skill CI", ci_text)
        self.assertNotIn("name: TossInvest API Skills CI", ci_text)

        checklist = (ROOT / ".github" / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
        self.assertIn("agents/openai.yaml", checklist)
        self.assertIn("consistent with `SKILL.md`", checklist)
        self.assertIn("description starts with `Use`", checklist)
        self.assertIn("sensitive query/body keys", checklist)
        self.assertIn("exact allowlist", checklist)
        self.assertIn("natural TossInvest/토스증권 language", checklist)
        self.assertIn("do not", checklist)
        self.assertIn("depend on `$...` skill selectors or aliases", checklist)
        self.assertNotIn("matches the public skill name", checklist)
        self.assertNotIn("description starts with `Use when`", checklist)
        self.assertNotIn(
            "Public prompt examples use `$tossinvest-web-api`, not aliases.", checklist
        )

    def test_readme_documents_current_codex_skill_paths(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("$HOME/.agents/skills", text)
        self.assertIn(".agents/skills/tossinvest-web-api/", text)
        self.assertNotIn(".co" + "dex/skills", text)

    def test_readme_distinguishes_gemini_context_from_agent_skills(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("extension-level context", text)
        self.assertIn("skills/<name>/SKILL.md", text)
        self.assertFalse((ROOT / "skills").exists())

    def test_skill_uses_single_us_stock_candle_caution(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("For US stock candles"), 1)
        self.assertIn("Use `day:1` or `min:1`", text)

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

    def test_release_checklist_tracks_versioned_release_metadata(self):
        checklist = (ROOT / ".github" / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
        self.assertIn("gemini-extension.json", checklist)
        self.assertIn("matching Git tag", checklist)
        self.assertIn("GitHub release", checklist)

    def test_gitignore_covers_python_build_and_local_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in [".venv/", "build/", "dist/", "*.egg-info/", ".coverage", "htmlcov/"]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
