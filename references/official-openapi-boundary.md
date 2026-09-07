# Official Open API Boundary

Checked: 2026-09-07

Published-document verification only; no authenticated API or WebSocket session
was executed. Sources were fetched at 2026-09-06 23:42:56-23:42:57 UTC
(2026-09-07 08:42:56-08:42:57 KST). Exact response-byte SHA-256 values,
36 REST operations, 90 schema inventories, 10 AsyncAPI operations, and comparison
limits are recorded in [the dated audit](official-api-audit-2026-09-07.md).

Sources:

- `https://developers.tossinvest.com/docs`
- `https://developers.tossinvest.com/llms.txt`
- `https://openapi.tossinvest.com/openapi-docs/overview.md`
- `https://openapi.tossinvest.com/openapi-docs/latest/openapi.json`
- `https://openapi.tossinvest.com/openapi-docs/latest/api-reference/README.md`
- `https://openapi.tossinvest.com/openapi-docs/latest/asyncapi.json`

Use this reference only to distinguish this skill from the official TossInvest
Open API or to answer a rate-limit question about the official API. Treat the
official limits as reference-only operational context, not as permission to set
traffic levels for this unauthenticated web-endpoint skill. Do not use this file
to add OAuth, account, asset, or order workflows to this skill.

## Contents

