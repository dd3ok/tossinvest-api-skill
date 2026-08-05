# Response Notes

Most checked endpoints returned JSON with a top-level `result` key. Do not assume this for every endpoint; verify the response shape before writing client code or documentation.

## Contents

- [Stock And Price Shapes](#stock-and-price-shapes)
- [Index And Indicator Shapes](#index-and-indicator-shapes)
- [Analytics Shapes](#analytics-shapes)
- [Filings And News Shapes](#filings-and-news-shapes)
- [Discovery And Screener Shapes](#discovery-and-screener-shapes)
- [Public Community Shapes](#public-community-shapes)
- [Financial POST Shapes](#financial-post-shapes)
- [Transaction Status Shapes](#transaction-status-shapes)

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
| `/api/v1/c-chart/kr-s/{productCode}/{range}` | Object: `code`, `nextDateTime`, `exchangeRate`, `exchange`, `candles[]`; observed stock ranges include `min:1`, `day:1`, `week:1`, `month:1`; candle entries include OHLCV and amount fields |

No dedicated RSI/MACD/Bollinger response field or endpoint was observed from
`/stocks/A005930/order`. Playwright verification on 2026-04-20 clicked the chart
`+` / `보조지표` button and selected `RSI`; the new requests were icon/font/log
or unrelated dashboard refreshes, not a stock technical-indicator data API. Use
`scripts/stock_chart.py` indicator flags when technical indicators are needed;
they calculate from candle `close` prices and annotate the output with
`source=local-calculation-from-c-chart-candles`.

Do not infer c-chart acceptance from price-details acceptance. On 2026-05-10,
price details accepted `Q520072` and `AMX0221116003`, but c-chart returned HTTP
400 for `us-s/Q520072` and `kr-s/AMX0221116003`. Consumers should validate codes
per endpoint family and record/report skipped incompatible targets separately
from network or payload-shape failures.

Ticker strings are not TossInvest product codes. For US stocks, scripts that accept
display tickers should first resolve `ticker -> TossInvest product/source code`
through a maintained alias table or a verified search/page capture. If the alias is
missing and the raw ticker is sent to price or c-chart endpoints, TossInvest may
return HTTP 400; report this as a product-code resolution failure, not as proof
that TossInvest has no real-time quote/chart path. Keep alias-table details in the
calling application, not in this public skill.

## Index And Indicator Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v2/index-infos/{indexCode}` | Object: `code`, `name`, `logoImageUrl`, `priceFeedType`, optional trading-window fields such as `tradingStartAt`, `tradingEndAt`, and `isMarketOpen`; commodity responses can include `helperText` and `indexUnitDto` |
| `/api/v1/index-prices/{indexCode}` | Object: `open`, `high`, `low`, `close`, `base`, `changeType`, `high52w`, `low52w`, and related price fields |
| `/api/v1/r-chart/{securitiesType}/{indexCode}/{range}/{step}` | Object: `code`, trading window metadata, and `candles[]`; direct checks returned candles for `KGG01P`, `RFU.GCv1`, `KR1BENCH0010`, `ROB.US10YT-RR`, and `VWAP.KRW-BTC` with `securitiesType=crypto`; current page controls include crypto `1w/min:10`, `1y/week:1`, `5y/month:1` and FX `1y/week:1`, `5y/month:1` |
| `/api/v1/c-chart/{securitiesType}/{indexCode}/day:1` | Object: `code`, `nextDateTime`, `exchangeRate`, optional `exchange`, and `candles[]`; `scripts/indices.py --include-daily-quotes` uses cursor paging via `--daily-quote-from` |
| `/api/v1/crypto-prices?productCodes={codes}` | List: `productCode`, OHLCV fields, `changeType`, `high52w`, `low52w`, `usdPerKrwExchangeRate`, `premium`, `premiumRate` |
| `/api/v1/product/exchange-rate?buyCurrency=USD&sellCurrency=KRW` | Object: `code`, `base`, `close` |
| `wts-cert-api /api/v3/dashboard/wts/overview/indicator/mini-chart` | Object: `indexMap`; public overview mini-chart metadata |
| `wts-cert-api /api/v4/dashboard/wts/overview/indicator` | Current public home indicator aggregate; `scripts/dashboard_ranking.py --kind indicator` uses the exact GET path with no query or body |
| `/api/v3/dashboard/wts/overview/indicator/{indexCode}/related-etfs` | Object: `indexCode`, `etfs[]`; empty POST body accepted in verification |
| `/api/v1/stock-infos/index/net-buying/range` | Object: `code`, `step`, `nextDate`, `investorActivityAmounts[]`; current public page accepts `range=week|month|year` |
| `/api/v1/stock-infos/index/net-buying/daily` | Object: `code`, `nextDate`, `investorActivityAmounts[]` |

`scripts/indices.py` has chart presets for these verified r-chart windows:
`intraday=1d/min:5`, `quarter=3m/day:1`, and `daily=1y/day:1`. The script uses
`--securities-type auto` by default: `VWAP.KRW-*` codes infer `crypto`, other
dotted codes such as `RFU.GCv1` and `ROB.US10YT-RR` infer `us-s`, and non-dotted
codes such as `KGG01P` and `KR1BENCH0010` infer `kr-s`. Preserve the original
case for dotted indicator codes.

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

## Calendar Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `wts-cert-api /api/v4/calendar/monthly/{YYYY-MM}` | Object: `events[]`, `includeMajorStock`; monthly page filters are applied client-side by `calendar.py` |
| `wts-cert-api /api/v4/calendar/monthly/{YYYY-MM}/index?countryType=kr|us` | Object: `events[]`, `includeMajorStock`; public index-page calendar subset |
| `wts-cert-api /api/v1/calendar/economic-indicators/{ric}` | Object: `category`, `frequency`, `name`, `announcementDate`, `announcementTime`, `indicatorDetail`, `historicalData[]`, `relatedNews`, `relatedArticles[]`, `upcomingIndicators`, `upcomingLive` |
| `wts-cert-api /api/v1/nova-calendar/ai/analysis/indicators` | Object: `title`, `contents`, `cacheCreatedAt`; public page AI text only |

## Discovery And Screener Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v3/search-all/wts-auto-complete` | List of typed sections. Each row has `type` and `data`; `data.items[]` contains public products, news, industries, screeners, or market indices. `scripts/market_search.py` keeps only bounded UI-useful fields. |
| `/api/v2/dashboard/wts/overview/tics/ranking` | Object: `basedAt`, `duration`, `tics[]`; rows include `ticsId`, `name`, `rank`, `fluctuationRate`, market-cap/trading-amount totals, and leading stock. |
| `/api/v2/dashboard/wts/overview/tics/{ticsId}/stocks` | Object: `nation`, `page`, `size`, `sortBy`, `sortOrder`, `totalCount`, `stocks[]`; rows include price, change, market cap, trading value, volume, analyst opinion, and signal. |
| `/api/v2/dashboard/wts/overview/tics/{ticsId}/etfs` | Object: paging/sort metadata plus `etfs[]`; rows include price, change, trading value, expense ratio, leverage factor, and top holding. |
| `wts-cert-api /api/v1/screener/filters/base` | Object with `basedAt`; `scripts/screener_count.py --include-filter-base` uses exact `{filterId, nation}` bodies for selected allowlisted filters. |
| `wts-cert-api /api/v1/screener/filters/range` | Object with current `min` and `max`; `--include-filter-range` accepts only filters already validated by the script. |

| Endpoint | Observed `result` shape |
|---|---|
| `/api/v1/tics/all` | Object: `baseDateTime`, `ticsItems[]` |
| `/api/v1/rankings/contents/tics_margin_depth1/tags/{tag}` | Object: ranking metadata such as `rankingId`, `info`, `type`, and ranking rows |
| `/api/v2/news/tics/{ticsId}` | Object: `pagingParam`, `body[]`, `lastPage` |
| `POST /api/v2/dashboard/wts/overview/tics/ranking` | Object: `basedAt`, `duration`, `tics[]`; rows include `rank`, `ticsId`, `name`, `fluctuationRate`, KRW/USD trading amount and market cap, `stockCount`, `leadingStock` |
| `/api/v2/dashboard/wts/overview/tics/{ticsId}/overview` | Object: `ticsId`, `name`, `description`, `summary`, `companyCount`, `etfCount`, `depth`, `relatedTics[]` |
| `/api/v2/dashboard/wts/overview/tics/{ticsId}/simple` | Object: `ticsId`, `name`, `summary`, `imageUrl`, `duration`, `changeRate` |
| `/api/v1/dashboard/wts/overview/tics/{ticsId}/comparison-chart` | Object: `baseDate`, `indicators[]`; indicator rows include identity fields plus `prices` and `fluctuationRates` arrays |
| `POST /api/v2/dashboard/wts/overview/tics/{ticsId}/stocks` | Object: `ticsId`, `nation`, `page`, `size=10`, `totalCount`, `sortBy`, `sortOrder`, `stocks[]`; rows include price, change, market cap, trading value, volume, analyst opinion, and public UI signal fields |
| `POST /api/v2/dashboard/wts/overview/tics/{ticsId}/etfs` | Object: `ticsId`, `nation`, `page`, `size=10`, `totalCount`, `sortBy`, `sortOrder`, `includeLeverageInverse`, `etfs[]`; rows include price, change, trading value, expense ratio, leverage factor, and top holding |
| `/api/v2/dashboard/wts/overview/tics/{ticsId}/news?number={page}` | Object: `body[]`, `lastPage`, next `pagingParam`, `totalCount`; fixed observed page size 5 |
| `wts-cert-api /api/v1/screener/screen/count` | Number count for body `{ "filters": [], "nation": "kr" }` or `"us"`; also accepted `RSI_범위`, selected price-condition filters, and selected technical-analysis `conditions[]` filters in verification |
| `wts-cert-api /api/v2/screener/screen` | Object: `totalCount`, `page`, `lastPage`, `stocks[]`, `columns[]`; body requires `pagingParam.size` in addition to `filters[]` and `nation`; `pagingParam.number` worked for page selection; observed `sort` shape uses `column`, `label`, `order` |
| `/api/v1/dashboard/wts/overview/signals?codes={codes}` | Object: `stockCode`, `signals[]`; used for the home live-chart AI summary column |

The checked RSI screen uses filter id `RSI_범위` with condition id
`NUMBER_RANGE_DEFAULT` and type `NUMBER_RANGE`. Oversold-style requests use
`to: 30` with `includeTo: true`; overbought-style requests use `from: 70` with
`includeFrom: true`.

The checked technical screens use these type strings: `PRICE_MOVING_AVERAGE_CROSS_ARRAY`,
`MOVING_AVERAGE_CROSS_ARRAY`, `MOVING_AVERAGE_ALIGN_ARRAY`, and
`PRICE_BOLLINGER_BAND_CROSS_ARRAY`. Direct checks on 2026-04-20 accepted
`conditions[]` bodies for price moving-average cross, moving-average cross,
volume moving-average cross, moving-average alignment, and Bollinger Band cross.

For sorting, guessed shapes such as `{id, order}` returned HTTP 400. A Playwright
capture of the screener page showed the working shape
`{"column":"C_시가총액","label":"시가총액","order":"DESC"}`. Direct checks accepted
that shape for market capitalization, volume, analyst-rating, and the current
preset-specific `C_주가등락률_1W` price-change column.

Direct checks on 2026-04-20 also accepted price-condition filters for 5-day
price change up/down, 20-day price change up, 5-day consecutive rise/fall,
52-week high within 20 days, and 52-week low within 20 days. These use the same
`conditions[]` wrapper as the technical presets.

## Public Community Shapes

| Endpoint | Observed `result` shape |
|---|---|
| `wts-cert-api /api/v4/comments` | Object: `results[]`, `hasNext`, `key`, `totalCount`; use `lastCommentId={key}` for the next page |
| `wts-cert-api /api/v2/comments/{commentId}/replies` | Object: `results[]`, `hasNext`, `key`, `totalCount`; v1 replies returned object keys `comment`, `replies`, `topic` |
| `wts-cert-api /api/v1/boards/STOCK/{productCode}/related` | Object: `about`, `commentCount`, `followingCount`, `isMember`, `logoImageUrl`, `subjectId`, `title` |
| `wts-cert-api /api/v1/community/board/{productCode}/recommend-profiles` | List of profile suggestions; sanitize before displaying |
| `wts-cert-api /api/v1/community/top-rankings/{ranking}` | Object: `type`, `items[]`; `scripts/feed.py --kind community-ranking` emits at most 10 rows and removes profile ids, avatar URLs, and follow/personal flags |

Raw comment rows include public profile and interaction fields such as
`authorUserProfileId`, `author.userProfileId`, `profilePictureUrl`,
`shortDescription`, `statistic.followerCount`, `isFollowing`, `isBookmarked`,
and `isMyProfile`. Do not return raw rows from user-facing scripts.

`scripts/community_comments.py` supports `subjectType=STOCK` and bounded
`subjectType=LOUNGE` reads. It emits sanitized rows with fields such as
`commentId`, `type`, `authorNickname`, `message`, `board`, `statistic`,
`holding`, `createdAt`, `updatedAt`, and optional media summary. The sanitizer
removes profile ids, profile/avatar URLs, follow/bookmark flags, follower counts,
and replaces obvious phone, email, and long-number strings with tokens such as
`redacted-phone`.

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
| `/api/v1/stock-infos/trade/trend/trading-trend` | Object: `pagingParam`, `body[]`, `lastPage`; body entries include investor buy/sell/net volume fields. Live KR rows include aggregate net fields for individual/foreigner/institution total/other corporation plus institution-detail fields: `netFinancialInvestmentBuyVolume`, `netInsuranceBuyVolume`, `netOtherFinancialInstitutionsBuyVolume`, `netTrustBuyVolume`, `netPrivateEquityFundBuyVolume`, `netPensionFundBuyVolume`, `netBankBuyVolume`. Some detail categories expose gross buy fields but not matching sell fields; use explicit `net*BuyVolume` fields for net-flow semantics. |
| `/api/v1/stock-infos/trade/trend/program-trading` | Object: `pagingParam`, `body[]`, `lastPage`; body entries include arbitrage, non-arbitrage, and total buy/sell/net quantities |
| `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | List: date-bounded investor buy/sell/net volume rows. Live KR rows include `netIndividualsBuyVolume` (개인), `netForeignerBuyVolume` (외국인), `netInstitutionBuyVolume` (기관계), `netOtherCorporationBuyVolume` (기타법인), and institution-detail net fields such as `netFinancialInvestmentBuyVolume`, `netInsuranceBuyVolume`, `netOtherFinancialInstitutionsBuyVolume`, `netTrustBuyVolume`, `netPrivateEquityFundBuyVolume`, `netPensionFundBuyVolume`, `netBankBuyVolume`. |
| `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | List: date-bounded accumulated net investor-volume rows |
| `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | Object: accumulated net investor-volume fields by detail category |
| `/api/v1/mds/info/credit` | Object: `pagingParam`, `body[]`, `lastPage`; rows include margin loan and securities lending balance/rate fields |
| `/api/v1/mds/info/lending-trading` | Object: `pagingParam`, `body[]`, `lastPage`; rows include `executionQuantity`, `repaymentQuantity`, `lendingTradingBalanceVolume`, `lendingTradingBalanceAmount` |
| `/api/v1/mds/info/short-selling-trend` | Object: `pagingParam`, `body[]`, `lastPage`; rows include `shortTradingVolume`, `shortTradingAmount`, `shortSellingTradingAmountRatio`, `shortSellingAveragePrice` |
| `/api/v1/mds/info/cfd` | Object: `pagingParam`, `body[]`, `lastPage`; rows include new/settle/balance buy and sell quantity/rate fields |
