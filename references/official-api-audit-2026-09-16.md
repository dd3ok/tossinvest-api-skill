# Official API Audit — 2026-09-16

Repository baseline: `9afa5d531721a76f3c82cffbafab442f373945f2` on `main`.
Compared with [the 2026-09-07 audit](official-api-audit-2026-09-07.md).
Official checks read public documentation only; no OAuth token, account, order,
or official WebSocket request was made. Six separate public-web requests
checked the implementation impact described below.

## Contents

- [Result](#result)
- [Source Evidence](#source-evidence)
- [Changed Operations](#changed-operations)
- [Changed Schemas](#changed-schemas)
- [Current Contract Notes](#current-contract-notes)
- [Public Client Impact](#public-client-impact)
- [Validation](#validation)

## Result

- REST document `1.2.14` → `1.2.17`; OpenAPI remains `3.1.0`.
- All 33 paths / 36 method-path pairs and 90 named schemas remain; 13 tags.
- Complete-object fingerprints changed for 8 operations and 12 schemas;
  the remaining 28 operations and 78 schemas match the old fingerprints.
- Top-level schema field names and required lists match the old inventory.
  This does not establish unchanged nested fields, enums, or constraints.
- AsyncAPI `3.0.0` / document `1.2.2`, 4 channels / 10 operations:
  exact response bytes are unchanged. `llms.txt` and the Markdown API index
  also match byte-for-byte. The overview changed; listed rate limits match
  the 2026-09-07 boundary, including peak-period limits.

The 1.2.14 raw JSON and old overview are unavailable locally. Fingerprints
prove which complete objects changed, but cannot identify the exact changed
property or separate documentation edits from functional changes. The notes
below describe the current contract in those objects, not newly introduced
features or verified server behavior. Release-by-release changes in
1.2.15–1.2.17 are undetermined.

## Source Evidence

All responses were HTTP 200 with final URL equal to requested URL. Hashes
cover exact response bytes, including any BOM. Retrieved at 10:37:57 KST.

| Source | Retrieved UTC | Bytes | SHA-256 |
| --- | --- | --- | --- |
| [llms](https://developers.tossinvest.com/llms.txt) | 2026-09-16T01:37:57+00:00 | 2668 | `a57be4baa04d60b68897b2766802bd626b9c88d7fcea1c5306d2318cb36a9988` |
| [overview](https://openapi.tossinvest.com/openapi-docs/overview.md) | 2026-09-16T01:37:57+00:00 | 28115 | `d0f63ff1a8e7ff24b762ab465f1a46ebba207689012fa815ef0d5009b564f44f` |
| [rest](https://openapi.tossinvest.com/openapi-docs/latest/openapi.json) | 2026-09-16T01:37:57+00:00 | 420256 | `791082da4cb379117ed9fdc29a45bd42746f7a1aec368da1e9f4e1f3bfbff5b4` |
| [markdown](https://openapi.tossinvest.com/openapi-docs/latest/api-reference/README.md) | 2026-09-16T01:37:57+00:00 | 23895 | `30c0532c1cc4010d1d7ec0878cbb0a1c2cfd291d104eb4e3cc99683d7f8da0f5` |
| [async](https://openapi.tossinvest.com/openapi-docs/latest/asyncapi.json) | 2026-09-16T01:37:57+00:00 | 41523 | `130251057fd9535a3e276099f9166b445f8c51f505f30540758e4b209231282e` |

The [snapshot archive](official-api-snapshot-2026-09-16.zip) retains these
five exact public documents, `sources.json` (URLs/times/status/byte hashes),
and `inventory.json` (all operation/schema fingerprints). It contains public
documentation only, not authenticated responses or public-web payloads.
Use it as the original source for the next field-level diff; read the short
boundary document for ordinary official API questions.

Fingerprint encoding: SHA-256 of UTF-8 `json.dumps(value, sort_keys=True,
ensure_ascii=False, separators=(',', ':'))`. This reproduces the prior
inventory for unchanged objects. Reusable objects are compared separately;
an unchanged operation hash alone does not prove its referenced schemas unchanged.

Reference traversal resolved all 370 REST and 20 AsyncAPI
local `$ref` occurrences. This is an integrity check, not a full schema validator.
No current REST operation declares `deprecated: true`.

## Changed Operations

Every row is `current-doc-verified`, reference-only in this skill.

| Method / path | Current SHA-256 |
| --- | --- |
| `GET /api/v1/candles` | `47000e1197c961ed5f250b8897a93bae7a774433f98c98a739b6aee55037be4e` |
| `GET /api/v1/stocks/{symbol}/short-selling` | `ab6640930d061e45ec561c5b0e8ddbe94d77a64bf2178e13ca7071618a765115` |
| `GET /api/v1/market-calendar/KR` | `4fef40d25adeff7912e2b6a37e1c1b1f552bce7b7137e5a49c812761fb094cd4` |
| `GET /api/v1/market-indicators/{symbol}/candles` | `a3319d1a56a6ec1edc861175bf9bac1a8811f908db6a2ecbf45d22e5603f4d5a` |
| `GET /api/v1/holdings` | `bf153aba6c0207cc149b2e79e0a199dc2a60cad723604959ffa31f16f221cf90` |
| `GET /api/v1/orders` | `41075c679c5622029082b184e99caf05d6d6b60cf253b37e8a802e842eb5f624` |
| `POST /api/v1/orders` | `fb54a5ef5e4c5acff0ea8e881e80c98386e8771c3e6441cae2066c9c1b41dcaa` |
| `GET /api/v1/conditional-orders` | `2397726f5e70c569c82d272f9274e797a78d3403dab57b689d6182a0ba923f84` |

## Changed Schemas

| Schema | Current SHA-256 |
| --- | --- |
| `CandlePageResponse` | `4ecf596cb46946c388a5824394dfe86adab90c625eb2935a72c9e3ebbdbd9de3` |
| `Candle` | `f6c17c1c364c78fa79e5000325e00572713ac7e940937bb567b66790c9ec2c21` |
| `ShortSellingRecord` | `31c473de5192b003933127d4c578459dd26c472748f2a65c0545fa1995366f9c` |
| `IntegratedHour` | `a280dc8a0cc2f01d17a2e206204a32f9759e22a6f951dbba03a249d1b13dddfa` |
| `AfterMarketSession` | `ab0cabae3d6a0ef66ac93940ae51e87b85ab29a1a93ff342f946e0db1764af9d` |
| `RankingItem` | `d1f0b6cdcc12c333441d0e5f8b7c05e502112f4f7f21cd16a3d560652462e07d` |
| `MarketIndicatorCandlePageResponse` | `7a0a20ff890428c31abbf646407f0a857a65089858ec1c95dc8d409c5aa1aa98` |
| `HoldingsItem` | `8ffce21bffb71fb353114cb8443f756cf68cee8f9347c5ae45920117c6f2cafd` |
| `OrderCreateRequest` | `0159b4901f4581846ad01106e10b90892959d338a240a5853e9709f7dd2cc11f` |
| `ConditionalOrderCreateRequest` | `4d2709878b16b8ef622fa71f4b9963873860225513a04dc64b6746fed970c0d9` |
| `ConditionalOrderDetailResponse` | `dac916fa3215e72167c870fd8ae937d64855241feb07c0021de60db5b6227cd2` |
| `Order` | `5d985859ed8ae6dc304d3837346b82d28ef030f4b5ed62cdbb46069c9ffa5043` |

## Current Contract Notes

These are current details to preserve when interpreting the changed objects.

| Area | Current documentation |
| --- | --- |
| Stock and indicator candles | Newest first. Stock `1m` timestamp is the end of `[timestamp - 1 minute, timestamp)`; daily stock time is local midnight. Do not assume the official stock definition also documents web `dt` or indicator timestamps. |
| Short selling | Decimal ratios, not percentage-point values: volume ratio up to five decimal places, amount ratio up to four. Denominators include non-regular sessions; missing denominator is null, zero denominator produces zero. |
| KR calendar | `integrated` excludes pre/post-market closing-price sessions. Pre/regular/after sessions can individually be null; all-null means `integrated=null`. After-market boundaries span the KRX/NXT union; the NXT auction end can be null. |
| Rankings | `tradingVolume` / `tradingAmount` accumulate over `duration`; `TOSS_SECURITIES_*` uses Toss executions and other types use the whole market. |
| Holdings / symbols | Holdings is KR/US stocks only; empty holdings returns zero summaries and an empty list. KR symbols can contain letters as well as digits. Preserve this in a separate official client. |
| Order creation / response | `timeInForce=OPG` is documented for domestic opening auction with LIMIT or MARKET. US fractional quantity is MARKET SELL only, at most six decimal places. Fractional quantity and amount orders are accepted from regular-session start until one hour before its end. |
| Order history | Only supported order types are returned; pre/post-market closing-price orders are excluded from list and detail. OPEN ignores cursor/limit; CLOSED uses them. |
| Conditional orders | OPEN and CLOSED both support `symbol` and cursor paging. KR alphanumeric symbol descriptions occur in create/detail schemas. Other channels' orders are included. |

Document disagreements remain: `llms.txt` calls REST OpenAPI 3.0 and mentions
JWKS, while canonical JSON is 3.1.0 with no JWKS operation. The overview
omits `stocks/all` in its feature table. The order-history supported-type
description does not explicitly list OPG even though creation/response
schemas include it; this check cannot establish actual history behavior.
The overview's broad amount-order error wording also omits the one-hour
cutoff specified by the operation. `/docs/connection` was not revisited;
its 2026-09-07 not-found observation remains historical.

## Public Client Impact

The official and public-web interfaces have separate symbols, candle fields,
cursors, limits, and session semantics. The official calendar is a trading
session calendar; `calendar.py` handles market events. No official endpoint
is a drop-in replacement for a bundled web script.

Six sequential requests, spaced about one second apart, used existing
script builders and the guarded HTTP transport, without cookies or auth.
Checked 2026-09-16 01:39:12–01:39:17 UTC (10:39:12–10:39:17 KST).
This is a targeted compatibility sample, not a new audit of all public APIs.

| Public request | Observed result / action |
| --- | --- |
| A005930 `c-chart/kr-s`, `day:1`, count 3, all/krx/adjusted | 3 newest-first candles; `dt`, OHLCV, `base`, `amount`; existing parser works. |
| Same daily chart, returned `nextDateTime` → `from` | 3 older candles, no date overlap; cursor advances. Preserve web `nextDateTime/from`, not official `nextBefore/before`. |
| A005930 `min:1`, same options, count 3 | 3 newest-first candles; existing shape. Response order does not establish web timestamp interval semantics. |
| A005930 MDS `short-selling-trend`, number 1, size 3 | 2 rows, `lastPage=false`, continuation number 2/key 2026-09-10. A short page is not the end. Existing code preserves raw ratios and paging fields. |
| KGG01P `c-chart/kr-s/day:1`, count 3, adjusted | 3 daily candles with `nextDateTime`; existing index daily-quote parser works. |
| Ranking POST `biggest_total_amount`, kr, 1d, empty filters | Existing `products`, `basedAt`, `duration`, ranking/type/tag fields remain. No official ranking field mapping was introduced. |

Inspected `stock_chart.py`, `indices.py`, `trading_trend.py`,
`dashboard_ranking.py`, and their current tests. Chart indicators already
sort by `dt` for calculation and map results back to the input order.
No public runtime defect or new public capability was established by this
change set. Updated the reference contracts, public chart/short-selling
interpretation notes, entrypoint links, and changelog; runtime behavior and
CLI compatibility are unchanged. Account/order features stay reference-only.

## Validation

- Python 3.14.7: all 275 existing tests passed without skips. Updated the
  existing official-document test's expected date/version to the checked source.
- Ruff format and lint checks passed; `git diff --check` passed.
- All 21 scripts compiled and their help commands completed; 3 JSON examples
  parsed. The help harness used explicit UTF-8 after its initial decoding
  assumption conflicted with Windows' default output encoding.
- Skill Creator `quick_validate.py` and the CI Agent Skills validator passed;
  the latter used a fresh installed layout named `tossinvest-web-api`.
- The 80,325-byte snapshot archive passed ZIP integrity, all five original-byte
  size/hash checks, and recalculation of all 36 REST operation, 90 schema, and
  10 AsyncAPI operation fingerprints from the archived source JSON.

No authenticated official API behavior, WebSocket session, or broader public
endpoint coverage is claimed by these checks.
