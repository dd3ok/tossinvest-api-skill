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

Observed on stock detail pages such as `/stocks/A005930`.

| Purpose | Status | Method | Path | Key response fields / notes |
|---|---|---:|---|---|
| Common stock detail UI | `script-backed` | GET | `/api/v1/stock-detail/ui/{productCode}/common` | `name`, `detailName`, `guid`, `symbol`, `marketCode`, `companyCode`, `badges`, `notices` |
| Header info | `script-backed` | GET | `/api/v1/stock-infos/header/{productCode}` | `sections[]`; section keys include ranking fields such as `netBuyVolumeRanking` |
| WTS badges | `script-backed` | GET | `/api/v1/stock-infos/{productCode}/wts-badges` | Badges shown around stock header/detail |
| Stock info | `script-backed` | GET | `/api/v2/stock-infos/{productCode}` | `code`, `guid`, `symbol`, `isinCode`, `status`, `name`, `market`, `companyCode`, `companyName` |
| Code or symbol lookup | `script-backed` | GET | `/api/v2/stock-infos/code-or-symbol/{productCode}` | Same general metadata shape as stock info; used by stock-page and community scripts to resolve display symbols |
| Batch stock info | `observed` | GET | `/api/v1/stock-infos?codes={codes}` | Long comma-separated code list |
| Price batch v1 | `observed` | GET | `/api/v1/product/stock-prices?meta=true&productCodes={codes}` | Price list with optional metadata |
| Price batch v3 | `observed` | GET | `/api/v3/stock-prices?meta=true&productCodes={codes}` | Newer price list shape |
| Price details | `script-backed` | GET | `/api/v3/stock-prices/details?productCodes={codes}` | List items include `code`, `exchange`, `tradeDateTime`, `open`, `high`, `low`, `close`, `volume`, `value`, `base`, `changeType`, `currency` |
| Quote book v2 | `observed` | GET | `/api/v2/stock-prices/{productCode}/quotes` | Query can include `investMode`, `viewType`, `preMarketHours`; observed result includes `sellPrices`, `sellQuantities`, `buyPrices`, `buyQuantities`, `estimatedPrice` |
| Quote book v3 | `script-backed` | GET | `/api/v3/stock-prices/{productCode}/quotes` | Query can include `investMode`, `viewType`, `fallbackKrx`; observed result includes `offerPrices`, `offerVolumes`, `bidPrices`, `bidVolumes`, `midPrices` |
| Intraday ticks | `script-backed` | GET | `/api/v2/stock-prices/{productCode}/ticks` | Query: `viewType`, `count`, `investMode`; observed rows include `time`, `price`, `base`, `volume`, `tradeType`, `cumulativeVolume` |
| Main-session prices | `observed` | GET | `/api/v1/stock-prices/mainsession?codes={codes}` | Observed result object includes `prices` |
| After-session prices | `observed` | GET | `/api/v1/stock-prices/after?codes={codes}` | Observed list items include `code`, `changeType`, `close`, `value`, `volume`, `amount` |
| Upper/lower price bounds | `script-backed` | GET | `/api/v2/stock-prices/{productCode}/upper-lower` | `date`, `upperLimit`, `lowerLimit` |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v2/stock-infos/A005930
GET https://wts-info-api.tossinvest.com/api/v3/stock-prices/details?productCodes=A005930
GET https://wts-info-api.tossinvest.com/api/v3/stock-prices/A005930/quotes?investMode=krx
GET https://wts-info-api.tossinvest.com/api/v2/stock-prices/A005930/ticks?viewType=krx&count=5&investMode=krx
```

## Chart APIs

Observed on home and stock detail pages.

| Purpose | Status | Method | Path | Params and notes |
|---|---|---:|---|---|
| KR stock candle chart | `script-backed` | GET | `/api/v1/c-chart/kr-s/{productCode}/{range}` | Observed ranges include `min:1`, `day:1`, `week:1`, `month:1`; query: `count`, `session=all`, `investMode=krx`, `useAdjustedRate=true`; result includes `code`, `nextDateTime`, `exchangeRate`, `exchange`, `candles[]` |
| US stock candle chart | `script-backed` | GET | `/api/v1/c-chart/us-s/{productCode}/{range}` | Direct recheck accepted `min:1` and `day:1` for opaque US product/source codes such as `US20100311002` and `US20100629001`; use the same query fields as KR. Display tickers are not interchangeable with product codes: recent smoke checks returned HTTP 400 for `SPY`, `QQQ`, `NVDA`, and `BRK.B` when passed directly as `productCode`. |

Example:

```text
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/day:1?count=61&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/min:1?count=5&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/week:1?count=5&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/month:1?count=5&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/us-s/US20100311002/day:1?count=5&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/us-s/US20100311002/min:1?count=5&session=all&investMode=krx&useAdjustedRate=true
```

Do not substitute uppercase or legacy range aliases such as `1D` or `1H`, and do
not use `hour:1` unless a fresh browser capture verifies it. Direct rechecks on
2026-04-29 returned HTTP 400 for `1D`, `1H`, and `hour:1`.

Endpoint compatibility is narrower for `c-chart` than for price details. A
small direct smoke check on 2026-05-10 found `/api/v3/stock-prices/details`
accepted `Q520072` and `AMX0221116003`, while `c-chart` returned HTTP 400 for
`us-s/Q520072` and `kr-s/AMX0221116003`. Treat `productCode` validation as
endpoint-specific: price-details-compatible does not imply candle-compatible.

Observed values:

| Param | Example | Meaning |
|---|---|---|
| `count` | `1`, `61` | Number of candles requested |
| `session` | `all` | Includes all sessions in observed calls |
| `investMode` | `krx` | Market mode in observed Korean stock calls |
| `useAdjustedRate` | `true` | Adjusted price flag |

Observed candle keys:

```text
dt, base, open, high, low, close, volume, amount
```

The `/stocks/A005930/order` chart's `+` button has `aria-label="보조지표"`.
Playwright verification on 2026-04-20 showed that opening the menu and selecting
`RSI` loaded icon/font/log requests only; no dedicated TossInvest RSI/MACD/
Bollinger data endpoint was called. The page uses TradingView chart studies from
`https://static.tossinvest.com/assets/libraries/trading-view/v27.001_251222/charting_library/`
over the `c-chart` candle datafeed. Treat technical indicators as client-side or
local calculations from `c-chart` candles unless a current network capture shows
a dedicated indicator endpoint.

## Index And Market Indicator APIs

Observed from `/indices/KGG01P` and the index/FX dashboard widgets. These are market context APIs rather than single-stock APIs, but they are useful alongside stock lookups.

