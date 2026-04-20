# TossInvest Web API Catalog

Base observation date: 2026-04-16
Additional bundle/API check: 2026-04-20 against `buildId=SUN83tZwsh5murULLiDPr`
Additional page check: 2026-04-20 for `/stocks/A005930/order`, home ranking variants, `/indices/KGG01P`, `/feed/recommended`, and `/feed/news`
Observed from: public `tossinvest.com` pages in a non-authenticated browser session.
Primary data host: `https://wts-info-api.tossinvest.com`

This catalog is for read-only stock information workflows. Re-verify endpoints before depending on them because TossInvest web APIs are undocumented and may change without notice.

## Host Map

| Host | Observed purpose | Usage guidance |
|---|---|---|
| `wts-info-api.tossinvest.com` | Stock info, prices, quotes/ticks, chart, analytics, financial statements, consensus, dividends, investor trading trend, filings, news, themes | Primary read-only host |
| `wts-api.tossinvest.com` | WTS init, time, trading hours, system status, guest/login bootstrap | Use as page context only |
| `wts-cert-api.tossinvest.com` | Red flags, trading status, dashboard ranking, comments, some authenticated data | Treat as sensitive unless clearly public page metadata |
| `cdn-api.tossinvest.com` | Deployment refresh checks | Exclude from data catalog |
| `log.tossinvest.com` | Telemetry and performance logs | Exclude |
| `sentry-public.tossinvest.com` | Error reporting | Exclude |

## Identifier Conventions

| Identifier | Example | Meaning |
|---|---|---|
| `productCode` | `A005930`, `A000660` | TossInvest stock/product code used by stock detail APIs |
| `companyCode` | `005930`, `000660` | Company code used by some `/companies/` APIs |
| `codes` | `A005930,A000660` | Comma-separated product code list |
| `subjectId` | `KR7005930003` | Community/comment subject id, observed in comments APIs |

Use `productCode` for stock pages and prices. Strip the leading `A` only where the observed endpoint uses `companyCode`.

## Stock Summary APIs

Observed on stock detail pages such as `/stocks/A005930`.

