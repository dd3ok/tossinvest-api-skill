# Response Notes

Most checked endpoints returned JSON with a top-level `result` key. Do not assume this for every endpoint; verify the response shape before writing client code or documentation.

## Stock And Price Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v1/stock-detail/ui/{productCode}/common` | Object: `name`, `detailName`, `guid`, `symbol`, `marketCode`, `tradingSuspended`, `companyCode`, `badges`, `notices` |
| `/api/v1/stock-infos/header/{productCode}` | Object: `sections[]`; section entries include ranking fields |
| `/api/v2/stock-infos/{productCode}` | Object: `code`, `guid`, `symbol`, `isinCode`, `status`, `name`, `englishName`, `market`, `companyCode`, `companyName` |
| `/api/v2/stock-infos/code-or-symbol/{productCode}` | Same shape as `/api/v2/stock-infos/{productCode}` |
| `/api/v3/stock-prices/details?productCodes={codes}` | List: `code`, `exchange`, `tradeDateTime`, `open`, `high`, `low`, `close`, `volume`, `value`, `base`, `changeType`, `currency` |
| `/api/v3/stock-prices/{productCode}/quotes` | Object: `close`, quote price/volume ladder fields such as `offerPrices`, `offerVolumes`, `bidPrices`, `bidVolumes` |
| `/api/v2/stock-prices/{productCode}/ticks` | List: intraday rows with `time`, `code`, `price`, `base`, `volume`, `tradeType`, `cumulativeVolume` |
| `/api/v2/stock-prices/{productCode}/upper-lower` | Object: `date`, `upperLimit`, `lowerLimit` |
| `/api/v1/c-chart/kr-s/{productCode}/day:1` | Object: `code`, `nextDateTime`, `exchangeRate`, `exchange`, `candles[]`; candle entries include OHLCV and amount fields |

## Analytics Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v1/companies/{companyCode}/sales-compositions` | Object: `code`, `fiscalYear`, `endDate`, `compositions[]`, `dataSource`; compositions include `business`, `product`, `ratio` |
| `/api/v2/companies/{companyCode}/tics` | Object: `baseDate`, `majorList[]`, `minorList[]`; list entries include `id`, `title`, `imageUrl`, `representative`, `companyCount`, `rankings` |
| `/api/v2/stock-infos/{productCode}/overview` | Object: `type`, `market`, `company`, `marketValueKrw`, `marketValue`, `enterpriseValueKrw`, `enterpriseValue`, `dataSource`, `listDate` |
| `/api/v2/stock-infos/consensus/{productCode}` | Object: `targetPrice`, `pointDate`, `pastClosePrices[]` |
| `/api/v1/stock-detail/ui/wts/{productCode}/analyst-opinion` | Object: opinion counts, `targetPrice`, `description` |
| `/api/v1/stock-detail/ui/wts/{productCode}/analyst-reports` | Object: `analystReportGroups[]` |
| `/api/v1/stock-detail/ui/wts/{productCode}/investment-indicators` | Object: `indicatorSections[]` |
| `/api/v1/stock-infos/dividend/{productCode}/summary` | List: `exDate`, `paymentDate`, `currency`, `ratio`, `cash`, `cashKrw`, `yieldRatio`, `ttmYieldRatio` |

## Filings And News Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v1/stock-detail/companies/{companyCode}/filings` | Object: `pagingParam`, `body[]`, `lastPage` |
| `/api/v2/news/companies/{companyCode}` | Object: `pagingParam`, `body[]`, `lastPage` |
| `/api/v2/news/{newsId}` | News detail object; verify exact keys per current response before transforming |

## Discovery And Screener Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v1/tics/all` | Object: `baseDateTime`, `ticsItems[]` |
| `/api/v1/rankings/contents/tics_margin_depth1/tags/{tag}` | Object: ranking metadata such as `rankingId`, `info`, `type`, and ranking rows |
| `/api/v2/news/tics/{ticsId}` | Object: `pagingParam`, `body[]`, `lastPage` |
| `wts-cert-api /api/v1/screener/screen/count` | Number count for body `{ "filters": [], "nation": "kr" }` or `"us"` |

## Financial POST Shapes

The checked analytics POST endpoints accepted `Content-Type: application/json` with `{}` during manual verification:

```text
POST /api/v2/companies/{productCode}/financial-statements/comprehensive
POST /api/v2/companies/{productCode}/financial-statement-records
POST /api/v2/companies/{productCode}/financial/estimate/revenue
POST /api/v2/companies/{productCode}/financial/estimate/eps
POST /api/v2/companies/{productCode}/financial/estimate/operating-income
POST /api/v2/stock-infos/evaluation/{productCode}
POST /api/v2/stock-infos/evaluation-comparison/{productCode}
POST /api/v2/stock-infos/stability/{productCode}
POST /api/v2/stock-infos/revenue-and-net-profit/{productCode}
POST /api/v2/stock-infos/operating-income/{productCode}
```

Observed result keys:

| Endpoint family | Observed `result` keys |
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

## Transaction Status Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v1/mds/broker/trading-ranking?code={productCode}` | Object: `code`, `top5ActivityList[]`, foreign ask/bid volume and value fields, `updatedAt` |
| `/api/v1/stock-infos/trade/trend/trading-trend` | Object: `pagingParam`, `body[]`, `lastPage`; body entries include investor buy/sell/net volume fields |
| `/api/v1/stock-infos/trade/trend/program-trading` | Object: `pagingParam`, `body[]`, `lastPage`; body entries include arbitrage, non-arbitrage, and total buy/sell/net quantities |
| `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | List: date-bounded investor buy/sell/net volume rows |
| `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | List: date-bounded accumulated net investor-volume rows |
| `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | Object: accumulated net investor-volume fields by detail category |
| `/api/v1/mds/info/credit` | Object: `pagingParam`, `body[]`, `lastPage`; verify each `/mds/info/{type}` variant separately |

## Pension-Fund Trend Notes

Use `netPensionFundBuyVolume` as the UI-matching pension-fund net-buy value. Positive values indicate pension-fund net buying; negative values indicate pension-fund net selling.

Treat `pensionFundBuyVolume` as a reference gross-buy field. It was observed in recent `trading-trend` rows and matched the institution detail buy-volume aggregation, but it is not the investor-status net-buy value and is not present in every date-bounded response.

For `A005930`, `fixed-trading-trend` returned date-bounded `netPensionFundBuyVolume` rows back to `2019-04-01` during verification. Older date windows returned `200` with an empty list. Long windows can be truncated, so prefer yearly or smaller windows when collecting history.