| Purpose | Status | Method | URL/path | Params and notes |
|---|---|---:|---|---|
| Index info | `script-backed` | GET | `/api/v2/index-infos/{indexCode}` | Returned `code`, `name`, `logoImageUrl`, `priceFeedType`, `tradingStartAt`, `tradingEndAt`, `isMarketOpen`; current crypto-like responses can also include `indexUnitDto` and `helperText` |
| Index price | `script-backed` | GET | `/api/v1/index-prices/{indexCode}` | Returned `open`, `high`, `low`, `close`, `volume`, `value`, `base`, `changeType`, `high52w`, `low52w`; `tradeTime` may appear on some index responses |
| Index/market chart | `script-backed` | GET | `/api/v1/r-chart/{securitiesType}/{indexCode}/{range}/{step}` | Query: `session=main`, `investMode=krx`, `last=false`; example `kr-s/KGG01P/1d/min:5` |
| Index daily quote table | `script-backed` | GET | `/api/v1/c-chart/{securitiesType}/{indexCode}/day:1` | `scripts/indices.py --include-daily-quotes`; query includes `count`, optional ISO 8601 cursor `from`, and `useAdjustedRate=true`; result includes `nextDateTime` and `candles[]` |
| Crypto prices | `script-backed` | GET | `/api/v1/crypto-prices?productCodes={codes}` | Direct 2026-06-08 check accepted `VWAP.KRW-BTC`, `VWAP.KRW-ETH`, `VWAP.KRW-XRP`, and `VWAP.KRW-SOL`; returned OHLCV, `changeType`, `high52w`, `low52w`, `usdPerKrwExchangeRate`, `premium`, and `premiumRate` |
| USD/KRW product exchange rate | `script-backed` | GET | `/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW` | Direct 2026-05-29 check returned `code`, `base`, `close`; `scripts/indices.py --include-product-exchange-rate` fetches this helper |
| FX chart | `script-backed` | GET | `/api/v1/r-chart/fx/EXCHANGE_RATE/{range}/{step}` | Query includes `last=false`, `useAdjustedRate=true`, `currency=USD` |
| Overview indicators v3 | `observed` | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator` | Returned `leftSection`, `rightSection`, `indicators`, `landingUrl`; public page widget on cert host |
| Overview indicator by type | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/{type}` | Query: `market`; observed `type` values include `index`, `bond`, and `commodity`, each returning `majorIndicatorInfos[]` |
| Overview indicator mini-chart | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/mini-chart` | Returned `indexMap`; public page widget on cert host |
| Related ETFs | `script-backed` | POST | `/api/v3/dashboard/wts/overview/indicator/{indexCode}/related-etfs` | Empty JSON body accepted; returned `indexCode`, `etfs[]` |
| Index net buying range | `script-backed` | GET | `/api/v1/stock-infos/index/net-buying/range` | Query: `code`, `range=week|month|year`, `from`, `count`; returned `investorActivityAmounts[]` |
| Index net buying daily | `script-backed` | GET | `/api/v1/stock-infos/index/net-buying/daily` | Query: `code`, `from`, `count`; returned `investorActivityAmounts[]` |
| Exchange rates widget | `script-backed` | GET | `/api/v1/dashboard/wts/overview/exchange-rates` | Returned `exchangeRates[]` |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v2/index-infos/KGG01P
GET https://wts-info-api.tossinvest.com/api/v1/index-prices/KGG01P
GET https://wts-info-api.tossinvest.com/api/v2/index-infos/SPX.CBI
GET https://wts-info-api.tossinvest.com/api/v1/index-prices/SPX.CBI
GET https://wts-info-api.tossinvest.com/api/v2/index-infos/COMP.NAI
GET https://wts-info-api.tossinvest.com/api/v1/index-prices/COMP.NAI
GET https://wts-info-api.tossinvest.com/api/v2/index-infos/VWAP.KRW-BTC
GET https://wts-info-api.tossinvest.com/api/v1/index-prices/VWAP.KRW-BTC
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KGG01P/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KGG01P/1d/min:1?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KGG01P/1d/min:3?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KGG01P/1d/min:10?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/us-s/RFU.GCv1/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/crypto/VWAP.KRW-BTC/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/crypto/VWAP.KRW-BTC/1w/min:10?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/crypto/VWAP.KRW-BTC/1y/week:1?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/crypto/VWAP.KRW-BTC/5y/month:1?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KR1BENCH0010/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/fx/EXCHANGE_RATE/1d/min:5?last=false&useAdjustedRate=true&currency=USD
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/fx/EXCHANGE_RATE/1y/week:1?last=false&useAdjustedRate=true&currency=USD
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/fx/EXCHANGE_RATE/5y/month:1?last=false&useAdjustedRate=true&currency=USD
GET https://wts-info-api.tossinvest.com/api/v1/crypto-prices?productCodes=VWAP.KRW-BTC
GET https://wts-info-api.tossinvest.com/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW
GET https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/mini-chart
POST https://wts-info-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/KGG01P/related-etfs
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=week&from=2026-04-20&count=5
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=month&from=2026-06-08&count=5
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=year&from=2026-06-08&count=5
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/index/net-buying/daily?code=KGG01P&count=35&from=2026-04-20
GET https://wts-info-api.tossinvest.com/api/v1/dashboard/wts/overview/exchange-rates
GET https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator
GET https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/bond?market=kr
GET https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/commodity?market=kr
```

Direct checks on 2026-04-20 returned public page bond indicators such as
Korean and US Treasury yields, and commodity indicators such as gold, silver,
WTI, natural gas, copper, and wheat. The v3 overview indicator endpoint returned
`leftSection`, `rightSection`, `indicators`, and `landingUrl`; the v1 `bond` and
`commodity` endpoints returned `majorIndicatorInfos[]`. `exchange-rate`/`exchange`
were not accepted as indicator types in direct checks; use the separate
exchange-rates widget for FX lists. `scripts/indices.py --include-fx-chart`
fetches the FX r-chart, and `scripts/indices.py --include-exchange-rates`
fetches the exchange-rates widget.

Additional Playwright checks on 2026-04-20 used a browser context with no stored
cookies or session state and no HAR capture. They showed that bond and commodity
indicator codes such as `KR1BENCH0010`, `ROB.US10YT-RR`, `RFU.GCv1`, and
`RFU.CLv1` are accepted by the same index info and price endpoints. Dotted codes
can be case-sensitive, so preserve the code exactly as returned by the indicator
payload. The browser also called chart endpoints for checked indicator pages:
`RFU.GCv1` used `r-chart/us-s/RFU.GCv1/1d/min:5`, and `KR1BENCH0010` used
`r-chart/kr-s/KR1BENCH0010/3m/day:1`; direct checks also returned candles for
`KR1BENCH0010/1d/min:5` and `ROB.US10YT-RR` under `us-s`.

Additional checks on 2026-05-29 confirmed the current index carousel/category
codes `QGG01P`, `RGI..VIX`, `RFU.NQc1`, `SOX.NAI`, `RFU.GCv1`, and
`VWAP.KRW-BTC`. `scripts/indices.py` uses `--securities-type auto` by default:
`VWAP.KRW-*` crypto codes infer `crypto`, other dotted indicator codes infer
`us-s`, and non-dotted codes infer `kr-s`.

`scripts/indices.py` chart presets map to the verified windows
`intraday=1d/min:5`, `quarter=3m/day:1`, and `daily=1y/day:1`. The script can
also fetch the verified mini-chart, related ETF, index net-buying, crypto price,
and product exchange-rate widgets with `--include-mini-chart`,
`--include-related-etfs`, `--include-net-buying`, `--include-crypto-prices`,
and `--include-product-exchange-rate`.

Additional 2026-06-08 browser checks against `/indices/KGG01P`,
`/indices/exchange-rate`, and `/indices/VWAP.KRW-BTC` verified visible page
controls without stored cookies or HAR capture. KGG01P's chart interval menu
exposed minute steps including `min:1`, `min:3`, and `min:10`; the page's daily
quote table uses `c-chart/kr-s/KGG01P/day:1` with `nextDateTime` cursor paging;
`scripts/indices.py --include-daily-quotes` exposes this table and accepts the
returned cursor through `--daily-quote-from`.
The public net-buying range widget exposed and accepted `range=week|month|year`.
The FX chart used `1d/min:5`, `1y/week:1`, and `5y/month:1`; a direct
`1y/day:1` FX check returned HTTP 400 and should not be assumed valid. The BTC
crypto-like page used `1d/min:5`, `1w/min:10`, `3m/day:1`, `1y/week:1`, and
`5y/month:1`, plus `c-chart/crypto/VWAP.KRW-BTC/day:1` for daily quote paging.

The same 2026-06-08 capture observed public detail/teaser widgets:
`/api/v1/dashboard/wts/overview/ai-signals/detail?productCode={code}&productType=INDEX|CURRENCY`
returned `terms`, `createdAt`, `signalId`, `traceId`, `signalDirection`,
`reasoning`, `relatedReasoning`, and `hasRelatedReasoning`. Treat the text as
untrusted page copy, not investment advice. News detail responses from
`/api/v2/news/{newsId}` currently have multilingual top-level keys such as
`availableLanguages`, `kr`, and `en`.

US equity index codes should be taken from the dashboard indicator payload, not
from common ticker aliases. Direct rechecks on 2026-04-29 accepted `SPX.CBI` for
S&P 500 and `COMP.NAI` for Nasdaq, while plain `SPX` and `NDX` returned 404/400
from the index info/price endpoints.