| Purpose | Method | Path | Key response fields / notes |
|---|---:|---|---|
| Common stock detail UI | GET | `/api/v1/stock-detail/ui/{productCode}/common` | `name`, `detailName`, `guid`, `symbol`, `marketCode`, `companyCode`, `badges`, `notices` |
| Header info | GET | `/api/v1/stock-infos/header/{productCode}` | `sections[]`; section keys include ranking fields such as `netBuyVolumeRanking` |
| WTS badges | GET | `/api/v1/stock-infos/{productCode}/wts-badges` | Badges shown around stock header/detail |
| Stock info | GET | `/api/v2/stock-infos/{productCode}` | `code`, `guid`, `symbol`, `isinCode`, `status`, `name`, `market`, `companyCode`, `companyName` |
| Code or symbol lookup | GET | `/api/v2/stock-infos/code-or-symbol/{productCode}` | Same general metadata shape as stock info |
| Batch stock info | GET | `/api/v1/stock-infos?codes={codes}` | Long comma-separated code list |
| Price batch v1 | GET | `/api/v1/product/stock-prices?meta=true&productCodes={codes}` | Price list with optional metadata |
| Price batch v3 | GET | `/api/v3/stock-prices?meta=true&productCodes={codes}` | Newer price list shape |
| Price details | GET | `/api/v3/stock-prices/details?productCodes={codes}` | List items include `code`, `exchange`, `tradeDateTime`, `open`, `high`, `low`, `close`, `volume`, `value`, `base`, `changeType`, `currency` |
| Quote book v2 | GET | `/api/v2/stock-prices/{productCode}/quotes` | Query can include `investMode`, `viewType`, `preMarketHours`; observed result includes `sellPrices`, `sellQuantities`, `buyPrices`, `buyQuantities`, `estimatedPrice` |
| Quote book v3 | GET | `/api/v3/stock-prices/{productCode}/quotes` | Query can include `investMode`, `viewType`, `fallbackKrx`; observed result includes `offerPrices`, `offerVolumes`, `bidPrices`, `bidVolumes`, `midPrices` |
| Intraday ticks | GET | `/api/v2/stock-prices/{productCode}/ticks` | Query: `viewType`, `count`, `investMode`; observed rows include `time`, `price`, `base`, `volume`, `tradeType`, `cumulativeVolume` |
| Main-session prices | GET | `/api/v1/stock-prices/mainsession?codes={codes}` | Observed result object includes `prices` |
| After-session prices | GET | `/api/v1/stock-prices/after?codes={codes}` | Observed list items include `code`, `changeType`, `close`, `value`, `volume`, `amount` |
| Upper/lower price bounds | GET | `/api/v2/stock-prices/{productCode}/upper-lower` | `date`, `upperLimit`, `lowerLimit` |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v2/stock-infos/A005930
GET https://wts-info-api.tossinvest.com/api/v3/stock-prices/details?productCodes=A005930
GET https://wts-info-api.tossinvest.com/api/v3/stock-prices/A005930/quotes?investMode=krx
GET https://wts-info-api.tossinvest.com/api/v2/stock-prices/A005930/ticks?viewType=krx&count=5&investMode=krx
```

## Chart APIs

Observed on home and stock detail pages.

| Purpose | Method | Path | Params and notes |
|---|---:|---|---|
| KR stock candle chart | GET | `/api/v1/c-chart/kr-s/{productCode}/{range}` | Observed ranges include `min:1`, `day:1`, `week:1`, `month:1`; query: `count`, `session=all`, `investMode=krx`, `useAdjustedRate=true`; result includes `code`, `nextDateTime`, `exchangeRate`, `exchange`, `candles[]` |

Example:

```text
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/day:1?count=61&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/min:1?count=5&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/week:1?count=5&session=all&investMode=krx&useAdjustedRate=true
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/month:1?count=5&session=all&investMode=krx&useAdjustedRate=true
```

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

| Purpose | Method | URL/path | Params and notes |
|---|---:|---|---|
| Index info | GET | `/api/v2/index-infos/{indexCode}` | Returned `code`, `name`, `logoImageUrl`, `priceFeedType`, `tradingStartAt`, `tradingEndAt`, `isMarketOpen` for `KGG01P` |
| Index price | GET | `/api/v1/index-prices/{indexCode}` | Returned `open`, `high`, `low`, `close`, `volume`, `value`, `base`, `tradeTime` |
| Index/market chart | GET | `/api/v1/r-chart/{securitiesType}/{indexCode}/{range}/{step}` | Query: `session=main`, `investMode=krx`, `last=false`; example `kr-s/KGG01P/1d/min:5` |
| USD/KRW product exchange rate | GET | `/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW` | Observed in index/FX bundle |
| FX chart | GET | `/api/v1/r-chart/fx/EXCHANGE_RATE/{range}/{step}` | Query includes `last=false`, `useAdjustedRate=true`, `currency=USD` |
| Overview indicators v3 | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator` | Returned `leftSection`, `rightSection`, `indicators`, `landingUrl`; public-looking but cert host |
| Overview indicator by type | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/{type}` | Query: `market`; observed `type` values include `index`, `bond`, and `commodity`, each returning `majorIndicatorInfos[]` |
| Overview indicator mini-chart | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/mini-chart` | Returned `indexMap`; public-looking but cert host |
| Related ETFs | POST | `/api/v3/dashboard/wts/overview/indicator/{indexCode}/related-etfs` | Empty JSON body accepted; returned `indexCode`, `etfs[]` |
| Index net buying range | GET | `/api/v1/stock-infos/index/net-buying/range` | Query: `code`, `range`, `from`, `count`; returned `investorActivityAmounts[]` |
| Index net buying daily | GET | `/api/v1/stock-infos/index/net-buying/daily` | Query: `code`, `from`, `count`; returned `investorActivityAmounts[]` |
| Exchange rates widget | GET | `/api/v1/dashboard/wts/overview/exchange-rates` | Returned `exchangeRates[]` |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v2/index-infos/KGG01P
GET https://wts-info-api.tossinvest.com/api/v1/index-prices/KGG01P
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KGG01P/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/us-s/RFU.GCv1/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/kr-s/KR1BENCH0010/1d/min:5?session=main&investMode=krx&last=false
GET https://wts-info-api.tossinvest.com/api/v1/r-chart/fx/EXCHANGE_RATE/1d/min:5?last=false&useAdjustedRate=true&currency=USD
GET https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/mini-chart
POST https://wts-info-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator/KGG01P/related-etfs
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/index/net-buying/range?code=KGG01P&range=week&from=2026-04-20&count=5
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/index/net-buying/daily?code=KGG01P&count=35&from=2026-04-20
GET https://wts-info-api.tossinvest.com/api/v1/dashboard/wts/overview/exchange-rates
GET https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator
GET https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/bond?market=kr
GET https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/commodity?market=kr
```

Direct checks on 2026-04-20 returned public-looking bond indicators such as
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
`KR1BENCH0010/1d/min:5` and `ROB.US10YT-RR` under `us-s`. `scripts/indices.py`
uses `--securities-type auto` by default: dotted indicator codes infer `us-s`,
and other codes infer `kr-s`.

`scripts/indices.py` chart presets map to the verified windows
`intraday=1d/min:5`, `quarter=3m/day:1`, and `daily=1y/day:1`. The script can
also fetch the verified mini-chart, related ETF, and index net-buying widgets
with `--include-mini-chart`, `--include-related-etfs`, and
`--include-net-buying`.

## Analytics APIs

Observed from `/stocks/A005930/analytics`.

| Purpose | Method | Path | Key response fields / notes |
|---|---:|---|---|
| Sales composition | GET | `/api/v1/companies/{companyCode}/sales-compositions` | `code`, `fiscalYear`, `endDate`, `compositions[]`, `dataSource`; company code without leading `A` |
| Related themes/categories | GET | `/api/v2/companies/{companyCode}/tics` | `baseDate`, `majorList[]`, `minorList[]`; company code without leading `A` |
| Stock overview | GET | `/api/v2/stock-infos/{productCode}/overview` | `type`, `market`, `company`, `marketValueKrw`, `enterpriseValueKrw`, `dataSource`, `listDate` |
| Business/holding composition | GET | `/api/v2/stock-infos/{productCode}/compositions` | Observed result includes `code`, `type`, `fiscalYear`, `endDate`, `items[]`, `dataSource`; used for composition widgets |
| ETF/ETN investment detail | GET | `/api/v2/stock-infos/{productCode}/investment` | Useful for ETF/ETN pages; observed result includes market/asset/NAV-style fields and base date fields |
| Consensus | GET | `/api/v2/stock-infos/consensus/{productCode}` | `targetPrice`, `pointDate`, `pastClosePrices[]` |
| Analyst opinion | GET | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-opinion` | `type`, `strongSell`, `sell`, `hold`, `buy`, `strongBuy`, `targetPrice`, `description` |
| Analyst reports | GET | `/api/v1/stock-detail/ui/wts/{productCode}/analyst-reports` | `analystReportGroups[]` with `displayDateAndEditor`, `analystReports`, `publishedAt` |
| Investment indicators | GET | `/api/v1/stock-detail/ui/wts/{productCode}/investment-indicators` | `indicatorSections[]` with `sectionName`, `data` |
| Analytics section order | GET | `/api/v1/stock-detail/ui/wts/{productCode}/section-orders` | UI ordering metadata |
| Dividend summary | GET | `/api/v1/stock-infos/dividend/{productCode}/summary` | List items include `exDate`, `paymentDate`, `currency`, `ratio`, `cash`, `cashKrw`, `yieldRatio`, `ttmYieldRatio` |
| Dividend years | GET | `/api/v1/stock-infos/dividend/{productCode}/years` | Dividend year options |
| Dividend yield history | GET | `/api/v1/stock-infos/{productCode}/dividends/yield-ratio/histories` | Yield-ratio history |
| Comprehensive financial statements | POST | `/api/v2/companies/{productCode}/financial-statements/comprehensive` | JSON body `{}` accepted in verification |
| Financial statement records | POST | `/api/v2/companies/{productCode}/financial-statement-records` | JSON body `{}` accepted in verification |
| Financial estimate date | GET | `/api/v2/companies/{productCode}/financial/estimate/date` | Estimate reference date |
| Revenue estimate | POST | `/api/v2/companies/{productCode}/financial/estimate/revenue` | JSON body `{}` accepted in verification |
| EPS estimate | POST | `/api/v2/companies/{productCode}/financial/estimate/eps` | JSON body `{}` accepted in verification |
| Operating income estimate | POST | `/api/v2/companies/{productCode}/financial/estimate/operating-income` | JSON body `{}` accepted in verification |
| Valuation | POST | `/api/v2/stock-infos/evaluation/{productCode}` | Result keys include `per`, `pbr`, `psr`, `median`, `position` |
| Valuation comparison | POST | `/api/v2/stock-infos/evaluation-comparison/{productCode}` | Peer/sector comparison data |
| Stability | POST | `/api/v2/stock-infos/stability/{productCode}` | Result keys include liability/current/coverage ratios |
| Revenue and net profit | POST | `/api/v2/stock-infos/revenue-and-net-profit/{productCode}` | Result includes graph/table data |
| Operating income | POST | `/api/v2/stock-infos/operating-income/{productCode}` | Result includes graph/table data |

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

