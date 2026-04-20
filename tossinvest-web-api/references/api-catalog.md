# TossInvest Web API Catalog

Base observation date: 2026-04-16
Observed from: public `tossinvest.com` pages in a non-authenticated browser session.
Primary data host: `https://wts-info-api.tossinvest.com`

This catalog is for read-only stock information workflows. Re-verify endpoints before depending on them because TossInvest web APIs are undocumented and may change without notice.

## Host Map

| Host | Observed purpose | Usage guidance |
|---|---|---|
| `wts-info-api.tossinvest.com` | Stock info, prices, chart, analytics, financial statements, consensus, dividends, investor trading trend | Primary read-only host |
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
| Upper/lower price bounds | GET | `/api/v2/stock-prices/{productCode}/upper-lower` | `date`, `upperLimit`, `lowerLimit` |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v2/stock-infos/A005930
GET https://wts-info-api.tossinvest.com/api/v3/stock-prices/details?productCodes=A005930
```

## Chart APIs

Observed on home and stock detail pages.

| Purpose | Method | Path | Params and notes |
|---|---:|---|---|
| Daily KR stock chart | GET | `/api/v1/c-chart/kr-s/{productCode}/day:1` | Query: `count`, `session=all`, `investMode=krx`, `useAdjustedRate=true`; result includes `code`, `nextDateTime`, `exchangeRate`, `exchange`, `candles[]` |

Example:

```text
GET https://wts-info-api.tossinvest.com/api/v1/c-chart/kr-s/A005930/day:1?count=61&session=all&investMode=krx&useAdjustedRate=true
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

## Analytics APIs

Observed from `/stocks/A005930/analytics`.

| Purpose | Method | Path | Key response fields / notes |
|---|---:|---|---|
| Sales composition | GET | `/api/v1/companies/{companyCode}/sales-compositions` | `code`, `fiscalYear`, `endDate`, `compositions[]`, `dataSource`; company code without leading `A` |
| Related themes/categories | GET | `/api/v2/companies/{companyCode}/tics` | `baseDate`, `majorList[]`, `minorList[]`; company code without leading `A` |
| Stock overview | GET | `/api/v2/stock-infos/{productCode}/overview` | `type`, `market`, `company`, `marketValueKrw`, `enterpriseValueKrw`, `dataSource`, `listDate` |
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

## Transaction Status APIs

Observed from `/stocks/A005930/transaction-status` and the `contentType=net-buy` URL variant.

| Purpose | Method | Path | Params and key response fields |
|---|---:|---|---|
| Broker trading ranking | GET | `/api/v1/mds/broker/trading-ranking` | Query: `code={productCode}`; result includes `top5ActivityList[]`, foreign ask/bid volume/value fields, `updatedAt` |
| Investor trading trend | GET | `/api/v1/stock-infos/trade/trend/trading-trend` | Query: `productCode={productCode}&size=60`; result includes `pagingParam`, `body[]`, `lastPage` |
| Program trading | GET | `/api/v1/stock-infos/trade/trend/program-trading` | Query: `productCode={productCode}&size=50`; result includes `pagingParam`, `body[]`, `lastPage` |
| Fixed-date trading trend | GET | `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | Query: `productCode={productCode}&from={YYYY-MM-DD}&to={YYYY-MM-DD}`; result is a date-bounded list |

Examples:

```text
GET https://wts-info-api.tossinvest.com/api/v1/mds/broker/trading-ranking?code=A005930
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/trading-trend?productCode=A005930&size=60
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/program-trading?productCode=A005930&size=50
GET https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A005930&from=2026-04-09&to=2026-04-16
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
| Reasoning content interest | GET | `/api/v2/reasoning-contents/interest` | Discovery/personalization content |
| Screener modal | GET | `/api/v2/screener/screen/search/modal` | Screener modal data |

## Cert And Status Helpers

These endpoints were observed during public page loads but live under `wts-cert-api`. Treat them as sensitive unless their current behavior is clearly public metadata.

| Purpose | Method | URL |
|---|---:|---|
| Stock red flags | GET | `https://wts-cert-api.tossinvest.com/api/v1/stock-infos/{productCode}/red-flags` |
| Trading status | GET | `https://wts-cert-api.tossinvest.com/api/v3/trading/order/{productCode}/trading-status` |
| Overview indicator | GET | `https://wts-cert-api.tossinvest.com/api/v1/dashboard/wts/overview/indicator/index?market=kr` |
| Overview ranking | POST | `https://wts-cert-api.tossinvest.com/api/v2/dashboard/wts/overview/ranking` |

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
