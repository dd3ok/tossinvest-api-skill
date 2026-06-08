# TossInvest Web API Catalog

Base observation date: 2026-04-16
Additional bundle/API check: 2026-04-20 against `buildId=SUN83tZwsh5murULLiDPr`
Additional page check: 2026-04-20 for `/stocks/A005930/order`, home ranking variants, `/indices/KGG01P`, `/feed/recommended`, and `/feed/news`
Additional direct recheck: 2026-04-29 for US `c-chart` product candles and US overview indicator codes.
Additional page/API recheck: 2026-05-29 for home tabs, stock detail tabs, `/screener`, `/feed/news`, `/indices/KGG01P`, `/indices/exchange-rate`, and `/indices/VWAP.KRW-BTC`.
Additional page/API recheck: 2026-06-01 for `/calendar`, `/calendar/economic-indicator`, index-page calendar subsets, stock-news paging, and observed drift/excluded page calls.
Additional page/API recheck: 2026-06-08 for `/indices/KGG01P`, `/indices/exchange-rate`, and `/indices/VWAP.KRW-BTC` chart controls, related widgets, paging, and response shapes.
Status labels added: 2026-04-20
Observed from: public `tossinvest.com` pages in a non-authenticated browser session.
Primary data host: `https://wts-info-api.tossinvest.com`

This catalog is for read-only stock-information workflows. Include endpoints only when they help answer stock, market, index, theme, financial, filing, news, ranking, investor-trend, or screener questions. Do not collect page bootstrapping, telemetry, login/certificate, guest/session, account, order, following/subscription, or personalization endpoints as cataloged APIs.

Re-verify endpoints before depending on them because TossInvest web APIs are undocumented and may change without notice. Keep checks small, sequential, and user-initiated. If TossInvest returns access-denied, throttling, challenge, login, or otherwise unexpected responses, stop and re-check the endpoint in current public browser traffic instead of retrying or working around service-protection behavior.

## Contents

