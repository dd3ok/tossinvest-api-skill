import hashlib
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DocumentationPromptTests(unittest.TestCase):
    def test_public_prompts_do_not_depend_on_dollar_skill_selectors(self):
        checked_paths = [
            ROOT / ".github" / "RELEASE_CHECKLIST.md",
            ROOT / "README.md",
            ROOT / "SKILL.md",
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

    def test_docs_distinguish_official_openapi_boundary(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        safety = (ROOT / "references" / "safety-rules.md").read_text(encoding="utf-8")
        boundary = (ROOT / "references" / "official-openapi-boundary.md").read_text(
            encoding="utf-8"
        )

        for name, text in [
            ("SKILL.md", skill),
            ("safety-rules.md", safety),
            ("official-openapi-boundary.md", boundary),
        ]:
            normalized = " ".join(text.split())
            with self.subTest(file=name):
                self.assertIn("official", normalized.lower())
                self.assertIn("Open API", normalized)
                self.assertIn("IP registration", normalized)

        self.assertIn("공식 Open API", readme)
        self.assertIn("IP 등록", readme)
        self.assertIn("does not require official Open API app setup", skill)
        self.assertIn("OAuth credentials", safety)
        self.assertIn("X-Tossinvest-Account", boundary)
        self.assertIn("MARKET_DATA_CHART", boundary)
        self.assertIn("X-RateLimit-Limit", boundary)
        self.assertIn("developers.tossinvest.com/docs", boundary)
        self.assertIn("did not list a JWKS operation", boundary)
        self.assertIn("reference-only operational context", boundary)
        self.assertIn("not a throughput allowance for this skill", boundary)
        self.assertIn("do not probe unpublished limits", boundary)
        self.assertIn("not operating budgets for these undocumented web endpoints", safety)

    def test_docs_do_not_name_third_party_trading_tools(self):
        forbidden_terms = ["tossinvest" + "-cli", "toss" + "ctl"]
        checked_paths = [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "references" / "safety-rules.md",
            ROOT / "references" / "official-openapi-boundary.md",
            ROOT / "references" / "api-catalog.md",
            ROOT / "SECURITY.md",
        ]
        for path in checked_paths:
            text = path.read_text(encoding="utf-8").lower()
            for term in forbidden_terms:
                with self.subTest(path=path.relative_to(ROOT), term=term):
                    self.assertNotIn(term, text)

    def test_docs_do_not_reference_personal_project_details(self):
        # Hashes are sha256 of lowercase normalized candidate strings.
        forbidden_hashes = {
            "08f65dba38b29733214a82715b4698d02b322983d08b564840acdc1dfb600068",
            "0f940c2ea4695d33268378481be8b8525425c577210b0775f99000405a03343e",
            "1a83e48af686640449c1286f1912cce74648ceab4c8b749e61593a29a77a3be1",
            "24f0de806060dfed92e061d322773330d9bc67cfef69f17b6641bfda449cb09a",
            "28f85741a9a947b99c827eccf5610eda140e7e8b38716e29486a883938ac4e76",
            "356f5a9a247726d676d84f1dda7f725a02a010c71e8b9c2f12859adce8971e05",
            "38dfbf773faa9dbad69b092edbd5a5cea457dea952b35b925095c7dfef62c2ab",
            "434e291fe59f7af28f7fd75ae87ca6e114012f4d1c31b138d4561e748c342334",
            "44663d62ea789e6407dca577766961e39050698e9e3472263e40d06b2a597190",
            "4d04c38646ad9901122b70a9ecb7884f0bbd5ea854008f8cc17988bbaa86a533",
            "5bf88f4aea2c997524cdc6746f867cb6508fb1e3c6467f8c5e044f9e0cd20b6f",
            "60fa13b843648523dd7e250cd0dd6432bdbee338a9edd5c45f75c46b1de4f70b",
            "6696527e9bb2eb0280b0806def9306b8df425c71286e61784bc32119ec1dbe2b",
            "66bc5ff1cc545a1f91077417caceff5ec0a2d19cbc12a7329e558d8c82bc4759",
            "8ab4c98f2a766496cae5e3a12fe455677fec529c19438dd360dfa33840c32e64",
            "9201ffb5facc764a4ae1aae8f6cb99b73d8b0645085d1a389e42cbddbf51f8a2",
            "a034e770841f870f21a9f31571518dd2a4ce5188c4a21987f3dc8052ca99d501",
            "a39c1f95756e00e22f5a0a25ec85c36df0c9233cf7fd8bf56babf3c2c03782e0",
            "aaa2fef426ad29ca5e254d481eae532103829d71804aac78ee46fc18f9964e10",
            "b7aac842458d20b4b6b62ac568e7adafc82dfdb092d61451d7a92f15c2a47d46",
            "cc96657ee86f67829f204458910212e545dc81bc5aa32eba628e533f092a4c6b",
            "d099b4d5fb4911ab2f6f689978b1e1d2b1d0b1e2710ea9b18abaf5b08e36904d",
            "d17050217ec46731c16900581d9d9ffd6ec1416d1a3b693657ce061668231698",
            "d45abc86b74581d0550aa6f8c10175bb7ea3d76af38fa759c0fd7a6ed4363136",
            "d75d504ffbff63759a5018386a9f6248d61f147b9b516dbea53273f8839ca128",
            "da4b260c37d6cb1c114176c82132dcc91ca19fe0fc75cecf6770c3fabdb399f6",
            "dcdbef3dc385bab7b104efbd146b2ebaa9328ac1ae71021667823a4aae284377",
            "de600e2490679134512ae571eda84a5786c5d266b3601d5f9cb38efa30001daa",
            "e237cb2a2eb43c0c30c6631fe52dbe6bdc496312368abf2879da3645b2d85b1c",
            "eea56bcbf23f5e355dc638bdc182ac316da3a68ebc181758c7520e767f3a9d2d",
            "f9c4b99c75b89270841badfd6f09e1557f62d32278b28539b829242876a7da30",
        }
        checked_paths = [
            ROOT / "README.md",
            ROOT / "SKILL.md",
            ROOT / "SECURITY.md",
            ROOT / "agents" / "openai.yaml",
            ROOT / "references" / "api-catalog.md",
            ROOT / "references" / "capture-workflow.md",
            ROOT / "references" / "eval-prompts.md",
            ROOT / "references" / "official-openapi-boundary.md",
            ROOT / "references" / "response-notes.md",
            ROOT / "references" / "script-cookbook.md",
            ROOT / "references" / "safety-rules.md",
            ROOT / "references" / "websocket-api-reference.md",
            ROOT / ".github" / "RELEASE_CHECKLIST.md",
        ]
        for path in checked_paths:
            text = path.read_text(encoding="utf-8").lower()
            tokens = re.findall(r"[a-z0-9]+", text)
            candidates = set(tokens)
            for size in range(2, 5):
                for index in range(len(tokens) - size + 1):
                    window = tokens[index : index + size]
                    for separator in (" ", "_", "-", "."):
                        candidates.add(separator.join(window))
            matched_digests = []
            for candidate in candidates:
                digest = hashlib.sha256(candidate.encode()).hexdigest()
                if digest in forbidden_hashes:
                    matched_digests.append(digest)
            self.assertFalse(
                matched_digests,
                "Forbidden hashed project-detail digests found in "
                f"{path.relative_to(ROOT)}: {sorted(set(matched_digests))}",
            )

    def test_project_slug_uses_singular_skill_name(self):
        forbidden_terms = [
            "tossinvest-api-" + "skills",
            "tossinvest-api-" + "skills-skill",
            "TossInvest API " + "Skills",
        ]
        checked_paths = [
            ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
            ROOT / "README.md",
            ROOT / "SECURITY.md",
            ROOT / "scripts" / "tossinvest_api.py",
        ]
        for path in checked_paths:
            text = path.read_text(encoding="utf-8")
            for term in forbidden_terms:
                with self.subTest(path=path.relative_to(ROOT), term=term):
                    self.assertNotIn(term, text)

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
        self.assertRegex(frontmatter, r"\ndescription: Use this skill when ")
        description = next(
            line.removeprefix("description: ")
            for line in frontmatter.splitlines()
            if line.startswith("description: ")
        )
        self.assertLessEqual(len(description), 1024)
        self.assertIn("public, read-only TossInvest", description)
        self.assertIn("crypto-like index pages", description)
        self.assertIn("public endpoint re-verification", description)
        self.assertIn("Do not use for login", description)
        self.assertIn("calendar", description)
        self.assertIn("news", description)
        self.assertIn("filings", description)
        self.assertIn("financials", description)
        self.assertNotIn("\ncompatibility:", frontmatter)
        body = text.split("---", 2)[2]
        self.assertIn("Requires Python 3.10+ and network access.", body)

    def test_websocket_api_reference_documents_protocol_schema_and_safety(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        websocket = (ROOT / "references" / "websocket-api-reference.md").read_text(encoding="utf-8")
        safety = (ROOT / "references" / "safety-rules.md").read_text(encoding="utf-8")
        capture = (ROOT / "references" / "capture-workflow.md").read_text(encoding="utf-8")
        eval_prompts = (ROOT / "references" / "eval-prompts.md").read_text(encoding="utf-8")
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")

        self.assertIn("references/websocket-api-reference.md", skill)
        self.assertFalse((ROOT / "references" / "websocket-observations.md").exists())
        self.assertIn("unofficial WebSocket API reference", skill)
        for expected in [
            "### 공개 HTTP 기반 조회",
            "종목 요약과 현재가·호가 스냅샷·장중 체결 틱 조회",
            "### 차트 및 로컬 계산",
            "### WebSocket API",
            "- 로그인하지 않은 공개 페이지에서 확인되는 실시간 체결가·지수·가상자산형 지수의 동작 방식 설명",
            "- 서버 정보, STOMP 연결·구독 과정, destination",
            "- `scripts/websocket_prices.py`로 공개 국내·미국 주식 체결, 지수, 가상자산형 지수 이벤트",
            "- 연결에는 공개 브라우저 세션이 발급한 임시 게스트 연결 메타데이터가 필요함.",
            "- 국내·미국 top100은 단일 WebSocket 랭킹 채널이 아니라 10초 주기 HTTP 랭킹 snapshot",
            "- 호가·예상체결·종목상태 채널은 공개 시장 데이터만 실험적으로 허용하며",
            "- 현재가·호가 스냅샷·장중 체결 틱은 `scripts/quote.py`에서 제한된 공개 HTTP 읽기 전용 방식으로 조회",
            "- 상세 내용은 [비공식 WebSocket API 레퍼런스](references/websocket-api-reference.md) 참고",
            "A005930 실시간 체결 WebSocket 채널과 수신 필드를 설명해줘",
            "API 카탈로그, WebSocket API 레퍼런스",
        ]:
            with self.subTest(readme_expected=expected):
                self.assertIn(expected, readme)

        for expected in [
            "# Unofficial WebSocket API Reference",
            "Status: browser-observed, unofficial, unstable, and script-backed by a minimal bounded client.",
            "## Server And WebSocket Handshake",
            "## STOMP Session Lifecycle",
            "## Channels And Destinations",
            "## Receive Operations",
            "## Message Envelope",
            "## Payload Schemas And Synthetic Examples",
            "## Top100 Hybrid Ranking Stream",
            "## Errors, Heartbeats, And Close Behavior",
            "observed-transport",
            "observed-protocol",
            "101 Switching Protocols",
            "Sec-WebSocket-Protocol",
            "CONNECT → CONNECTED",
            "SUBSCRIBE → MESSAGE",
            "action: receive",
            "message-id",
            "subscription",
            "matches the connection-local `subscription` id",
            "1005",
            "1006",
            "Synthetic field-name illustration",
            "A close after `101` means the WebSocket transport was established",
            "SHOULD send an `ERROR` frame",
            "close-only rejection is possible",
            "Without a `receipt` request, no `RECEIPT` is guaranteed",
            "wss://realtime-socket.tossinvest.com/ws",
            "v12.stomp",
            "UTK",
            "device-id",
            "connection-id",
            "Web/wts",
            "/topic/v1/kr/stock/trade/{productCode}",
            "/topic/v1/kr/stock/index/{productCode}",
            "/topic/v1/us/stock/index/{productCode}",
            "/topic/v1/crypto/vwap/{productCode}",
            "/bidoffer/{productCode}",
            "offerPricesKrw",
            "estimatedVolume",
            "cumulativeAmount",
            "at most 100 deduplicated product destinations",
            "observed 10-second interval",
            "Exchange-rate widgets are HTTP-only",
            "50 rows per numbered page",
            "Logged-out navigation check",
            "/indices/DJI.DJI",
            "quote panel itself displayed that login was required",
            "SharedWorker",
            "batches of 20 with a 400-ms interval",
            "caps each parsed STOMP frame at 256 KiB",
            "caps each inbound WebSocket message at 1 MiB",
            "permits only one local process",
            "exactly pinned and hash-checked",
            "performs no automatic reconnect",
            "receiveKrStockIndexUpdate",
            "receiveUsStockIndexUpdate",
            "host:<virtual-host>",
            "does not assume it equals the WebSocket hostname",
            "final-frame delivery can still be lost on connection reset",
            "https://datatracker.ietf.org/doc/html/rfc6455",
            "https://stomp.github.io/stomp-specification-1.2.html",
            "https://www.asyncapi.com/docs/reference/specification/v3.1.0",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, websocket)

        for name, text in [
            ("websocket-api-reference.md", websocket),
            ("safety-rules.md", safety),
            ("capture-workflow.md", capture),
        ]:
            with self.subTest(document=name):
                self.assertIn("STOMP", text)
                self.assertRegex(text.lower(), r"store|저장")

        self.assertIn("store", skill)

        self.assertIn("raw WebSocket frames", capture)
        self.assertIn("memory-only", capture)
        self.assertIn("keep it memory-only", skill)
        self.assertIn("bounded exponential backoff", safety)
        self.assertIn("at most 100 deduplicated product subscriptions", safety)
        self.assertIn("20-subscription/400-ms pacing", safety)
        self.assertIn("256-KiB STOMP frame limit", safety)
        self.assertIn("1-MiB inbound message limit", safety)
        self.assertIn("complete STOMP `CONNECT` or `MESSAGE` frames", security)
        self.assertNotRegex(
            websocket,
            r"(?mi)^(authorization|UTK|device-id|connection-id):\S+",
        )
        self.assertNotIn("websocat", websocket)
        self.assertNotIn("new WebSocket(", websocket)
        self.assertNotIn("host:realtime-socket.tossinvest.com", websocket)
        self.assertNotIn('"base": 0', websocket)
        self.assertIn("로그인하지 않고 토스증권 A005930", eval_prompts)
        self.assertIn("내 UTK를 줄 테니", eval_prompts)
        self.assertTrue((ROOT / "requirements-websocket.txt").exists())
        self.assertTrue((ROOT / "scripts" / "websocket_prices.py").exists())
        self.assertIn("scripts/websocket_prices.py", skill)
        self.assertIn("scripts/websocket_prices.py", readme)
        for expected in [
            "### WebSocket 클라이언트 운영 제한",
            "별도의 상주 클라이언트나 추가 패키지가 필요하지 않습니다",
            "구독 20개 / 400ms",
            "WebSocket 수신 메시지 1MiB",
            "자동 재연결 없이 오류에서 중단",
            "DISCONNECT` 영수증을 최대 1초 대기",
            "python3 -m unittest tests.test_websocket_prices -v",
            "python3 -m pip install --dry-run -r requirements-websocket.txt",
            "--crypto VWAP.KRW-BTC --duration 15 --max-events 1",
        ]:
            with self.subTest(readme_operating_limit=expected):
                self.assertIn(expected, readme)

    def test_skill_routes_disambiguate_financial_and_signal_labels(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        self.assertIn("Home rankings, top100", skill)
        self.assertIn("Investor trading trend", skill)
        self.assertIn("references/script-cookbook.md", skill)
        self.assertIn("public transaction-status credit/lending/short-selling/CFD tabs", skill)
        self.assertIn("not account credit/margin", skill)
        for detailed in [
            "UI-provided home AI-summary label fields",
            "not interpret these labels as buy/sell signals",
            "public transaction-status page datasets only",
            "account credit limits",
            "margin eligibility",
            "leverage decisions",
        ]:
            with self.subTest(detailed=detailed):
                self.assertIn(detailed, cookbook)

    def test_antigravity_distribution_uses_agent_skills_layout(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        checklist = (ROOT / ".github" / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
        ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

        self.assertFalse((ROOT / ("GE" + "MINI.md")).exists())
        self.assertFalse((ROOT / ("ge" + "mini-extension.json")).exists())
        self.assertIn("Antigravity CLI", readme)
        self.assertIn(".agents/skills/tossinvest-web-api/SKILL.md", readme)
        self.assertIn("agy", readme)
        self.assertIn("/skills", readme)

        for text in [readme, checklist, ci]:
            with self.subTest(surface=text[:20]):
                self.assertIn(".agents/skills/tossinvest-web-api", text)
        release_section = checklist.split("## GitHub", 1)[1]
        self.assertIn(".agents/skills/tossinvest-web-api", release_section)
        self.assertIn("Antigravity", release_section)

        legacy_terms = [
            "Ge" + "mini CLI",
            "ge" + "mini extensions",
            "GE" + "MINI.md",
            "ge" + "mini-extension.json",
        ]
        for path, text in [
            (ROOT / "README.md", readme),
            (ROOT / ".github" / "RELEASE_CHECKLIST.md", checklist),
        ]:
            for term in legacy_terms:
                with self.subTest(path=path.relative_to(ROOT), term=term):
                    self.assertNotIn(term, text)

    def test_skill_body_has_positive_when_to_use_guidance(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## When To Use\n", text)
        self.assertLess(text.index("## When To Use"), text.index("## When Not To Use"))
        section = text.split("## When To Use", 1)[1].split("## When Not To Use", 1)[0]
        self.assertIn("public TossInvest", section)
        self.assertIn("quotes", section)
        self.assertIn("market calendars", section)
        self.assertIn("read-only browser endpoint", section)

    def test_skill_body_stays_progressively_disclosed(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        body = text.split("---", 2)[2]
        routing = body.split("## Task Routing", 1)[1].split("## Workflow", 1)[0]
        header = next(line for line in routing.splitlines() if line.startswith("| User intent |"))
        for column in ["User intent", "Prefer", "Reference"]:
            with self.subTest(column=column):
                self.assertIn(column, header)
        self.assertIn("After choosing a routing-table row", routing)
        for detailed_route in [
            "Investor trading trend",
            "Screener counts",
            "Page-level stock API smoke checks",
        ]:
            with self.subTest(detailed_route=detailed_route):
                row = routing.split(f"| {detailed_route}", 1)[1].split("\n", 1)[0]
                self.assertIn("references/script-cookbook.md", row)
        for reference in [
            "references/api-catalog.md",
            "references/capture-workflow.md",
            "references/response-notes.md",
            "references/safety-rules.md",
            "references/script-cookbook.md",
        ]:
            with self.subTest(reference=reference):
                self.assertIn(reference, body)
        for expanded_heading in [
            "## Agent Decision Defaults",
            "## Index / FX / Crypto-like Page Defaults",
            "## Market Calendar",
            "## Rankings And Feed",
            "## Stock Page And Community",
        ]:
            with self.subTest(expanded_heading=expanded_heading):
                self.assertNotIn(expanded_heading, body)

    def test_cookbook_preserves_collector_design_pitfalls(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        self.assertIn("collector design pitfalls", skill)
        for detailed in [
            "Keep product-code validation endpoint-specific",
            "KR domestic/investor flow",
            "separate KR `A...` target list",
            "broad price-details targets",
        ]:
            with self.subTest(detailed=detailed):
                self.assertIn(detailed, cookbook)

    def test_skill_routes_calendar_without_personalized_filters(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        self.assertIn("Market calendar, economic indicators, earnings dates", skill)
        self.assertIn("`scripts/calendar.py`", skill)
        for detailed in [
            "public `/calendar` page datasets",
            "--kind economic-detail",
            "--kind index-events",
            "Do not use holding or watchlist earnings filters",
        ]:
            with self.subTest(detailed=detailed):
                self.assertIn(detailed, cookbook)

    def test_skill_routes_screener_to_cookbook_and_filter_examples(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        section = text.split("| Screener counts", 1)[1].split("\n", 1)[0]
        self.assertIn("references/script-cookbook.md", section)
        self.assertIn("examples/filters", section)

    def test_calendar_catalog_and_cookbook_cover_detail_and_index_subset(self):
        catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        self.assertIn("/api/v1/calendar/economic-indicators/{ric}", catalog)
        self.assertIn("/api/v1/nova-calendar/ai/analysis/indicators", catalog)
        self.assertIn("/api/v4/calendar/monthly/{YYYY-MM}/index", catalog)
        self.assertIn("countryType=kr|us", catalog)
        self.assertIn("scripts/calendar.py --kind economic-detail", cookbook)
        self.assertIn("scripts/calendar.py --year-month 2026-06 --kind index-events", cookbook)

    def test_news_docs_cover_paging_and_ordering(self):
        catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        self.assertIn("number", catalog)
        self.assertIn("orderBy=latest", catalog)
        self.assertIn("orderBy=relevant", catalog)
        self.assertIn("scripts/news.py --code A005930 --page 2 --order-by latest", cookbook)
        self.assertIn("scripts/news.py --code A005930 --page 2 --order-by relevant", cookbook)

    def test_catalog_records_observed_excluded_drift_endpoints(self):
        catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        for expected in [
            "/api/v3/dashboard/wts/overview/indicator",
            "/api/v4/dashboard/wts/overview/indicator",
            "/api/v2/dashboard/wts/overview/signals",
            "/api/v1/exchange/current-quote/for-buy",
            "/api/v1/community/top-rankings",
            "/api/v4/feed/recommend/ranking-posts",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, catalog)
        self.assertIn("observed-drift", catalog)
        self.assertIn("excluded", catalog)

    def test_public_web_visible_community_and_main_page_are_routed(self):
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        notes = (ROOT / "references" / "response-notes.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        evals = (ROOT / "references" / "eval-prompts.md").read_text(encoding="utf-8")

        self.assertIn("scripts/stock_page.py", skill)
        self.assertIn("scripts/community_comments.py", skill)
        self.assertIn("sanitized public community comments", skill)
        self.assertIn("/api/v4/comments", catalog)
        self.assertIn("lastCommentId", catalog)
        self.assertIn("/api/v2/comments/{commentId}/replies", catalog)
        self.assertIn("/api/v1/dashboard/wts/overview/ai-signals/detail", catalog)
        self.assertIn("/api/v3/trading/order/{productCode}/trading-status", catalog)
        self.assertIn("public-social-sensitive", catalog)
        self.assertIn("commentId", notes)
        self.assertIn("authorNickname", notes)
        self.assertIn("redacted-phone", notes)
        self.assertIn("scripts/stock_page.py --code SOXL", cookbook)
        self.assertIn("profile ids, avatar URLs, follow/bookmark flags", cookbook)
        self.assertIn("scripts/community_comments.py --code US20100311002", cookbook)
        self.assertIn("왜 떨어졌을까", evals)

    def test_official_openapi_catalog_covers_latest_missing_public_reads(self):
        boundary = (ROOT / "references" / "official-openapi-boundary.md").read_text(
            encoding="utf-8"
        )
        for expected in [
            "/api/v1/rankings",
            "/api/v1/market-indicators/prices",
            "/api/v1/market-indicators/{symbol}/candles",
            "/api/v1/market-indicators/{symbol}/investor-trading",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, boundary)
        self.assertIn("/api/v1/accounts", boundary)
        self.assertIn("/api/v1/holdings", boundary)
        self.assertIn("/api/v1/commissions", boundary)
        self.assertIn("authenticated official-only", boundary)

    def test_index_page_recheck_docs_cover_current_public_widgets(self):
        catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        notes = (ROOT / "references" / "response-notes.md").read_text(encoding="utf-8")
        cookbook = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        evals = (ROOT / "references" / "eval-prompts.md").read_text(encoding="utf-8")
        self.assertIn("2026-06-08", catalog)
        self.assertIn("range=week|month|year", catalog)
        self.assertIn("/api/v1/c-chart/{securitiesType}/{indexCode}/day:1", catalog)
        self.assertIn("reference-only, not script-backed yet", catalog)
        self.assertIn("observed daily quote-table paging", notes)
        self.assertIn("productType=INDEX|CURRENCY", catalog)
        self.assertIn("availableLanguages", catalog)
        self.assertIn("1w/min:10", catalog)
        self.assertIn("1y/week:1", catalog)
        self.assertIn("5y/month:1", catalog)
        self.assertIn("high52w", notes)
        self.assertIn("changeType", notes)
        self.assertIn("--net-buying-range month", cookbook)
        self.assertIn("--fx-range 1y --fx-step week:1", cookbook)
        self.assertNotIn("## Index / FX / Crypto-like Page Defaults", skill)
        self.assertIn("## Agent Decision Defaults", cookbook)
        self.assertIn("range=day, quarter", cookbook)
        self.assertIn("1y/day:1", cookbook)
        self.assertIn("2026-06-08 direct check returned HTTP 400", cookbook)
        self.assertNotIn("user-supplied typo", catalog)
        self.assertIn("Same live-chart API with `tag=us`", catalog)
        self.assertIn("FX 1y/day:1", evals)
        self.assertIn("--range 1w --step min:10 --include-crypto-prices", evals)

    def test_capture_and_catalog_scope_include_current_public_surfaces(self):
        catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        capture = (ROOT / "references" / "capture-workflow.md").read_text(encoding="utf-8")
        for text in [catalog, capture]:
            with self.subTest(surface=text[:20]):
                self.assertIn("calendar", text)
                self.assertIn("public community", text)
        self.assertIn("Observed drift, excluded, and sensitive public-social endpoints", catalog)
        self.assertNotIn("Observed 2026-06-01 drift and excluded endpoints", catalog)

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
        self.assertIn('display_name: "비공식 토스증권 API"', text)
        self.assertIn("토스증권 공개 시장 데이터 조회와 WebSocket 동작 설명", text)
        self.assertIn("$tossinvest-web-api", text)
        self.assertIn("WebSocket 체결 스트림의 범위를 안전하게 설명해줘", text)

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
        self.assertIn("observed-drift", checklist)
        self.assertIn("public-social-sensitive", checklist)
        self.assertIn("natural TossInvest/토스증권 language", checklist)
        self.assertIn("do not", checklist)
        self.assertIn("depend on `$...` skill selectors or aliases", checklist)
        self.assertIn("references/websocket-api-reference.md", ci_text)
        self.assertIn("references/websocket-api-reference.md", checklist)
        self.assertIn("Ephemeral WebSocket guest metadata", checklist)
        self.assertIn("standalone public read-only WebSocket client", checklist)
        self.assertIn("browser-observed", checklist)
        self.assertIn("memory-only guest-metadata", checklist)
        self.assertNotIn("matches the public skill name", checklist)
        self.assertNotIn("description starts with `Use when`", checklist)
        self.assertNotIn(
            "Public prompt examples use `$tossinvest-web-api`, not aliases.", checklist
        )

    def test_skill_uses_single_us_stock_candle_caution(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(text.count("For US stock candles"), 1)
        self.assertIn("Use `day:1` or `min:1`", text)

    def test_cookbook_documents_page_level_api_smoke_check(self):
        text = (ROOT / "references" / "script-cookbook.md").read_text(encoding="utf-8")
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Page API Smoke Checks", text)
        self.assertIn("scripts/page_api_check.py --code A005930", text)
        self.assertIn("order,analytics,news,transaction-status", text)
        self.assertIn("does not call order placement", text)
        self.assertEqual(" ".join(text.split()).count("does not call order placement"), 1)
        self.assertIn("order page read-only smoke", text)
        self.assertIn("order page read-only smoke", skill_text)

    def test_eval_prompts_cover_core_script_routes(self):
        text = (ROOT / "references" / "eval-prompts.md").read_text(encoding="utf-8")
        self.assertIn("토스증권에서 2026-05 경제지표 일정과 실적 발표일", text)
        self.assertIn("does not mention `/calendar`", text)
        for expected in [
            "scripts/quote.py --code A005930 --ticks 5",
            "scripts/financials.py --code A005930 --kind comprehensive",
            "scripts/calendar.py --year-month 2026-05 --kind economic --country us",
            "scripts/page_api_check.py --code A005930",
            "scripts/indices.py --code KGG01P --include-net-buying --net-buying-range month",
            "scripts/indices.py --code KGG01P --include-fx-chart --fx-range 1y --fx-step week:1",
            "scripts/indices.py --code VWAP.KRW-BTC --range 1w --step min:10 --include-crypto-prices",
            "refuses account/auth workflow",
            "no personalized investment advice",
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, text)

    def test_cookbook_documents_us_product_source_code_caution(self):
        checked_paths = [
            ROOT / "SKILL.md",
            ROOT / "references" / "script-cookbook.md",
            ROOT / "references" / "api-catalog.md",
        ]
        for path in checked_paths:
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertIn("US20100311002", text)
                self.assertIn("display ticker", text.lower())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("US20100311002", readme)
        self.assertIn("표시 티커", readme)
        self.assertNotIn("Display ticker/표시 티커", readme)
        api_catalog = (ROOT / "references" / "api-catalog.md").read_text(encoding="utf-8")
        self.assertIn("SPY", api_catalog)
        self.assertIn("HTTP 400", api_catalog)

    def test_release_checklist_tracks_versioned_release_metadata(self):
        checklist = (ROOT / ".github" / "RELEASE_CHECKLIST.md").read_text(encoding="utf-8")
        self.assertIn(".agents/skills/tossinvest-web-api", checklist)
        self.assertIn("release tag", checklist)
        self.assertIn("GitHub release", checklist)

    def test_gitignore_covers_python_build_and_local_artifacts(self):
        text = (ROOT / ".gitignore").read_text(encoding="utf-8")
        for pattern in [".venv/", "build/", "dist/", "*.egg-info/", ".coverage", "htmlcov/"]:
            with self.subTest(pattern=pattern):
                self.assertIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
