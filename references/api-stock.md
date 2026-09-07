# Stock API reference

Use this reference for individual stock metadata, quotes, candles, financials,
company news, filings, and public investor-trend data.
For stock-page composition with comments, see
[stock main-page and community APIs](api-community.md#public-community-and-main-page-apis).
Sector membership and sector news belong to the
[market reference](api-market.md#current-industry-dashboard-and-sector-behavior).

For commands, start with the [stock cookbook](script-cookbook.md#stock-detail);
for returned fields, use [stock and price shapes](response-notes.md#stock-and-price-shapes).

Status labels and host/identifier rules are defined in the
[common catalog](api-catalog.md#verification-status). A script-backed label is
not a current-availability guarantee. Dates below remain scoped observations;
the [2026-09-07 audit](update-audit-2026-09-07.md) states the latest checked scope.

## Contents

- [Stock Summary APIs](#stock-summary-apis)
- [Chart APIs](#chart-apis)
- [Analytics APIs](#analytics-apis)
- [Filings And News APIs](#filings-and-news-apis)
- [Transaction Status APIs](#transaction-status-apis)

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