- [Verification Status](#verification-status)
- [Host Map](#host-map)
- [Identifier Conventions](#identifier-conventions)
- [Stock Summary APIs](#stock-summary-apis)
- [Chart APIs](#chart-apis)
- [Index And Market Indicator APIs](#index-and-market-indicator-apis)
- [Analytics APIs](#analytics-apis)
- [Filings And News APIs](#filings-and-news-apis)
- [Transaction Status APIs](#transaction-status-apis)
- [Dashboard And Discovery APIs](#dashboard-and-discovery-apis)
- [Feed And News APIs](#feed-and-news-apis)
- [Screener APIs](#screener-apis)
- [Cert And Status Helpers](#cert-and-status-helpers)
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
| Common stock detail UI | `observed` | GET | `/api/v1/stock-detail/ui/{productCode}/common` | `name`, `detailName`, `guid`, `symbol`, `marketCode`, `companyCode`, `badges`, `notices` |
| Header info | `observed` | GET | `/api/v1/stock-infos/header/{productCode}` | `sections[]`; section keys include ranking fields such as `netBuyVolumeRanking` |
| WTS badges | `observed` | GET | `/api/v1/stock-infos/{productCode}/wts-badges` | Badges shown around stock header/detail |
| Stock info | `script-backed` | GET | `/api/v2/stock-infos/{productCode}` | `code`, `guid`, `symbol`, `isinCode`, `status`, `name`, `market`, `companyCode`, `companyName` |
| Code or symbol lookup | `observed` | GET | `/api/v2/stock-infos/code-or-symbol/{productCode}` | Same general metadata shape as stock info |
| Batch stock info | `observed` | GET | `/api/v1/stock-infos?codes={codes}` | Long comma-separated code list |
| Price batch v1 | `observed` | GET | `/api/v1/product/stock-prices?meta=true&productCodes={codes}` | Price list with optional metadata |
| Price batch v3 | `observed` | GET | `/api/v3/stock-prices?meta=true&productCodes={codes}` | Newer price list shape |
| Price details | `script-backed` | GET | `/api/v3/stock-prices/details?productCodes={codes}` | List items include `code`, `exchange`, `tradeDateTime`, `open`, `high`, `low`, `close`, `volume`, `value`, `base`, `changeType`, `currency` |
| Quote book v2 | `observed` | GET | `/api/v2/stock-prices/{productCode}/quotes` | Query can include `investMode`, `viewType`, `preMarketHours`; observed result includes `sellPrices`, `sellQuantities`, `buyPrices`, `buyQuantities`, `estimatedPrice` |
| Quote book v3 | `script-backed` | GET | `/api/v3/stock-prices/{productCode}/quotes` | Query can include `investMode`, `viewType`, `fallbackKrx`; observed result includes `offerPrices`, `offerVolumes`, `bidPrices`, `bidVolumes`, `midPrices` |
| Intraday ticks | `script-backed` | GET | `/api/v2/stock-prices/{productCode}/ticks` | Query: `viewType`, `count`, `investMode`; observed rows include `time`, `price`, `base`, `volume`, `tradeType`, `cumulativeVolume` |
| Main-session prices | `observed` | GET | `/api/v1/stock-prices/mainsession?codes={codes}` | Observed result object includes `prices` |
| After-session prices | `observed` | GET | `/api/v1/stock-prices/after?codes={codes}` | Observed list items include `code`, `changeType`, `close`, `value`, `volume`, `amount` |
| Upper/lower price bounds | `observed` | GET | `/api/v2/stock-prices/{productCode}/upper-lower` | `date`, `upperLimit`, `lowerLimit` |

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
| Index daily quote table | `observed` | GET | `/api/v1/c-chart/{securitiesType}/{indexCode}/day:1` | Current index pages use this for visible daily quote paging; query includes `count`, optional cursor `from`, and `useAdjustedRate=true`; result includes `nextDateTime` and `candles[]`; reference-only, not script-backed yet |
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
this observed daily quote table is reference-only, not script-backed yet.
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

## Analytics APIs

Observed from `/stocks/A005930/analytics`.

| Purpose | Status | Method | Path | Key response fields / notes |
|---|---|---:|---|---|
| Sales composition | `observed` | GET | `/api/v1/companies/{companyCode}/sales-compositions` | `code`, `fiscalYear`, `endDate`, `compositions[]`, `dataSource`; company code without leading `A` |
| Related themes/categories | `observed` | GET | `/api/v2/companies/{companyCode}/tics` | `baseDate`, `majorList[]`, `minorList[]`; company code without leading `A` |
| Stock overview | `script-backed` | GET | `/api/v2/stock-infos/{productCode}/overview` | `type`, `market`, `company`, `marketValueKrw`, `enterpriseValueKrw`, `dataSource`, `listDate` |
| Business/holding composition | `observed` | GET | `/api/v2/stock-infos/{productCode}/compositions` | Observed result includes `code`, `type`, `fiscalYear`, `endDate`, `items[]`, `dataSource`; used for composition widgets |
| ETF/ETN investment detail | `observed` | GET | `/api/v2/stock-infos/{productCode}/investment` | Useful for ETF/ETN pages; observed result includes market/asset/NAV-style fields and base date fields |
| Consensus | `observed` | GET | `/api/v2/stock-infos/consensus/{productCode}` | `targetPrice`, `pointDate`, `pastClosePrices[]` |
| Analyst opinion | `observed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-opinion` | `type`, `strongSell`, `sell`, `hold`, `buy`, `strongBuy`, `targetPrice`, `description` |
| Analyst reports | `observed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-reports` | `analystReportGroups[]` with `displayDateAndEditor`, `analystReports`, `publishedAt` |
| Investment indicators | `observed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/investment-indicators` | `indicatorSections[]` with `sectionName`, `data` |
| Analytics section order | `observed` | GET | `/api/v1/stock-detail/ui/wts/{productCode}/section-orders` | UI ordering metadata |
| Dividend summary | `observed` | GET | `/api/v1/stock-infos/dividend/{productCode}/summary` | List items include `exDate`, `paymentDate`, `currency`, `ratio`, `cash`, `cashKrw`, `yieldRatio`, `ttmYieldRatio` |
| Dividend years | `observed` | GET | `/api/v1/stock-infos/dividend/{productCode}/years` | Dividend year options |
| Dividend yield history | `observed` | GET | `/api/v1/stock-infos/{productCode}/dividends/yield-ratio/histories` | Yield-ratio history |
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
| `/financial/estimate/revenue` | `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `revenueEst`, `revenueEstKrw`, `fluctuationRate`, `graphs`, `tables` |
| `/financial/estimate/eps` | `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `epsEst`, `epsEstKrw`, `fluctuationRate`, `graphs`, `tables` |
| `/financial/estimate/operating-income` | `selectedRange`, `selectableRanges`, `selectedPeriod`, `selectablePeriods`, `operatingIncomeEst`, `operatingIncomeEstKrw`, `fluctuationRate`, `graphs`, `tables` |
| `/evaluation` | `per`, `pbr`, `psr`, `median`, `position` |
| `/evaluation-comparison` | `selectedFactor`, `selectableFactors`, `selectedTics`, `selectableTics`, `stockGraphs`, `stockTables`, `median`, `position`, `ttmValue` |
| `/stability` | `liabilityRatio`, `currentRatio`, `interestCoverageRatio`, `median`, `position` |
| `/revenue-and-net-profit` | `companyName`, `recentFiscalYear`, `recentFiscalQuarter`, `recentNetProfit`, `graph`, `table` |
| `/operating-income` | `companyName`, `recentFiscalYear`, `recentFiscalQuarter`, `recentOperatingIncome`, `graph`, `table` |

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

Observed from `/stocks/A005930/transaction-status` and the `contentType=net-buy` URL variant.

| Purpose | Status | Method | Path | Params and key response fields |
|---|---|---:|---|---|
| Broker trading ranking | `script-backed` | GET | `/api/v1/mds/broker/trading-ranking` | Query: `code={productCode}`; result includes `top5ActivityList[]`, foreign ask/bid volume/value fields, `updatedAt` |
| Investor trading trend | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/trading-trend` | Query: `productCode={productCode}&size=60`; result includes `pagingParam`, `body[]`, `lastPage` |
| Program trading | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/program-trading` | Query: `productCode={productCode}&size=50`; result includes `pagingParam`, `body[]`, `lastPage` |
| Fixed-date trading trend | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | Query: `productCode={productCode}&from={YYYY-MM-DD}&to={YYYY-MM-DD}`; result is a date-bounded list |
| Accumulated fixed trading trend | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | Query: `productCode`, `from`, `to`; observed rows include accumulated net investor-volume fields |
| Accumulated fixed trend detail | `script-backed` | GET | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | Query: `productCode`, `from`, `to`; observed object includes accumulated net detail fields by investor category |
| MDS info pages | `script-backed` | GET | `/api/v1/mds/info/{type}` | Query usually uses `stockCode`, `number`, `size`, optional `key`; direct 2026-05-29 checks accepted `credit`, `lending-trading`, `short-selling-trend`, and `cfd` |

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

- The `contentType=net-buy` page URL variant did not introduce a separate API in observed captures.
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
| Signal details | `observed` | GET | `/api/v1/dashboard/wts/overview/ai-signals/detail?productCode={productCode}&productType=STOCKS` | Per-stock signal detail |
| Overview stock signals | `script-backed` | GET | `/api/v1/dashboard/wts/overview/signals?codes={codes}` | Direct 2026-05-29 check returned `stockCode` and `signals[]`; used for the home live-chart `TossInvest AI summary` column |
| Exchange rates | `script-backed` | GET | `/api/v1/dashboard/wts/overview/exchange-rates` | FX/overview data |
| Trading info | `observed` | GET | `/api/v1/dashboard/wts/overview/trading-info` | Market overview data |
| WTS news feed | `observed` | GET | `/api/v1/dashboard/wts/news` | Feed/news panel data; `scripts/feed.py` uses the POST form documented under Feed And News APIs |
| Home live-chart top100 ranking | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | Body maps URL params to `id={live-chart}`, `tag={market}`, `duration`; returns `products[]`, usually 100 rows |
| Realtime investor rankings | `script-backed` | GET | `/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` | Observed under `wts-cert-api`; public page ranking widget, but keep sensitive-host caution |
| Economic calendar | `script-backed` | GET | `/api/v2/dashboard/wts/overview/calendar/economic-events` | Observed under `wts-cert-api`; result list includes `id`, `date`, `title` |
| Calendar AI key events | `script-backed` | GET | `/api/v1/calendar/ai-summary/key-events` | Direct 2026-05-30 check returned `eci` and `earnings[]`; public market-calendar context |
| Theme list | `script-backed` | GET | `/api/v1/tics/all` | Observed result includes `baseDateTime`, `ticsItems[]` |
| Theme ranking by tag | `script-backed` | GET | `/api/v1/rankings/contents/tics_margin_depth1/tags/{tag}` | Observed tags include market-style values such as `kr`/`us`; result contains ranking metadata and rows |
| Theme details | `script-backed` | GET | `/api/v1/tics/{ticsId}/details` | Returned `id`, `title`, `summary`, `description`, `companyCount`, `etfCount`, `stocks[]` |
| Theme company ranking | `script-backed` | GET | `/api/v1/companies/tics/rankings?ticsId={ticsId}&ticsRanking={ranking}` | Ranking data for a theme/category |
| Related themes | `script-backed` | GET | `/api/v1/tics/{ticsId}/related` | Related categories for a theme page |
| Theme news | `script-backed` | GET | `/api/v2/news/tics/{ticsId}` | Query can include `size`; related news for a theme |
| Theme fluctuations | `script-backed` | GET | `/api/v2/tics/{ticsId}/fluctuations` | Theme fluctuation/history data |

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

Observed request shape:

```text
POST https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking
Content-Type: application/json

{"id":"biggest_total_amount","tag":"kr","duration":"realtime","filters":[]}
```

For the user-provided top100 URLs checked on 2026-04-20, `market=kr`/`us` maps to `tag=kr`/`us`. The `biggest_total_amount`, `biggest_total_volume`, `heavy_soar`, and `heavy_descent` combinations returned `products[]` with 100 rows for both markets in direct response checks.

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
| Recommended feed posts | `script-backed` | GET | `/api/v3/feed/recommend/posts` | Optional `lastRecommendId`; returned `feeds[]` and `key.lastRecommendId` |
| Recommended ranking feed posts | `script-backed` | GET | `/api/v4/feed/recommend/ranking-posts` | Optional `lastRecommendId`; feature-flagged replacement for recommended feed |
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
| Screener base filters | `observed` | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/base` | Body depends on selected filters; returns `basedAt` in observed bundle |
| Screener range filters | `observed` | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/range` | Body depends on selected filters |
| Screener result count | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count` | Body shape `{ "filters": [], "nation": "kr" }` or `"us"` returned counts in verification; RSI, selected price, and selected technical filters accepted `conditions[]` |
| Screener results | `script-backed` | POST | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen` | Body includes `pagingParam`, `filters`, `sort`, and `nation`; `pagingParam.number/size` and selected sortable columns worked in verification |

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

## Cert And Status Helpers

These endpoints were observed during public page loads but live under `wts-cert-api`. Treat them as sensitive unless their current behavior is public visible page data or metadata with no cookies, auth headers, account identifiers, or personal data. Script-backed rows are restricted by `scripts/tossinvest_api.py` host/path policy.

| Purpose | Status | Method | URL | Sensitive-host note |
|---|---|---:|---|---|
| Stock red flags | `observed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/stock-infos/{productCode}/red-flags` | Public page metadata; re-check before scripting |
| Overview indicator | `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/index?market=kr` | Public dashboard metadata only |
| Overview indicator v3 | `observed` | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator?market=kr` | Public dashboard metadata; re-check before scripting |
| Overview indicator v4 | `observed-drift` | GET | `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | Public dashboard metadata observed on 2026-06-01 home traffic; not script-backed |
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

Observed 2026-06-01 drift and excluded endpoints:

| Endpoint | Status | Reason |
|---|---|---|
| `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator` | `observed-drift` | Home traffic exposes newer overview indicator aggregate; current scripts use narrower indicator routes |
| `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | `observed-drift` | Home traffic exposes newer overview indicator aggregate; not routed until separately scoped |
| `https://wts-info-api.tossinvest.com/api/v2/dashboard/wts/overview/signals` | `observed-drift` | Home traffic also exposes a v2 signals route; `dashboard_ranking.py --kind signals` remains on the verified public v1 helper |
| `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-buy` | `excluded` | `wts-api` exchange quote route observed on exchange-rate page; keep out until exact host/path safety review |
| `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-sell` | `excluded` | Same as above |
| `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | `excluded` | Community/social ranking surface, outside market-data skill scope |
| `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | `observed-drift` | Feed page currently calls cert-host mirror; `feed.py` still uses the working info-api route and should not widen cert allowlist without separate review |

## Excluded Non-Stock Calls

Do not collect these as cataloged APIs, even if they appear in browser network traffic:

- Telemetry, Sentry, logging, deployment refresh, images, fonts, and static assets.
- Login, certificate, authentication, account, balance, holding, transfer, order, orderable-amount, order mutation, and session-storage calls.
- Order-adjacent status helpers such as `https://wts-cert-api.tossinvest.com/api/v3/trading/order/{productCode}/trading-status`; keep them unscripted unless a future safety review explicitly reclassifies them.
- Guest bootstrap/upsert, experiment variables, tab/session initialization, and other page bootstrapping calls that do not directly return stock or market information.
- Following/subscription feeds, personalized interest/reasoning content, comments-only feeds, or account-personalized discovery surfaces.

## Known Observed Pages

Use this table as the first stop for endpoint drift or lookup failures. Open the public page that should expose the missing data, follow [capture-workflow.md](capture-workflow.md), and update this catalog before changing scripts. Do not guess a replacement endpoint from a stale path.

| Page | Key endpoint groups |
|---|---|
| `https://www.tossinvest.com/?focusedProductCode=A000660` | Chart, stock summary, ranking, dashboard signals |
| `https://www.tossinvest.com/stocks/A005930/analytics` | Analytics, financials, dividends, analyst data |
| `https://www.tossinvest.com/stocks/A005930/transaction-status` | Broker ranking, investor trend, program trading, credit, lending trading, short-selling trend, CFD |
| `https://www.tossinvest.com/stocks/A005930/transaction-status?contentType=net-buy...` | Same transaction-status APIs; URL query appears to focus a section |
| `https://www.tossinvest.com/stocks/A005930/order` | Price details, quote/tick, upper/lower bounds, `c-chart` stock candles, TradingView chart studies; order namespace helpers and mutations excluded; no dedicated RSI/MACD/Bollinger data endpoint observed |
| `https://www.tossinvest.com/?ranking-type=trending_category` | TICS rankings and TICS detail modal APIs |
| `https://www.tossinvest.com/?ranking-type=domestic_investor_trend` | Investor buy/sell rankings from dashboard ranking APIs |
| `https://www.tossinvest.com/?market=kr&live-chart=biggest_total_amount` | Live-chart top100 ranking via overview ranking API |
| `https://www.tossinvest.com/?market=us&live-chart=biggest_total_amount` | Same live-chart API with `tag=us`; user-supplied typo `ttps://` should be corrected to `https://` |
| `https://www.tossinvest.com/?market=kr&live-chart=biggest_total_volume&duration=realtime` | Live-chart top100 ranking via overview ranking API |
| `https://www.tossinvest.com/?market=us&live-chart=biggest_total_volume&duration=realtime` | Same live-chart API with `tag=us` |
| `https://www.tossinvest.com/?market=kr&live-chart=heavy_soar&duration=1d` | Live-chart top100 ranking via overview ranking API |
| `https://www.tossinvest.com/?market=us&live-chart=heavy_soar&duration=1d` | Same live-chart API with `tag=us` |
| `https://www.tossinvest.com/?market=kr&live-chart=heavy_descent&duration=1d` | Live-chart top100 ranking via overview ranking API |
| `https://www.tossinvest.com/?market=us&live-chart=heavy_descent&duration=1d` | Same live-chart API with `tag=us` |
| `https://www.tossinvest.com/indices/KGG01P` | Index info, price, chart, indicator/news widgets |
| `https://www.tossinvest.com/indices/exchange-rate` | FX chart and exchange-rate widgets |
| `https://www.tossinvest.com/indices/VWAP.KRW-BTC` | Crypto-like index info/price, `r-chart/crypto`, crypto prices, related news |
| `https://www.tossinvest.com/calendar` | Monthly market calendar, economic/earnings and domestic/overseas local filters, weekly/key-event summary text |
| `https://www.tossinvest.com/calendar/economic-indicator?date=2026-06-01&ric=USPMI%3DECI` | Economic indicator detail, historical data, related articles, upcoming indicators, AI analysis text |
| `https://www.tossinvest.com/screener` | Screener presets, filter metadata, result count, result screen |
| `https://www.tossinvest.com/feed/recommended` | Recommended community/feed posts |
| `https://www.tossinvest.com/feed/news` | Dashboard news categories and news detail |
