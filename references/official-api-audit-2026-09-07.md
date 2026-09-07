# Official API Audit — 2026-09-07

Documentation-only audit of the official Open API. No OAuth token issuance, authenticated API request, account/order action, or WebSocket connection was performed. Public document GET responses were read and parsed in memory.

Repository baseline: `3451e9825e3ff4202c23eb133a659f26cbfe57ce`. Findings describe published contracts, not verified runtime behavior. All official operations remain reference-only in this unauthenticated public-web skill.

## Contents

- [Source Evidence](#source-evidence)
- [Comparison Limits](#comparison-limits)
- [REST Operation Inventory](#rest-operation-inventory)
- [Schema Inventory](#schema-inventory)
- [AsyncAPI Inventory](#asyncapi-inventory)
- [Contract Findings](#contract-findings)
- [Document Disagreements](#document-disagreements)

## Source Evidence

SHA-256 below hashes the exact response bytes before UTF-8 decoding, including any BOM. A successful document GET proves document availability only. Final URL equaled requested URL for every source.

| Source | Retrieved UTC | HTTP / bytes | SHA-256 |
| --- | --- | --- | --- |
| [llms](https://developers.tossinvest.com/llms.txt) | 2026-09-06T23:42:56+00:00 | 200 / 2668 | `a57be4baa04d60b68897b2766802bd626b9c88d7fcea1c5306d2318cb36a9988` |
| [overview](https://openapi.tossinvest.com/openapi-docs/overview.md) | 2026-09-06T23:42:56+00:00 | 200 / 27864 | `dfad8c9251917daf39d2b2a9e455f0d7cadddafb42a34f47b2ee8d67bf4addd8` |
| [rest](https://openapi.tossinvest.com/openapi-docs/latest/openapi.json) | 2026-09-06T23:42:57+00:00 | 200 / 417769 | `a7b32ba754401d13fa649ba91eebd212420eb1afab28e9c2c0d6ea8d43055fed` |
| [markdown](https://openapi.tossinvest.com/openapi-docs/latest/api-reference/README.md) | 2026-09-06T23:42:57+00:00 | 200 / 23895 | `30c0532c1cc4010d1d7ec0878cbb0a1c2cfd291d104eb4e3cc99683d7f8da0f5` |
| [async](https://openapi.tossinvest.com/openapi-docs/latest/asyncapi.json) | 2026-09-06T23:42:57+00:00 | 200 / 41523 | `130251057fd9535a3e276099f9166b445f8c51f505f30540758e4b209231282e` |

REST: OpenAPI `3.1.0`, document `1.2.14`, 33 paths, 36 operations, 13 tags, 90 component schemas.
AsyncAPI: specification `3.0.0`, document `1.2.2`, 4 channels, 10 operations.
Structural reference traversal: 370 REST `$ref` occurrences and 20 AsyncAPI occurrences; unresolved local references: 0. This is reference-integrity checking, not a full OpenAPI/AsyncAPI validator.

## Comparison Limits

The prior local boundary recorded document 1.2.9, 27 paths and 13 tags on 2026-08-05. The original 1.2.9 JSON is unavailable locally. Current path count is +6 and tag count unchanged, but a complete historical schema/operation diff cannot be claimed.
All 24 distinct explicitly documented method/path pairs from the prior boundary remain present. Missing explicit pairs: none. This does not prove that every historical path or field survived.

Six GET paths absent from that local record are present now: `/api/v1/stocks/all` and `/api/v1/stocks/{symbol}/investor-trading`, `/program-trades`, `/short-selling`, `/credit-trades`, `/securities-lending`. Treat these as additions to the local reference; the exact upstream introduction release is unverified. Existing operations and all schemas below are current-doc-verified with historical property changes undetermined.

## REST Operation Inventory

Each row was parsed from the current canonical REST document. Status: `current-doc-verified`, not script-backed or runtime-verified. An operation fingerprint hashes the canonicalized complete operation object; reusable schemas/parameters are inventoried separately in the source document. Crosswalk entries describe a comparison target, not interchangeable endpoints.

| Method / path | operationId / tag | Parameters (location:name) | Public-web comparison / boundary | Operation SHA-256 |
| --- | --- | --- | --- | --- |
| `POST /oauth2/token` | `issueOAuth2Token` / Auth | none | official-only; reference-only; no web CLI | `89e51b8863f321d51461e2ae99417660afe295d2ffa3709b15b342068e355399` |
| `GET /api/v1/orderbook` | `getOrderbook` / Market Data | query:symbol* | quote.py; REST snapshot overlap only | `1e98532c5eb98097b0f56c38eae264f722462d741fd80b32b15826cb0ab68b92` |
| `GET /api/v1/prices` | `getPrices` / Market Data | query:symbols* | quote.py; REST snapshot overlap only | `5cf23f43dbda5cfea48973d27baf206d1560f25e2a515b16fa0ec9c24b17c86f` |
| `GET /api/v1/trades` | `getTrades` / Market Data | query:symbol*, query:count | quote.py; REST snapshot overlap only | `9c4e5238b7e5eed0a93d0857c60e668875705cb038159f385144d3fceced49f5` |
| `GET /api/v1/price-limits` | `getPriceLimit` / Market Data | query:symbol* | quote.py; REST snapshot overlap only | `6ed638176b3a924e956b2bf5570ed60c8db4353193e2783e467f8a31b33051cd` |
| `GET /api/v1/candles` | `getCandles` / Market Data | query:symbol*, query:interval*, query:count, query:before, query:adjusted | stock_chart.py; interval/cursor/adjustment mapping required | `8cbfe1e4a42337572671c33ca2922012aac285e93e22e780d92c8392497184b5` |
| `GET /api/v1/stocks` | `getStocks` / Stock Info | query:symbols* | stock_summary.py / stock_page.py; resolve identifiers | `575100f7ea5e075a3b2e4d02fa2e31b7860d6c316970d4166e09da10bb7f095a` |
| `GET /api/v1/stocks/all` | `listStocks` / Stock Info | query:market*, query:status, query:securityType, query:commonShare | universe discovery; web market_search/screener differ | `2ff3af52a1bd08450a82f4347efc0af5833618d57d5f6b20178cc3af609a49e1` |
| `GET /api/v1/stocks/{symbol}/warnings` | `getStockWarnings` / Stock Info | path:symbol* | stock_summary.py / stock_page.py; resolve identifiers | `08913f2fd2487e6307c4e51e12b685e6d0a1ac715d988c8aa1560c09ee04b32f` |
| `GET /api/v1/stocks/{symbol}/investor-trading` | `getStockInvestorTrading` / Stock Info | path:symbol*, query:count, query:until | trading_trend.py; compare volume/money, venue and finalization | `35dd291c3aba6292a993818fd5b5f22a49e13184c5f8b2e9e98acfeaf196b00b` |
| `GET /api/v1/stocks/{symbol}/program-trades` | `getStockProgramTrades` / Stock Info | path:symbol*, query:count, query:until | trading_trend.py; compare volume/money, venue and finalization | `19790ca73dc455ea30e5f2a76f9fe690cb3087e2ce7fefde48ef2204954918ab` |
| `GET /api/v1/stocks/{symbol}/short-selling` | `getStockShortSelling` / Stock Info | path:symbol*, query:count, query:until | trading_trend.py; compare volume/money, venue and finalization | `ca89e4ce16d66656b2a1b6c4d5d5a3e99b06d8231b399940000a8d0379163ab3` |
| `GET /api/v1/stocks/{symbol}/credit-trades` | `getStockCreditTrades` / Stock Info | path:symbol*, query:count, query:until | trading_trend.py; compare volume/money, venue and finalization | `ba25590dfd36d441eb816473a75e3097d0a55bf6b374d15d08201f5c9b736e4f` |
| `GET /api/v1/stocks/{symbol}/securities-lending` | `getStockSecuritiesLending` / Stock Info | path:symbol*, query:count, query:until | trading_trend.py; compare volume/money, venue and finalization | `3690e5d87aebb8f1fb3de44249bf43a7cb93c008b71988ce8ac33a9f7640a92c` |
| `GET /api/v1/exchange-rate` | `getExchangeRate` / Market Info | query:dateTime, query:baseCurrency*, query:quoteCurrency* | indices.py; symbol/asset/unit mapping required | `f17d09748171418e700d25b4f025c3f09289f18aed44cb6f5a6fd6b92f4bd82f` |
| `GET /api/v1/market-calendar/KR` | `getKrMarketCalendar` / Market Info | query:date | market sessions; calendar.py is event calendar, not equivalent | `b55026a3c5465660606366c2478f82d35cc9d2139cd1703e0a7fecf1f16b7e74` |
| `GET /api/v1/market-calendar/US` | `getUsMarketCalendar` / Market Info | query:date | market sessions; calendar.py is event calendar, not equivalent | `ce972ad04afa71e12cb480f9ebfef8ebb59c64376b8be526c615cb8a1d384ee0` |
| `GET /api/v1/rankings` | `getRankings` / Ranking | query:type*, query:marketCountry*, query:duration*, query:excludeInvestmentCaution, query:count | dashboard_ranking.py; type/duration semantics differ | `6119de8b7c7cbe93abbf2404a1b5cf54fb6cfeebf8c67471bf096d9a79d50a8a` |
| `GET /api/v1/market-indicators/prices` | `getMarketIndicatorPrices` / Market Indicators | query:symbols* | indices.py; symbol/asset/unit mapping required | `db3b4ab2ec7a1d69e24d4d3459ea3b97a7861393cc65656ba254f9cc82316cde` |
| `GET /api/v1/market-indicators/{symbol}/candles` | `getMarketIndicatorCandles` / Market Indicators | path:symbol*, query:interval*, query:count, query:before | indices.py; symbol/asset/unit mapping required | `e577b308d916bdfdbfa3d2e38773f9f9b8e41a8439175b437231853f906af3e2` |
| `GET /api/v1/market-indicators/{symbol}/investor-trading` | `getMarketIndicatorInvestorTrading` / Market Indicators | path:symbol*, query:interval*, query:count, query:until | indices.py; symbol/asset/unit mapping required | `5870951ee4f2a5bfbb2a6651a4f302396b53e9a0c68d27634f2aa333d7e72573` |
| `GET /api/v1/accounts` | `getAccounts` / Account | none | official-only; reference-only; no web CLI | `fd9e336c85af6ea51ff8226b70ef5d9afd934f0fda8d9ff2b030b84355fb9afb` |
| `GET /api/v1/holdings` | `getHoldings` / Asset | header:X-Tossinvest-Account*, query:symbol | official-only; reference-only; no web CLI | `78b969a1fbc8ca7dca28317028ec16e4cc0c38635e87751be40360fb851897fa` |
| `GET /api/v1/orders` | `getOrders` / Order History | header:X-Tossinvest-Account*, query:status*, query:symbol, query:from, query:to, query:cursor, query:limit | official-only; reference-only; no web CLI | `0d63c3fa7d0550395c7891144bbd6a2cda43f497985ad2a080cea0316f4f1360` |
| `POST /api/v1/orders` | `createOrder` / Order | header:X-Tossinvest-Account* | official-only; reference-only; no web CLI | `72f3c3bd129a76fc6326f335c3eeece2ee1ca59cca468be00916e6d92d27cfa1` |
| `GET /api/v1/orders/{orderId}` | `getOrder` / Order History | header:X-Tossinvest-Account*, path:orderId* | official-only; reference-only; no web CLI | `d4f9b3d083a9b0895612544e9eb6e9ef9f0d1150eb5569623ac11d12df4f501d` |
| `POST /api/v1/orders/{orderId}/modify` | `modifyOrder` / Order | header:X-Tossinvest-Account*, path:orderId* | official-only; reference-only; no web CLI | `e67e93fe39c4bf064c01f36cd0ab9d88d7f7dd45d6ee959bcafb2a1f79127a3a` |
| `POST /api/v1/orders/{orderId}/cancel` | `cancelOrder` / Order | header:X-Tossinvest-Account*, path:orderId* | official-only; reference-only; no web CLI | `ebcc1b4a1c2ff929d6bc157a24d954097bf9b8da1234099a5dfd10dc7f3b03ee` |
| `POST /api/v1/conditional-orders` | `createConditionalOrder` / Conditional Order | header:X-Tossinvest-Account* | official-only; reference-only; no web CLI | `1eeb617e6a27db0962543040a706e3cbc6dbf9a3b7fee0995e47451699a9c5ea` |
| `GET /api/v1/conditional-orders` | `getConditionalOrders` / Conditional Order History | header:X-Tossinvest-Account*, query:status*, query:symbol, query:cursor, query:limit | official-only; reference-only; no web CLI | `d24af80db5e1042348823eab051ce6e24c111629240565028b7569c51f9e3dbe` |
| `GET /api/v1/conditional-orders/{conditionalOrderId}` | `getConditionalOrder` / Conditional Order History | header:X-Tossinvest-Account*, path:conditionalOrderId* | official-only; reference-only; no web CLI | `e3dcab0c3df1ef555a130320f41e9e7ee18af5ca7eb290fb9b23cd8411dbcd5e` |
| `DELETE /api/v1/conditional-orders/{conditionalOrderId}` | `cancelConditionalOrder` / Conditional Order | header:X-Tossinvest-Account*, path:conditionalOrderId* | official-only; reference-only; no web CLI | `a0f69d16279e820c5d4a19ff4b764a564e41b7ed8b9f124a8ce019a56abd573e` |
| `POST /api/v1/conditional-orders/{conditionalOrderId}/modify` | `modifyConditionalOrder` / Conditional Order | header:X-Tossinvest-Account*, path:conditionalOrderId* | official-only; reference-only; no web CLI | `02b8bdaf34b623de4d68969fe0b227c74273f24b93ff6c9c50eb59612a25f2a9` |
| `GET /api/v1/buying-power` | `getBuyingPower` / Order Info | header:X-Tossinvest-Account*, query:currency* | official-only; reference-only; no web CLI | `246ffc18853bd995c8f90c2d05fa164fdf08b40124fa7cd496f19181fd1bafe5` |
| `GET /api/v1/sellable-quantity` | `getSellableQuantity` / Order Info | header:X-Tossinvest-Account*, query:symbol* | official-only; reference-only; no web CLI | `5da3b979e81f73996a2c3ee877220caf38b2d6f100d6ae9139e81e24bcaf7f84` |
| `GET /api/v1/commissions` | `getCommissions` / Order Info | header:X-Tossinvest-Account* | official-only; reference-only; no web CLI | `bc1cd601992301381c96b23f51e1f32105a9ac5958f82dad89787e985cc41b6f` |

`*` marks a required parameter. Request bodies, response status maps, security overrides, nested schemas, descriptions and examples are included in each operation fingerprint; the source JSON remains authoritative for their full definitions. No current operation declares `deprecated: true`.

## Schema Inventory

All 90 named REST component schemas were enumerated and traversed recursively, including nested properties, union/composition schemas, references, formats, enums, constraints and examples. The table shows top-level fields/requiredness and a fingerprint of the complete schema object. A fingerprint is a reproducible comparison baseline, not proof of unchanged historical behavior. Field-level historical additions/removals remain unverified because the old JSON is absent.

| Schema | Top-level type | Fields | Required fields | Complete schema SHA-256 |
| --- | --- | --- | --- | --- |
| `Account` | object | accountNo, accountSeq, accountType | accountNo, accountSeq, accountType | `fd38a922bb07ad031f31aefeadbb888644864be8b5470d5bdcbd5e61f6c8fb70` |
| `AfterMarketSession` | object | startTime, singlePriceAuctionEndTime, endTime | startTime, endTime | `d9f921381e575966009794cb30109895c75310666d8728eda064fbb9adc72063` |
| `ApiError` | object | requestId, code, message, data | requestId, code, message | `39632db404dd6701424226253722c3b6123bef1873feee8bcb68e190fbdc10a0` |
| `ApiResponse` | object | result | result | `a28de11365d367a0aa66960f7726861e08b43c1ace53b4d9d5ebc0d68b7219ef` |
| `BuyingPowerResponse` | object | currency, cashBuyingPower | currency, cashBuyingPower | `a533482fdbbde359d60c5aceed758c31798cfe4224c773b0dd949630567cf23f` |
| `Candle` | object | timestamp, openPrice, highPrice, lowPrice, closePrice, volume, currency | timestamp, openPrice, highPrice, lowPrice, closePrice, volume, currency | `947cef6035f0907db00f6b85ac3ae63054a02213e144cfea70b4c9086b756619` |
| `CandlePageResponse` | object | candles, nextBefore | candles | `2af5c23a9555fe5efbfd6751d33be65c9e37de9c60147db026e9b2b582a8e371` |
| `CfdBalance` | object | buyBalanceQuantity, buyBalanceRate, sellBalanceQuantity, sellBalanceRate | buyBalanceQuantity, buyBalanceRate, sellBalanceQuantity, sellBalanceRate | `3072a334963b5d8136fd8cc05d80fda376626874e88c507fa11e391473a90f95` |
| `Commission` | object | marketCountry, commissionRate, startDate, endDate | marketCountry, commissionRate | `55e0c15bfa066be4553d4c43ee8e5f37f012923c8e7df3bad34d464d039e4aab` |
| `ConditionRequest` | object | orderSide, triggerPrice, orderPrice | orderSide, triggerPrice | `728ca7e826c608d5a00cd36ea4123d58f4fe89fb3d939e3d36ec01c97f0411d5` |
| `ConditionalOrderCondition` | object | type, status, triggerPrice, targetProfitRate, orderPrice, triggeredOrderId | type, status | `d5ad8d0d719f6d6683fe7b73a4cefd02b055f286dd1969f35813f87658826f81` |
| `ConditionalOrderCreateRequest` | object | symbol, type, quantity, orderType, clientOrderId, expireDate, first, second, confirmHighValueOrder | symbol, type, quantity, orderType, expireDate, first | `b66ab8bf8918a910bec21ecc2172b4d98ce231f1b7d79ebb1914cadf31472d27` |
| `ConditionalOrderCreateResponse` | object | conditionalOrderId, clientOrderId | conditionalOrderId | `b937601657b864859b3882df0c05575e24c18890fb2388c77eed85c27b69ac37` |
| `ConditionalOrderDetailResponse` | object | conditionalOrderId, type, status, symbol, market, quantity, orderType, expireDate, first, second, createdAt | conditionalOrderId, type, status, symbol, market, quantity, orderType, first, createdAt | `a3a37acf98ddcd43dc04dfe11e14ba3ef992a469b86011e096b6cc4da98fe599` |
| `ConditionalOrderModifyRequest` | object | type, quantity, orderType, expireDate, first, second, confirmHighValueOrder | type, quantity, orderType, expireDate, first | `7fa83ddc75b352061307fd679f51bac075610c2c117146d9fa6b66d56bd9cbef` |
| `ConditionalOrderResponse` | object | conditionalOrderId | conditionalOrderId | `c4fa28bc0579371f270ba697625213f2c6552b07550e56a743ee981de98e3d5b` |
| `Cost` | object | commission, tax | commission | `5f6485669ee858a68e4356a8beed5c2081054d37aaa8d60e32d06aed5ada8eaa` |
| `CreditTradeDetail` | object | newQuantity, returnQuantity, balanceQuantity, balanceRate, tradingRate | newQuantity, returnQuantity, balanceQuantity, balanceRate, tradingRate | `776a9db2d1d7f09f2790c54e1803fafcd8c00701cdafa3c1c2b902ff4bca38b3` |
| `CreditTradeRecord` | object | date, updatedAt, marginLoan, stockLoan | date, updatedAt | `79d12a97095b47277e69653b07124beaf75bb6672c7fcf75d1a1e1ddb5a73cc5` |
| `CreditTradesResponse` | object | nextUntil, records | records | `4273db3bacae87f848008e161a1e8ebfa5ea3663dc5b4ff5d5280f6bf7d2183c` |
| `Currency` | string | — | — | `08e8bcc53390bcdf1aae249eb23ec7eff4e914d843bccb370e8b76d37135991a` |
| `DailyProfitLoss` | object | amount, rate | amount, rate | `0bd2aab453f5eb4d8da2eb302d0c37558904c55de9d4faffcfa00ae2215dd62e` |
| `ErrorResponse` | object | error | error | `3ce28f97a461c29574cbd5c91de4007f2ace7100c40fe8ec370acd9148ac6eca` |
| `ExchangeRateResponse` | object | baseCurrency, quoteCurrency, rate, midRate, basisPoint, rateChangeType, validFrom, validUntil | baseCurrency, quoteCurrency, rate, midRate, basisPoint, rateChangeType, validFrom, validUntil | `e3cd9b226377b960a286b273ee50c22e9e90ee1cd8eeac580ed7572bc0a7537b` |
| `ForeignerHolding` | object | holdingQuantity, limitQuantity, holdingRate | holdingQuantity, limitQuantity, holdingRate | `d33b88afc5ddb0b58995aa2e723bb4e0a94118d45c2b82679870d6ebddae9fc2` |
| `HoldingsItem` | object | symbol, name, marketCountry, currency, quantity, lastPrice, averagePurchasePrice, marketValue, profitLoss, dailyProfitLoss, cost | symbol, name, marketCountry, currency, quantity, lastPrice, averagePurchasePrice, marketValue, profitLoss, dailyProfitLoss, cost | `4407dbd53bae7da6c799feb741c50ba2a1981dbd4daf89a21d6eff2264178756` |
| `HoldingsOverview` | object | totalPurchaseAmount, marketValue, profitLoss, dailyProfitLoss, items | totalPurchaseAmount, marketValue, profitLoss, dailyProfitLoss, items | `18b898a0eeef83f983a6b9481521c959e1ea7453cfbfdf0784a164e541aea488` |
| `InstitutionTradingAmount` | object | buyAmount, sellAmount, breakdown | buyAmount, sellAmount, breakdown | `bb4633179e89dd184e1c9b34e4b34e292bbf38d511849c84ec896e73d7b28422` |
| `InstitutionTradingBreakdown` | object | financialInvestment, insurance, trust, privateEquityFund, bank, otherFinancialInstitution, pensionFund | financialInvestment, insurance, trust, privateEquityFund, bank, otherFinancialInstitution, pensionFund | `8ea3ef4fb526e46cf4b56b88581321a32f0f97254e0e53fb02cb2bedb134df8a` |
| `IntegratedHour` | object | preMarket, regularMarket, afterMarket | — | `adca08284c711604800498df0f4b8e1a6ed8d039d039ce52b0147f62a2aa18bf` |
| `InvestorTradingAmount` | object | buyAmount, sellAmount | buyAmount, sellAmount | `fc2b0e3769a7c2c693c0f71e1a26ff6698446adfd6b89e80ea026bbcc3f85a03` |
| `InvestorTradingRecord` | object | date, updatedAt, individual, foreigner, institution, otherCorporation | date, updatedAt, individual, foreigner, institution, otherCorporation | `a8dad7399252557d47867c9973baff6a6adc1e2d57714f166690d362cf5fabe1` |
| `InvestorTradingResponse` | object | nextUntil, records | records | `f38f3bffac6b890f87213427b0e3c0e470940621477c885df17f1291756ff634` |
| `InvestorTradingVolume` | object | buyVolume, sellVolume, netBuyVolume | buyVolume, sellVolume, netBuyVolume | `ca659cf8ad2627c469cc394048c9751697fc3c613beeb386b2464b98f0f15b08` |
| `KrMarketCalendarResponse` | object | today, previousBusinessDay, nextBusinessDay | today, previousBusinessDay, nextBusinessDay | `22c5bb6a6bcb408cf11135ebac6ac2960345561ab1fa2b21c4dae321cd5df780` |
| `KrMarketDay` | object | date, integrated | date | `6295f1cd58f74ba89224d87ac6905d7eea99dd708032ada7a82656bc859bf3ee` |
| `KrMarketDetail` | object | liquidationTrading, nxtSupported, krxTradingSuspended, nxtTradingSuspended | liquidationTrading, nxtSupported, krxTradingSuspended | `c10b1deb50bb8a61906c65babeef046b26a11a66820cf865fdd74b0f589f482c` |
| `ListedStock` | object | symbol, name, securityType, isCommonShare, isinCode | symbol, name, securityType, isCommonShare, isinCode | `47d9f31fd6454b5eaf50055f5b0ac62519c750e36cde0730a847464e161fc0e3` |
| `MarketCountry` | string | — | — | `df9e30290d787b7aa82c3ca7ea323eb8418955c00b4e21d0fca41119dc7b1bde` |
| `MarketIndicatorCandle` | object | timestamp, openPrice, highPrice, lowPrice, closePrice, volume | timestamp, openPrice, highPrice, lowPrice, closePrice, volume | `3dfc4fb7a34422cc25c1772c70d174477a4848bb6978ad8364a476a6cae265f1` |
| `MarketIndicatorCandlePageResponse` | object | candles, nextBefore | candles | `31cd5a24814f4c137a306ade3ed19e2038279cadb035e60815d08125d5c31c45` |
| `MarketIndicatorPriceResponse` | object | symbol, timestamp, lastPrice | symbol, lastPrice | `b8ef89cf99a01e6ac6dd35dea3b85bf7cfa7523ea4eb7e7d64a5b6f9250d3d41` |
| `MarketValue` | object | purchaseAmount, amount, amountAfterCost | purchaseAmount, amount, amountAfterCost | `32422e2d8919a8ec9fcda038c4e08625821b14329e4f2029c02f0b0acd644f73` |
| `OAuth2ErrorResponse` | object | error, error_description, error_uri | error | `be7f3255ac8b899cce667f499ee2262a42a5520732536c1e910c19d28a6a28b5` |
| `OAuth2TokenRequest` | object | grant_type, client_id, client_secret | grant_type, client_id, client_secret | `cff25aa9c21d7ca374d0af783d60b13cf1842cd25d4addd8a964bd8b60abcca1` |
| `OAuth2TokenResponse` | object | access_token, token_type, expires_in | access_token, token_type, expires_in | `b2c6cf2cf98194b9f1e5c10455fc7af6d8e99e76d37693cec850b633bf2d1537` |
| `Order` | object | orderId, symbol, side, orderType, timeInForce, status, price, quantity, orderAmount, currency, orderedAt, canceledAt, execution | orderId, symbol, side, orderType, timeInForce, status, quantity, currency, orderedAt, execution | `6c8125212184a3bcdff2331a0b0b1d2f2f0d97bd0675ed302487d61cb65a83c3` |
| `OrderCreateRequest` | composition/reference | — | — | `be69b084c27514e11120b88e29b1557b90a9b6ee771718144623817863f1f42e` |
| `OrderExecution` | object | filledQuantity, averageFilledPrice, filledAmount, commission, tax, filledAt, settlementDate | filledQuantity, averageFilledPrice, filledAmount, commission, tax, filledAt, settlementDate | `79e9c2c9fbe51343cbf9d4b76281fcf24dcf597835029456886256654b2462fe` |
| `OrderModifyRequest` | object | orderType, quantity, price, confirmHighValueOrder | orderType | `a31694b881630a01bd22129bdec6f651043b7ea3742d37e8aba4d4803a6c9ef8` |
| `OrderOperationResponse` | object | orderId | orderId | `199ac356757a4683a2c5ccdbf10ad4521538f06e781dd83b3e006109436165d7` |
| `OrderResponse` | object | orderId, clientOrderId | orderId | `5fca4087fa358d9dc3650a3dcac01b0719568ad669d045eba2ae21d680a7d675` |
| `OrderStatus` | string | — | — | `e1a151623cb8072f681a53b480fdc33af924cff7f90482274c938649bef6c4ac` |
| `OrderbookEntry` | object | price, volume | price, volume | `eb4215a5dd8cb7eb20ab84aa0b787b7bffdec1cdb56c6ea9e90289103e1051ae` |
| `OrderbookResponse` | object | timestamp, currency, asks, bids | currency, asks, bids | `8be63faac9ac01b9f11a65d54afca94eeb604c69f556806c254e594a3d78f45e` |
| `OverviewDailyProfitLoss` | object | amount, rate | amount, rate | `de76924f97829c29d9e72ec08bb8955b7cbd7fb2f22908a4a2740174119532e2` |
| `OverviewMarketValue` | object | amount, amountAfterCost | amount, amountAfterCost | `cc17f7374cf8ecac0f82ab9df62c0ad8bbfd9f90aa3ce6fceab9d3cc2cb6501f` |
| `OverviewProfitLoss` | object | amount, amountAfterCost, rate, rateAfterCost | amount, amountAfterCost, rate, rateAfterCost | `13c4d87527721cb42a1141cbc4f68551405bffcf5409ae7a7d33bab06912c364` |
| `PaginatedConditionalOrderResponse` | object | conditionalOrders, nextCursor, hasNext | conditionalOrders, hasNext | `28b75c769cb451b7ad6f56937bcf95a2a15cee25f1f451c5fb96224b72bf4069` |
| `PaginatedOrderResponse` | object | orders, nextCursor, hasNext | orders, nextCursor, hasNext | `a6df8759c1ec15dba3bfeb27cc99d7315f8d893c5e2943dc24541badc6040172` |
| `PreMarketSession` | object | startTime, singlePriceAuctionStartTime, endTime | startTime, endTime | `f161e5cf5c1a19654879dc42f94251a3a64fe99f83739e3cc5d910c64112972b` |
| `Price` | object | krw, usd | krw | `cc7e56e6a8d94b11100c716dc692bce1dfe7a1a6cab351a97e8eaef4ca1f662a` |
| `PriceLimitResponse` | object | timestamp, upperLimitPrice, lowerLimitPrice, currency | timestamp, currency | `6ebc3723b0c0a090fdc3600eccf34d857497d4040b75ee42473b88d954237107` |
| `PriceResponse` | object | symbol, timestamp, lastPrice, currency | symbol, lastPrice, currency | `94749bc112ab17fef39ea544603846dc731a36baee27025de21befda6abaa4ad` |
| `ProfitLoss` | object | amount, amountAfterCost, rate, rateAfterCost | amount, amountAfterCost, rate, rateAfterCost | `59358e8527d43b0a8ce20e034dddb9484a36c5ef47bc932d07716032e82f13b7` |
| `ProgramTradeRecord` | object | date, arbitrage, nonArbitrage | date, arbitrage, nonArbitrage | `1fd05f7b51d9dd9c9e7be9b91f5962186254f68e3456478d4a4253439f19ea6b` |
| `ProgramTradesResponse` | object | nextUntil, records | records | `622e2d64a40e3332f79ef8414c7fc4cc52190a6546d9ffdd999d132be0f12bfa` |
| `ProgramTradingVolume` | object | buyVolume, sellVolume, netBuyVolume | buyVolume, sellVolume, netBuyVolume | `c8ba55477b480d39b354d548260938f06c1a74db530d62eab00d69df3e225268` |
| `RankingItem` | object | rank, symbol, currency, price, tradingVolume, tradingAmount | rank, symbol, currency, price, tradingVolume, tradingAmount | `a00c2798f3bdb735d1d492460a31ffd15f9409f160b514961dd5f3e148ec08ac` |
| `RankingPrice` | object | lastPrice, basePrice, changeRate | lastPrice, basePrice | `afc30f720890034e91681134e3bcfada007bc8872ad29d45d7793357bfe97ad5` |
| `RankingResponse` | object | rankedAt, rankings | rankings | `8f47e26ac3ebfecef204b50f82202cdd2cbf5cd1b1661af1e5167b4d9f4a9d27` |
| `RegularMarketSession` | object | startTime, singlePriceAuctionStartTime, endTime | startTime, endTime | `939ae96ac0bb0ce77c0d2d520ff540ae241e07de48cca7e377fbb11975843e3d` |
| `SecuritiesLendingRecord` | object | date, updatedAt, executionQuantity, repaymentQuantity, balanceQuantity, balanceAmount | date, updatedAt, executionQuantity, repaymentQuantity, balanceQuantity, balanceAmount | `0ae8ca1a7fbea7501449e63d2654de330a2883c2fc9ca4cc082e8f198820ac2a` |
| `SecuritiesLendingResponse` | object | nextUntil, records | records | `2079120752c2e6aee0ba995145622bddb3a318e1f7e1f899e3c1ae6ef0daa59c` |
| `SellableQuantityResponse` | object | sellableQuantity | sellableQuantity | `7c7ae44ae4581155b2c6d4d2af7cd46891bfc9ec033058f197cec47e54645abc` |
| `ShortSellingRecord` | object | date, updatedAt, shortSellingVolume, shortSellingAmount, shortSellingVolumeRate, shortSellingAmountRate | date, updatedAt, shortSellingVolume, shortSellingAmount | `4de828820254fffff16e16cb0a6da2890d8147b32b29935f65e47e7e10087a2a` |
| `ShortSellingResponse` | object | nextUntil, records | records | `e39eaa55e1b3f8b27876057fa5936bb4b9b2aab9561e92881687b6ae5f87fc66` |
| `StockInfo` | object | symbol, name, englishName, isinCode, market, securityType, isCommonShare, status, currency, listDate, delistDate, sharesOutstanding, leverageFactor, koreanMarketDetail | symbol, name, englishName, isinCode, market, securityType, isCommonShare, status, currency, sharesOutstanding | `2e23dae3733e2a1a79d39a750372c6dc04b4333796efc50dd7c572da9a57c08e` |
| `StockInstitutionTradingBreakdown` | object | financialInvestment, insurance, trust, privateEquityFund, bank, otherFinancialInstitution, pensionFund | financialInvestment, insurance, trust, privateEquityFund, bank, otherFinancialInstitution, pensionFund | `d3c0ad81add7f1e8fdbf59edfad5ee32b85f5d4d766d0487545b6e011ccb97d4` |
| `StockInstitutionTradingVolume` | object | buyVolume, sellVolume, netBuyVolume, breakdown | buyVolume, sellVolume, netBuyVolume | `ff951139f6e96b9b04af8d08521e95754e0b639e6167c7d21f65095b0798d3ca` |
| `StockInvestorTradingRecord` | object | date, updatedAt, individual, foreigner, institution, otherCorporation, foreignerHolding, cfd | date, updatedAt, foreigner, institution | `da62598352396dc9299b95c882a7ce825aa911847b36498be45e6349b65034ca` |
| `StockInvestorTradingResponse` | object | nextUntil, records | records | `41c7dc249559c2a65357323452b785c5c5ae9fa0e5532613d323016d32c298b0` |
| `StockWarning` | object | warningType, exchange, startDate, endDate | warningType | `74ff7fa7f1e927f23c19b4b71167ec55e4fb7787e78919fbd8222f9784811be2` |
| `Trade` | object | price, volume, timestamp, currency | price, volume, timestamp, currency | `a44324c837dd3852179ede5e10dd5dc7341643589e77de34661185c4fb358e82` |
| `UsAfterMarketSession` | object | startTime, endTime | startTime, endTime | `42ef0a0bad3f275763d147abc3e2ab4cca1f918faeba8cf5a0f5f454412321d3` |
| `UsDayMarketSession` | object | startTime, endTime | startTime, endTime | `e3857f0b538c1d86b2ebc988db9ad1d89700a8bec8c3cdfcf2618dba5a0e4770` |
| `UsMarketCalendarResponse` | object | today, previousBusinessDay, nextBusinessDay | today, previousBusinessDay, nextBusinessDay | `945c1b1865e59aca23699d0cb66f695c4412b5d01e8ee5ab8a0588a59dc82ca4` |
| `UsMarketDay` | object | date, dayMarket, preMarket, regularMarket, afterMarket | date | `e7a85e5e259fddb1e566e0ba4ae58644abd2341fcefc98178a8b249ba7bed7c3` |
| `UsPreMarketSession` | object | startTime, endTime | startTime, endTime | `1490b8be27a1c67b281a827391b9bd1c6a34663b35813a6eb96b8e8bd8af090e` |
| `UsRegularMarketSession` | object | startTime, endTime | startTime, endTime | `eaee26ffa3f625f9c4723c1be46187d4da87b5a0a47299e7ea9d337fc95c9739` |

## AsyncAPI Inventory

Official server: `wss://openapi-ws.tossinvest.com/ws/v1`. All four channel keys share `/ws/v1`; they are logical channels rather than four server endpoints. Server security is HTTP Bearer during handshake. These contracts are separate from the public-web guest/STOMP client in `scripts/websocket_prices.py`.

| Channel | Message names | Status / public-web correspondence |
| --- | --- | --- |
| `connection` (Connection) | subscriptionsAck, errorFrame, ping, pong | current-doc-verified; protocol/identifier mapping required, not web-STOMP support |
| `realtime-trade` (Trade) | declare, tradeStream | current-doc-verified; protocol/identifier mapping required, not web-STOMP support |
| `realtime-orderbook` (Orderbook) | declare, orderbookStream | current-doc-verified; protocol/identifier mapping required, not web-STOMP support |
| `realtime-order` (Order Event) | declare, orderStream | official-only personal account events; excluded from web client |

| Operation | Action | Channel | Complete operation SHA-256 |
| --- | --- | --- | --- |
| `subscribeTrade` | send | `#/channels/realtime-trade` | `5ae36b70cda9aa570d8f71997d45c52509765325605678dd9b011ad4833a9130` |
| `receiveTrade` | receive | `#/channels/realtime-trade` | `312fafbffdb6c602c968b778dbf0ecf6baf2ff9ddd39016514516808592ebdb7` |
| `subscribeOrderbook` | send | `#/channels/realtime-orderbook` | `611c312cd03ed5e314f52cf2ffb114f94af34e79099a287a0991a43807e55e48` |
| `receiveOrderbook` | receive | `#/channels/realtime-orderbook` | `5e156a32bdb328591d21ce3276f422b9b93460f57d7712bbf7312e2725cd3e5d` |
| `subscribeOrder` | send | `#/channels/realtime-order` | `291771749ff2d53c0e697b6510d5ba5ed58aab961d5df2b5b2bcef16af7f4ca0` |
| `receiveOrder` | receive | `#/channels/realtime-order` | `4d63f458cf71bcb90878e52ec625503d000d3eb293a2d98ae80b9a13aea822ea` |
| `receiveSubscriptionsAck` | receive | `#/channels/connection` | `f14f763d060c1e58d9d72b5297027157381cdaf6facc27ed1be559e0ac09777f` |
| `receiveError` | receive | `#/channels/connection` | `b19648ea333ef95ca3b0826c01d91258fe430ea6daf934e60a79b791d5786619` |
| `sendPing` | send | `#/channels/connection` | `d1bf5029bd2a01a487e487f13827632ca3a727121c758d4cf7637bcd60084922` |
| `receivePong` | receive | `#/channels/connection` | `6086c4731bb598ea196ce9bf4495b1a4436e75642e22becf95c34e880eb2b747` |

## Contract Findings

See [the maintained boundary](official-openapi-boundary.md) for authentication exceptions, six stock-reference additions, paging, nullability, finalized/provisional data, current rate groups, and official WebSocket delivery/connection constraints. Those findings were reread against the same document responses hashed above.

## Document Disagreements

- llms.txt labels the REST source OpenAPI 3.0; its actual `openapi` field is 3.1.0. llms Auth mentions JWKS, but no current REST operation supplies it.
- Overview Stock Info feature table omits `GET /api/v1/stocks/all`; REST JSON and Markdown index include `listStocks`.
- Overview summarizes Bearer/account headers and a common error envelope broadly; token issuance and account-list header behavior have operation-specific exceptions. Token errors use OAuth error shape and form encoding.
- The parent task observed the browser Connection sidebar link `/docs/connection` rendering a not-found page on 2026-09-07. This is attributed UI evidence; this audit did not use a browser or observe that route HTTP status. The official AsyncAPI was still available, so it is not evidence of API deletion.
