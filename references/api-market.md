# Market API reference

Use this reference for indices, FX, bonds, calendars, rankings, search, sectors,
and screeners. Stock and ETF lists within a sector belong here; an individual
stock's quotes and financials belong to the [stock reference](api-stock.md).

For commands, choose the matching section in the
[cookbook](script-cookbook.md#contents); for returned index fields, use
[index and indicator shapes](response-notes.md#index-and-indicator-shapes).
WebSocket protocol and client setup remain in the
[WebSocket reference](websocket-api-reference.md).

Status labels and host/identifier rules are defined in the
[common catalog](api-catalog.md#verification-status). A script-backed label is
not a current-availability guarantee. Dates below remain scoped observations;
the [2026-09-07 audit](update-audit-2026-09-07.md) states the latest checked scope.

## Contents

- [Index And Market Indicator APIs](#index-and-market-indicator-apis)
- [Bond APIs](#bond-apis)
- [Dashboard And Discovery APIs](#dashboard-and-discovery-apis)
  - [Current Industry Dashboard And Sector Behavior](#current-industry-dashboard-and-sector-behavior)
- [Calendar APIs](#calendar-apis)
- [Dashboard And Screener Page Behavior](#dashboard-and-screener-page-behavior)
  - [Home Ranking Values And Filters](#home-ranking-values-and-filters)
  - [Live Price Updates And Page Observations](#live-price-updates-and-page-observations)
  - [RSI Screener And Sorting](#rsi-screener-and-sorting)
  - [Price Condition Presets](#price-condition-presets)
  - [Technical Analysis Presets](#technical-analysis-presets)
- [Screener APIs](#screener-apis)

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

Jump to [home rankings](#home-ranking-values-and-filters),
[live price updates](#live-price-updates-and-page-observations),
[RSI and sorting](#rsi-screener-and-sorting),
[price presets](#price-condition-presets), or
[technical presets](#technical-analysis-presets).

Direct checks on 2026-04-20 for `scripts/theme.py --tag kr --include-all --tics-id 289 --include-details --company-ranking marketcap --company-ranking revenue --company-ranking operating-margin` returned `ranking`, `allThemes`, `details`, `related`, `news`, `fluctuations`, and all three requested company ranking groups.

Observed `ticsRanking` values:

| Value | Meaning observed in UI |
|---:|---|
| `1` | Market capitalization |
| `3` | Revenue |
| `4` | Operating margin |

### Home Ranking Values And Filters

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

### Live Price Updates And Page Observations

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

### RSI Screener And Sorting

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

### Price Condition Presets

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

### Technical Analysis Presets

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