## Bond APIs

Observed from the deployed public `/bonds/[guid]` page bundle on 2026-08-05.
No stable public bond GUID was available from the logged-out navigation used for
this audit, so these routes are bundle-observed and intentionally not
script-backed. Re-open a current public bond page and confirm the exact response
shape before depending on either endpoint.

| Purpose | Status | Method | Path | Params and notes |
|---|---|---:|---|---|
| Bond detail | `observed` | GET | `/api/v1/bond-infos` | Query: `guid={bondGuid}`; the current page bundle passes one page GUID |
| Simple bond metadata | `observed` | GET | `/api/v1/bond-infos/simple` | Query: repeated `guids={bondGuid}` values; current bundle serializes arrays with repeated keys |

These endpoints are public-page bond metadata candidates, not the official
OAuth Open API and not evidence for account holdings, buying power, or bond
order workflows. Do not invent or enumerate GUIDs; use only a GUID visible on a
public TossInvest bond page.

## Analytics APIs

Observed from `/stocks/A005930/analytics`.

| Purpose | Status | Method | Path | Key response fields / notes |
|---|---|---:|---|---|
| Sales composition | `script-backed` | GET | `/api/v1/companies/{companyCode}/sales-compositions` | `code`, `fiscalYear`, `endDate`, `compositions[]`, `dataSource`; company code without leading `A` |
| Related themes/categories | `script-backed` | GET | `/api/v2/companies/{companyCode}/tics` | `baseDate`, `majorList[]`, `minorList[]`; company code without leading `A` |
| Stock overview | `script-backed` | GET | `/api/v2/stock-infos/{productCode}/overview` | `type`, `market`, `company`, `marketValueKrw`, `enterpriseValueKrw`, `dataSource`, `listDate`, `etp`, `etf`, `etn` |
| Business/holding composition | `script-backed` | GET | `/api/v2/stock-infos/{productCode}/compositions` | Observed result includes `code`, `type`, `fiscalYear`, `endDate`, `items[]`, `dataSource`; used for composition widgets |
| ETF/ETN investment detail | `observed` | GET | `/api/v2/stock-infos/{productCode}/investment` | Useful for ETF/ETN pages; observed result includes market/asset/NAV-style fields and base date fields |
| Consensus | `script-backed` | GET | `/api/v2/stock-infos/consensus/{productCode}` | `targetPrice`, `pointDate`, `pastClosePrices[]` |
| Analyst opinion | `script-backed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-opinion` | `type`, `strongSell`, `sell`, `hold`, `buy`, `strongBuy`, `targetPrice`, `description` |
| Analyst reports | `script-backed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-reports` | `analystReportGroups[]` with `displayDateAndEditor`, `analystReports`, `publishedAt` |
| Investment indicators | `script-backed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/investment-indicators` | `indicatorSections[]` with `sectionName`, `data` |
| Analytics section order | `script-backed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/section-orders` | UI ordering metadata |
| Dividend summary | `script-backed` | GET | `/api/v1/stock-infos/dividend/{productCode}/summary` | List items include `exDate`, `paymentDate`, `currency`, `ratio`, `cash`, `cashKrw`, `yieldRatio`, `ttmYieldRatio` |
| Dividend years | `script-backed` | GET | `/api/v1/stock-infos/dividend/{productCode}/years` | Dividend year options |
| Dividend yield history | `script-backed` | GET | `/api/v1/stock-infos/{productCode}/dividends/yield-ratio/histories` | Yield-ratio history |
| Comprehensive financial statements | `script-backed` | POST | `/api/v2/companies/{productCode}/financial-statements/comprehensive` | JSON body `{}` accepted in verification |
| Financial statement records | `script-backed` | POST | `/api/v2/companies/{productCode}/financial-statement-records` | JSON body `{}` accepted in verification |
| Financial estimate date | `script-backed` | GET | `/api/v2/companies/{productCode}/financial/estimate/date` | Estimate reference date |
| Revenue estimate | `script-backed` | POST | `/api/v2/companies/{productCode}/financial/estimate/revenue` | JSON body `{}` accepted in verification |
| EPS estimate | `script-backed` | POST | `/api/v2/companies/{productCode}/financial/estimate/eps` | JSON body `{}` accepted in verification |
| Operating income estimate | `script-backed` | POST | `/api/v2/companies/{productCode}/financial/estimate/operating-income` | JSON body `{}` accepted in verification |
| Valuation | `script-backed` | POST | `/api/v2/stock-infos/evaluation/{productCode}` | Result keys include `per`, `pbr`, `psr`, `median`, `position` |
| Valuation comparison | `script-backed` | POST | `/api/v2/stock-infos/evaluation-comparison/{productCode}` | Peer/sector comparison data |
| Stability | `script-backed` | POST | `/api/v2/stock-infos/stability/{productCode}` | Result keys include liability/current/coverage ratios |
| Revenue and net profit | `script-backed` | POST | `/api/v2/stock-infos/revenue-and-net-profit/{productCode}` | Result includes graph/table data |
| Operating income | `script-backed` | POST | `/api/v2/stock-infos/operating-income/{productCode}` | Result includes graph/table data |

POST examples:

```text
POST https://wts-info-api.tossinvest.com/api/v2/companies/A005930/financial-statements/comprehensive
Content-Type: application/json

{}
```

Observed response-shape highlights:

| Endpoint family | Result keys observed |
|---|---|
| `/financial-statements/comprehensive` | `selectedFactor`, `selectableFactors`, `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `graph`, `table` |
| `/financial-statement-records` | `selectedFactor`, `selectableFactors`, `selectedPeriod`, `selectablePeriods`, `isKr`, `table` |
| `/financial/estimate/revenue` | `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `revenueEst`, `revenueEstKrw`, `revenueEstJpy`, `fluctuation`, `fluctuationKrw`, `fluctuationRate`, `position`, `graphs`, `tables` |
| `/financial/estimate/eps` | `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `epsEst`, `epsEstKrw`, `epsEstJpy`, `fluctuation`, `fluctuationKrw`, `fluctuationRate`, `position`, `graphs`, `tables` |
| `/financial/estimate/operating-income` | `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `operatingIncomeEst`, `operatingIncomeEstKrw`, `operatingIncomeEstJpy`, `fluctuation`, `fluctuationKrw`, `fluctuationRate`, `position`, `graphs`, `tables` |
| `/evaluation` | `per`, `pbr`, `psr`, `median`, `position` |
| `/evaluation-comparison` | `selectedFactor`, `selectableFactors`, `selectableFactorsList`, `selectedTics`, `selectableTics`, `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `graphType`, `stockGraphs`, `stockTables`, `ticsStocks`, `median`, `position`, `ttmValue` |
| `/stability` | `liabilityRatio`, `currentRatio`, `interestCoverageRatio`, `median`, `position` |
| `/revenue-and-net-profit` | `companyName`, `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `recentFiscalYear`, `recentFiscalQuarter`, `recentNetProfit`, `recentNetProfitKrw`, `recentNetProfitJpy`, `fluctuationRate`, `position`, `graph`, `table` |
| `/operating-income` | `companyName`, `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `recentFiscalYear`, `recentFiscalQuarter`, `recentOperatingIncome`, `recentOperatingIncomeKrw`, `recentOperatingIncomeJpy`, `fluctuationRate`, `position`, `graph`, `table` |

## Filings And News APIs

Observed from stock detail, analytics bundles, and direct response checks.

| Purpose | Status | Method | Path | Params and notes |
|---|---|---:|---|---|
| Company filings list | `script-backed` | GET | `/api/v1/stock-detail/companies/{companyCode}/filings` | Query: `number`, `size`, optional `key`; observed result includes `pagingParam`, `body[]`, `lastPage` |
| Filing detail | `observed` | GET | `/api/v1/stock-infos/filings/companies/{companyCode}/report/{reportId}` | Query may include `reportItem`; observed in bundle for filing detail modal |
| Company news | `script-backed` | GET | `/api/v2/news/companies/{companyCode}` | Query can include `size`, `number`, `orderBy=latest`, and `orderBy=relevant`; observed result includes `pagingParam`, `body[]`, `lastPage` |
| News detail | `script-backed` | GET | `/api/v2/news/{newsId}` | Detail payload for a news item |
| Exclude headline news | `observed` | GET | `/api/v2/forum/news/headline/exclude/{newsId}` | Related/headline news excluding a selected item |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v1/stock-detail/companies/005930/filings?number=1&size=3
GET https://wts-info-api.tossinvest.com/api/v2/news/companies/005930?size=3
GET https://wts-info-api.tossinvest.com/api/v2/news/companies/005930?size=20&number=2&orderBy=latest
GET https://wts-info-api.tossinvest.com/api/v2/news/companies/005930?size=20&orderBy=relevant
```

