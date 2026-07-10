# WebSocket Observations

Checked: 2026-07-10

Status: observed, unofficial, unstable, and not script-backed.

Use this reference only for sanitized analysis of real-time behavior already visible on public TossInvest pages. It does not define a supported public API or authorize a standalone WebSocket client.

## Boundary

Anonymous TossInvest pages can display live trade prices over an observed STOMP WebSocket transport, but anonymous page access is not credential-free access. The public page bootstrap supplies ephemeral guest connection metadata, including an authorization value commonly labeled `UTK`, a `device-id`, a generated `connection-id`, and platform metadata such as `Web/wts`.

Treat every guest value and STOMP `CONNECT` header as sensitive. Do not ask a user to provide these values. Do not print, store, log, share, replay, or add them as script arguments. Do not document the guest bootstrap endpoint or automate its reproduction. A credential-free STOMP `CONNECT` was not sufficient during the check.

The observed endpoint and subprotocol were:

```text
wss://realtime-socket.tossinvest.com/ws
v12.stomp
```

This skill documents browser-observed trade-price behavior only. WebSocket bid/offer order-book subscriptions and every order, account, holding, balance, and authenticated workflow remain excluded. The bounded HTTP order-book snapshot exposed through `scripts/quote.py` is a separate public read-only lookup and does not change this WebSocket exclusion.

## Observed Destinations

Use the following status labels conservatively:

- `confirmed-public`: a logged-out public page visibly changed while the destination was active.
- `observed-code`: the current public page and deployed bundle contain the subscription path, but a live tick was not independently observed during the bounded check.
- `excluded`: do not subscribe or implement it in this skill.
- `defined-unverified`: a builder exists, but logged-out public use was not established.

| Data | Normalized destination | Status | Notes |
| --- | --- | --- | --- |
| KR stock trades and current price | `/topic/v1/kr/stock/trade/{productCode}` | `confirmed-public` | Logged-out stock page showed changing trade time, price, and cumulative volume. |
| US stock trades and current price | `/topic/v1/us/stock/trade/{productCode}` | `observed-code` | Logged-out US stock page exposed the real-time trade table and current subscription path. |
| Standard KR/US indices | `/topic/v1/{kr|us}/stock/index/{productCode}` | `confirmed-public` | Logged-out KOSPI page visibly updated. |
| Crypto-like reference prices | `/topic/v1/crypto/vwap/{productCode}` | `observed-code` | Logged-out crypto-like page and current bundle use this path; no tick arrived in the short observation window. |
| Bid/offer order book | `/topic/v1/{kr|us}/{stock|option}/bidoffer/{productCode}` | `excluded` | The public order-book UI required login. Do not implement or subscribe. |
| KR stock status | `/topic/v1/kr/stock/status/{productCode}` | `defined-unverified` | A destination builder exists, but no logged-out public subscription was verified. |
| Option trade or order book | trade/bid-offer builders with `option` | `defined-unverified` / `excluded` | Do not claim anonymous support; bid/offer remains excluded. |

Optional query parameters observed in destination builders included `viewType`, `fallbackKrx`, and `investMode`. Treat them as unstable implementation details, not a supported contract.

Observed trade messages were used for fields such as `base`, `baseKrw`, `close`, `closeKrw`, `volume`, `cumulativeVolume`, `dt`, `tradeType`, `session`, `high`, `low`, and `tradingStrength`. Record field names only; never retain raw frames when they may contain guest or session metadata.

## Public Page Coverage

| Public route or tab | Real-time portion | Non-WebSocket portion |
| --- | --- | --- |
| `/stocks/{code}/order` chart and trade-price views | Header price, trade ticks, trading strength, and the current chart bar | Full bid/offer order-book view is login-gated; order panels are excluded. |
| `/stocks/{code}/analytics` | Stock header and shared live-price overlays | Company analysis widgets use HTTP. |
| `/stocks/{code}/news` | Stock header and shared live-price overlays | News and filings use HTTP paging. |
| `/stocks/{code}/transaction-status` | Stock header and shared live-price overlays | Investor, program, credit, lending, short-selling, and CFD tables use HTTP. |
| `/stocks/{code}/community` | Stock header and shared live-price overlays | Posts, comments, and replies use HTTP cursor paging. |
| `/indices/{index-code}` | Standard index or crypto-like reference price | Historical tables, news, and related products use HTTP. |
| `/indices/exchange-rate` | None verified | Exchange-rate widgets use HTTP and must not be described as WebSocket data. |
| `/`, `/screener`, `/sector/{tics-id}` | Shared current-price overlays may update from trade destinations | Ranking, screener, and sector result sets use HTTP and virtualized lists. |

## Paging And Tab Lifecycle

- Real-time trade ticks have no server page number. The page first loads bounded HTTP history, prepends WebSocket batches, and keeps a bounded client buffer observed at up to 1,000 rows.
- Historical candles remain HTTP cursor data. Trade messages update only the current candle displayed by the page.
- Index tables observed with page buttons preloaded a bounded HTTP result set and paged it in the client.
- News, filings, community, feed, screener, ranking, and sector data remain HTTP page/cursor datasets even when their visible price cells receive WebSocket overlays.
- The current deployment prefers a `SharedWorker` named `WTS Socket Worker` so browser tabs can share one connection and reference-count destinations. Hidden tabs can release non-background subscriptions. Treat this as an observed implementation detail, not a stable API guarantee.
- Do not add automatic reconnection loops, high-frequency subscription churn, multi-symbol fan-out, or unbounded buffering.

## Safe Verification

1. Read [safety-rules.md](safety-rules.md) and [capture-workflow.md](capture-workflow.md).
2. Use a logged-out public TossInvest page and observe only information visibly rendered there.
3. Record the public page URL, checked date, normalized destination, subprotocol, and message field names.
4. Do not capture or retain guest-bootstrap responses, STOMP `CONNECT` headers, cookies, tokens, storage state, raw frames, or raw HAR files.
5. Stop on login prompts, access-control errors, challenges, abnormal disconnects, or any request for account/order data. Do not retry or bypass the control.
6. Report WebSocket observations as unstable and browser-internal. Do not present them as part of the official TossInvest Open API.
