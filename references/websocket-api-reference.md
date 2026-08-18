# Unofficial WebSocket API Reference

Checked: 2026-07-10

Additional sector-page live-overlay check: 2026-08-04.

Additional bounded public-channel and page check: 2026-08-13.

Additional bounded US-index channel check during regular market hours: 2026-08-18.

Status: browser-observed, unofficial, unstable, and script-backed by a minimal bounded client.

This document describes the read-only real-time interface in API-reference form. It is not a TossInvest-supported public API or a complete AsyncAPI contract. The optional `scripts/websocket_prices.py` client implements only the confirmed public trade/index/crypto subset with memory-only guest metadata and strict runtime limits.

## Contents

- [Documentation Model](#documentation-model)
- [Status And Security Boundary](#status-and-security-boundary)
- [Server And WebSocket Handshake](#server-and-websocket-handshake)
- [STOMP Session Lifecycle](#stomp-session-lifecycle)
- [Channels And Destinations](#channels-and-destinations)
- [Receive Operations](#receive-operations)
- [Message Envelope](#message-envelope)
- [Payload Schemas And Synthetic Examples](#payload-schemas-and-synthetic-examples)
- [HTTP Snapshot And Stream Semantics](#http-snapshot-and-stream-semantics)
- [Top100 Hybrid Ranking Stream](#top100-hybrid-ranking-stream)
- [Public Page And Tab Coverage](#public-page-and-tab-coverage)
- [Errors, Heartbeats, And Close Behavior](#errors-heartbeats-and-close-behavior)
- [Safe Verification](#safe-verification)
- [Sources](#sources)

## Documentation Model

This reference follows three official protocol/documentation layers:

- RFC 6455 for the WebSocket opening handshake, subprotocol negotiation, message framing, and close behavior.
- STOMP 1.2 for `CONNECT`, `CONNECTED`, `SUBSCRIBE`, `MESSAGE`, `UNSUBSCRIBE`, `DISCONNECT`, `RECEIPT`, and `ERROR` frames.
- AsyncAPI 3.1 for the `server` → `channel` → `operation` → `message` information model. Operations are described from the logged-out browser application's perspective, so incoming price events use `action: receive`.

Do not force REST request/response terminology onto a subscription stream:

| Interaction | Client side | Server side | Documentation term |
| --- | --- | --- | --- |
| WebSocket establishment | HTTP Upgrade request | `101 Switching Protocols` or HTTP failure | Handshake |
| STOMP session establishment | `CONNECT` | `CONNECTED`; rejection SHOULD send `ERROR`, then close; close-only rejection is possible | Frame pair |
| Subscription | `SUBSCRIBE` | Zero or more `MESSAGE` frames, or `ERROR` | Receive operation / event stream |
| Unsubscription | `UNSUBSCRIBE`, optionally with a `receipt` header | Matching `RECEIPT` after successful processing when requested; final-frame delivery can still be lost on connection reset | Lifecycle frame |
| Graceful shutdown | `DISCONNECT` with a `receipt` header | Matching `RECEIPT`, then socket close | Receipt-confirmed lifecycle path |

A market tick is a `MESSAGE` event, not a one-time response. A literal `asyncapi.yaml` is intentionally not included because payload types, requiredness, units, enum values, and guest-session bootstrap stability are not verified strongly enough for generated-client use.

## Status And Security Boundary

Use these evidence labels:

- `standard`: behavior defined by RFC 6455 or STOMP 1.2; not proof of TossInvest-specific behavior.
- `observed-transport`: host, path, Upgrade result, or subprotocol token directly confirmed in sanitized browser network metadata.
- `observed-protocol`: deployed browser client code directly identifies STOMP protocol/frame use without retaining raw frames.
- `confirmed-public`: a logged-out public page visibly changed while the destination was active.
- `bounded-live`: at least one read-only event arrived in one no-retry sample capped at 10 seconds and one event. It does not establish delivery guarantees, field requiredness, or schema completeness.
- `observed-code`: the current public page and deployed bundle contain the destination and consumer path, but a live event was not independently observed in the bounded check.
- `observed-field`: the deployed page consumer reads the field name; requiredness, type, units, and enum values remain undocumented unless stated separately.
- `defined-unverified`: a builder exists, but logged-out public use was not established.
- `excluded`: do not subscribe, implement, or present as supported by this skill.

A zero-event bounded sample never promotes a channel to `bounded-live`; it remains inconclusive even when the deployed bundle contains a matching consumer.

Logged-out page access is not credential-free access. The browser supplies ephemeral guest connection metadata associated with names such as `UTK`, `device-id`, `connection-id`, and platform metadata such as `Web/wts`.

Treat every guest value and complete STOMP `CONNECT` frame as sensitive. Never ask a user for these values or print, store, log, share, replay, or accept them as input. A read-only client may obtain the current logged-out public-page bootstrap automatically, use it in process memory, and discard it when the connection closes. Credential-free STOMP session establishment was not successful in the bounded check.

Every order, account, holding, balance, and authenticated workflow remains excluded. Public bid/offer and estimated-price subscriptions are experimental market-data inputs: use them only when a logged-out page exposes the same data and never connect them to an order workflow. The bounded public HTTP quote/order-book snapshot in `scripts/quote.py` remains the stable fallback.

## Server And WebSocket Handshake

| Property | Value | Evidence |
| --- | --- | --- |
| Scheme | `wss` | `observed-transport` |
| Host | `realtime-socket.tossinvest.com` | `observed-transport` |
| Path | `/ws` | `observed-transport` |
| Full server URL | `wss://realtime-socket.tossinvest.com/ws` | `observed-transport` |
| Transport | WebSocket over TLS | `standard` + `observed-transport` |
| Requested/selected subprotocol token | `v12.stomp` | `observed-transport` |
| Application messaging protocol | STOMP, compatible with the 1.2 frame model | `standard` + `observed-protocol` |

RFC 6455 establishes the connection through an HTTP Upgrade exchange. The client proposes `v12.stomp` with `Sec-WebSocket-Protocol`; successful negotiation returns `101 Switching Protocols` and selects the subprotocol. Do not preserve or publish the complete browser handshake headers.

If the server returns a non-`101` response, redirects to login, or presents a challenge, the WebSocket transport was not established. A close after `101` means the WebSocket transport was established and then closed; it does not provide a usable or lasting STOMP session unless a `CONNECTED` frame had already arrived. Do not retry or work around either condition.

## STOMP Session Lifecycle

```text
HTTP Upgrade → 101 → CONNECT → CONNECTED → SUBSCRIBE → MESSAGE → ...
                                                   ↘ UNSUBSCRIBE
                                                    DISCONNECT(receipt) → RECEIPT → close
```

The following is a standards-only, sanitized frame shape. It is not a runnable TossInvest connection recipe because required browser-supplied guest metadata is deliberately omitted.

Client frame:

```text
CONNECT
accept-version:1.2
host:<virtual-host>

^@
```

Server frame on accepted STOMP session:

```text
CONNECTED
version:1.2

^@
```

STOMP 1.2 requires `accept-version` and `host` on `CONNECT`, and `version` on `CONNECTED`. The bundled standalone client sends the public WebSocket hostname as `host`; a bounded 2026-08-13 live sample accepted that frame. This does not establish that the hostname is TossInvest's unique or required STOMP virtual-host value. The complete `CONNECT` frame remains sensitive and is never shown or retained. `heart-beat` is optional. A server may reject session establishment and SHOULD send an `ERROR` frame before closing; a failed `SUBSCRIBE` MUST produce `ERROR` followed by close. These are protocol rules; the presence of optional headers in TossInvest frames is not guaranteed by this reference.

## Channels And Destinations

STOMP treats destination strings as opaque. Their names do not prove delivery guarantees, durability, replay, ordering, acknowledgment mode, or broker topology.

### Available logged-out page channels

| Channel ID | STOMP destination | Parameters | Message | Evidence | Bundled client |
| --- | --- | --- | --- | --- | --- |
| `krStockTradeUpdates` | `/topic/v1/kr/stock/trade/{productCode}` | TossInvest KR product code | `TradeUpdatePayload` | `confirmed-public`; `A005930` was `bounded-live` | Supported for typed KR product codes |
| `usStockTradeUpdates` | `/topic/v1/us/stock/trade/{productCode}` | TossInvest US product/source code | `TradeUpdatePayload` | `confirmed-public`; `US20100311002` was `bounded-live` | Supported for typed US product/source codes |
| `krStockIndexUpdates` | `/topic/v1/kr/stock/index/{productCode}` | Exactly `KGG01P` or `QGG01P` | `IndexUpdatePayload` | Both codes were `bounded-live` | Supported for those two codes only |
| `usStockIndexUpdates` | `/topic/v1/us/stock/index/{productCode}` | Exactly `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, or `SOX.NAI` | `IndexUpdatePayload` | Every listed code was `bounded-live` | Supported for those four codes only |
| `cryptoVwapUpdates` | `/topic/v1/crypto/vwap/{productCode}` | Exactly `VWAP.KRW-BTC`, `VWAP.KRW-ETH`, `VWAP.KRW-XRP`, or `VWAP.KRW-SOL` | `CryptoVwapUpdatePayload` | Every listed code was `bounded-live` | Supported for those four codes only |

`confirmed-public` means usable by the logged-out page, not usable without guest connection metadata. In the 2026-08-13 bounded checks, each supported KR index and crypto code received one event; `A005930` and `US20100311002` had also each produced one event in bounded public checks. These single events establish neither ongoing availability nor delivery guarantees. Arbitrary `VWAP.*` codes are not supported.

The 2026-08-13 US-index checks ran outside regular market hours and received zero events, so they remained inconclusive. During regular US market hours on 2026-08-18, `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, and `SOX.NAI` each produced one event in an independent no-retry check capped at 10 seconds and one event. The client supports those exact four codes and still rejects login-gated `DJI.DJI`, `RFU.NQc1`, and `RFU.GCv1`. A destination builder existing in deployed JavaScript is not by itself permission to subscribe.

Destination builders also contained optional values named `viewType`, `fallbackKrx`, and `investMode`. Their format and effect are implementation details, not supported parameters.

### Experimental or unverified destinations

| Data | Normalized destination | Status | Rule |
| --- | --- | --- | --- |
| Stock bid/offer and pre-open estimates | `/topic/v1/{market}/stock/bidoffer/{productCode}` | `observed-code` / experimental | Consumers read public quote volumes and KR pre-open estimate fields. Verify logged-out delivery before enabling and never connect to order actions. |
| KR stock status invalidation | `/topic/v1/kr/stock/status/{productCode}` | `observed-code` | The consumer treats a message as an invalidation signal and refetches the public trading-status HTTP endpoint; payload fields are not consumed. |
| Option trades | trade builder with `instrumentType=option` | `defined-unverified` | Do not claim support. |
| Option bid/offer | bid/offer builder with `instrumentType=option` | `observed-code` / experimental | Deployed consumers exist, but logged-out public delivery was not confirmed. Keep disabled by default. |

## Receive Operations

These operations use AsyncAPI's application perspective: the logged-out browser application receives events from a channel.

| Operation ID | Action | Client frame | Server frames | Channel | Message |
| --- | --- | --- | --- | --- | --- |
| `receiveKrStockTrade` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `krStockTradeUpdates` | `TradeUpdatePayload` |
| `receiveUsStockTrade` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `usStockTradeUpdates` | `TradeUpdatePayload` |
| `receiveKrStockIndexUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `krStockIndexUpdates` | `IndexUpdatePayload` |
| `receiveUsStockIndexUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `usStockIndexUpdates` | `IndexUpdatePayload` |
| `receiveCryptoVwapUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `cryptoVwapUpdates` | `CryptoVwapUpdatePayload` |
| `receiveStockBidOfferUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | Experimental stock bid/offer destination | `BidOfferUpdatePayload` |
| `receiveKrStockStatusSignal` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | KR stock status invalidation destination | Payload not consumed |

Sanitized subscription shape:

```text
SUBSCRIBE
id:<unique-subscription-id>
destination:/topic/v1/kr/stock/trade/A005930

^@
```

STOMP 1.2 requires a connection-unique `id` and `destination`. The `ack` header is optional and defaults to `auto`. Both the deployed worker and the bundled standalone client omit `ack`; the bounded 2026-08-13 live sample accepted that subscription shape. This records an observed compatible shape, not a broader TossInvest acknowledgment guarantee.

## Message Envelope

A STOMP `MESSAGE` frame has a protocol envelope plus an application payload.

```text
MESSAGE
subscription:<matching-subscription-id>
destination:/topic/v1/kr/stock/trade/A005930
message-id:<server-generated-id>

<JSON payload>
^@
```

STOMP 1.2 requires `destination`, `message-id`, and `subscription` on `MESSAGE`. An `ack` header is required only for explicit-ack subscriptions. `content-type`, `content-length`, and other headers are conditional and must not be claimed as TossInvest guarantees without fresh sanitized evidence.

The 2026-07-10 live client check observed TossInvest `MESSAGE` frames that carried `subscription`, `message-id`, `content-type`, and `content-length` but omitted `destination`. The bundled parser therefore matches the connection-local `subscription` id when `destination` is absent. This is a defensive compatibility rule for the observed deployment, not a change to the STOMP standard.

### Normalized JSONL output contract

For every accepted JSON object, the standalone client injects `kind` and the canonical `destination`. It then copies only scalar or `null` values from this 26-key allowlist:

```text
code, exchange, currency, changeType,
base, baseKrw, close, closeKrw,
open, openKrw, high, highKrw, low, lowKrw,
high52w, low52w, high1y, low1y,
volume, cumulativeVolume, cumulativeAmount, cumulativeAmountKrw,
dt, tradeType, session, tradingStrength
```

Here, scalar means a JSON string, number, or boolean. Unknown keys and array/object values are removed; explicit `null` is preserved only for an allowlisted key. This is a privacy- and stability-oriented normalized-output contract, not a claim that all listed keys occur on every channel or event.

## Payload Schemas And Synthetic Examples

These are partial consumer-observed field catalogs, not validation schemas. `observed-field` confirms a field name is read by deployed page code; it does not prove requiredness, nullability, exact JSON type, units, precision, enum membership, or compatibility.

### `TradeUpdatePayload`

| Field | Page consumer use | Evidence |
| --- | --- | --- |
| `code` | Product identifier | `observed-field` |
| `base`, `baseKrw` | Base/reference price and KRW variant | `observed-field` |
| `close`, `closeKrw` | Latest price and KRW variant | `observed-field` |
| `currency`, `changeType` | Display currency and change classification | `observed-field` |
| `volume` | Event volume-like value | `observed-field` |
| `cumulativeVolume` | Cumulative volume-like value | `observed-field` |
| `dt` | Event time-like value | `observed-field` |
| `tradeType` | Trade classification; enum undocumented | `observed-field` |
| `session` | Market session classification; enum undocumented | `observed-field` |
| `high`, `low` | High/low price-like values | `observed-field` |
| `high52w`, `low52w`, `high1y`, `low1y` | Rolling high/low values used by shared stock-price cards | `observed-field` |
| `cumulativeAmount` | Cumulative trading-amount value used to update the current candle | `observed-field` |
| `tradingStrength` | Trading-strength display value | `observed-field` |

Synthetic field-name illustration — not a captured payload and not evidence of container shape, JSON types, values, or required fields:

```text
code
base
close
volume
cumulativeVolume
dt
```

### `IndexUpdatePayload`

The standard-index page consumer reads `base` and `close`. The bounded samples below contained additional top-level fields, but their requiredness and cross-event stability remain unverified.

### `CryptoVwapUpdatePayload`

The crypto-like page consumer reads `base`, `close`, and `cumulativeVolume`, mapping the cumulative value to its displayed volume state. The bounded samples below contained additional top-level fields, but their requiredness and cross-event stability remain unverified.

### 2026-08-13 bounded sampled shapes

The following field/type inventories came from one event per named code in read-only, no-retry checks capped at 10 seconds and one event. Values, guest metadata, complete frames, and raw payloads were not retained. JSON represents both integer-like and floating-point observations as `number`.

| Sample | Top-level `string` fields | Top-level `number` fields |
| --- | --- | --- |
| KR stock `A005930` | `changeType`, `code`, `currency`, `dt`, `exchange`, `session`, `tradeType` | `base`, `close`, `cumulativeAmount`, `cumulativeVolume`, `tradingStrength`, `volume` |
| KR indices `KGG01P`, `QGG01P` | `changeType`, `code`, `dt` | `base`, `close`, `cumulativeAmount`, `cumulativeVolume` |
| Crypto `VWAP.KRW-BTC`, `VWAP.KRW-ETH`, `VWAP.KRW-XRP`, `VWAP.KRW-SOL` | `changeType`, `code`, `currency`, `dt` | `base`, `close`, `cumulativeAmount`, `cumulativeVolume` |

An earlier one-event bounded check for US stock `US20100311002` retained normalized output fields only: injected `kind` and `destination`, plus `base`, `baseKrw`, `changeType`, `close`, `closeKrw`, `code`, `cumulativeAmount`, `cumulativeAmountKrw`, `cumulativeVolume`, `currency`, `dt`, `session`, `tradeType`, `tradingStrength`, and `volume`. That list is not a raw top-level payload inventory.

The 2026-08-18 one-event checks for US indices `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, and `SOX.NAI` also retained normalized output fields only. Every code produced injected `kind` and `destination`, plus `base`, `changeType`, `close`, `code`, `cumulativeAmount`, `cumulativeVolume`, `dt`, and `volume`. This common list is not a raw top-level payload inventory and does not make any field required.

Every row is a single-event sample, not a complete schema. It establishes neither requiredness nor fields that may appear in other events, sessions, or future deployments.

### `BidOfferUpdatePayload`

Deployed consumers read these partial field groups. They are not guaranteed to appear together:

| Field group | Consumer use | Evidence |
| --- | --- | --- |
| `offerVolume`, `bidVolume` | Aggregate sell-waiting and buy-waiting volume | `observed-field` |
| `offerPrices`, `offerPricesKrw`, `offerVolumes` | Sell-side price levels and quantities | `observed-field` |
| `bidPrices`, `bidPricesKrw`, `bidVolumes` | Buy-side price levels and quantities | `observed-field` |
| `singlePrice`, `estimatedPrice`, `estimatedVolume` | KR pre-open expected match price and volume | `observed-field` |
| `close`, `closeKrw`, `dt` | Quote context and update time | `observed-field` |

The KR stock-status consumer does not use message-body fields. It invalidates the corresponding public HTTP trading-status query and lets that endpoint provide the current KRX/NXT status.

### Session-specific consumers

The deployed consumers do not treat every trade event identically:

| Consumer context | Fields applied by the page | Evidence boundary |
| --- | --- | --- |
| KR regular session | `base`, `close`, daily/52-week/1-year high and low, `cumulativeVolume`, `tradingStrength` | `observed-code`; individual fields are `observed-field` |
| KR after-hours single-price view | Trade `open`, `close`, `high`, and `low`; bid/offer consumer may expose `singlePrice`, `estimatedPrice`, and `estimatedVolume` | `observed-code`; logged-out quote UI remained login-gated |
| US day/pre/main sessions | `base`, `baseKrw`, `close`, `closeKrw`, range fields, and cumulative volume | `observed-code`; a logged-out SOXL header visibly changed |
| US after-hours session | After-hours `close`, `high`, `low`, KRW variants, cumulative volume, and a session marker | `observed-code` |
| US option views | Trade and level-quote consumers exist, including KRW price arrays | `defined-unverified`; do not enable by default |

Session names, transitions, and enum values are not a stable public contract. Preserve the source session value, do not infer market-open state from the destination name alone, and keep the HTTP market-status helper as the fallback.

Do not convert these catalogs into strict JSON Schema or generated models until sanitized evidence establishes types and requiredness across multiple current messages.

## HTTP Snapshot And Stream Semantics

WebSocket channels do not use REST page numbers.

| Dataset | Initial/history source | Real-time behavior |
| --- | --- | --- |
| Stock trade ticks | Bounded HTTP `/api/v2/stock-prices/{code}/ticks` history | Prepend `MESSAGE` events; observed client buffer capped at 1,000 rows. |
| Stock quote/order-book snapshot | HTTP `/api/v3/stock-prices/{code}/quotes` | Experimental bid/offer events can overlay quote fields after logged-out delivery is verified. |
| Historical candles | HTTP cursor/range data using `nextDateTime`/`from` | Trade events update only the current displayed candle, including `dt`, prices, cumulative volume, and cumulative amount. |
| Index tables | Bounded HTTP result set | Page buttons can divide already-loaded rows in the client. |
| Screener | HTTP `POST /api/v2/screener/screen`, 50 rows per numbered page, loaded through a virtualized infinite list | Visible current-price cells may receive trade-event overlays. |
| Feed/community | HTTP cursor datasets; feed cursors include values such as `actedAt`, `lastCommentId`, and `lastTradeHistoryId` | Related-stock chips may receive shared trade-price overlays. |
| News, filings, search, ranking, sector | HTTP result sets or cursors | Visible current-price cells may receive trade-event overlays. |
| Home live-chart top100 | HTTP `POST /api/v2/dashboard/wts/overview/ranking` every observed 10 seconds | Up to 100 product trade destinations update current-price overlays between snapshots. |

Document the combination as `snapshot + event stream`, not as WebSocket pagination or request/response polling.

## Top100 Hybrid Ranking Stream

There is no single KR-top100 or US-top100 WebSocket destination in the current deployed builder. The public page combines two data paths:

1. `POST /api/v2/dashboard/wts/overview/ranking` returns the ranked `products[]` snapshot, normally 100 rows, and is refreshed at the observed 10-second interval.
2. Each product row registers its product code with a shared real-time price store. The store reference-counts product codes and subscribes to the normalized trade destination for each active code.

The 2026-07-10 logged-out checks found 101 grid rows including the header and 100 unique stock links for both KR and US views. On the US view, multiple visible rows changed current price and change rate during a five-second observation while rank, amount, market capitalization, TossInvest buy/sell ratio, industry, and AI summary remained unchanged.

A client that mirrors this page should:

- keep one shared STOMP connection and at most 100 deduplicated product destinations for one top100 view;
- refresh the HTTP ranking no faster than 10 seconds;
- diff old and new product-code sets, subscribing only additions and unsubscribing only removals;
- treat rank, list membership, TossInvest-specific amount/volume, buy/sell ratio, industry, and AI summary as HTTP snapshot fields;
- treat current price, reference price, change rate derived from them, cumulative volume, high/low, session, and trading strength as WebSocket overlay candidates;
- avoid running KR and US plus multiple ranking categories concurrently unless a new bounded verification establishes a safe subscription budget.

## Public Page And Tab Coverage

| Public route or tab | WebSocket-fed portion | HTTP or excluded portion |
| --- | --- | --- |
| `/stocks/{code}/order` chart/trade views | Header price, trade ticks, trading strength, current chart bar | Full bid/offer UI is login-gated; order panels are excluded. |
| `/stocks/{code}/analytics` | Header and shared live-price overlays | Analysis widgets use HTTP. |
| `/stocks/{code}/news` | Header and shared live-price overlays | News and filings use HTTP paging. |
| `/stocks/{code}/transaction-status` | Header and shared live-price overlays | Investor/program/credit/lending/short-selling/CFD tables use HTTP. |
| `/stocks/{code}/community` | Header and shared live-price overlays | Posts, comments, and replies use HTTP cursor paging. |
| `/indices/{index-code}` | Client-supported current-value streams are limited to KR indices `KGG01P`, `QGG01P`; US indices `COMP.NAI`, `SPX.CBI`, `RGI..VIX`, `SOX.NAI`; and crypto codes `VWAP.KRW-BTC`, `VWAP.KRW-ETH`, `VWAP.KRW-XRP`, `VWAP.KRW-SOL` | History, news, and related products use HTTP; no other index-route code is implied to be WebSocket-supported. |
| `/indices/exchange-rate` | None verified | Exchange-rate widgets are HTTP-only. |
| `/` live-chart top100 | Up to 100 per-product trade subscriptions update current price and change rate | Ranking membership and non-price columns use a 10-second HTTP snapshot. |
| `/` general index and market cards | Deployed cards reuse standard-index or crypto current-value consumers for their selected code (`observed-code`) | Card membership and metadata use HTTP; only the exact client-supported code allowlists above may be streamed. |
| `/` search dialog | Popular/result stock prices and related-stock chips register with the shared live-price store | Search results, news, industry matches, and ranking membership use HTTP. |
| `/` trending-industry tab | No ranking-specific WebSocket channel was found | Industry rank, change, amount, market cap, representative stock, and signal are HTTP data. |
| `/` domestic-investor-trend tab | Stock price/change cells can use shared trade-price overlays | Foreign/institution/individual rank, time, and net amount use HTTP ranking data. |
| `/screener` | Each rendered result can register a shared trade-price subscription | Filters, count, sort columns, and 50-row numbered pages use HTTP; the UI virtualizes/infinite-loads them. |
| `/sector/{tics-id}` | Stock cards and comparison/ETF rows can use shared trade-price overlays | Sector metrics, membership, sorting, signals, and list loading use HTTP. |
| `/calendar/economic-indicator` | The selected indicator can reuse a standard-index or crypto current-value consumer (`observed-code`) | Calendar, history, and selector data use HTTP; the page creates no separate calendar destination and does not expand standalone client support. |
| `/feed/news` and `/feed/recommended` | Related-stock price chips can use the shared live-price store | Articles, posts, reactions, comments, and feed cursors use HTTP; mutations require login and are excluded. |

This table is an explicit route scope, not a pattern that grants support to similar pages. A route absent from the table does not imply a WebSocket destination. Community lists, post permalinks, and lounge/feed content are HTTP cursor surfaces; they may reuse a related-stock price chip, but no separate community, permalink, or lounge WebSocket destination was found.

On 2026-08-04, `/sector/79?nation=US` showed current price/change changes in
two visible stock rows during a 3.5-second observation while rank, market cap,
trading value, volume, analyst opinion, and signal cells stayed unchanged. This
confirms the sector table as another `HTTP snapshot + per-product trade overlay`
consumer. No sector-ranking or sector-page-specific WebSocket destination was
found; stock rows reuse `/topic/v1/{market}/stock/trade/{productCode}`.

### Logged-out navigation check

The following routes were opened directly from or alongside public home-page links on 2026-07-10, with the `QGG01P` page and bounded event rechecked on 2026-08-13 and the four public US-index channels rechecked during regular market hours on 2026-08-18. This is an access observation, not a promise that the same route will remain public.

| Result | Routes | Real-time conclusion |
| --- | --- | --- |
| Public KR index pages | `/indices/KGG01P`, `/indices/QGG01P` | Both pages were public and both exact codes produced one bounded-live index event; both are client-supported. |
| Public US index pages | `/indices/COMP.NAI`, `/indices/SPX.CBI`, `/indices/RGI..VIX`, `/indices/SOX.NAI` | Every exact code produced one bounded-live index event during regular US market hours; all four are client-supported. |
| Public crypto-like pages | `/indices/VWAP.KRW-BTC`, `/indices/VWAP.KRW-ETH`, `/indices/VWAP.KRW-XRP`, `/indices/VWAP.KRW-SOL` | All four logged-out pages rendered live value and volume data, and every exact code produced one bounded-live crypto VWAP event. |
| Public but HTTP-only in this check | `/indices/exchange-rate` | No exchange-rate WebSocket consumer was verified. |
| Redirected to sign-in | `/indices/DJI.DJI`, `/indices/RFU.NQc1`, `/indices/RFU.GCv1` | Stop at the redirect. Do not bootstrap or subscribe on behalf of a login-gated page. |

On the logged-out SOXL detail page, the document title changed from one price to another while the page remained open, across the chart/order, analytics, news, transaction-status, and community routes. The quote panel itself displayed that login was required, so bid/offer delivery remains experimental rather than `confirmed-public`.

The visible numeric buttons on index and feed screens were local carousels or client-side page controls, not WebSocket pages. WebSocket subscriptions have no `page`, `size`, `nextDateTime`, or feed cursor; those values belong to the corresponding HTTP snapshot/history request.

The current deployment prefers a `SharedWorker` named `WTS Socket Worker` so tabs can share one connection and reference-count destinations. Hidden tabs can release non-background subscriptions. Treat this as an implementation detail, not an API guarantee.

The browser worker sends new subscriptions in batches of 20 with a 400-ms interval. The standalone client mirrors that pacing, deduplicates and canonicalizes every destination, permits only one local process, caps each parsed STOMP frame at 256 KiB, and caps each inbound WebSocket message at 1 MiB. It keeps no automatic reconnect queue. Normalized JSONL flushes the first event immediately and then uses a 20-event or 500-ms batch, avoiding a disk flush for every tick while preserving short-run visibility.

## Errors, Heartbeats, And Close Behavior

Keep protocol layers separate:

- HTTP/WebSocket handshake failure: non-`101`, login redirect, or challenge means the WebSocket transport was not established. A close after `101` is a post-handshake transport/session closure, not an opening-handshake failure.
- STOMP session rejection: the server SHOULD send `ERROR` before close. Subscription creation failure: the server MUST send `ERROR` and close.
- STOMP heartbeats: optional EOL traffic negotiated through `heart-beat` on `CONNECT`/`CONNECTED`.
- WebSocket keepalive/control: Ping/Pong control frames are not STOMP heartbeats.
- WebSocket close: RFC 6455 Close frame/code/reason belongs to the transport layer. Status values `1005` and `1006` are reserved for reporting absence conditions and must not be sent in a Close frame.
- Graceful STOMP shutdown: `DISCONNECT` with a `receipt` header can be followed by the matching `RECEIPT` before socket close. Without a `receipt` request, no `RECEIPT` is guaranteed. TossInvest receipt behavior was not independently verified.

RFC 6455 discusses delayed/backoff recovery after abnormal closure. A client may reconnect with bounded exponential backoff, jitter, and a maximum retry count. It must stop on access-control failures, avoid full-set subscription churn, deduplicate destinations, and keep buffers bounded.

The bundled minimal client deliberately performs no automatic reconnect. It exits on an unexpected close or STOMP `ERROR`, requests a receipt on graceful `DISCONNECT`, waits at most one second for the matching `RECEIPT`, and then closes the socket. This keeps retry and shutdown behavior small and predictable; final-frame delivery can still be lost on connection reset.

## Safe Verification

1. Read [safety-rules.md](safety-rules.md) and [capture-workflow.md](capture-workflow.md).
2. Use a logged-out public TossInvest page and observe only information visibly rendered there.
3. Record the public page URL, checked date, server host/path, subprotocol token, normalized destination, field names, and evidence status.
4. A read-only client may process guest-bootstrap responses and STOMP frames in memory, but must not retain complete handshake headers, guest values, `CONNECT` frames, raw messages, cookies, tokens, storage state, or raw HAR files.
5. A field name alone does not establish type, requiredness, nullability, units, enum values, or compatibility.
6. Stop on login prompts, access-control errors, challenges, account/order data, or exhausted bounded reconnect attempts. Do not bypass controls.
7. Report every TossInvest-specific claim as unstable and browser-internal. Do not present it as the official TossInvest Open API.

Install and run the bounded client only when continuous updates are needed.
Keep the optional dependency in a project-local environment:

```text
python -m venv .venv
.venv/bin/python -m pip install -r requirements-websocket.txt
.venv/bin/python scripts/websocket_prices.py --us-stock US20100311002 --duration 10 --max-events 5
```

On Windows PowerShell, replace `.venv/bin/python` with
`.venv/Scripts/python.exe`. After a one-off check, deactivate if needed and
remove only `.venv`; the global Python environment remains unchanged.

The client accepts only typed stock/index/crypto code flags and reconstructs each canonical destination internally. It does not accept a server URL, destination, guest key, device id, connection id, cookie, or authorization header from the command line or environment. The optional dependency is exactly pinned and hash-checked in `requirements-websocket.txt`.

## Sources

- [RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [STOMP Protocol Specification, Version 1.2](https://stomp.github.io/stomp-specification-1.2.html)
- [AsyncAPI Specification 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0)
- [AsyncAPI channels](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-channels)
- [AsyncAPI operations](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-operations)
- [AsyncAPI messages](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-messages)