| Purpose | Method | Path | Params and notes |
|---|---:|---|---|
| Company filings list | GET | `/api/v1/stock-detail/companies/{companyCode}/filings` | Query: `number`, `size`, optional `key`; observed result includes `pagingParam`, `body[]`, `lastPage` |
| Filing detail | GET | `/api/v1/stock-infos/filings/companies/{companyCode}/report/{reportId}` | Query may include `reportItem`; observed in bundle for filing detail modal |
| Company news | GET | `/api/v2/news/companies/{companyCode}` | Query can include `size`; observed result includes `pagingParam`, `body[]`, `lastPage` |
| News detail | GET | `/api/v2/news/{newsId}` | Detail payload for a news item |
| Exclude headline news | GET | `/api/v2/forum/news/headline/exclude/{newsId}` | Related/headline news excluding a selected item |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v1/stock-detail/companies/005930/filings?number=1&size=3
GET https://wts-info-api.tossinvest.com/api/v2/news/companies/005930?size=3
```

## Transaction Status APIs

Observed from `/stocks/A005930/transaction-status` and the `contentType=net-buy` URL variant.

| Purpose | Method | Path | Params and key response fields |
|---|---:|---|---|
| Broker trading ranking | GET | `/api/v1/mds/broker/trading-ranking` | Query: `code={productCode}`; result includes `top5ActivityList[]`, foreign ask/bid volume/value fields, `updatedAt` |
| Investor trading trend | GET | `/api/v1/stock-infos/trade/trend/trading-trend` | Query: `productCode={productCode}&size=60`; result includes `pagingParam`, `body[]`, `lastPage` |
| Program trading | GET | `/api/v1/stock-infos/trade/trend/program-trading` | Query: `productCode={productCode}&size=50`; result includes `pagingParam`, `body[]`, `lastPage` |
| Fixed-date trading trend | GET | `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | Query: `productCode={productCode}&from={YYYY-MM-DD}&to={YYYY-MM-DD}`; result is a date-bounded list |
| Accumulated fixed trading trend | GET | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | Query: `productCode`, `from`, `to`; observed rows include accumulated net investor-volume fields |
| Accumulated fixed trend detail | GET | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | Query: `productCode`, `from`, `to`; observed object includes accumulated net detail fields by investor category |
| MDS info pages | GET | `/api/v1/mds/info/{type}` | Query usually uses `stockCode`, `number`, `size`, optional `key`; `credit` returned paging data in verification; verify each type before documenting as stable |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v1/mds/broker/trading-ranking?code=A005930
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/trading-trend?productCode=A005930&size=60
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/program-trading?productCode=A005930&size=50
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A005930&from=2026-04-09&to=2026-04-16
GET https://wts-info-api.tossinvest.com/api/v1/mds/info/credit?stockCode=A005930&number=1&size=5
```

Notes:

- The `contentType=net-buy` page URL variant did not introduce a separate API in observed captures.
- Treat `from` and `to` as dynamic dates derived by the page, not hard-coded constants.
- Direct response checks showed top-level key `result` for all four endpoints above.
- For pension-fund trend, match the TossInvest investor-status UI against `netPensionFundBuyVolume`: positive values are net buys and negative values are net sells.
- Treat `pensionFundBuyVolume` as a reference gross-buy field. It has been observed in recent `trading-trend` rows and sums into `institutionBuyVolume` with other institution detail buy fields, but it is not the UI net-buy value.
- `fixed-trading-trend` is the preferred endpoint for date-bounded pension-fund history. It returned rows back to `2019-04-01` for `A005930` in verification; earlier ranges returned no rows.
- Long date-bounded requests may be truncated. A single `A005930` request from `2019-04-01` through `2026-04-16` returned 1,731 rows; query by year or smaller windows for stable history collection.
- Use `scripts/pension_fund_trend.py --year YYYY` for one calendar year or `--all-history --format csv --output pension.csv` for yearly-window collection from the verified history start. Use `--summary-only` when only row count, net total, and net-buy/net-sell day counts are needed.

Observed investor trend row keys include:

```text
baseDate,
individualsBuyVolume, individualsSellVolume, netIndividualsBuyVolume,
foreignerBuyVolume, foreignerSellVolume, netForeignerBuyVolume,
institutionBuyVolume, institutionSellVolume, netInstitutionBuyVolume
```

Observed pension-fund fields:

```text
netPensionFundBuyVolume   # primary UI-matching net-buy/net-sell value
pensionFundBuyVolume      # reference gross-buy field, not available in every endpoint
```

Observed program trading row keys include:

```text
baseDate,
arbitrageBuyQuantity, arbitrageSellQuantity, arbitrageNetBuyQuantity,
nonArbitrageBuyQuantity, nonArbitrageSellQuantity, nonArbitrageNetBuyQuantity,
totalBuyQuantity, totalSellQuantity, totalNetBuyQuantity
```

## Dashboard And Discovery APIs

Observed on home, stock detail, analytics, and transaction-status pages.

| Purpose | Method | Path | Notes |
|---|---:|---|---|
| Realtime stock ranking | GET | `/api/v1/rankings/realtime/stock?size=10` | Ranking widgets |
| Dashboard intelligences | POST | `/api/v1/dashboard/intelligences/all` | Empty observed body |
| AI signals | POST | `/api/v1/dashboard/wts/overview/ai-signals` | Home/detail signal data |
| Signal details | GET | `/api/v1/dashboard/wts/overview/ai-signals/detail?productCode={productCode}&productType=STOCKS` | Per-stock signal detail |
| Overview signals v2 | POST | `/api/v2/dashboard/wts/overview/signals` | Home/detail signal data |
| Exchange rates | GET | `/api/v1/dashboard/wts/overview/exchange-rates` | FX/overview data |
| Trading info | GET | `/api/v1/dashboard/wts/overview/trading-info` | Market overview data |
| WTS news feed | GET | `/api/v1/dashboard/wts/news` | Feed/news panel data |
| Home live-chart top100 ranking | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` | Body maps URL params to `id={live-chart}`, `tag={market}`, `duration`; returns `products[]`, usually 100 rows |
| Realtime investor rankings | GET | `/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` | Observed under `wts-cert-api`; public-looking ranking widget, but keep sensitive-host caution |
| Economic calendar | GET | `/api/v1/dashboard/wts/overview/calendar/economic-events` | Observed under `wts-cert-api`; result list includes `id`, `date`, `title` |
| Reasoning content interest | GET | `/api/v2/reasoning-contents/interest` | Discovery/personalization content |
| Screener modal | GET | `/api/v2/screener/screen/search/modal` | Screener modal data |
| Screener filter ranges | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/range` | Observed in bundle for numeric filter metadata; keep sensitive-host caution |
| Screener filter bases | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/base` | Observed in bundle for base filter metadata; keep sensitive-host caution |
| Screener count | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count` | Body includes `filters[]` and `nation`; returns a number |
| Screener results | POST | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen` | Body requires `pagingParam.size`; accepts `pagingParam.number` and observed `sort`; returns `totalCount`, `page`, `lastPage`, `stocks[]` |
| Theme list | GET | `/api/v1/tics/all` | Observed result includes `baseDateTime`, `ticsItems[]` |
| Theme ranking by tag | GET | `/api/v1/rankings/contents/tics_margin_depth1/tags/{tag}` | Observed tags include market-style values such as `kr`/`us`; result contains ranking metadata and rows |
| Theme details | GET | `/api/v1/tics/{ticsId}/details` | Returned `id`, `title`, `summary`, `description`, `companyCount`, `etfCount`, `stocks[]` |
| Theme company ranking | GET | `/api/v1/companies/tics/rankings?ticsId={ticsId}&ticsRanking={ranking}` | Ranking data for a theme/category |
| Related themes | GET | `/api/v1/tics/{ticsId}/related` | Related categories for a theme page |
| Theme news | GET | `/api/v2/news/tics/{ticsId}` | Query can include `size`; related news for a theme |
| Theme fluctuations | GET | `/api/v2/tics/{ticsId}/fluctuations` | Theme fluctuation/history data |

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

