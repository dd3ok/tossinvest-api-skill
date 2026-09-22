# Feed and community API reference

Use this reference for public news discovery, recommended feeds, community
comments, replies, and the stock-page composite. Company-specific news and
filings use the [stock reference](api-stock.md#filings-and-news-apis);
sector news uses the [market reference](api-market.md#current-industry-dashboard-and-sector-behavior).
The stock-page composite combines stock metadata/prices with sanitized comments;
it is different from the home dashboard ranking.

For commands and cursor continuation, use the
[stock main-page and community cookbook](script-cookbook.md#stock-main-page-and-community);
for social output fields, use [public community shapes](response-notes.md#public-community-shapes).

Status labels and host/identifier rules are defined in the
[common catalog](api-catalog.md#verification-status). A script-backed label is
not a current-availability guarantee. Dates below remain scoped observations;
the [2026-09-07 audit](update-audit-2026-09-07.md) records this domain's checked scope.

## Contents

- [Feed And News APIs](#feed-and-news-apis)
- [Public Community And Main-Page APIs](#public-community-and-main-page-apis)

## Feed And News APIs

Observed from `/feed/recommended` and `/feed/news`. Keep only feed endpoints that can help with public market or stock-news discovery. Do not catalog followings, subscriptions, or account-personalized feed endpoints.

| Purpose | Status | Method | URL/path | Params/body and notes |
|---|---|---:|---|---|
| Historical recommended feed posts | `needs-recheck` | GET | `/api/v3/feed/recommend/posts` | Returned HTTP 404 in the bounded 2026-08-13 direct check; do not retry or fall back to this stale path |
| Current recommended feed posts | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | Optional `lastRecommendId`; current public `/feed/recommended` traffic; `feed.py --kind recommended` emits only sanitized comments plus `nextLastRecommendId` |
| Dashboard/news tab feed | `script-backed` | POST | `/api/v1/dashboard/wts/news` | Body `{ "type": "HOT" }` etc.; result includes `type`, `title`, `news[]` |
| News detail | `script-backed` | GET | `/api/v2/news/{newsId}` | Detail payload for a selected news item |

The 2026-09-16
[deployed recommendation query](https://www.tossinvest.com/assets/v2/_next/static/chunks/1901-e370805f386c219f.js)
continues only when the raw `feeds[]` is nonempty and `key.lastRecommendId` is
present. `feed.py` follows this rule: an empty raw page clears `hasNext` and the
normalized cursor. A nonempty raw page may produce zero sanitized comments;
that alone does not mean the server reached the end.

Cataloged public dashboard news `type` values:

```text
ALL_HIGHLIGHT, HOT, SOARING_STOCK, INDEX
```

Observed 2026-05-29 `/feed/news` UI mapping:

| UI label | API `type` | Script status |
|---|---|---|
| Major news | `ALL_HIGHLIGHT` | `scripts/feed.py --kind news --news-type ALL_HIGHLIGHT` |
| Latest news | `HOT` | `scripts/feed.py --kind news --news-type HOT` |
| Soaring-stock news | `SOARING_STOCK` | `scripts/feed.py --kind news --news-type SOARING_STOCK` |
| Index news | `INDEX` + `indexCode` | `scripts/feed.py --kind news --news-type INDEX --index-code KGG01P` |
| Popular news | `PERSONALIZED` | excluded because it is personalized |

`INDEX` requires `indexCode`, for example:

```text
POST https://wts-info-api.tossinvest.com/api/v1/dashboard/wts/news
Content-Type: application/json

{"type":"INDEX","indexCode":"KGG01P"}
```

## Public Community And Main-Page APIs

Additional web check: 2026-07-08 for `/?focusedProductCode=US20100311002`,
`/stocks/US20100311002/community`, `/feed/recommended`, and `/feed/news`.
These routes rendered without login and returned HTTP 200 from public APIs.
Additional logged-out check: 2026-08-13 for
`/community/lounges/LOUNGE_193394`, `/community/posts/{post-id}`, and the
recommended-feed v4 continuation shape.

Use `scripts/stock_page.py` when the user asks for the public stock main-page
bundle: resolved product metadata, price details, AI signal detail, and
sanitized public comments. Use `scripts/community_comments.py` for comments,
lounges, sorted public replies, or public post permalinks; stock mode resolves display symbols through
`code-or-symbol` before comment lookup.

| Purpose | Status | Method | Path | Params and notes |
|---|---|---:|---|---|
| Stock page composite | `script-backed` | mixed | `scripts/stock_page.py` | Uses `code-or-symbol`, price details, AI detail, optional red flags/trading status/trading analysis, and sanitized comments |
| Public stock comments | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/comments` | Query exactly `subjectType=STOCK`, `subjectId={stockInfo.guid}`, `commentSortType=POPULAR\|RECENT`, optional `lastCommentId`; resolve every product code or display symbol through `code-or-symbol` first. Confirmed 2026-09-07: `A005930` must use `KR7005930003`; sending the product code returned an empty result despite visible comments. Accept a prior cursor through `--last-comment-id`. |
| Public lounge comments | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/comments` | Query exactly `subjectType=LOUNGE`, `subjectId=LOUNGE_{digits}`, `commentSortType=POPULAR\|RECENT`, optional `lastCommentId`; same sanitizer, start-cursor option, and page limits as stock comments |
| Public comment replies | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v2/comments/{commentId}/replies` | Query: optional `replySortType=POPULAR\|NEWEST\|OLDEST`, paired numeric `lastCommentId` and nonnegative integer `lastLikeCount`; result: `results[]`, `hasNext`, `key`, `totalCount`; sorted v2 replies are distinct from the v1 permalink contract |
| Public community post permalink and replies | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/comments/{postId}/replies` | Result has `topic`, `comment`, and `replies.body`; optional numeric `lastReplyId` continues replies; `community_comments.py --post-id --last-reply-id` sanitizes both the post and reply rows |
| Stock community related board | `public-social-sensitive` | GET | `https://wts-cert-api.tossinvest.com/api/v1/boards/STOCK/{productCode}/related` | Board metadata only |
| Stock community recommended profiles | `public-social-sensitive` | GET | `https://wts-cert-api.tossinvest.com/api/v1/community/board/{productCode}/recommend-profiles` | Public profile suggestions; strip profile ids, URLs, avatars, and follow flags before display |
| Popular-follower feed support | `public-social-sensitive` | GET | `https://wts-cert-api.tossinvest.com/api/v1/boards/popular-follower` | Observed in current public feed traffic; no first-class script output; sanitize any future wrapper before exposing fields |
| Community top rankings | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | `scripts/feed.py --kind community-ranking`; only the two exact allowlisted ranking ids are used, output is capped at 10 rows, and profile ids/URLs/follow flags are removed |
| Feed community ranking posts | `public-social-sensitive` / `script-backed` | GET | `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | Public `/feed/recommended` traffic; optional `lastRecommendId`; both recommended CLI aliases sanitize posts and normalize `nextLastRecommendId` |

Observed `GET /api/v4/comments` response shape:

- Top-level keys: `results`, `hasNext`, `key`, `totalCount`
- Page size observed: 11
- Pagination: pass `lastCommentId={key}` for the next page
- Comment row keys include `commentId`, `author`, `authorUserProfileId`,
  `message`, `statistic`, `holding`, `board`, `createdAt`, and `updatedAt`

On 2026-09-16, the public `A005930/community` page exposed reply expansion.
The deployed [community bundle](https://www.tossinvest.com/assets/v2/_next/static/chunks/1901-e370805f386c219f.js)
defines reply sorts `POPULAR`, `NEWEST`, and `OLDEST` (main-comment latest sort
uses `RECENT`, a different enum). Its v2 caller sends `replySortType` and, when
`hasNext` is true, continues with `lastCommentId=result.key` and
`lastLikeCount=results[-1].statistic.likeCount`. It deduplicates reply IDs.
This continuation contract is source-verified; the bounded live check is
recorded in [Public Community Shapes](response-notes.md#public-community-shapes).
Only these exact query keys are allowed on the already cataloged GET route.

Sanitization requirements:

- Keep only UI-useful fields such as `commentId`, `authorNickname`, message
  text, board topic, holding status, created/updated timestamps, and counts.
- Remove profile ids, avatar/profile URLs, profile descriptions, follower
  counts, follow/bookmark/my-profile flags, and account-personalized fields.
- Remove numeric profile ids embedded in public mention markup while retaining
  the visible mention label.
- Redact obvious phone, email, and long-number strings from free-form text.
- Keep pagination bounded; do not bulk harvest public social content.
- Treat v4 feed `feeds[].comment` and permalink v1 `comment`/`replies.body[]`
  as the same sanitizer boundary; never expose either source object directly.

For overview indicator v3/v4 contracts and status, use the owning
[market reference](api-market.md#index-and-market-indicator-apis).

Observed drift, excluded, and sensitive public-social endpoints:

| Endpoint | Status | Reason |
|---|---|---|
| `https://wts-cert-api.tossinvest.com/api/v4/dashboard/wts/overview/indicator` | `script-backed` | Current home aggregate is exposed through `dashboard_ranking.py --kind indicator`; the client permits only the exact GET path with no query or body |
| `https://wts-info-api.tossinvest.com/api/v2/dashboard/wts/overview/signals` | `observed-drift` | Home traffic also exposes a v2 signals route; `dashboard_ranking.py --kind signals` remains on the verified public v1 helper |
| `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-buy` | `excluded` | `wts-api` exchange quote route observed on exchange-rate page; keep out until exact host/path safety review |
| `https://wts-api.tossinvest.com/api/v1/exchange/current-quote/for-sell` | `excluded` | Same as above |
| `https://wts-cert-api.tossinvest.com/api/v1/community/top-rankings/{ranking}` | `public-social-sensitive` | Public community/social ranking surface; only verified ranking ids are allowed and outputs must be sanitized |
| `https://wts-cert-api.tossinvest.com/api/v4/feed/recommend/ranking-posts` | `public-social-sensitive` / `script-backed` | Current feed route; `feed.py --kind recommended` and its compatibility alias sanitize every emitted post |