## Transaction Status APIs

Observed from `/stocks/A005930/transaction-status`. On 2026-08-13, the program,
credit, lending, short-selling, and CFD sub-tabs kept this URL unchanged; treat
older `contentType` variants as historical client state, not stable deep links.

| Purpose | Status | Method | Path | Params and key response fields |
|---|---|---:|---|---|
| Broker trading ranking | `script-backed` | GET | `/api/v1/mds/broker/trading-ranking` | Query: `code={productCode}`; result includes `top5ActivityList[]`, foreign ask/bid volume/value fields, `updatedAt` |
| Investor trading trend | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/trading-trend` | Query: `productCode={productCode}&size=60`; result includes `pagingParam`, `body[]`, `lastPage` |
| Program trading | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/program-trading` | Query: `productCode={productCode}&size=50`; result includes `pagingParam`, `body[]`, `lastPage` |
| Fixed-date trading trend | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | Query: `productCode={productCode}&from={YYYY-MM-DD}&to={YYYY-MM-DD}`; result is a date-bounded list |
| Accumulated fixed trading trend | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | Query: `productCode`, `from`, `to`; observed rows include accumulated net investor-volume fields |
| Accumulated fixed trend detail | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | Query: `productCode`, `from`, `to`; observed object includes accumulated net detail fields by investor category |
| MDS info pages | `script-backed` | GET | `/api/v1/mds/info/{type}` | Query uses `stockCode`, `number`, `size`, optional `key`; direct checks accepted `credit`, `lending-trading`, `short-selling-trend`, and `cfd`; continue with the returned `pagingParam.number` and `pagingParam.key` |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v1/mds/broker/trading-ranking?code=A005930
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/trading-trend?productCode=A005930&size=60
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/program-trading?productCode=A005930&size=50
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A005930&from=2026-04-09&to=2026-04-16
GET https://wts-info-api.tossinvest.com/api/v1/mds/info/credit?stockCode=A005930&number=1&size=5
GET https://wts-info-api.tossinvest.com/api/v1/mds/info/lending-trading?stockCode=A005930&number=1&size=5
GET https://wts-info-api.tossinvest.com/api/v1/mds/info/short-selling-trend?stockCode=A005930&number=1&size=5
GET https://wts-info-api.tossinvest.com/api/v1/mds/info/cfd?stockCode=A005930&number=1&size=5
```

These transaction-status endpoints are KR-stock oriented in observed workflows.
Use KR TossInvest product codes such as `A005930`. Do not feed US opaque codes,
exchange-prefixed codes (`AMX...`, `NAS...`, `NYS...`), or `Q...` codes into the
KR domestic-flow/trading-trend collectors unless current browser traffic verifies
that exact use case; a 2026-05-10 smoke check returned HTTP 400 for
`productCode=AMX0221116003` on `trading-trend`.

Notes:

- Historical `contentType=net-buy` URL state did not introduce a separate API;
  the current sub-tabs did not rewrite the URL.
- Treat `from` and `to` as dynamic dates derived by the page, not hard-coded constants.
- Direct response checks showed top-level key `result` for all four endpoints above.
- `fixed-trading-trend` is the preferred endpoint for date-bounded pension-fund history. It returned rows back to `2019-04-01` for `A005930` in verification; earlier ranges returned no rows.
- Long date-bounded requests may be truncated. A single `A005930` request from `2019-04-01` through `2026-04-16` returned 1,731 rows; query by year or smaller windows for stable history collection.
- Use `scripts/pension_fund_trend.py --year YYYY` for one calendar year or `--all-history --format csv --output pension.csv` for yearly-window collection from the verified history start. Use `--summary-only` when only row count, net total, and net-buy/net-sell day counts are needed.

Observed investor trend row keys include:

```text
baseDate,
individualsBuyVolume, individualsSellVolume, netIndividualsBuyVolume,
foreignerBuyVolume, foreignerSellVolume, netForeignerBuyVolume,
institutionBuyVolume, institutionSellVolume, netInstitutionBuyVolume,
netFinancialInvestmentBuyVolume,
netInsuranceBuyVolume,
netOtherFinancialInstitutionsBuyVolume,
netTrustBuyVolume,
netPrivateEquityFundBuyVolume,
netPensionFundBuyVolume,
netBankBuyVolume,
netOtherCorporationBuyVolume
```

Recommended normalized investor taxonomy for KR net-flow rows:

| Normalized type | Korean UI label | Net field |
|---|---|---|
| `individual` | 개인 | `netIndividualsBuyVolume` |
| `foreigner` | 외국인 | `netForeignerBuyVolume` |
| `institution_total` | 기관계 | `netInstitutionBuyVolume` |
| `financial_investment` | 금융투자 | `netFinancialInvestmentBuyVolume` |
| `insurance` | 보험 | `netInsuranceBuyVolume` |
| `other_financial` | 기타금융 | `netOtherFinancialInstitutionsBuyVolume` |
| `trust` | 투신 | `netTrustBuyVolume` |
| `private_equity_fund` | 사모펀드 | `netPrivateEquityFundBuyVolume` |
| `pension_fund` | 연기금등 | `netPensionFundBuyVolume` |
| `bank` | 은행 | `netBankBuyVolume` |
| `other_corporation` | 기타법인 | `netOtherCorporationBuyVolume` |

Institution total is an aggregate row; other corporation is a separate category, not part of institution-detail totals.

Observed pension-fund fields:

```text
netPensionFundBuyVolume
```

Observed program trading row keys include:

```text
baseDate,
arbitrageBuyQuantity, arbitrageSellQuantity, arbitrageNetBuyQuantity,
nonArbitrageBuyQuantity, nonArbitrageSellQuantity, nonArbitrageNetBuyQuantity,
totalBuyQuantity, totalSellQuantity, totalNetBuyQuantity
```

Observed 2026-05-29 transaction-status UI sub-tabs map as follows:

| UI sub-tab | Endpoint family | Selected row keys |
|---|---|---|
| Program trading | `/api/v1/stock-infos/trade/trend/program-trading` | `totalNetBuyQuantity`, `nonArbitrageNetBuyQuantity`, `arbitrageNetBuyQuantity` |
| Credit | `/api/v1/mds/info/credit` | `marginLoanBalanceQuantity`, `marginLoanIncreaseDecreaseQuantity`, `marginLoanBalanceRate` |
| Lending trading | `/api/v1/mds/info/lending-trading` | `executionQuantity`, `repaymentQuantity`, `lendingTradingBalanceVolume`, `lendingTradingBalanceAmount` |
| Short selling | `/api/v1/mds/info/short-selling-trend` | `shortTradingVolume`, `shortTradingAmount`, `shortSellingTradingAmountRatio`, `shortSellingAveragePrice` |
| CFD | `/api/v1/mds/info/cfd` | `newBuyQuantity`, `settleBuyQuantity`, `buyBalanceQuantity`, `sellBalanceQuantity` |

## Dashboard And Discovery APIs

Observed on home, stock detail, analytics, and transaction-status pages.

| Purpose | Status | Method | Path | Notes |
|---|---|---:|---|---|
| Realtime stock ranking | `observed` | GET | `/api/v1/rankings/realtime/stock?size=10` | Ranking widgets |
| Dashboard intelligences | `observed` | POST | `/api/v1/dashboard/intelligences/all` | Empty observed body |
| Observed legacy/detail AI signals | `observed` | POST | `/api/v1/dashboard/wts/overview/ai-signals` | Home/detail signal data; not used by `dashboard_ranking.py --kind signals` |
| Signal details | `script-backed` | GET | `/api/v1/dashboard/wts/overview/ai-signals/detail?productCode={productCode}&productType=STOCKS` | Per-stock signal detail used by `scripts/stock_page.py`; treat text as page copy, not advice |
| Overview stock signals | `script-backed` | GET | `/api/v1/dashboard/wts/overview/signals?codes={codes}` | Direct 2026-05-29 check returned `stockCode` and `signals[]`; used for the home live-chart `TossInvest AI summary` column |
| Exchange rates | `script-backed` | GET | `/api/v1/dashboard/wts/overview/exchange-rates` | FX/overview data |
| Trading info | `observed` | GET | `/api/v1/dashboard/wts/overview/trading-info` | Market overview data |
| WTS news feed | `observed` | GET | `/api/v1/dashboard/wts/news` | Feed/news panel data; `scripts/feed.py` uses the POST form documented under Feed And News APIs |
| Public WTS search | `script-backed` | POST | `/api/v3/search-all/wts-auto-complete` | `scripts/market_search.py`; body contains a bounded query plus observed `PRODUCT`, `NEWS`, `TICS`, `SCREENER`, and `MARKET_INDEX` sections; output is limited and field-filtered |
| Home live-chart top100 ranking | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | Body maps URL params to `id={live-chart}`, `tag={market}`, `duration`; returns `products[]`, usually 100 rows; page refresh interval observed as 10 seconds and current-price cells receive per-product WebSocket overlays |
| Realtime investor rankings | `script-backed` | GET | `/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` | Observed under `wts-cert-api`; `rankings.foreigner`, `.institution`, and `.individual` each expose `buyStocks` and `sellStocks`; the script emits the chosen side as `selectedRankings` |
| Economic calendar | `script-backed` | GET | `/api/v2/dashboard/wts/overview/calendar/economic-events` | Observed under `wts-cert-api`; result list includes `id`, `date`, `title` |
| Calendar AI key events | `script-backed` | GET | `/api/v1/calendar/ai-summary/key-events` | Direct 2026-05-30 check returned `eci` and `earnings[]`; public market-calendar context |
| Current home industry ranking | `script-backed` | POST | `/api/v2/dashboard/wts/overview/tics/ranking` | Body: `nation=KR|US`, `duration=1d|1w|1m|3m|1y`, `sortBy=FLUCTUATION_RATE|TRADING_AMOUNT`; result has `basedAt`, `duration`, `tics[]`; deployed page refresh interval observed as 10 seconds |
| Current sector overview | `script-backed` | GET | `/api/v2/dashboard/wts/overview/tics/{ticsId}/overview` | `ticsId`, `name`, `description`, `summary`, `companyCount`, `etfCount`, `depth`, `relatedTics[]` hierarchy |
| Current sector compact header | `script-backed` | GET | `/api/v2/dashboard/wts/overview/tics/{ticsId}/simple` | Query: `nation=KR|US`, `duration=1d|1w|1m|3m|1y`; result includes `changeRate`, `imageUrl`, `name`, `summary` |
| Current sector comparison chart | `script-backed` | GET | `/api/v1/dashboard/wts/overview/tics/{ticsId}/comparison-chart` | Query: `nation`, `securitiesType=STOCK`, `indicatorCode`; current selector exposes `SPX.CBI`, `COMP.NAI`, `KGG01P`, `QGG01P`; result has `baseDate`, `indicators[]` |
| Current sector stocks | `script-backed` | POST | `/api/v2/dashboard/wts/overview/tics/{ticsId}/stocks` | Body: `nation=ALL|KR|US`, `sortBy=MARKET_CAP|TRADING_VALUE|VOLUME|ANALYST`, `sortOrder=ASC|DESC`, one-based `page`; fixed `size=10` response with `stocks[]`, `totalCount`; page refetch observed every 10 seconds |
| Current sector ETFs | `script-backed` | POST | `/api/v2/dashboard/wts/overview/tics/{ticsId}/etfs` | Body: `nation=ALL|KR|US`, `sortBy=TRADING_VALUE|EXPENSE_RATIO`, `sortOrder=ASC|DESC`, `includeLeverageInverse`, one-based `page`; fixed `size=10` response with `etfs[]`, `totalCount`; page refetch observed every 10 seconds |
| Current sector news | `script-backed` | GET | `/api/v2/dashboard/wts/overview/tics/{ticsId}/news` | Query: one-based `number`; fixed page size 5; result has `body[]`, `lastPage`, `pagingParam`, `totalCount`; news clicks open the existing `/api/v2/news/{newsId}` detail flow |
| Auxiliary TICS ranking | `observed` | GET | `/api/v1/tics/rankings` | Current bundle-defined read-only route; direct check returned ranking metadata plus `data[]`; do not confuse it with the current home industry POST ranking |
| Theme list | `script-backed` | GET | `/api/v1/tics/all` | Observed result includes `baseDateTime`, `ticsItems[]` |
| Theme ranking by tag | `script-backed` | GET | `/api/v1/rankings/contents/tics_margin_depth1/tags/{tag}` | Observed tags include market-style values such as `kr`/`us`; result contains ranking metadata and rows |
| Theme details | `script-backed` | GET | `/api/v1/tics/{ticsId}/details` | Returned `id`, `title`, `summary`, `description`, `companyCount`, `etfCount`, `stocks[]` |
| Theme company ranking | `script-backed` | GET | `/api/v1/companies/tics/rankings?ticsId={ticsId}&ticsRanking={ranking}` | Ranking data for a theme/category |
| Related themes | `script-backed` | GET | `/api/v1/tics/{ticsId}/related` | Related categories for a theme page |
| Theme news | `script-backed` | GET | `/api/v2/news/tics/{ticsId}` | Query can include `size`; related news for a theme |
| Theme fluctuations | `script-backed` | GET | `/api/v2/tics/{ticsId}/fluctuations` | Theme fluctuation/history data |
### Current Industry Dashboard And Sector Behavior

The 2026-08-04 industry-page check established three different paging models:

- the home industry ranking returns the full ranked `tics[]` snapshot and has no server page field;
- `/stocks` and `/etfs` use one-based server pages of 10 rows; sorting or nation changes reset the UI page to 1;
- `/news` uses one-based `number` pages of 5 rows, while the sector sidebar slices the already-loaded home ranking into client-side pages of 10 rows.

`scripts/sector.py` preserves the applied request values and emits separate
catalog-check and runtime-fetch timestamps. Its `clientMaxPage=100` metadata is
a local safety cap, not an observed server maximum; the transport label remains
`rest_snapshot` because the generic stock-trade WebSocket overlay is not merged
into the composite.

Home URL state uses `ranking-type=trending_category` plus optional
`tics-nation`, `tics-duration`, `tics-sort`, and `focusedTicsId`. Clicking another
home ranking tab clears `focusedTicsId` and `focusedProductCode`; the TICS filter
parameters remain in the URL even while another ranking tab is selected. On a
sector detail page, the `nation=KR|US` query seeds the header/chart market, but a
later header market click changes local UI state without rewriting the URL.

The home `focusedTicsId` aside reuses the current `/simple`,
`/comparison-chart`, `/stocks`, and `/etfs` endpoints. Its stock request sends
`{nation, page: 1}` and its ETF request sends `{nation}`, relying on server
defaults for omitted sort and toggle fields. The aside displays the first five
rows from each response and refreshes those stock and ETF requests on a
one-minute interval. The `종목 전체보기` action navigates to
`/sector/{ticsId}?nation=KR|US`.

Screener endpoints are documented only in [Screener APIs](#screener-apis) to keep
their `wts-cert-api` handling and filter-body constraints in one place.

## Calendar APIs

Observed on `https://www.tossinvest.com/calendar` during the 2026-05-30
recheck, and on public `/calendar/economic-indicator` plus index-page calendar
subsets during the 2026-06-01 recheck. These endpoints live under
`wts-cert-api`, so keep exact or pattern-scoped allowlisting and do not use
cookies, auth headers, account identifiers, or personalized filters.
`scripts/calendar.py` applies the public page's monthly event filters locally.