Observed from `/feed/recommended` and `/feed/news`. These endpoints can be useful as market/news discovery signals, but community feeds are less directly stock-information focused than company news or TICS news.

| Purpose | Method | URL/path | Params/body and notes |
|---|---:|---|---|
| Recommended feed posts | GET | `/api/v3/feed/recommend/posts` | Optional `lastRecommendId`; returned `feeds[]` and `key.lastRecommendId` |
| Recommended ranking feed posts | GET | `/api/v4/feed/recommend/ranking-posts` | Optional `lastRecommendId`; feature-flagged replacement for recommended feed |
| Subscription feed posts | GET | `/api/v3/feed/subscription/posts` | Query: `filterType=COMMENT`; returned `feeds[]`, `key.actedAt`, `key.lastCommentId`, `key.lastTradeHistoryId` |
| Feed followings | GET | `https://wts-cert-api.tossinvest.com/api/v2/feed/subscription/followings` | Returned `followings[]`; empty for non-authenticated verification |
| Dashboard/news tab feed | POST | `/api/v1/dashboard/wts/news` | Body `{ "type": "HOT" }` etc.; result includes `type`, `title`, `news[]` |
| News detail | GET | `/api/v2/news/{newsId}` | Detail payload for a selected news item |

Observed dashboard news `type` values:

