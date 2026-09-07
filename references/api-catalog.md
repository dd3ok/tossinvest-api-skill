# TossInvest Web API Catalog

Latest bounded update: **2026-09-07**, web build `7r39ou7dRVa7AiAbxAXNF`.
See the [update audit](update-audit-2026-09-07.md) for direct request coverage,
UI states, changed contracts, and remaining unverified cases; the dated checks
below remain historical evidence rather than a blanket current verification.
Stock comments now resolve `code-or-symbol` metadata and use its **`guid`** as
`subjectId`. The [bundle audit](web-bundle-audit-2026-09-07.md) records 63 route
templates, independent sector paging, and the current community caller.

Base observation date: 2026-04-16
Additional bundle/API check: 2026-04-20 against `buildId=SUN83tZwsh5murULLiDPr`
Additional page check: 2026-04-20 for `/stocks/A005930/order`, home ranking variants, `/indices/KGG01P`, `/feed/recommended`, and `/feed/news`
Additional direct recheck: 2026-04-29 for US `c-chart` product candles and US overview indicator codes.
Additional page/API recheck: 2026-05-29 for home tabs, stock detail tabs, `/screener`, `/feed/news`, `/indices/KGG01P`, `/indices/exchange-rate`, and `/indices/VWAP.KRW-BTC`.
Additional page/API recheck: 2026-06-01 for `/calendar`, `/calendar/economic-indicator`, index-page calendar subsets, stock-news paging, and observed drift/excluded page calls.
Additional page/API recheck: 2026-06-08 for `/indices/KGG01P`, `/indices/exchange-rate`, and `/indices/VWAP.KRW-BTC` chart controls, related widgets, paging, and response shapes.
Additional logged-out WebSocket/page recheck: 2026-07-10 for home tabs and search, sector, screener, feeds, stock-detail tabs, all home index links, real-time consumers, and HTTP paging boundaries.
Additional public page/bundle/API recheck: 2026-07-16 for home search sections, all visible ranking durations, sector stock/ETF paging and sorts, index daily quotes, lounge comments, community rankings, and stock status helpers.
Additional industry dashboard/sector recheck: 2026-08-04 against `buildId=-owfs18fvEJHIHRdmooMq` for home industry URL state, `/sector/79?nation=US|KR`, stock/ETF/news paging, comparison-index clicks, current response shapes, and shared live-price overlays.
Additional route-manifest/bundle recheck: 2026-08-05 against `buildId=-owfs18fvEJHIHRdmooMq` for `/bonds/[guid]`, `/news`, `/cheetah`, `/cheetah/[code]`, `/stocks/[code]/option`, and account/marketing route boundaries.
Additional public surface/API recheck: 2026-08-13 against `buildId=Sg-uF4vsHmKQC9cjQ6v9G` for all five stock-detail tabs, stock news/disclosure state, community post and lounge pages, recommended-feed v4 paging/sanitization, `/indices/QGG01P`, `/screener/[preset-id]`, numbered/cursor pagination, and 44 bounded read-only page endpoints. The old and current route manifests both contained 59 routes with no additions or removals.

Additional bounded WebSocket recheck: 2026-08-13 for public KR/US stock, KR/US index, and `VWAP.KRW-*` channels; see [Unofficial WebSocket API Reference](websocket-api-reference.md) for exact event evidence and client allowlists.
Additional bounded US-index WebSocket recheck: 2026-08-18 during regular US market hours for `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, and `SOX.NAI`; each exact code delivered an event.
Status labels added: 2026-04-20
Observed from: public `tossinvest.com` pages in a non-authenticated browser session.
Primary data host: `https://wts-info-api.tossinvest.com`

This catalog is for read-only public TossInvest workflows. Include endpoints only when they help answer stock, market, index, calendar, theme, financial, filing, news, ranking, investor-trend, screener, or public community questions visible without login. Do not collect page bootstrapping, telemetry, login/certificate, guest/session, account, order, following/subscription, or personalization endpoints as cataloged APIs.

Re-verify endpoints before depending on them because TossInvest web APIs are undocumented and may change without notice. Keep checks small, sequential, and user-initiated. If TossInvest returns access-denied, throttling, challenge, login, or otherwise unexpected responses, stop and re-check the endpoint in current public browser traffic instead of retrying or working around service-protection behavior.

## Contents