- [Boundary](#boundary)
- [Official API Shape](#official-api-shape)
- [Stock Reference And Paging Contracts](#stock-reference-and-paging-contracts)
- [Official Rate Limits](#official-rate-limits)
- [Official WebSocket Boundary](#official-websocket-boundary)
- [Document Disagreements](#document-disagreements)
- [Refresh Policy](#refresh-policy)

## Boundary

This skill works with public TossInvest web pages and observed unauthenticated
page-data endpoints. It is not a client for the official Open API service at
`https://openapi.tossinvest.com`.

Because this skill does not call the official Open API, it does not need official
Open API app setup, OAuth credentials, `X-Tossinvest-Account`, or IP registration.
Do not ask users for those values for this skill, and do not add scripts that
handle them here.

That sentence describes this skill's non-use of the official service; it is not
a claim about the current official developer-console onboarding requirements.
For a separate authenticated client project, the current official overview
requires IP registration under WTS Settings > Open API. The token endpoint and
WebSocket handshake also document 403 for an unregistered IP. Re-check these
requirements before implementation; they do not apply to this skill's non-use
of the official service.

If the user wants official Open API integration, treat it as a separate
authenticated client project and read the official docs directly.

## Official API Shape

Official OpenAPI JSON checked on 2026-09-07:

- OpenAPI specification version: `3.1.0`
- Official API document version: `1.2.14`
- Base server: `https://openapi.tossinvest.com`
- Auth: OAuth 2.0 Client Credentials via `POST /oauth2/token`
- Resource calls use `Authorization: Bearer {access_token}`. Token issuance is
  the exception: `POST /oauth2/token` declares `security: []` and uses
  `application/x-www-form-urlencoded` Client Credentials, not an existing Bearer.
- `GET /api/v1/accounts` needs Bearer but has no account-header parameter. Its
  `accountSeq` supplies `X-Tossinvest-Account` for the other account-context
  operations, including holdings, orders, and conditional orders.
- One valid access token per client is documented; reissuance immediately
  invalidates the previous token. Refresh tokens are not provided.
- Coverage: Auth, Market Data, Stock Info, Market Info, Ranking, Market
  Indicators, Account, Asset, Order, Conditional Order, Conditional Order
  History, Order History, and Order Info
- Canonical document size: 33 paths, 36 operations (29 GET, 6 POST, 1 DELETE),
  13 tags, and 90 component schemas

Historical local baseline: document `1.2.9`, 27 paths and 13 tags, checked
2026-08-05. All 24 distinct method/path pairs explicitly listed in that local
reference are still present. The original 1.2.9 JSON is unavailable locally;
therefore the +6 path count and locally missing paths below are verified, but a
complete historical field/operation diff or universal absence of deletions is
not established.

`llms.txt` mentions JWKS in its quick Auth summary, but the canonical OpenAPI
JSON checked on 2026-09-07 did not list a JWKS operation. Use the OpenAPI JSON as
the source of truth for exact official paths.

Official market-data overlap includes:

- `GET /api/v1/orderbook`
- `GET /api/v1/prices`
- `GET /api/v1/trades`
- `GET /api/v1/price-limits`
- `GET /api/v1/candles`
- `GET /api/v1/stocks`
- `GET /api/v1/stocks/{symbol}/warnings`
- `GET /api/v1/exchange-rate`
- `GET /api/v1/market-calendar/KR`
- `GET /api/v1/market-calendar/US`

This overlap does not make the official paths script-backed in this repository.
The bundled scripts continue to use the public page endpoint catalog.

Other official market-data reads retained from the prior local reference
(all still require OAuth and remain reference-only in this skill):

- `GET /api/v1/rankings`
- `GET /api/v1/market-indicators/prices`
- `GET /api/v1/market-indicators/{symbol}/candles`
- `GET /api/v1/market-indicators/{symbol}/investor-trading`

Authenticated official-only READ endpoints must remain reference-only here:

- `GET /api/v1/accounts`
- `GET /api/v1/holdings`
- `GET /api/v1/orders`
- `GET /api/v1/orders/{orderId}`
- `GET /api/v1/conditional-orders`
- `GET /api/v1/conditional-orders/{conditionalOrderId}`
- `GET /api/v1/buying-power`
- `GET /api/v1/sellable-quantity`
- `GET /api/v1/commissions`

These are authenticated official-only workflows. Except for the account-list
bootstrap, they also require `X-Tossinvest-Account`. Do not add unauthenticated
web-endpoint scripts for these operations. The dated audit also inventories the
official create/modify/cancel operations as reference-only, without executing
them or adding CLI support.

## Stock Reference And Paging Contracts

Six GET paths absent from the previous local reference are present in the
current canonical JSON. These are additions to the local documentation; the
exact upstream introduction release is unverified:

| Method and path | Contract and public-web comparison |
| --- | --- |
| `GET /api/v1/stocks/all` | Market universe; required `market`, optional `status` (default `ACTIVE`), `securityType`, `commonShare`. Symbol ascending, no pagination. `STOCK_ALL` group; daily cache recommended. Public-web search/screener is a comparison source, not an equivalent official call. |
| `GET /api/v1/stocks/{symbol}/investor-trading` | KR stock trading volumes, KRX+NXT, registered foreign investors; includes institution breakdown, foreign holdings and CFD. Compare `trading_trend.py` only after matching units and venues. |
| `GET /api/v1/stocks/{symbol}/program-trades` | KR program-trading volumes, KRX only, excludes NXT. |
| `GET /api/v1/stocks/{symbol}/short-selling` | KR short-sale volumes, amounts and ratios; denominator includes non-regular sessions. Missing denominator gives null, zero denominator gives zero. |
| `GET /api/v1/stocks/{symbol}/credit-trades` | KR margin loans and individual stock loans; an unavailable side is null. This is not institutional securities lending. |
| `GET /api/v1/stocks/{symbol}/securities-lending` | KR institutional securities lending; amounts are KRW without a separate currency field. |

The five stock-trend paths use `STOCK_TRADING_TREND`, default `count=10`
(1-100), and optional inclusive `until=YYYY-MM-DD`. Responses contain
`result.records` newest first; pass the returned `nextUntil` unchanged into the
next `until`. A null continuation means no further data. US targets receive
`unsupported-market`, not an empty KR series.

Data timeliness differs even inside one family. Investor-trading records can
contain intraday provisional figures with null individual, institution-detail,
other-corporation, foreign-holding and CFD fields. Investor final figures and
foreign holdings arrive in the evening; CFD arrives T+1 and foreign holdings may
be revised next morning. `updatedAt` covers the whole record. Program trading
can change intraday; short selling and securities lending finalize in the
evening; credit trades arrive next business-day dawn. Do not treat null or a
prior-business-day latest record as an endpoint deletion.

The market-indicator investor-trading endpoint is a separate contract: KRX
market-wide KRW amounts, with registered and unregistered foreign investors
combined. Its `interval` is `1d|1w|1mo|1y`; stock investor trading is daily share
volume. Matching endpoint suffixes do not imply matching meaning.

Other pagination and response contracts to preserve:

- Stock and market-indicator candles use `interval=1m|1d`, default count 100,
  maximum 200, and inclusive ISO 8601 `before`. Pass `nextBefore` unchanged;
  encode a timezone `+` as `%2B`. Stock candles default `adjusted=true`.
  Market-indicator bond candles support only `1d`; their 8-symbol catalog is
  KOSPI/KOSDAQ plus KR government bonds at 2/3/5/10/20/30 years.
- `nextBefore` and `nextUntil` are nullable and are not required by their
  response schemas; distinguish omitted, null and a usable continuation.
- `GET /api/v1/rankings` returns at most 100. Counts can be shorter after price
  lookup failures; unaggregated combinations return empty rankings and null
  `rankedAt`. TOP_GAINERS/TOP_LOSERS reject `duration=realtime`; their base price
  represents the selected period, while other ranking types use the prior-day
  base. Market-wide and Toss-only execution rankings are distinct.
- Official stock symbols (`005930`, `AAPL`) differ from public-web product
  codes (`A005930`, US source codes). `prices` and `stocks` accept comma-separated
  symbol batches up to 200. `PriceResponse.lastPrice` is a decimal string;
  timestamp is optional and nullable. Schema requiredness, nullability and
  numeric formats must be inspected separately.
- Official market calendars describe trading sessions; the web skill's
  `calendar.py` describes market events and is not a direct substitute.
- Reference-only order paging differs by endpoint: `GET /api/v1/orders`
  ignores limit/cursor for OPEN, applies them for CLOSED (default 20, maximum
  100), and filters `from`/`to` by orderedAt KST dates. Conditional-order lists
  use nextCursor/cursor for both OPEN and CLOSED. No account calls were tested.

The complete method/path and schema inventory is in
[the dated audit](official-api-audit-2026-09-07.md). These published contracts
do not promote official endpoints to this skill's public-web script support.

## Official Rate Limits

The official docs describe rate limits as client x API group TPS limits. Values
can change without prior notice, and current limits should be checked from the
official response headers before making exact operational claims. These official
TPS values are not a throughput allowance for this skill, because this skill does
not call the official Open API and the public web endpoints do not publish a
separate quota.

| Official group | Limit in docs |
| --- | --- |
| `AUTH` | 5 TPS |
| `ACCOUNT` | 1 TPS |
| `ASSET` | 5 TPS |
| `STOCK` | 5 TPS |
| `STOCK_ALL` | 1 TPS |
| `STOCK_TRADING_TREND` | 10 TPS |
| `MARKET_INFO` | 3 TPS |
| `MARKET_DATA` | 15 TPS |
| `MARKET_DATA_CHART` | 20 TPS |
| `RANKING` | 5 TPS |
| `MARKET_INDICATOR_PRICE` | 10 TPS |
| `MARKET_INDICATOR` | 10 TPS |
| `MARKET_INDICATOR_CHART` | 5 TPS |
| `ORDER` | 10 TPS; 10 TPS during 09:00-09:10 KST |
| `CONDITIONAL_ORDER` | 5 TPS |
| `CONDITIONAL_ORDER_HISTORY` | 10 TPS |
| `ORDER_HISTORY` | 5 TPS |
| `ORDER_INFO` | 6 TPS; 3 TPS during 09:00-09:10 KST |

Official normal and 429 responses include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`
- `Retry-After` on 429 responses

These are published limits, not runtime-header observations. Relative to the
prior local record, MARKET_DATA changed from 10 to 15, MARKET_DATA_CHART from
5 to 20, and STOCK_ALL/STOCK_TRADING_TREND are newly recorded groups. Other
listed values match the previous record. `X-RateLimit-Reset` is estimated seconds
until one token replenishes, not a Unix reset timestamp. The official guide's
Retry-After/backoff advice does not change the public-web stop rule below.

For this skill, keep the stricter safety rule: stop on 403, 429, login redirects,
challenge pages, or abnormal responses; do not retry, poll, fan out, or bypass
service protection; do not probe unpublished limits, including by testing higher
TPS than the official Open API documents.

## Official WebSocket Boundary

The current REST document links a separate AsyncAPI document: specification
`3.0.0`, document `1.2.2`, four logical channels and ten operations.
Its server is `wss://openapi-ws.tossinvest.com/ws/v1`, using Bearer and registered
IP at handshake. It is not the anonymous-page guest/STOMP transport documented
in [websocket-api-reference.md](websocket-api-reference.md); do not move its
credentials, symbols, limits or subscription protocol into that client.

Documented contracts, not live-tested here:

- Connection, Trade, Orderbook and Order Event share one connection. A JSON
  array declares the entire subscription set (full-replace); omitted entries
  unsubscribe and `[]` removes all. Types are `trade:kr|us`, `orderbook:kr|us`
  and account-specific `personal:order`. Personal events remain out of scope.
- Account-wide maximum two connections; a new excess connection replaces the
  oldest. Each connection allows 100 channel/code combinations and five
  declarations per second. These are separate from public-web runtime caps.
- Client inactivity for 180 seconds closes the connection even while server
  data arrives. Plain uppercase text `PING` every 60 seconds is recommended;
  it is not a JSON string message. Standard WebSocket ping/pong also works.
- Trade/orderbook send no initial snapshot and are lossy with no sequence;
  summing received trades cannot reconstruct cumulative volume. Domestic
  streams combine KRX+NXT sessions. Official REST can provide initial snapshots
  only in a separately authorized authenticated client.
- Subscription acknowledgments distinguish accepted and rejected entries;
  declaration-wide errors retain the previous subscription. Reconnect requires
  redeclaration. Personal-order lossless delivery is limited to a connection
  session, with no replay of the disconnected interval.

## Document Disagreements

- `llms.txt` calls the REST source OpenAPI 3.0; the actual JSON says 3.1.0.
  Its JWKS quick summary still has no corresponding canonical operation.
- The overview's Stock Info feature table omits `GET /api/v1/stocks/all`, while
  canonical JSON and the Markdown API index include `listStocks`. Follow linked
  sources instead of treating the introductory list as exhaustive.
- Introductory statements about all calls requiring Bearer/account headers
  have token/account-list exceptions described above. Common error-envelope
  and JSON-body summaries also have an OAuth exception: token 400/401/403
  responses use OAuth `error`/`error_description`, and token requests use form
  encoding. Resource success uses `result`; resource failure uses `error`.
- A separate browser pass in this audit observed the Connection sidebar link
  `/docs/connection` rendering a not-found page on 2026-09-07. Its HTTP status
  was not observed. This is a documentation-UI finding, not API deletion:
  the linked AsyncAPI document was successfully fetched in the evidence above.

## Refresh Policy

Before each release, and before answering an exact current official version,
path, authentication, or rate-limit question, re-read the canonical OpenAPI JSON,
AsyncAPI JSON, linked Markdown reference and official overview. Record source
URLs, final URLs, retrieval times, byte hashes and normalized method/path,
operation/schema inventories. Inspect query/body/response/security/error and
transport changes, not just document versions or endpoint counts. If an old
raw specification is absent, distinguish local-reference differences from a
complete historical diff. Keep the checked date tied to the observed values; never
roll it forward without completing that comparison. If the official sources are
unavailable or disagree, retain the prior value only as historical context and
label the current claim `needs-recheck`.
