# Unofficial WebSocket API Reference

Checked: 2026-07-10

Status: browser-observed, unofficial, unstable, and not script-backed.

This document describes the read-only real-time interface in API-reference form. It is not a TossInvest-supported public API, a complete AsyncAPI contract, or authorization to build a standalone client.

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

A market tick is a `MESSAGE` event, not a one-time response. A literal `asyncapi.yaml` is intentionally not included because the guest bootstrap is unsupported and payload types, requiredness, units, and enum values are not verified strongly enough for generated-client use.

## Status And Security Boundary

Use these evidence labels:

- `standard`: behavior defined by RFC 6455 or STOMP 1.2; not proof of TossInvest-specific behavior.
- `observed-transport`: host, path, Upgrade result, or subprotocol token directly confirmed in sanitized browser network metadata.
- `observed-protocol`: deployed browser client code directly identifies STOMP protocol/frame use without retaining raw frames.
- `confirmed-public`: a logged-out public page visibly changed while the destination was active.
- `observed-code`: the current public page and deployed bundle contain the destination and consumer path, but a live event was not independently observed in the bounded check.
- `observed-field`: the deployed page consumer reads the field name; requiredness, type, units, and enum values remain undocumented unless stated separately.
- `defined-unverified`: a builder exists, but logged-out public use was not established.
- `excluded`: do not subscribe, implement, or present as supported by this skill.

Logged-out page access is not credential-free access. The browser supplies ephemeral guest connection metadata associated with names such as `UTK`, `device-id`, `connection-id`, and platform metadata such as `Web/wts`.

Treat every guest value and complete STOMP `CONNECT` frame as sensitive. Never ask a user for these values or print, store, log, share, replay, or accept them as input. Do not document or reproduce the guest-bootstrap endpoint. Credential-free STOMP session establishment was not successful in the bounded check.

WebSocket bid/offer subscriptions and every order, account, holding, balance, and authenticated workflow remain excluded. The bounded public HTTP quote/order-book snapshot in `scripts/quote.py` is a separate read-only interface.

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

STOMP 1.2 requires `accept-version` and `host` on `CONNECT`, and `version` on `CONNECTED`. The `host` value identifies a STOMP virtual host; this reference does not assume it equals the WebSocket hostname or document a TossInvest-specific value. `heart-beat` is optional. A server may reject session establishment and SHOULD send an `ERROR` frame before closing; a failed `SUBSCRIBE` MUST produce `ERROR` followed by close. These are protocol rules; the presence of optional headers in TossInvest frames is not guaranteed by this reference.

## Channels And Destinations

STOMP treats destination strings as opaque. Their names do not prove delivery guarantees, durability, replay, ordering, acknowledgment mode, or broker topology.

### Available logged-out page channels

| Channel ID | STOMP destination | Parameters | Message | Evidence |
| --- | --- | --- | --- | --- |
| `krStockTradeUpdates` | `/topic/v1/kr/stock/trade/{productCode}` | TossInvest KR product code | `TradeUpdatePayload` | `confirmed-public` |
| `usStockTradeUpdates` | `/topic/v1/us/stock/trade/{productCode}` | TossInvest US product/source code | `TradeUpdatePayload` | `observed-code` |
| `krStockIndexUpdates` | `/topic/v1/kr/stock/index/{productCode}` | KR index product code | `IndexUpdatePayload` | `confirmed-public` for KOSPI |
| `usStockIndexUpdates` | `/topic/v1/us/stock/index/{productCode}` | US index product code | `IndexUpdatePayload` | `observed-code` |
| `cryptoVwapUpdates` | `/topic/v1/crypto/vwap/{productCode}` | crypto-like product code, for example `VWAP.KRW-BTC` | `CryptoVwapUpdatePayload` | `observed-code` |

`confirmed-public` means usable by the logged-out page, not usable without guest connection metadata. `observed-code` means the public code path exists but this reference does not claim an independently witnessed live event.

Destination builders also contained optional values named `viewType`, `fallbackKrx`, and `investMode`. Their format and effect are implementation details, not supported parameters.