| Purpose | Status | Method | URL | Notes |
|---|---|---:|---|---|
| Monthly market calendar | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}` | Empty JSON body; returns `events[]`; validate `{YYYY-MM}` as month `01`-`12` only |
| Index-page calendar subset | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v4/calendar/monthly/{YYYY-MM}/index?countryType=kr|us` | Empty JSON body; returns `events[]` for the index page's country-specific calendar block |
| Economic indicator detail | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/calendar/economic-indicators/{ric}?announceDate={YYYY-MM-DD}` | Public `/calendar/economic-indicator` detail payload; result keys include `announcementDate`, `announcementTime`, `indicatorDetail`, `historicalData`, `relatedArticles`, `upcomingIndicators`, and `upcomingLive` |
| Economic indicator AI analysis | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/analysis/indicators?announceDateTime={YYYY-MM-DDTHH:mm:ss}&ricId={ric}` | Public detail-page AI analysis text; derive `announceDateTime` and `ricId` from the detail response when possible |
| Calendar key events | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/calendar/ai-summary/key-events` | Returns `eci.indicators[]` and `earnings[]` for the public key-events block |
| Weekly AI summary | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/nova-calendar/ai/summary/weekly` | Returns `title`, `contents`, `additionalContents`, `cacheCreatedAt`, and `contentSources[]`; treat as public page text, not investment advice |
| Overview economic events | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/calendar/economic-events` | Compact public economic-event list used by overview widgets |

Monthly calendar category filters observed in the page bundle:

| UI tab | `scripts/calendar.py` selector | Event rule |
|---|---|---|
| 전체 | `--kind monthly` | All events except `excludeFromAll=true` |
| 경제지표 | `--kind economic` | `event.id.group == "ECONOMIC"` |
| 실적 | `--kind earnings` | `event.id.group` is `KRX_EARNINGS_ANNOUNCEMENT` or `USD_EARNINGS_ANNOUNCEMENT` |
| 국내 | `--kind domestic` or `--country kr` | Applies the same category behavior as the selected category, then filters economic `view.economicIndicatorValue.countryType == "kr"` or earnings `stockEarnings.countryType == "kr"`; with default `--category all`, still excludes `excludeFromAll=true` |
| 해외 | `--kind overseas` or `--country us` | Applies the same category behavior as the selected category, then filters economic `view.economicIndicatorValue.countryType == "us"` or earnings `stockEarnings.countryType == "us"`; with default `--category all`, still excludes `excludeFromAll=true` |

The page bundle also exposes earnings stock-category labels such as `HOLDING`
and `WATCHLIST`; do not script those as public filters unless a current
unauthenticated capture proves they are non-personalized public data.

The index-page subset route is separate from the main `/calendar` page. It
accepts only `countryType=kr|us`, uses an empty POST body, and should not be
extended to arbitrary query keys. The economic-indicator detail route is linked
from monthly economic events via `view.economicIndicatorValue.ric` plus the
event `date`.

## Dashboard And Screener Page Behavior

Direct checks on 2026-04-20 for `scripts/theme.py --tag kr --include-all --tics-id 289 --include-details --company-ranking marketcap --company-ranking revenue --company-ranking operating-margin` returned `ranking`, `allThemes`, `details`, `related`, `news`, `fluctuations`, and all three requested company ranking groups.

Observed `ticsRanking` values:

| Value | Meaning observed in UI |
|---:|---|
| `1` | Market capitalization |
| `3` | Revenue |
| `4` | Operating margin |

Observed home live-chart values from `https://www.tossinvest.com/?market={market}&live-chart={id}&duration={duration}`:

| UI label | `live-chart` / request `id` | Typical `duration` | Notes |
|---|---|---|---|
| 토스증권 거래대금 | `biggest_total_amount` | `realtime` | Toss Securities internal trading amount ranking |
| 토스증권 거래량 | `biggest_total_volume` | `realtime` | Toss Securities internal trading volume ranking |
| 거래대금 | `biggest_market_amount` | `realtime` | Market trading amount ranking |
| 거래량 | `biggest_market_volume` | `realtime` | Market trading volume ranking |
| 급상승 | `heavy_soar` | `1d` | Market price-rise ranking |
| 급하락 | `heavy_descent` | `1d` | Market price-decline ranking |
| 인기 | `realtime_stock` | `realtime` | Realtime popular stock ranking |

The 2026-07-16 duration menu mapped `1일`, `1주일`, `1개월`, `3개월`,
`6개월`, `1년`, and `실시간` to `1d`, `5d`, `20d`, `60d`, `120d`,
`240d`, and `realtime`. `scripts/dashboard_ranking.py` accepts all seven
values.

Observed request shape:

```text
POST https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking
Content-Type: application/json

{"id":"biggest_total_amount","tag":"kr","duration":"realtime","filters":[]}
```

The logged-out home bundle and live page checked on 2026-07-16 implement
`투자위험 주식 숨기기` as one composite ranking filter. The checked state sends
all three observed filter ids:

```json
{
  "id": "biggest_total_amount",
  "tag": "us",
  "duration": "realtime",
  "filters": [
    "KRX_MANAGEMENT_STOCK",
    "MARKET_CAP_GREATER_THAN_50M",
    "STOCKS_PRICE_GREATER_THAN_ONE_DOLLAR"
  ]
}
```

Use `scripts/dashboard_ranking.py --hide-investment-risk` to reproduce that
composite. The frontend names indicate filters for KRX management stocks, US
market capitalization above USD 50 million, and US prices above USD 1. Treat
this as the public page's current discovery filter, not as a complete legal or
investment-risk classification API. A direct logged-out US ranking comparison
returned 100 rows in both cases while rotating 29 products out of that live
snapshot; ranking membership and exact counts change with the market.

For the user-provided top100 URLs checked on 2026-04-20, `market=kr`/`us` maps to `tag=kr`/`us`. The `biggest_total_amount`, `biggest_total_volume`, `heavy_soar`, and `heavy_descent` combinations returned `products[]` with 100 rows for both markets in direct response checks.

The 2026-07-10 logged-out bundle and page check confirmed that top100 is a
hybrid rather than a dedicated ranking WebSocket channel:

- the overview ranking POST is configured with a 10-second refresh interval;
- both KR and US pages rendered 100 unique stock links plus the grid header;
- each rendered product registers its code with the shared real-time price
  store, which reference-counts and deduplicates the product trade destination;
- US rows visibly changed current price and change rate within five seconds,
  while rank, amount, market capitalization, TossInvest buy/sell ratio,
  industry, and AI summary remained snapshot fields;
- a mirror client should maintain one ranking view, one shared connection, and
  at most 100 product destinations, applying only the added/removed code diff
  after each HTTP refresh.

Additional WebSocket consumers found in the same deployment include public
quote-volume and KR pre-open estimate fields on the bid/offer destination, and
a KR stock-status destination used only to invalidate and refetch the public
trading-status HTTP helper. See
[websocket-api-reference.md](websocket-api-reference.md) for evidence labels and
the memory-only guest-session boundary.

The expanded 2026-07-10 logged-out navigation audit also opened the home search
dialog, industry and investor-trend tabs, a public US sector, the screener,
news/recommended feeds, all public stock-detail tabs, and each index link shown
on the home page. The recurring architecture was:

- search, industry membership, investor ranking, news/feed items, sector
  membership, screener results, and detail widgets are HTTP datasets;
- rendered stock cards register product codes with the shared real-time price
  store, so price/change chips can receive per-product trade overlays;
- screener results request `pagingParam.number` with `size: 50` and are exposed
  through a virtualized infinite list;
- candle history uses the HTTP `nextDateTime`/`from` cursor while a trade event
  updates only the current candle;
