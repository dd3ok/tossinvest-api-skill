# Transaction Status Audit — 2026-09-16

The baseline repository covered most transaction-status endpoint families, but
did not fully reproduce the current page. The main gaps were the two credit-detail
endpoints, investor availability and intraday grouping in normalized output,
and cursor paging for recent investor/program history. This is an audit of the
implementation at commit `7d2b7611ef9d3e8dab2e07fa6682cccebd319dca`, followed by
the [authorized implementation follow-up](#implementation-follow-up).

## Contents

- [Evidence and scope](#evidence-and-scope)
- [Verified routes and request shapes](#verified-routes-and-request-shapes)
- [Findings requiring changes](#findings-requiring-changes)
- [Field mappings and units](#field-mappings-and-units)
- [Interpretation cautions](#interpretation-cautions)
- [Implementation follow-up](#implementation-follow-up)

## Evidence and scope

- **UI-observed:** the logged-out [A010170 transaction-status page][page],
  including investor, program, credit, lending, short-selling, and CFD views.
- **Deployed-code verified:** the page's [stock-layout bundle][layout] supplies
  the UI field mappings; [shared query bundle][query], module `34755`, supplies
  endpoint selection, query parameters, and continuation behavior.
- **Live-verified:** 15 read-only requests covering 12 distinct paths on
  `https://wts-info-api.tossinvest.com`, including the older `credit` route.
  Direct checks ran on 2026-09-16, 11:06:09–11:12:27 KST. They used one KR stock,
  `A010170`, three-row pages, one bounded date range, and one CFD request with
  the deployed client's `size=50`.

The browser tool did not expose network capture. UI observations, downloaded
public JavaScript, and independently executed API requests are separate evidence;
these are not captured browser requests. The findings do not establish behavior
for other securities, every date range, or authenticated trading functions.
Only selected public values and field names are recorded here.

The downloaded layout bundle SHA-256 was
`c9ce66a0ae68a1f72eedfc102d3cfbf71fd8f1d200848ef76fa439aef634667b`;
the shared query bundle SHA-256 was
`789062555b7523a69ad84016206a93fe888a0ce878b97338b6ac4ac57c2427d4`.

## Verified routes and request shapes

All routes below use GET on `wts-info-api.tossinvest.com`. Recent and MDS page
results contain `body`, `pagingParam`, and `lastPage`. The shared query function
uses `productCode` for recent investor/program data and `stockCode` for MDS
data, with `size=50` and optional `number`/`key`; it continues using the returned
`pagingParam` when `lastPage` is false. A separate investor query also supports
cursor paging with a default size of 60. [Source: deployed query bundle][query].

| Purpose | Path | Verified parameters / result |
|---|---|---|
| Broker ranking | `/api/v1/mds/broker/trading-ranking` | `code=A010170`; object with five `top5ActivityList` entries |
| Recent investor table | `/api/v1/stock-infos/trade/trend/trading-trend` | `productCode=A010170&size=3`; page 2 accepted returned `number` and `key` |
| Program trading | `/api/v1/stock-infos/trade/trend/program-trading` | `productCode=A010170&size=3`; page 2 accepted returned `number` and `key` |
| Fixed-date investor data | `/api/v1/stock-infos/trade/trend/fixed-trading-trend` | `productCode=A010170&from=2026-09-09&to=2026-09-16`; six-item list |
| Accumulated investor data | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend` | Same date parameters; six-item list |
| Accumulated investor detail | `/api/v1/stock-infos/trade/trend/accumulated-fixed-trading-trend/detail` | Same date parameters; object with accumulated category fields |
| Credit financing / 신용융자 | `/api/v1/mds/info/margin-loan` | `stockCode=A010170&number=1&size=3`; two rows |
| Credit stock lending / 신용대주 | `/api/v1/mds/info/securities-landing` | Same paging parameters; two rows; `landing` is the exact deployed spelling |
| Lending / 대차거래 | `/api/v1/mds/info/lending-trading` | Same paging parameters; two rows |
| Short selling / 공매도 | `/api/v1/mds/info/short-selling-trend` | Same paging parameters; two rows |
| CFD | `/api/v1/mds/info/cfd` | Three-row request was empty; `stockCode=A010170&size=50` returned 25 rows |
| Older combined credit route | `/api/v1/mds/info/credit` | Three-row request returned two rows, but lacks the current credit UI's complete fields |

The direct request paths can be reproduced from this table. The current UI
selection of `margin-loan` and `securities-landing`, rather than `credit`, is
established by the layout's credit selector and the query module together.
[Sources: layout][layout], [query module][query], [margin-loan response][loan],
[securities-landing response][stock-loan], [older credit response][credit].

## Findings requiring changes

### 1. Current credit UI coverage is incomplete

[`MDS_INFO_TYPES` in trading_trend.py](../scripts/trading_trend.py) exposes
`credit`, `lending-trading`, `short-selling-trend`, and `cfd`. It lacks both
current credit selectors. The older route still responds, so this is a coverage
gap rather than an endpoint outage. Its `marginLoan*` and `securitiesLending*`
fields provide balance and change data, but not all the new/returned quantities
and lending-rate values shown by the current credit UI.
[Sources: credit selector and row definitions][layout], [current loan data][loan],
[older combined data][credit].

Add the two verified selectors while preserving the older route as an explicitly
separate compatibility option. Update the credit mapping in
[api-stock.md](api-stock.md#transaction-status-apis),
[response-notes.md](response-notes.md#transaction-status-shapes), and the
[page checker](../scripts/page_api_check.py) alongside the CLI.

### 2. Normalization can turn unavailable investor data into an apparent zero

For 2026-09-16, the direct recent response had `hasIndividual=false` and
`netIndividualsBuyVolume=0`; the UI rendered an unavailable marker. The same row
had `hasForeigner=true` and `hasInstitution=true`. The deployed table gates its
three aggregate cells on the corresponding availability flags, whereas
`normalize_investor_rows()` copies numeric fields without those flags. It also
drops `updatedAt` and `inMarketTime`, which prevents normalized consumers from
distinguishing this intraday state. The raw `result` remains available in the
script's output. [Sources: recent response][investor], [UI rendering][layout],
[normalizer](../scripts/trading_trend.py).

Intraday detail also differs from the normalizer's fixed eleven-category shape.
In the layout's `TT` renderer, `inMarketTime` selects grouped columns: financial
investment/insurance/other financial use `netInsuranceOtherBuyVolume`, and
trust/private equity use **`trustAndPrivateEquityFundBuyVolume`**, exactly as
spelled, without a `net` prefix. After-hours rendering uses separate category
net fields. Institution detail cells, including pension, bank, and other
corporation, are gated by `hasInstitution` in that renderer. This is a rendering
observation, not proof that the flag provides an independent availability
contract for each category. [Source: layout's `TT` renderer][layout].

Preserve availability flags, intraday state, timestamp, and source fields during
normalization; represent unavailable values explicitly. Model grouped intraday
data separately from detailed category data. Validate the semantics of the
unprefixed trust/private-equity field before assigning it a normalized net-flow
meaning.

### 3. Recent investor/program cursor paging is supported by the API, but rejected by the CLI

`fetch_trading_trend()` accepts `--page`/`--key` only for MDS types; its recent
path builder sends only `productCode` and `size`. Both recent APIs accepted the
returned first-page cursor in direct checks:

| Endpoint | Page-2 cursor used | Returned rows | Next cursor |
|---|---|---:|---|
| `trading-trend` | `number=2&size=3&key=2026-09-13` | 3 | `number=3&size=3&key=2026-09-08` |
| `program-trading` | `number=2&size=3&key=2026-09-11` | 3 | `number=3&size=3&key=2026-09-08` |

Extend the existing validated cursor interface to these two types; preserve
server-returned cursor values instead of deriving dates locally.
[Sources: investor page 2][investor-p2], [program page 2][program-p2],
[query module][query], [CLI](../scripts/trading_trend.py).

Offline checks reproduced all three gaps without additional HTTP calls:
normalizing the saved live row emitted individual net volume `0` without its
availability flag; building either current credit path raised an unknown-type
error; requesting page 2 for investor/program data raised the MDS-only paging
validation error. The existing `TradingTrendScriptTests` and
`PageApiCheckScriptTests` passed (16 tests). Those tests do not establish coverage
of the availability/grouping, new credit selectors, or recent paging cases
identified here. These checks describe the baseline, before the follow-up below.

## Field mappings and units

The following mappings come from the deployed row definitions and were checked
against available response fields. Quantities are displayed as shares; KRW
amounts may be abbreviated by the UI. Percentage fields listed here contain
percentage points: the renderer divides them by 100 before percent formatting,
so `1.85` displays as `1.85%`. Null handling varies by field; preserve nulls in
data output. [Source: UI row definitions][layout].

In the checked response samples, quantities were JSON integers; rate fields and
lending/short-selling amount fields were floating-point numbers. `baseDate` and
`updatedAt` were strings; availability flags and `inMarketTime` were booleans
where present. The recent investor response's `buyBalanceQuantity`,
`sellBalanceQuantity`, `buyBalanceRate`, and `sellBalanceRate` were null in the
saved samples. These are observed types, not a guaranteed schema.
[Sources: investor][investor], [credit][loan], [lending][lending], [short selling][short].

| UI / metric | Exact response fields | Rendering / interpretation |
|---|---|---|
| Broker buy/sell ranking | `top5ActivityList[].bidBrokerName`, `bidTradingVolume`, `askBrokerName`, `askTradingVolume` | Buy and sell lists independently filter empty broker names; quantities are shares |
| Investor aggregate net flow | `netIndividualsBuyVolume`, `netForeignerBuyVolume`, `netInstitutionBuyVolume` | Signed shares, gated by `hasIndividual`, `hasForeigner`, `hasInstitution` |
| Foreign holding ratio | `foreignerRatio` | Percentage points; UI uses `0%` when absent |
| Investor price columns | `close`, `base` | Close is KRW; change is `close - base`; rate derives from `(close - base) / base`, with a zero-base guard |
| Program total | `totalNetBuyQuantity`, `totalNetBuyChangeQuantity`, `totalBuyQuantity`, `totalSellQuantity` | Net, net change, buy, sell quantities |
| Program non-arbitrage / arbitrage | `nonArbitrageNetBuyQuantity`, `nonArbitrageNetBuyChangeQuantity`, `nonArbitrageBuyQuantity`, `nonArbitrageSellQuantity`; equivalent `arbitrage*` fields | Same four metrics per category; change fields need inclusion in the documentation |
| Both current credit views | `increaseDecreaseQuantity`, `newQuantity`, `returnQuantity`, `balanceQuantity`, `balanceRate`, `lendingRate` | Change/new/returned/balance shares; balance ratio and lending ratio in percentage points |
| Lending | `lendingTradingFluctuation`, `executionQuantity`, `repaymentQuantity`, `lendingTradingBalanceVolume`, `lendingTradingBalanceAmount` | Change/new/returned/balance shares and balance KRW amount; the UI change field is **not** `lendingTradingIncreaseDecreaseQuantity` |
| Short selling | `shortSellingTradingAmountRatio`, `shortTradingVolume`, `shortTradingAmount`, `shortSellingAveragePrice`, `tradingAmount`, `volume` | Amount ratio in percentage points; short shares/amount, average KRW price, total KRW amount/shares; average price is rounded down to integer KRW |
| CFD buy | `newBuyQuantity`, `settleBuyQuantity`, `buyBalanceQuantity`, `buyBalanceRate` | New/settled/balance shares and balance percentage points |
| CFD sell | `newSellQuantity`, `settleSellQuantity`, `sellBalanceQuantity`, `sellBalanceRate` | New/settled/balance shares and balance percentage points |

The short-selling response also includes `shortSellingRatio`, which is distinct
from the UI's amount-ratio field: on 2026-09-14 they were `0.544` and `0.54`,
respectively. Use the field corresponding to the intended measure.
[Sources: short-selling response][short], [UI mapping][layout].

Selected stable-date comparisons between direct responses and the visible page:

| Date / section | Values checked |
|---|---|
| 2026-09-15 program | Net `86,382`; buy `1,078,476`; sell `992,094` shares |
| 2026-09-15 credit financing | Balance `3,097` shares; change/new/returned quantities and both ratios zero |
| 2026-09-15 credit stock lending | All six displayed metrics zero |
| 2026-09-15 lending | Change `122,151`; new `354,566`; returned `232,415`; balance `8,298,862` shares; API balance amount `118,092,806,260` KRW, displayed as `1,180억원` |
| 2026-09-15 short selling | `93,141` shares; amount ratio `1.85%`; API amount `1,325,743,070` KRW, displayed as `13억원`; API average `14,233.7217`, displayed as `14,233원` |
| 2026-09-07 CFD buy | New `0`; settled `300`; balance `0` shares |

[Sources: observed page][page], [program response][program], [credit financing][loan],
[credit stock lending][stock-loan], [lending response][lending],
[short-selling response][short], [CFD response][cfd50].

## Interpretation cautions

**An empty CFD page does not establish an empty history.** The request with
`number=1&size=3` returned `body=[]`, `lastPage=false`, and next cursor
`number=2&size=3&key=2026-09-02`. The deployed client's initial `size=50` request
returned 25 rows, most recent date 2026-09-07, also with `lastPage=false`.
Preserve pagination metadata and use bounded continuation when history is
needed. A short page is not itself an end-of-history signal. This is a consumer
and documentation caution; the current single-page script preserves the raw
pagination metadata. [Sources: small CFD page][cfd3], [UI-sized CFD page][cfd50],
[query continuation rule][query].

**Recent and fixed-date investor series are not interchangeable.** For
2026-09-15, `netForeignerBuyVolume` was `103,327` in the recent endpoint and
`97,744` in the fixed-date endpoint. The visible daily table showed `103,327`.
The page states that foreign net purchases include off-market transactions,
but these observations do not establish the cause of the endpoint discrepancy
or prove that fixed-date data excludes such transactions. Preserve endpoint
provenance when comparing, aggregating, or exporting these series.
[Sources: recent response][investor], [fixed-date response][fixed],
[page note][page].

Historical documentation should retain its observation dates. The older credit
mapping in [api-stock.md](api-stock.md#transaction-status-apis) should be
qualified with this current mapping; a successful older route alone does not
verify coverage of the current UI.

## Implementation follow-up

After the user authorized fixes, the three identified gaps were addressed:
both current credit selectors coexist with legacy `credit`; recent investor
and program data accept validated response cursors; normalized category rows
preserve availability/timing metadata and mask unavailable or grouped values.
Separate `normalizedInvestorGroups` retain source fields with `valueKind=net`
or `unspecified`, preserving the trust/private-equity semantic uncertainty.
Raw results remain unchanged. The page checker includes both current credit
routes. The focused transaction/page-check suite passes 25 tests, including
nine added regressions; implementation validation used no additional HTTP calls.

[page]: https://www.tossinvest.com/stocks/A010170/transaction-status
[layout]: https://www.tossinvest.com/assets/v2/_next/static/chunks/3035-9aab83074d3fb73e.js
[query]: https://www.tossinvest.com/assets/v2/_next/static/chunks/9196-5e2fc6fb74a48df3.js
[investor]: https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/trading-trend?productCode=A010170&size=3
[investor-p2]: https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/trading-trend?productCode=A010170&number=2&size=3&key=2026-09-13
[program]: https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/program-trading?productCode=A010170&size=3
[program-p2]: https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/program-trading?productCode=A010170&number=2&size=3&key=2026-09-11
[fixed]: https://wts-info-api.tossinvest.com/api/v1/stock-infos/trade/trend/fixed-trading-trend?productCode=A010170&from=2026-09-09&to=2026-09-16
[loan]: https://wts-info-api.tossinvest.com/api/v1/mds/info/margin-loan?stockCode=A010170&number=1&size=3
[stock-loan]: https://wts-info-api.tossinvest.com/api/v1/mds/info/securities-landing?stockCode=A010170&number=1&size=3
[credit]: https://wts-info-api.tossinvest.com/api/v1/mds/info/credit?stockCode=A010170&number=1&size=3
[lending]: https://wts-info-api.tossinvest.com/api/v1/mds/info/lending-trading?stockCode=A010170&number=1&size=3
[short]: https://wts-info-api.tossinvest.com/api/v1/mds/info/short-selling-trend?stockCode=A010170&number=1&size=3
[cfd3]: https://wts-info-api.tossinvest.com/api/v1/mds/info/cfd?stockCode=A010170&number=1&size=3
[cfd50]: https://wts-info-api.tossinvest.com/api/v1/mds/info/cfd?stockCode=A010170&size=50