### Excluded or unverified destinations

| Data | Normalized destination | Status | Rule |
| --- | --- | --- | --- |
| Bid/offer order book | `/topic/v1/{market}/{instrumentType}/bidoffer/{productCode}` | `excluded` | Logged-out order-book UI required login. Never pair this path with a subscription operation or example. |
| KR stock status | `/topic/v1/kr/stock/status/{productCode}` | `defined-unverified` | Builder existence is not proof of logged-out availability. |
| Option trades | trade builder with `instrumentType=option` | `defined-unverified` | Do not claim support. |
| Option bid/offer | bid/offer builder with `instrumentType=option` | `excluded` | Do not subscribe or implement. |

## Receive Operations

These operations use AsyncAPI's application perspective: the logged-out browser application receives events from a channel.

| Operation ID | Action | Client frame | Server frames | Channel | Message |
| --- | --- | --- | --- | --- | --- |
| `receiveKrStockTrade` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `krStockTradeUpdates` | `TradeUpdatePayload` |
| `receiveUsStockTrade` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `usStockTradeUpdates` | `TradeUpdatePayload` |
| `receiveKrStockIndexUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `krStockIndexUpdates` | `IndexUpdatePayload` |
| `receiveUsStockIndexUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `usStockIndexUpdates` | `IndexUpdatePayload` |
| `receiveCryptoVwapUpdate` | `receive` | `SUBSCRIBE` | `MESSAGE*` or `ERROR` | `cryptoVwapUpdates` | `CryptoVwapUpdatePayload` |

Sanitized subscription shape:

```text
SUBSCRIBE
id:<unique-subscription-id>
destination:/topic/v1/kr/stock/trade/A005930

^@
```

STOMP 1.2 requires a connection-unique `id` and `destination`. The `ack` header is optional; the TossInvest acknowledgment mode is not documented here. Do not add an `ack` mode based only on the STOMP default.

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

## Payload Schemas And Synthetic Examples

These are partial consumer-observed field catalogs, not validation schemas. `observed-field` confirms a field name is read by deployed page code; it does not prove requiredness, nullability, exact JSON type, units, precision, enum membership, or compatibility.

### `TradeUpdatePayload`

| Field | Page consumer use | Evidence |
| --- | --- | --- |
| `code` | Product identifier | `observed-field` |
| `base`, `baseKrw` | Base/reference price and KRW variant | `observed-field` |
| `close`, `closeKrw` | Latest price and KRW variant | `observed-field` |
| `volume` | Event volume-like value | `observed-field` |
| `cumulativeVolume` | Cumulative volume-like value | `observed-field` |
| `dt` | Event time-like value | `observed-field` |
| `tradeType` | Trade classification; enum undocumented | `observed-field` |
| `session` | Market session classification; enum undocumented | `observed-field` |
| `high`, `low` | High/low price-like values | `observed-field` |
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

The standard-index page consumer reads `base` and `close`. Additional field names, requiredness, and types are unverified.

### `CryptoVwapUpdatePayload`

The crypto-like page consumer reads `base`, `close`, and `cumulativeVolume`, mapping the cumulative value to its displayed volume state. Additional field names, requiredness, and types are unverified.

Do not convert these catalogs into strict JSON Schema or generated models until sanitized evidence establishes types and requiredness across multiple current messages.

## HTTP Snapshot And Stream Semantics

WebSocket channels do not use REST page numbers.

| Dataset | Initial/history source | Real-time behavior |
| --- | --- | --- |
| Stock trade ticks | Bounded HTTP `/api/v2/stock-prices/{code}/ticks` history | Prepend `MESSAGE` events; observed client buffer capped at 1,000 rows. |
| Stock quote/order-book snapshot | HTTP `/api/v3/stock-prices/{code}/quotes` | WebSocket bid/offer is excluded from this skill. |
| Historical candles | HTTP cursor/range data | Trade events update only the current displayed candle. |
| Index tables | Bounded HTTP result set | Page buttons can divide already-loaded rows in the client. |
| News, filings, community, feed, screener, ranking, sector | HTTP page/cursor datasets | Visible current-price cells may receive trade-event overlays. |

