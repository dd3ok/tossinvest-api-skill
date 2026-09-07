# API Update Audit — 2026-09-07

Repository baseline: `3451e9825e3ff4202c23eb133a659f26cbfe57ce` on `main`.
The GitHub default branch matched that commit when this execution began.
This audit implements the local ignored `UPDATE_STRATEGY.local.md` strategy.
The original strategy-only observations are historical; this report records the
subsequent code, documentation, browser, and regression work.

## Contents

- [Result And Classification](#result-and-classification)
- [Evidence And Coverage](#evidence-and-coverage)
- [Browser Traversal](#browser-traversal)
- [Direct Public Requests](#direct-public-requests)
- [Implementation And Compatibility](#implementation-and-compatibility)
- [Verification](#verification)
- [Remaining Checks](#remaining-checks)

## Result And Classification

| Classification | Finding | Action |
| --- | --- | --- |
| Modified public contract | Stock comment subjects now use metadata `guid`; `A005930` as `subjectId` returned zero rows while `KR7005930003` returned 11 with continuation | Resolve every stock input before comment requests; update builders, output meaning, tests, catalog, and cookbook |
| Additional client defects | Dotted index codes lost case; comments/replies could repeat cursors or lose continuation; HTTP requests followed redirects and read unbounded bodies | Fix and test the affected code and shared callers |
| Additional request-budget defects | Extreme pension date ranges could produce thousands of calls; invalid chart indicators were validated after a request | Limit pension ranges to 20 calendar years and validate enabled indicators before requests |
| Official additions relative to local explicit list | Six GET routes: all stocks and five stock trading-trend categories | Update the official boundary and full official inventory; keep OAuth-only functions outside the public-web client |
| Official modified documentation | REST document `1.2.14`, 36 operations, 90 schemas; changed rate limits and paging/authentication nuances | Record canonical JSON evidence and precise exceptions |
| Web route discovery candidates | Manifest has 63 routes versus the historical count 59; `/live-event/[event-id]` and its tab route were not in local references | Document candidates and require a real public link/ID before implementation |
| Removal | No removal established from the checked evidence; all 24 explicitly documented old official method/path pairs remain | Preserve uncertainty: old complete manifests/specs are unavailable, so this is not proof of zero removals |
| Unverified | Remaining endpoint/selector combinations, event routes, and authenticated features | Keep their historical status or explicit exclusion; do not label them newly verified |

## Evidence And Coverage

- [Full static web inventory](web-api-inventory-2026-09-07.md): 153 catalog entries and 11 WebSocket-reference entries, including duplicates. This is a source inventory, not 164 distinct APIs or successful live calls.
- [Current bundle audit](web-bundle-audit-2026-09-07.md): build `7r39ou7dRVa7AiAbxAXNF`, all 63 route templates, ten bounded public JavaScript reads, source URLs, retrieval times, SHA-256, sector request/state logic, and GUID caller evidence.
- [Official audit](official-api-audit-2026-09-07.md): all 36 REST operations, 90 schemas, ten AsyncAPI operations; source fingerprints and reference integrity. The canonical REST specification is OpenAPI `3.1.0` / document `1.2.14`; AsyncAPI is `3.0.0` / document `1.2.2`.
- [Official boundary](official-openapi-boundary.md): separate OAuth service, stock/indicator unit differences, rate-limit changes, cursor semantics, and authentication exceptions.

The browser was logged out. Interactions used the actual in-app browser DOM and
UI. This browser tool did not provide request/response network capture: UI
observations, publicly fetched deployed code, and independent Python requests
are separate evidence types. No browser request headers, raw HAR, session
storage, account data, or raw comment/news bodies were retained. Local audit
records contain bounded request metadata, response shapes, counts, and paging
comparisons. Response-shape hashes are not hashes of complete server payloads.

## Browser Traversal

| Page / action | Observed state and relationship |
| --- | --- |
| [Home](https://www.tossinvest.com/) → industry → overseas | `ranking-type=trending_category&tics-nation=US`; country, rate/amount sort, and 1d/1w/1m/3m/1y controls. Industry links changed to `nation=US`. |
| Home → investor trends | `ranking-type=domestic_investor_trend`; foreign/institution lists and net-buy/net-sell control. Stale `tics-nation=US` remained in the URL although this view is domestic, so URL presence alone does not identify active filters. |
| [Sector 553](https://www.tossinvest.com/sector/553?nation=US) → stock next | Stock rows 1–10 then 11–12, with next disabled at the end and the URL unchanged. Overview counts 17 companies/55 ETFs are not the stock-table country count. |
| Sector → ETF exclusion toggle | The visible `레버리지·인버스 미포함` control changed the list to six non-leveraged/inverse rows. Current bundle confirms `includeLeverageInverse = !hideLeverageInverse`; the label alone does not encode the current boolean. |
| Sector independent sections | Separate stock, ETF, news, and related-industry paging controls; stock/ETF use `page`, news uses `number`. Bundle confirms stock/ETF country or sort changes reset that table to page 1. Header nation, stock nation, ETF nation, and related-industry nation are distinct state. |
| [Samsung stock](https://www.tossinvest.com/stocks/A005930/order) → five tabs | Actual navigation to `order`, `analytics`, `news`, `transaction-status`, `community` succeeded. Order book showed a login prompt while public trade ticks were visible. |
| Stock → news → disclosures | News latest/relevant controls; disclosure changes URL to `?menu=disclosure`. Detail links use `contentType`, `contentParams` with ID/companyCode/reportItem, and `contentPrev`; these are overlay state, not additional API query parameters. |
| Stock → analytics | Main information, financials, earnings, dividends, peer comparison, analyst tabs; income statement/balance sheet/cashflow and period controls. Only representative default financial requests were directly checked. |
| Stock → transaction status | Investor timeline plus program, credit, lending, short-selling, CFD controls. No broker rows at that moment is not endpoint removal. |
| Stock → community | Popular and latest states were observed on the same URL. Current deployed list caller uses metadata GUID. Latest comments were visibly present when the old code-based direct request returned empty. |
| [KOSPI](https://www.tossinvest.com/indices/KGG01P) | Weekly/monthly/yearly investor controls; independent daily flow/quote tables; related news links. AI-detail panel required login. Before market open, some live fields were zero while historical daily rows were populated. |
| [Calendar](https://www.tossinvest.com/calendar) → next month | September → October header, unchanged URL, category/country controls. Followed an actual `date=2026-06-01&ric=USPMI%3DECI` link to economic detail. Use link parameters, not the visible current month, for the linked historical release. |
| [Economic detail](https://www.tossinvest.com/calendar/economic-indicator?date=2026-06-01&ric=USPMI%3DECI) | Release value, AI explanation/expand, 32-point history in direct response, related articles and upcoming indicators. No live event target was available from the checked `upcomingLive=null`. |
| [Screener](https://www.tossinvest.com/screener) | Public presets, filter controls, KR market, consecutive-rise filter, result count, sorting controls. This does not establish every preset or custom condition. |
| [Recommended feed](https://www.tossinvest.com/feed/recommended) | Public posts, expansion, community ranking and lounge links, including `/community/lounges/LOUNGE_193394`. News-tab click timed out in automation; do not count a successful news-feed transition. |
| [Official introduction](https://developers.tossinvest.com/docs#description/introduction) and linked specs | Introduction, Stock Info, Market Data, response-status tabs and canonical REST/AsyncAPI documents. The Connection sidebar destination rendered not-found UI; no HTTP status was captured, and this is not evidence that official WebSocket was removed. |

## Direct Public Requests

These were small sequential reads, generally separated by one second, without
cookies or authorization. Only documented public routes or a current
public-page/bundle-derived identifier were used for successful checks.

| Family | Sample / paging | Result and scope |
| --- | --- | --- |
| Industry rankings | KR and US, 1d, fluctuation-rate | Both returned current `tics[]` shapes (98/95 rows in this sample) |
| Sector detail | 553 overview, US simple, S&P comparison | Expected overview/simple/comparison shapes; nullable description/signal fields retained |
| Sector stocks | US market-cap descending, pages 1 and 2 | 10 + 2 rows, zero product overlap; page 2 matched the browser's last page |
| Sector ETFs | ALL, trading-value descending, include leverage/inverse, pages 1 and 6 | 10 + 5 rows, zero product overlap; page 6 was the visible last page. Intermediate ETF pages were not all fetched. |
| Sector news | `number=1,2` | Five rows each with paging metadata; news article-ID overlap was not measured |
| Stock metadata / price | A005930 | `code`, `guid`, `symbol` and price list shapes confirmed; zero/missing live data must retain market/session meaning |
| Stock chart | KR `day:1`, count 3, all/krx/adjusted | First and cursor-next pages each three candles, advancing `nextDateTime`, zero date overlap |
| Company news / filings | 005930, size 3; news pages 1 and 2 | Expected `pagingParam/body/lastPage`; filings first page checked. News overlap was not measured by article ID. |
| Financials | A005930 comprehensive, POST `{}` | Factor/range/period choices plus graph/table shapes; no custom-body variants promoted |
| Investor / program | A005930, size 3 | Expected rows/paging fields; investor provisional flags and nullable balance fields retained |
| Credit | A005930, size 3; returned key plus page 2 | First page had two rows and `lastPage=false`; next had three, zero date overlap. Do not stop solely because `len(rows) < size`. |
| Index / FX / discovery widgets | KGG01P, COMP.NAI, VWAP.KRW-BTC info and prices; exchange rates; mini-chart | All representative responses returned expected shape. This does not verify every indicator or stream. |
| Calendar | September and October POST `{}`; linked USPMI detail | 34/17 events respectively; detail had historical/related/upcoming fields |
| Search / screener | Samsung product/news/TICS search; KR consecutive-rise count and pages 1/2, size 3 | Search omitted an empty requested section; screen count remained scalar and pages returned three rows each. No row-count-equals-page-size end assumption. |
| Recommended feed | First and returned `lastRecommendId` continuation | 20 + 20 sanitized posts, advancing cursor, zero post-ID overlap |
| Stock comments after fix | A005930 → GUID, latest, limit 2, then returned cursor | Two + two sanitized rows, advancing cursor, zero comment-ID overlap; each standalone invocation made one metadata and one comment request |
| Related public post | First returned comment ID → v1 replies | Valid sanitized post and zero replies / `hasNext=false` in this sample |
| Public WebSocket | A005930 KR trade; one connection, 10-second / one-event caps, no retry | One normalized event arrived at 09:11 KST; retained field names/types only, no guest metadata or raw frames |

One audit harness typo used stock chart selector `kr` instead of the existing
builder's `kr-s` and received HTTP 400; that batch stopped. Inspection of the
existing builder established the correct selector, and a separately bounded
check succeeded. This was a checker-input error, not an API removal or newly
supported selector. No 403/429 was observed in these direct REST checks.

## Implementation And Compatibility

| Change | Impact / validation focus |
| --- | --- |
| Metadata GUID for stock comments | Existing `--code` inputs remain; output `subjectId` now reflects the actual GUID. No fallback to product code. One metadata lookup per standalone invocation; the stock-page composite validates and reuses its existing metadata without a second lookup. No global identity cache. |
| Cursor validation | Missing required continuation IDs, repeated cursor, multi-step cycle, or idless truncation fail explicitly; normal sanitization and bounded continuation remain. Invalid local inputs fail before metadata access. |
| Shared REST transport | HTTPS origin only, no redirect, 16 MiB local cap, JSON object requirement, safe HTTP errors and closed error responses. `get_result` separately checks the envelope key. Every HTTP script shares this change. |
| Import order | Redirect handler is created lazily; importing urllib first must work even with the repository's `calendar.py` on `sys.path`. Standalone CLI checks cover this regression. |
| WebSocket bootstrap / upgrade | No redirect, 4096-byte guest-response cap, closed/sanitized errors, `redirect_limit=0` plus status 101 before CONNECT. Actual pinned-library offline tests cover the subtle redirect response behavior. Existing subscription/event limits remain. |
| Dotted indices | News and AI-detail builders preserve case without changing stock normalization. Access restrictions remain independent. |
| Pension / technical indicators | At most 20 calendar years per history invocation; positive periods and finite positive Bollinger deviation checked before any network request. Existing default date span and valid indicator calculations remain. |
| Sector metadata | Catalog checked date updated to 2026-09-07; fetch timestamp remains separately computed at runtime. No blanket timestamp refresh elsewhere. |
| Official APIs | Reference-only updates; no official OAuth, account, order, or SDK execution added to this public client. |

## Verification

Local Windows verification, using the CI Python versions and pinned tools:

| Check | Result |
| --- | --- |
| Baseline unit suite before changes | 241 passed on Python 3.14.6 |
| Final unit suite, Python 3.12.13 with locked WebSocket dependency | 270 passed; no skips |
| Final unit suite, Python 3.10.20 without optional dependency | 270 discovered, 269 passed and one optional-library test skipped; that test passed in the 3.12 environment |
| Ruff 0.15.22 | Lint and format checks passed |
| Standalone scripts | All 21 compiled and all 21 `--help` commands passed on both Python versions |
| JSON filter examples | All three parsed successfully |
| Install layout | Copied the CI package file/directory set to `.agents/skills/tossinvest-web-api`; installed-layout stock and WebSocket help commands passed |
| Agent Skills validator | `skills-ref==0.1.1` validated that installed layout |
| Optional dependency lock | `pip download -r requirements-websocket.txt` verified the pinned 1.9.0 wheel hash; live and offline WebSocket checks used that exact dependency |
| Documentation | Existing documentation/anchor/contents tests and new audit local-file links passed; source table inventory matched 164 entries including duplicate multiplicity |
| Review / diff | Independent final review found no additional reproducible blocker after fixes; `git diff --check` passed |
| Local strategy | `UPDATE_STRATEGY.local.md` exists, matches its exact `.gitignore` rule, and is not tracked |

Review found and corrected the initial cursor-truncation edge case, debug HTTP
exception leakage, and urllib/calendar import cycle. Documentation checks also
caught a missing contents entry and two omitted inventory rows; these were fixed.
PR review additionally caught a duplicate metadata lookup in the stock-page
composite after introducing GUID resolution. The composite now validates and
reuses its existing metadata. Regression coverage verifies the complete request
sequence, failure before further requests when the GUID is invalid, and the
GUID-independent comments-disabled path. Independent follow-up review confirmed
the duplicate request was removed.

No new test contacts the live service. These rows describe local verification;
GitHub CI and review outcomes are recorded in [PR #32](https://github.com/dd3ok/tossinvest-api-skill/pull/32).

## Remaining Checks

- Static inventories are complete for the local tables and current manifest, but this bounded run does not claim a live success for every endpoint, nation, instrument, sort, filter, date, and last page. Unlisted direct combinations remain unverified in this run.
- Public bond GUIDs and live-event IDs were not obtained from an actionable visible link; their routes remain bundle evidence/candidates. No invented endpoint or identifier was added.
- Full removed/added sets cannot be reconstructed without the historical complete OpenAPI and build manifest. Counts alone do not prove particular removals.
- Login-gated order-book/AI widgets, every account/order/authentication route, and official authenticated requests were not exercised. A public heading or code path alone does not authorize access.
- Stock latest/recent pagination is a changing dataset; zero overlap in one bounded sample is not a permanent deduplication guarantee. Repeat-cursor guards prevent a known loop, not every possible server inconsistency.
- Optional identifier fields, nullable values, and schema variations are observations, not a complete generated schema for undocumented web responses. Keep endpoint-specific shape checks when adding consumers.
- Independent runtime review reproduced two HTTP edge cases on both the repository baseline and this update: a base URL ending in an empty `?` or `#` can pass validation while changing the actual request target; a malformed IPv6 redirect `Location` can fail inside urllib before the redirect rejection handler, exposing part of that value in the exception and leaving the response open. These are existing issues, not regressions introduced by this update. Preserve them as follow-up HTTP validation/cleanup work; details are in the [PR review record](https://github.com/dd3ok/tossinvest-api-skill/pull/32#issuecomment-5563406316).