```text
PERSONALIZED, PERSONALIZE_HOLD, PERSONALIZE_WATCH,
ALL_HIGHLIGHT, HOT, SOARING_STOCK, INDEX
```

`INDEX` requires `indexCode`, for example:

```text
POST https://wts-info-api.tossinvest.com/api/v1/dashboard/wts/news
Content-Type: application/json

{"type":"INDEX","indexCode":"KGG01P"}
```

## Screener APIs

Most screener endpoints currently live under `wts-cert-api`. They can return public-looking market data, but treat them as sensitive-host endpoints and avoid user-specific preset mutations.

| Purpose | Method | URL/path | Params and notes |
|---|---:|---|---|
| Common screener presets | GET | `https://wts-cert-api.tossinvest.com/api/v2/screener/presets/common?useCustom=true` | Returned 11 preset definitions in 2026-04-20 verification; `scripts/screener_count.py --include-common-presets` fetches this metadata |
| Screener search modal | GET | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen/search/modal` | Returned 3 modal groups in 2026-04-20 verification; `scripts/screener_count.py --include-search-modal` fetches this metadata |
| Screener base filters | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/base` | Body depends on selected filters; returns `basedAt` in observed bundle |
| Screener range filters | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/filters/range` | Body depends on selected filters |
| Screener result count | POST | `https://wts-cert-api.tossinvest.com/api/v1/screener/screen/count` | Body shape `{ "filters": [], "nation": "kr" }` or `"us"` returned counts in verification; RSI, selected price, and selected technical filters accepted `conditions[]` |
| Screener results | POST | `https://wts-cert-api.tossinvest.com/api/v2/screener/screen` | Body includes `pagingParam`, `filters`, `sort`, and `nation`; `pagingParam.number/size` and selected sortable columns worked in verification |

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