- feed and community history use HTTP cursors rather than WebSocket paging;
- the SOXL page title visibly changed across the order, analytics, news,
  transaction-status, and community routes, but the full bid/offer panel asked
  the logged-out user to sign in.

Public index navigation succeeded for `COMP.NAI`, `SPX.CBI`, `RGI..VIX`,
`KGG01P`, `QGG01P`, `SOX.NAI`, `VWAP.KRW-BTC`, and the HTTP-only
`exchange-rate` page.
`DJI.DJI`, `RFU.NQc1`, and `RFU.GCv1` redirected to sign-in during the same
check; do not treat a destination builder as authorization to bypass that
route-level access boundary.

Observed 2026-05-29 home tabs are live chart, trending categories, and domestic
investor trend. The live chart table still uses the overview ranking endpoint,
and the visible `TossInvest AI summary` column is backed by the overview stock
signals helper:

```text
GET https://wts-info-api.tossinvest.com/api/v1/dashboard/wts/overview/signals?codes=A005930,A000660
```

Observed RSI screener filter request shape:

```text
POST https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count
Content-Type: application/json

{
  "filters": [
    {
      "id": "RSI_범위",
      "conditions": [
        {
          "id": "NUMBER_RANGE_DEFAULT",
          "type": "NUMBER_RANGE",
          "value": {
            "from": null,
            "to": 30,
            "includeFrom": null,
            "includeTo": true
          }
        }
      ]
    }
  ],
  "nation": "kr"
}
```

Use `to: 30` / `includeTo: true` for an oversold-style screen and
`from: 70` / `includeFrom: true` for an overbought-style screen. Direct checks on
2026-04-20 returned counts for both `kr` and `us`. The results endpoint accepted
the same `filters[]` plus `pagingParam: {"number": 1, "size": 5}` and returned
stock rows.

Observed sort shape from Playwright capture and direct API checks:

```text
{
  "sort": {
    "column": "C_시가총액",
    "label": "시가총액",
    "order": "DESC"
  }
}
```

The checked sortable columns were `C_시가총액` / `시가총액`, `C_거래량` /
`거래량`, and `C_애널리스트평점` / `애널리스트 분석`. Other sort columns should be
captured from current browser traffic before use.

Observed price-condition screener filter IDs:

| Preset area | Filter id | Condition ids | Types | Verified default value |
|---|---|---|---|---|
| Price change | `주가등락률` | `기간_선택_DAY_TO_MONTH`, `NUMBER_RANGE_DEFAULT` | `PERIOD`, `NUMBER_RANGE` | `DAY_5` + `from=0.05`, `DAY_20` + `from=0.10`, or `DAY_5` + `to=-0.05` |
| Consecutive rise | `주가_연속_상승` | `NUMBER_RANGE_DEFAULT` | `NUMBER_RANGE` | `from=5`, `includeFrom=true` |
| Consecutive fall | `주가_연속_하락` | `NUMBER_RANGE_DEFAULT` | `NUMBER_RANGE` | `from=5`, `includeFrom=true` |
| 52-week high | `CUSTOM_N주_신고가_달성_경과일` | `WEEK_NEW_PRICE_HIT` | `WEEK_NEW_PRICE_HIT_WITHIN` | `numberOfWeeks=52`, `within=20` |
| 52-week low | `CUSTOM_N주_신저가_달성_경과일` | `WEEK_NEW_PRICE_HIT` | `WEEK_NEW_PRICE_HIT_WITHIN` | `numberOfWeeks=52`, `within=20` |

Example 52-week high filter:

```text
{
  "id": "CUSTOM_N주_신고가_달성_경과일",
  "conditions": [
    {
      "id": "WEEK_NEW_PRICE_HIT",
      "type": "WEEK_NEW_PRICE_HIT_WITHIN",
      "value": {
        "numberOfWeeks": 52,
        "within": 20
      }
    }
  ]
}
```

Observed technical-analysis screener filter IDs:

| Preset area | Filter id | Condition id | Type | Verified default value |
|---|---|---|---|---|
| Price moving-average cross | `CUSTOM_주가_이동평균선_돌파` | `주가_이동평균선_돌파` | `PRICE_MOVING_AVERAGE_CROSS_ARRAY` | `period=20`, `within=5`, `crossDirection=upward/downward` |
| Moving-average cross | `CUSTOM_이동평균선_돌파` | `이동평균선_돌파` | `MOVING_AVERAGE_CROSS_ARRAY` | `shortPeriod=5`, `longPeriod=20`, `within=5`, `crossDirection=upward/downward` |
| Volume moving-average cross | `CUSTOM_거래량_이동평균선_돌파` | `이동평균선_돌파` | `MOVING_AVERAGE_CROSS_ARRAY` | `shortPeriod=5`, `longPeriod=20`, `within=5`, `crossDirection=upward/downward` |
| Moving-average alignment | `CUSTOM_이동평균선_배열` | `이동평균선_배열` | `MOVING_AVERAGE_ALIGN_ARRAY` | `shortPeriod=5`, `midPeriod=20`, `longPeriod=60`, `within=5`, `alignType=positive/negative` |
| Price Bollinger Band cross | `CUSTOM_주가_볼린저밴드_돌파` | `주가_볼린저밴드_돌파` | `PRICE_BOLLINGER_BAND_CROSS_ARRAY` | `within=5`, `crossBand=upper/lower`, `crossDirection=upward/downward` |

Example price moving-average cross filter:

```text
{
  "id": "CUSTOM_주가_이동평균선_돌파",
  "conditions": [
    {
      "id": "주가_이동평균선_돌파",
      "type": "PRICE_MOVING_AVERAGE_CROSS_ARRAY",
      "value": [
        {
          "period": 20,
          "within": 5,
          "crossDirection": "upward"
        }
      ]
    }
  ]
}
```

## Feed And News APIs

Observed from `/feed/recommended` and `/feed/news`. Keep only feed endpoints that can help with public market or stock-news discovery. Do not catalog followings, subscriptions, or account-personalized feed endpoints.

| Purpose | Status | Method | URL/path | Params/body and notes |
|---|---|---:|---|---|
| Historical recommended feed posts | `needs-recheck` | GET | `/api/v3/feed/recommend/posts` | Returned HTTP 404 in the bounded 2026-08-13 direct check; do not retry or fall back to this stale path |
| Current recommended feed posts | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | Optional `lastRecommendId`; current public `/feed/recommended` traffic; `feed.py --kind recommended` emits only sanitized comments plus `nextLastRecommendId` |
| Dashboard/news tab feed | `script-backed` | POST | `/api/v1/dashboard/wts/news` | Body `{ "type": "HOT" }` etc.; result includes `type`, `title`, `news[]` |
| News detail | `script-backed` | GET | `/api/v2/news/{newsId}` | Detail payload for a selected news item |

Cataloged public dashboard news `type` values:

```text
ALL_HIGHLIGHT, HOT, SOARING_STOCK, INDEX
```

Observed 2026-05-29 `/feed/news` UI mapping:

| UI label | API `type` | Script status |
|---|---|---|
| Major news | `ALL_HIGHLIGHT` | `scripts/feed.py --kind news --news-type ALL_HIGHLIGHT` |
| Latest news | `HOT` | `scripts/feed.py --kind news --news-type HOT` |
| Soaring-stock news | `SOARING_STOCK` | `scripts/feed.py --kind news --news-type SOARING_STOCK` |
| Index news | `INDEX` + `indexCode` | `scripts/feed.py --kind news --news-type INDEX --index-code KGG01P` |
| Popular news | `PERSONALIZED` | excluded because it is personalized |

`INDEX` requires `indexCode`, for example:

```text
POST https://wts-info-api.tossinvest.com/api/v1/dashboard/wts/news
Content-Type: application/json

{"type":"INDEX","indexCode":"KGG01P"}
```

## Screener APIs

Most screener endpoints currently live under `wts-cert-api`. They can return public visible market data, but treat them as sensitive-host endpoints and avoid user-specific preset mutations.