Document the combination as `snapshot + event stream`, not as WebSocket pagination or request/response polling.

## Public Page And Tab Coverage

| Public route or tab | WebSocket-fed portion | HTTP or excluded portion |
| --- | --- | --- |
| `/stocks/{code}/order` chart/trade views | Header price, trade ticks, trading strength, current chart bar | Full bid/offer UI is login-gated; order panels are excluded. |
| `/stocks/{code}/analytics` | Header and shared live-price overlays | Analysis widgets use HTTP. |
| `/stocks/{code}/news` | Header and shared live-price overlays | News and filings use HTTP paging. |
| `/stocks/{code}/transaction-status` | Header and shared live-price overlays | Investor/program/credit/lending/short-selling/CFD tables use HTTP. |
| `/stocks/{code}/community` | Header and shared live-price overlays | Posts, comments, and replies use HTTP cursor paging. |
| `/indices/{index-code}` | Standard index or crypto-like current value | History, news, and related products use HTTP. |
| `/indices/exchange-rate` | None verified | Exchange-rate widgets are HTTP-only. |
| `/`, `/screener`, `/sector/{tics-id}` | Shared current-price overlays may update from trade channels | Result sets use HTTP and virtualized lists. |

The current deployment prefers a `SharedWorker` named `WTS Socket Worker` so tabs can share one connection and reference-count destinations. Hidden tabs can release non-background subscriptions. Treat this as an implementation detail, not an API guarantee.

## Errors, Heartbeats, And Close Behavior

Keep protocol layers separate:

- HTTP/WebSocket handshake failure: non-`101`, login redirect, or challenge means the WebSocket transport was not established. A close after `101` is a post-handshake transport/session closure, not an opening-handshake failure.
- STOMP session rejection: the server SHOULD send `ERROR` before close. Subscription creation failure: the server MUST send `ERROR` and close.
- STOMP heartbeats: optional EOL traffic negotiated through `heart-beat` on `CONNECT`/`CONNECTED`.
- WebSocket keepalive/control: Ping/Pong control frames are not STOMP heartbeats.
- WebSocket close: RFC 6455 Close frame/code/reason belongs to the transport layer. Status values `1005` and `1006` are reserved for reporting absence conditions and must not be sent in a Close frame.
- Graceful STOMP shutdown: `DISCONNECT` with a `receipt` header can be followed by the matching `RECEIPT` before socket close. Without a `receipt` request, no `RECEIPT` is guaranteed. TossInvest receipt behavior was not independently verified.

RFC 6455 discusses delayed/backoff recovery after abnormal closure. This repository keeps a stricter rule: do not add automatic reconnect loops, high-frequency subscription churn, concurrent multi-symbol fan-out, or unbounded buffering.

## Safe Verification

1. Read [safety-rules.md](safety-rules.md) and [capture-workflow.md](capture-workflow.md).
2. Use a logged-out public TossInvest page and observe only information visibly rendered there.
3. Record the public page URL, checked date, server host/path, subprotocol token, normalized destination, field names, and evidence status.
4. Do not retain guest-bootstrap responses, complete handshake headers, STOMP `CONNECT` frames, cookies, tokens, storage state, raw messages, or raw HAR files.
5. A field name alone does not establish type, requiredness, nullability, units, enum values, or compatibility.
6. Stop on login prompts, access-control errors, challenges, abnormal disconnects, or account/order data. Do not retry or bypass controls.
7. Report every TossInvest-specific claim as unstable and browser-internal. Do not present it as the official TossInvest Open API.

## Sources

- [RFC 6455 — The WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- [STOMP Protocol Specification, Version 1.2](https://stomp.github.io/stomp-specification-1.2.html)
- [AsyncAPI Specification 3.1.0](https://www.asyncapi.com/docs/reference/specification/v3.1.0)
- [AsyncAPI channels](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-channels)
- [AsyncAPI operations](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-operations)
- [AsyncAPI messages](https://www.asyncapi.com/docs/concepts/asyncapi-document/adding-messages)