## Cert And Status Helpers

These endpoints were observed during public page loads but live under `wts-cert-api`. Treat them as sensitive unless their current behavior is clearly public metadata.

| Purpose | Method | URL |
|---|---:|---|
| Stock red flags | GET | `https://wts-cert-api.tossinvest.com/api/v1/stock-infos/{productCode}/red-flags` |
| Trading status | GET | `https://wts-cert-api.tossinvest.com/api/v3/trading/order/{productCode}/trading-status` |
| Overview indicator | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/index?market=kr` |
| Overview indicator v3 | GET | `https://wts-cert-api.tossinvest.com/api/v3/dashboard/wts/overview/indicator?market=kr` |
| Overview ranking | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` |
| Live-chart top100 ranking | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` |
| Economic calendar | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/calendar/economic-events` |
| Investor rankings | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/rankings/by-investors?size={size}` |

The `/stocks/{code}/order` bundle also references order prepare/create/correct/cancel, account, orderable amount, and trading mutation APIs. Exclude them from this skill.

## WTS Context APIs

Use these to understand page bootstrapping, not as stock data sources.

| Purpose | Method | URL |
|---|---:|---|
| WTS init | GET | `https://wts-api.tossinvest.com/api/v3/init?tabId={tabId}` |
| Server time | GET | `https://wts-api.tossinvest.com/api/v1/time` |
| Domestic downtime recipes | GET | `https://wts-api.tossinvest.com/api/v1/system-down-recipes?type=domestic` |
| Integrated trading hours | GET | `https://wts-api.tossinvest.com/api/v2/system/trading-hours/integrated` |
| Certificate init | POST | `https://wts-api.tossinvest.com/api/v2/login/wts/toss/cert-init` |
| Login info bootstrap | POST | `https://wts-api.tossinvest.com/api/v3/login/wts/toss/login-info` |
| Guest upsert | POST | `https://wts-api.tossinvest.com/api/v1/tuba/wts/guests/upsert` |
| Guest variables | POST | `https://wts-api.tossinvest.com/api/v1/tuba/wts/guests/independent-variables` |