- [Choose a reference](#choose-a-reference)
- [Verification Status](#verification-status)
- [Host Map](#host-map)
- [Identifier Conventions](#identifier-conventions)
- [Stock Summary APIs](#stock-summary-apis)
- [Chart APIs](#chart-apis)
- [Index And Market Indicator APIs](#index-and-market-indicator-apis)
- [Bond APIs](#bond-apis)
- [Analytics APIs](#analytics-apis)
- [Filings And News APIs](#filings-and-news-apis)
- [Transaction Status APIs](#transaction-status-apis)
- [Dashboard And Discovery APIs](#dashboard-and-discovery-apis)
- [Calendar APIs](#calendar-apis)
- [Dashboard And Screener Page Behavior](#dashboard-and-screener-page-behavior)
- [Feed And News APIs](#feed-and-news-apis)
- [Screener APIs](#screener-apis)
- [Cert And Status Helpers](#cert-and-status-helpers)
- [Public Community And Main-Page APIs](#public-community-and-main-page-apis)
- [Excluded Non-Stock Calls](#excluded-non-stock-calls)
- [Known Observed Pages](#known-observed-pages)

## Choose a reference

| You need | Read |
| --- | --- |
| Stock quotes, candles, financials, company news/filings, investor trends | [Stock APIs](api-stock.md) |
| Indices, FX, bonds, calendars, rankings, search, sectors, screeners | [Market APIs](api-market.md) |
| Public news discovery, feeds, comments, replies, stock-page composition | [Feed and community APIs](api-community.md) |
| CLI commands and examples | [Script cookbook](script-cookbook.md#contents) |
| Response fields, cursors and sanitizer output | [Response notes](response-notes.md#contents) |
| Public stream protocol and client setup | [WebSocket reference](websocket-api-reference.md#contents) |
| Official OAuth API distinction and official limits | [Official Open API boundary](official-openapi-boundary.md) |

Select the relevant reference; normal lookups do not require reading every file.
The domain section owns the endpoint contract. The cert helper table below is a
cross-domain host-safety summary, and dated audits remain historical evidence.
Old section links below are retained for bookmarks; new links should go directly
to the domain section.

## Verification Status

Endpoint status values are conservative confidence labels, not stability guarantees. TossInvest can change undocumented internal APIs without notice.

| Status | Meaning |
|---|---|
| `script-backed` | A bundled script calls this exact endpoint or endpoint family. Re-run the script or direct request before relying on current production behavior. |
| `observed` | Observed from public browser traffic, bundled JavaScript, or prior direct checks, but not wrapped as a first-class script path. |
| `needs-recheck` | Observed indirectly, feature-flagged, host-sensitive, user-context-sensitive, or otherwise requiring a fresh browser/API check before use. |
| `observed-drift` | Current public traffic uses or also exposes this endpoint, but the script still uses a safer mirror, older route, or intentionally narrower route. Do not call from scripts until separately reviewed. |
| `excluded` | Observed but outside this skill's read-only stock-information scope. Do not call from this skill. |
| `public-social-sensitive` | Public unauthenticated social/community page data. Script only with bounded pagination and sanitized output. |

For duplicated families, the domain section is the source of truth. Cross-reference
sections should not widen a status or imply that `needs-recheck` or `excluded`
endpoints are safe to call.

## Host Map

| Host | Observed purpose | Usage guidance |
|---|---|---|
| `wts-info-api.tossinvest.com` | Stock info, prices, quotes/ticks, chart, analytics, financial statements, consensus, dividends, investor trading trend, filings, news, themes | Primary read-only host |
| `wts-api.tossinvest.com` | Time, trading hours, system status, guest/login bootstrap | Do not catalog unless the response directly helps explain market status or trading-hour context |
| `wts-cert-api.tossinvest.com` | Red flags, trading status, dashboard ranking, comments, some authenticated data | Treat as sensitive; use only cataloged/script-backed public page data or metadata with no cookies, auth headers, account identifiers, or personal data |
| `cdn-api.tossinvest.com` | Deployment refresh checks | Exclude from data catalog |
| `log.tossinvest.com` | Telemetry and performance logs | Exclude |
| `sentry-public.tossinvest.com` | Error reporting | Exclude |

## Identifier Conventions

| Identifier | Example | Meaning |
|---|---|---|
| `productCode` | `A005930`, `A000660` | TossInvest stock/product code used by stock detail APIs |
| `companyCode` | `005930`, `000660` | Company code used by some `/companies/` APIs |
| `codes` | `A005930,A000660` | Comma-separated product code list |
| `indexCode` | `KGG01P`, `QGG01P`, `RGI..VIX`, `VWAP.KRW-BTC` | Index, FX, commodity, futures, bond, or crypto-like market code used by `/indices/{code}` pages |

Use `productCode` for stock pages and prices. Strip the leading `A` only where the observed endpoint uses `companyCode`.

## Stock Summary APIs

See [Stock Summary APIs](api-stock.md#stock-summary-apis).

## Chart APIs

See [Chart APIs](api-stock.md#chart-apis).

## Index And Market Indicator APIs

See [Index And Market Indicator APIs](api-market.md#index-and-market-indicator-apis).

## Bond APIs

See [Bond APIs](api-market.md#bond-apis).

## Analytics APIs

See [Analytics APIs](api-stock.md#analytics-apis).

## Filings And News APIs

See [Filings And News APIs](api-stock.md#filings-and-news-apis).

## Transaction Status APIs

See [Transaction Status APIs](api-stock.md#transaction-status-apis).

## Dashboard And Discovery APIs

See [Dashboard And Discovery APIs](api-market.md#dashboard-and-discovery-apis).

### Current Industry Dashboard And Sector Behavior

See [Current Industry Dashboard And Sector Behavior](api-market.md#current-industry-dashboard-and-sector-behavior).

## Calendar APIs

See [Calendar APIs](api-market.md#calendar-apis).

## Dashboard And Screener Page Behavior

See [Dashboard And Screener Page Behavior](api-market.md#dashboard-and-screener-page-behavior).

### Home Ranking Values And Filters

See [Home Ranking Values And Filters](api-market.md#home-ranking-values-and-filters).

### Live Price Updates And Page Observations

See [Live Price Updates And Page Observations](api-market.md#live-price-updates-and-page-observations).

### RSI Screener And Sorting

See [RSI Screener And Sorting](api-market.md#rsi-screener-and-sorting).

### Price Condition Presets

See [Price Condition Presets](api-market.md#price-condition-presets).

### Technical Analysis Presets

See [Technical Analysis Presets](api-market.md#technical-analysis-presets).

## Feed And News APIs

See [Feed And News APIs](api-community.md#feed-and-news-apis).

## Screener APIs

See [Screener APIs](api-market.md#screener-apis).

## Cert And Status Helpers

These endpoints were observed during public page loads but live under `wts-cert-api`. Treat them as sensitive unless their current behavior is public visible page data or metadata with no cookies, auth headers, account identifiers, or personal data. Script-backed rows are restricted by `scripts/tossinvest_api.py` host/path policy.

| Purpose | Status | Method | URL | Sensitive-host note |
|---|---|---:|---|---|
| Stock red flags | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/stock-infos/{productCode}/red-flags` | Public page metadata |
| Product trading status | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v3/trading/order/{productCode}/trading-status` | Public product status helper observed on stock pages; only this exact read path is allowed |
| Trading analysis metadata | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/trading/analysis/productCode/{productCode}` | Public page metadata; may return `null` |
| Overview indicator | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/index?market=kr` | Public dashboard metadata only |
| Overview indicator v3 | `observed` | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator?market=kr` | Public dashboard metadata; re-check before scripting |
| Overview indicator v4 | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | Current public home aggregate; `dashboard_ranking.py --kind indicator` uses this exact read-only path with no query or body |
| Overview ranking | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | Public dashboard ranking body only |
| Live-chart top100 ranking | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | Public dashboard ranking body only |
| Monthly calendar | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}` | Public calendar metadata; exact month pattern only |
| Index-page calendar subset | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}/index?countryType=kr|us` | Public index-page calendar metadata; exact path/query shape only |
| Economic indicator detail | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/calendar/economic-indicators/{ric}?announceDate={YYYY-MM-DD}` | Public economic-indicator detail page data only |
| Economic indicator AI analysis | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/analysis/indicators` | Query is exactly `announceDateTime` plus `ricId`; public detail-page text only |
| Calendar key events | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/calendar/ai-summary/key-events` | Public calendar metadata and AI summary labels only |
| Calendar weekly summary | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/summary/weekly` | Public page summary text only; not investment advice |
| Economic calendar | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/calendar/economic-events` | Public calendar metadata |
| Investor rankings | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` | Public-looking ranking widget only |

The `/stocks/{code}/order` bundle also references order prepare/create/correct/cancel, account, orderable amount, and trading mutation APIs. Exclude them from this skill.

## Public Community And Main-Page APIs

See [Public Community And Main-Page APIs](api-community.md#public-community-and-main-page-apis).

## Excluded Non-Stock Calls

Do not collect these as cataloged APIs, even if they appear in browser network traffic:

- Telemetry, Sentry, logging, deployment refresh, images, fonts, and static assets.
- Login, certificate, authentication, account, balance, holding, transfer, order, orderable-amount, order mutation, and session-storage calls.
- Order-adjacent status helpers except the verified public read-only `https://wts-cert-api.tossinvest.com/api/v3/trading/order/{productCode}/trading-status`; keep all mutation, orderability, prepare, create, correct, and cancel routes excluded.
- Guest bootstrap/upsert, experiment variables, tab/session initialization, and other page bootstrapping calls that do not directly return stock or market information.
- Following/subscription feeds, personalized interest/reasoning content, account-personalized discovery surfaces, or unsanitized raw community/profile payloads.
- Marketing or account/provision surfaces such as `/ai-campaign`, `/asap`, and `/open-api/*`; the last family belongs to the separate official Open API flow.
- Feature-gated or blank logged-out routes whose current bundle does not expose a bounded public market-data workflow, including `/stocks/[code]/option` and `/cheetah*`.

## Known Observed Pages

Use this table as the first stop for endpoint drift or lookup failures. Open the public page that should expose the missing data, follow [capture-workflow.md](capture-workflow.md), and update this catalog before changing scripts. Do not guess a replacement endpoint from a stale path.

| Page | Key endpoint groups |
|---|---|
| `https://www.tossinvest.com/?focusedProductCode=A000660` | Chart, stock summary, ranking, dashboard signals |
| `https://www.tossinvest.com/?focusedProductCode=US20100311002` | US stock main-page metadata, price details, public AI detail, sanitized community comments |
| `https://www.tossinvest.com/stocks/A005930` | Redirects to the public `/order` tab; top tabs link to `/order`, `/analytics`, `/news`, `/transaction-status`, and `/community` |
| `https://www.tossinvest.com/stocks/US20100311002/community` | Public stock comments, comment replies, related board, recommended profiles |
| `https://www.tossinvest.com/stocks/A005930/analytics` | Analytics, financials, dividends, analyst data; visible statement tabs are income statement, balance sheet, and cash-flow statement, but their request bodies require a fresh capture before adding a selector |
| `https://www.tossinvest.com/stocks/A005930/news?menu=news` | Company news; the visible latest/relevance sort is client state on this URL |
| `https://www.tossinvest.com/stocks/A005930/news?menu=disclosure` | Company filings/disclosures |
| `https://www.tossinvest.com/stocks/A005930/transaction-status` | Broker ranking, investor trend, program trading, credit, lending trading, short-selling trend, and CFD; current sub-tabs keep the URL unchanged |
| `https://www.tossinvest.com/stocks/A005930/order` | Price details, quote/tick, upper/lower bounds, `c-chart` stock candles, TradingView chart studies; order namespace helpers and mutations excluded; no dedicated RSI/MACD/Bollinger data endpoint observed |
| `https://www.tossinvest.com/?ranking-type=trending_category&focusedTicsId=553` | Current home industry ranking with an industry detail aside; optional `tics-nation`, `tics-duration`, and `tics-sort` persist filter state |
| `https://www.tossinvest.com/?ranking-type=domestic_investor_trend` | Investor buy/sell rankings from dashboard ranking APIs |
| `https://www.tossinvest.com/?market={market}&live-chart={id}&duration={duration}` | `market` is `kr` or `us`; seven public live-chart ids: `biggest_total_amount`, `biggest_total_volume`, `biggest_market_amount`, `biggest_market_volume`, `heavy_soar`, `heavy_descent`, and `realtime_stock`; map only the cataloged duration values |
| `https://www.tossinvest.com/indices/KGG01P` | Index info, price, chart, indicator/news widgets |
| `https://www.tossinvest.com/indices/QGG01P` | Public KOSDAQ index price/chart, investor trend, numbered daily net-buy and daily-quote pages, and news; a bounded 2026-08-13 public WebSocket check received one standard-index event |
| `https://www.tossinvest.com/indices/COMP.NAI` | Public Nasdaq index value plus HTTP history/news/related-stock widgets |
| `https://www.tossinvest.com/indices/SPX.CBI` | Public S&P 500 index value plus HTTP history/news/related-stock widgets |
| `https://www.tossinvest.com/indices/RGI..VIX` | Public VIX index value plus HTTP history/news/related-stock widgets |
| `https://www.tossinvest.com/indices/SOX.NAI` | Public Philadelphia Semiconductor index value plus HTTP widgets |
| `https://www.tossinvest.com/indices/exchange-rate` | FX chart and exchange-rate widgets |
| `https://www.tossinvest.com/indices/VWAP.KRW-BTC` | Crypto-like index info/price, `r-chart/crypto`, crypto prices, related news |
| `https://www.tossinvest.com/indices/VWAP.KRW-ETH` | Public Ethereum crypto-like index price/chart, daily quotes, and live value |
| `https://www.tossinvest.com/indices/VWAP.KRW-XRP` | Public XRP crypto-like index price/chart, daily quotes, and live value |
| `https://www.tossinvest.com/indices/VWAP.KRW-SOL` | Public Solana crypto-like index price/chart, daily quotes, and live value |
| `https://www.tossinvest.com/bonds/{guid}` | Bundle-observed bond detail and simple metadata; requires a current public page GUID and live response-shape recheck |
| `https://www.tossinvest.com/indices/DJI.DJI` | Redirected to sign-in in the 2026-07-10 logged-out check; stop rather than probing a destination |
| `https://www.tossinvest.com/indices/RFU.NQc1` | Redirected to sign-in in the 2026-07-10 logged-out check |
| `https://www.tossinvest.com/indices/RFU.GCv1` | Redirected to sign-in in the 2026-07-10 logged-out check |
| `https://www.tossinvest.com/calendar` | Monthly market calendar, economic/earnings and domestic/overseas local filters, weekly/key-event summary text |
| `https://www.tossinvest.com/calendar/economic-indicator?date=2026-06-01&ric=USPMI%3DECI` | Economic indicator detail, historical data, related articles, upcoming indicators, AI analysis text |
| `https://www.tossinvest.com/screener` | Screener presets, filter metadata, result count, result screen |
| `https://www.tossinvest.com/screener/4` | Public preset-detail route with selected filters and the same numbered/virtualized screener result family |
| `https://www.tossinvest.com/sector/79?nation=US` | Public sector header/chart, ALL/KR/US stock and ETF filters, comparison-index menu, server-paged news, related-industry tree, and client-paged trending-industry sidebar |
| `https://www.tossinvest.com/sector/79?nation=KR` | Same sector id with the KR header/chart seed and KR stock default; switching the header market after load does not rewrite the URL |
| `https://www.tossinvest.com/community/lounges/LOUNGE_193394` | Public lounge description and sanitized popular/recent comments with `lastCommentId` paging |
| `https://www.tossinvest.com/community/posts/{post-id}` | Public community post permalink and sanitized replies with `lastReplyId` paging |
| `https://www.tossinvest.com/feed/recommended` | Recommended community/feed posts from the v4 cert route; sanitize post/profile fields and continue only with `nextLastRecommendId` |
| `https://www.tossinvest.com/feed/news` | Dashboard news categories and news detail |

### Route-manifest scope review

The 2026-08-13 deployed route manifest (`buildId=Sg-uF4vsHmKQC9cjQ6v9G`)
contains the same 59 routes as the 2026-08-05 manifest. Route presence alone is
not evidence of a usable public API, so the audit kept the following boundaries:

| Route | Audit result | Catalog decision |
|---|---|---|
| `/bonds/[guid]` | Public page bundle contains the two read-only bond-info calls above | `observed`; recheck with a visible GUID before scripting |
| `/news` | Logged-out direct navigation rendered no bounded data surface | `needs-recheck`; prefer the verified `/feed/news` flow |
| `/cheetah`, `/cheetah/[code]` | Logged-out pages were blank; only `/api/v1/reasoning-news/count` was visible in the checked bundle | `needs-recheck`; no script or broader endpoint claim |
| `/stocks/[code]/option` | Route module rendered no public content and loaded order-adjacent feature metadata | `excluded` until a logged-out public market-data surface is verified |
| `/community/posts/[post-id]` | Logged-out permalink rendered a bounded post plus v1 reply cursor | `public-social-sensitive` / `script-backed` through the sanitizer |
| `/community/lounges/[subjectId]` | Logged-out lounge rendered public description and comment tabs | `public-social-sensitive` / `script-backed` through the sanitizer |
| `/screener/[preset-id]` | Logged-out preset detail rendered the public filter/result surface | `observed`; use existing screener read-only families only |
| `/ai-campaign` | Marketing surface | `excluded` |
| `/asap` | Account/provision terms surface | `excluded` |
| `/open-api/*` | Official Open API onboarding/documentation flow | Separate scope; use `official-openapi-boundary.md` |

Cross-checking other plausible gaps did not justify inventing new endpoint
families. Display ticker resolution is already script-backed through
`/api/v2/stock-infos/code-or-symbol/{productCode}` in `stock_page.py`; ETF/ETN
detail has the observed `/api/v2/stock-infos/{productCode}/investment` route;
and the home live chart, recommended feed lists, sector pages, calendar,
community post permalinks, lounges, and screener preset pages are already
cataloged. A public AI earnings-call transcript/translation surface remains
`needs-recheck` because this audit did not establish a bounded logged-out route
and response shape for it. Do not infer endpoints from product announcements or
search results.