| Purpose | Status | Method | URL/path | Params and notes |
|---|---|---:|---|---|
| Common screener presets | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v2/screener/presets/common?useCustom=true` | Returned 11 preset definitions in 2026-05-29 verification; `scripts/screener_count.py --include-common-presets` fetches this metadata |
| Screener search modal | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen/search/modal` | Returned 3 suggested preset entries in 2026-05-29 verification; `scripts/screener_count.py --include-search-modal` fetches this metadata |
| Screener base filters | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/base` | `--include-filter-base`; exact body `{filterId, nation}` for selected allowlisted filters; returns `basedAt` |
| Screener range filters | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/range` | `--include-filter-range`; exact body `{filter, nation}` using a filter already accepted by `validate_filters`; returns current `min`/`max` |
| Screener result count | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count` | Body shape `{ "filters": [], "nation": "kr" }` or `"us"` returned counts in verification; RSI, selected price, and selected technical filters accepted `conditions[]` |
| Screener results | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen` | Body includes `pagingParam`, `filters`, `sort`, and `nation`; current UI requests numbered 50-row pages (`size: 50`) and renders them through a virtualized infinite list |

Examples:

```text
POST https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count
Content-Type: application/json

{"filters":[],"nation":"kr"}
```

Combination checks on 2026-04-20, with no cookies or auth headers, returned
result rows for:

- `--rsi oversold --include-results --size 5`
- `--price-filter price-change-5d-up-5 --technical-filter price-ma-cross-up --include-results --sort volume --size 5`
- `--price-filter new-high-52w-within-20d --technical-filter ma-align-positive --technical-filter volume-ma-cross-up --include-results --sort market-cap --size 5`
- `--price-filter new-low-52w-within-20d --technical-filter bollinger-lower-down --include-results --sort volume --size 5`
- `--nation us --rsi overbought --include-results --size 5`

Additional 2026-05-29 checks showed this public preset list:
`연속 상승세`, `저평가 성장주`, `아직 저렴한 가치주`, `꾸준한 배당주`,
`돈 잘버는 회사 찾기`, `저평가 탈출`, `미래의 배당왕 찾기`, `성장 기대주`,
`쌍끌이 매수`, `고수익 저평가`, and `안정 성장주`. The selected
`연속 상승세` preset includes `searchExposedColumns=["C_주가등락률_1W"]`
and sort `{"column":"C_주가등락률_1W","label":"주가등락률","order":"DESC"}`.
The result columns are still returned by `/api/v2/screener/screen`; visible
sortable columns include market capitalization, volume, analyst rating, and
the preset-specific `C_주가등락률_1W` column.

The public `/screener/{preset-id}` route reuses these count/result families.
`/screener/4` rendered the selected preset, filters, and virtualized result list
without login in the 2026-08-13 check; preset ids remain page identifiers, not
permission to call mutation or user-preset routes.

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

Additional web check: 2026-07-08 for `/?focusedProductCode=US20100311002`,
`/stocks/US20100311002/community`, `/feed/recommended`, and `/feed/news`.
These routes rendered without login and returned HTTP 200 from public APIs.
Additional logged-out check: 2026-08-13 for
`/community/lounges/LOUNGE_193394`, `/community/posts/{post-id}`, and the
recommended-feed v4 continuation shape.

Use `scripts/stock_page.py` when the user asks for the public stock main-page
bundle: resolved product metadata, price details, AI signal detail, and
sanitized public comments. Use `scripts/community_comments.py` for comments,
lounges, or public post permalinks; stock mode resolves display symbols through
`code-or-symbol` before comment lookup.

| Purpose | Status | Method | Path | Params and notes |
|---|---|---:|---|---|
| Stock page composite | `script-backed` | mixed | `scripts/stock_page.py` | Uses `code-or-symbol`, price details, AI detail, optional red flags/trading status/trading analysis, and sanitized comments |
| Public stock comments | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/comments` | Query exactly `subjectType=STOCK`, `subjectId={stockInfo.guid}`, `commentSortType=POPULAR|RECENT`, optional `lastCommentId`; resolve every product code or display symbol through `code-or-symbol` first. Confirmed 2026-09-07: `A005930` must use `KR7005930003`; sending the product code returned an empty result despite visible comments. Accept a prior cursor through `--last-comment-id`. |
| Public lounge comments | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/comments` | Query exactly `subjectType=LOUNGE`, `subjectId=LOUNGE_{digits}`, `commentSortType=POPULAR|RECENT`, optional `lastCommentId`; same sanitizer, start-cursor option, and page limits as stock comments |
| Public comment replies | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v2/comments/{commentId}/replies` | Sanitized reply rows; v1 replies also observed but v2 is preferred |
| Public community post permalink and replies | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/comments/{postId}/replies` | Result has `topic`, `comment`, and `replies.body`; optional numeric `lastReplyId` continues replies; `community_comments.py --post-id --last-reply-id` sanitizes both the post and reply rows |
| Stock community related board | `public-social-sensitive` | GET | `https://wts-cert-api.tossinvest.com/api/v1/boards/STOCK/{productCode}/related` | Board metadata only |
| Stock community recommended profiles | `public-social-sensitive` | GET | `https://wts-cert-api.tossinvest.com/api/v1/community/board/{productCode}/recommend-profiles` | Public profile suggestions; strip profile ids, URLs, avatars, and follow flags before display |
| Popular-follower feed support | `public-social-sensitive` | GET | `https://wts-cert-api.tossinvest.com/api/v1/boards/popular-follower` | Observed in current public feed traffic; no first-class script output; sanitize any future wrapper before exposing fields |
| Community top rankings | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | `scripts/feed.py --kind community-ranking`; only the two exact allowlisted ranking ids are used, output is capped at 10 rows, and profile ids/URLs/follow flags are removed |
| Feed community ranking posts | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | Public `/feed/recommended` traffic; optional `lastRecommendId`; both recommended CLI aliases sanitize posts and normalize `nextLastRecommendId` |

Observed `GET /api/v4/comments` response shape:

- Top-level keys: `results`, `hasNext`, `key`, `totalCount`
- Page size observed: 11
- Pagination: pass `lastCommentId={key}` for the next page
- Comment row keys include `commentId`, `author`, `authorUserProfileId`,
  `message`, `statistic`, `holding`, `board`, `createdAt`, and `updatedAt`

Sanitization requirements:

- Keep only UI-useful fields such as `commentId`, `authorNickname`, message
  text, board topic, holding status, created/updated timestamps, and counts.
- Remove profile ids, avatar/profile URLs, profile descriptions, follower
  counts, follow/bookmark/my-profile flags, and account-personalized fields.
- Remove numeric profile ids embedded in public mention markup while retaining
  the visible mention label.
- Redact obvious phone, email, and long-number strings from free-form text.
- Keep pagination bounded; do not bulk harvest public social content.
- Treat v4 feed `feeds[].comment` and permalink v1 `comment`/`replies.body[]`
  as the same sanitizer boundary; never expose either source object directly.

Observed drift, excluded, and sensitive public-social endpoints:

| Endpoint | Status | Reason |
|---|---|---|
| `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator` | `observed-drift` | Home traffic exposes newer overview indicator aggregate; current scripts use narrower indicator routes |
| `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | `script-backed` | Current home aggregate is exposed through `dashboard_ranking.py --kind indicator`; the client permits only the exact GET path with no query or body |
| `https://wts-info-api.tossinvest.com/api/v2/dashboard/wts/overview/signals` | `observed-drift` | Home traffic also exposes a v2 signals route; `dashboard_ranking.py --kind signals` remains on the verified public v1 helper |
| `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-buy` | `excluded` | `wts-api` exchange quote route observed on exchange-rate page; keep out until exact host/path safety review |
| `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-sell` | `excluded` | Same as above |
| `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | `public-social-sensitive` | Public community/social ranking surface; only verified ranking ids are allowed and outputs must be sanitized |
| `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | `public-social-sensitive` / `script-backed` | Current feed route; `feed.py --kind recommended` and its compatibility alias sanitize every emitted post |

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