## Excluded Telemetry

Do not catalog these as data APIs:

```text
GET  https://cdn-api.tossinvest.com/wts/shouldRefresh/{deploymentId}
POST https://log.tossinvest.com/api/v1/perf-log/bulk
POST https://log.tossinvest.com/api/v2/log/bulk
POST https://sentry-public.tossinvest.com/api/5/envelope/...
```

## Known Observed Pages

| Page | Key endpoint groups |
|---|---|
| `https://www.tossinvest.com/?focusedProductCode=A000660` | Chart, stock summary, ranking, dashboard signals |
| `https://www.tossinvest.com/stocks/A005930/analytics` | Analytics, financials, dividends, analyst data |
| `https://www.tossinvest.com/stocks/A005930/transaction-status` | Broker ranking, investor trend, program trading |
| `https://www.tossinvest.com/stocks/A005930/transaction-status?contentType=net-buy...` | Same transaction-status APIs; URL query appears to focus a section |
| `https://www.tossinvest.com/stocks/A005930/order` | Price details, quote/tick, upper/lower bounds, `c-chart` stock candles, TradingView chart studies, trading status; order mutations excluded; no dedicated RSI/MACD/Bollinger data endpoint observed |
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
| `https://www.tossinvest.com/feed/recommended` | Recommended community/feed posts |
| `https://www.tossinvest.com/feed/news` | Dashboard news categories and news detail |
