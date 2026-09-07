# Public Web Bundle Audit — 2026-09-07

Build ID: `7r39ou7dRVa7AiAbxAXNF`. Repository baseline: `3451e9825e3ff4202c23eb133a659f26cbfe57ce`. Source URLs for the manifest and sector page chunk were supplied by the parent task from the actual sector browser DOM `script[src]`. Five further public-page/dependency chunks were selected from that manifest.

Initial scope: one manifest plus exactly six JavaScript chunks, read as text with public HTTP GET. A separately authorized four-chunk community follow-up is documented below (ten chunks total). JavaScript was not executed. No API endpoint, authentication flow, account/personal endpoint, WebSocket, or telemetry destination was called. The selected public modules may contain shared instrumentation/feature references; these were not investigated or promoted to endpoint findings.

## Contents

- [Source Evidence](#source-evidence)
- [Route Inventory And Comparison](#route-inventory-and-comparison)
- [Sector State And Request Evidence](#sector-state-and-request-evidence)
- [Other Public Chunks](#other-public-chunks)
- [Disposition And Limits](#disposition-and-limits)
- [Community Identifier Follow-Up](#community-identifier-follow-up)

## Source Evidence

SHA-256 is calculated over the fetched response bytes. Final URL equaled requested URL for every source. Retrieval was 2026-09-07 08:49:27-08:50:20 KST (UTC timestamps below).

| Source | UTC | Bytes | SHA-256 |
| --- | --- | --- | --- |
| [manifest](https://www.tossinvest.com/assets/v2/_next/static/7r39ou7dRVa7AiAbxAXNF/_buildManifest.js) | 2026-09-06T23:49:27+00:00 | 12969 | `f54734836ac8602b43ef1d21099d7906b6ccd8aeb55e837eed1f04133df15514` |
| [sector](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/sector/%5Btics-id%5D-74632632ddaf3cb2.js) | 2026-09-06T23:49:27+00:00 | 38880 | `688896b36f45b5d962a47da505c9fd5c735a7b0c8998b30e2fb1e7aa2094cd92` |
| [sector-shared](https://www.tossinvest.com/assets/v2/_next/static/chunks/7677-0c72c3f29c7af117.js) | 2026-09-06T23:50:20+00:00 | 11527 | `4a79cded8328966298fe70a3a648ad0d95c22754a50abe3e788080352b8dac25` |
| [bonds](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/bonds/%5Bguid%5D-5e9609100c70c515.js) | 2026-09-06T23:50:20+00:00 | 15259 | `d22564af46631c0dd81031467a14f93fd56a20b0b1cf10882e67ff6bbf593370` |
| [analytics](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/stocks/%5Bsymbol-or-stock-code%5D/analytics-5ab3d025fe5252d8.js) | 2026-09-06T23:50:20+00:00 | 1991 | `455c3cab5abf1bdee7f27eea909abe404a69c9ca46eb0b949224e3e9fd093e66` |
| [transaction-status](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/stocks/%5Bsymbol-or-stock-code%5D/transaction-status-6923c9d175f94538.js) | 2026-09-06T23:50:20+00:00 | 2201 | `f44954e2fab05189f1aaba8bf326f32496993e7d5e9caf46a7a975f1a3f20237` |
| [screener-preset](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/screener/%5Bpreset-id%5D-4fe4b535a6f5aca6.js) | 2026-09-06T23:50:20+00:00 | 1281 | `b69f4d6e8040d5ea2f7c3685c73ae8d5cc1e6419b893eb87ec0148267e15ca7b` |

## Route Inventory And Comparison

The current manifest `sortedPages` has **63 routes**. The prior [catalog](api-catalog.md#route-manifest-scope-review) records 59 for its 2026-08-05/08-13 builds. This proves a count difference of +4 versus the historical record; the exact old manifest list is unavailable locally, so exact added/deleted route sets cannot be reconstructed from counts alone.

Current stock templates use `[symbol-or-stock-code]`, while the catalog used `[code]` in its old route-manifest descriptions. This is a template-key difference and does not prove that `/stocks/A005930/...` stopped working or that every display symbol resolves. Preserve the distinction among URL input, displayed ticker, product/source code, and endpoint-specific compatibility.

The two `/live-event/...` templates are not mentioned in the existing references and are discovery candidates. They were not opened and their chunks were not fetched within the six-chunk budget. A visible logged-out public link and real event ID are required before claiming support. Route existence alone is not public accessibility or API evidence. Other unrecorded auth/provision/option-adjacent routes remain excluded.

Full current `sortedPages` inventory follows. Status describes this bounded static audit; it is not a claim that every route was browsed.

| Route | Disposition |
| --- | --- |
| `/` | manifest-observed: existing public family; no live request captured here |
| `/404` | excluded: framework/error/service status; not a market-data endpoint |
| `/_app` | excluded: framework/error/service status; not a market-data endpoint |
| `/_error` | excluded: framework/error/service status; not a market-data endpoint |
| `/account/[[...menu]]` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/account-open` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/ai-campaign` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/asap` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/asset-trend` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/bonds/[guid]` | observed-code: existing two bond metadata builders; live GUID/response unverified |
| `/calendar` | manifest-observed: existing public family; no live request captured here |
| `/calendar/economic-indicator` | manifest-observed: existing public family; no live request captured here |
| `/cheetah` | needs-recheck: prior catalog already left public availability unresolved |
| `/cheetah/[code]` | needs-recheck: prior catalog already left public availability unresolved |
| `/community/events/profile-event` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/community/lounges/[subjectId]` | manifest-observed: existing bounded public-social family; no content collected |
| `/community/posts/[post-id]` | manifest-observed: existing bounded public-social family; no content collected |
| `/community/profile/[profile-id]` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/device-register` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/disclaimer/day-market-resume` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/disclaimer/sor-introduction` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/downtime` | excluded: framework/error/service status; not a market-data endpoint |
| `/feed/[[...menu]]` | manifest-observed: existing public family; no live request captured here |
| `/growth/luckybox/delivery` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/guides/kyc/special-finance-information` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/indices/exchange-rate` | manifest-observed: existing public family; no live request captured here |
| `/indices/[index-code]` | manifest-observed: existing public family; no live request captured here |
| `/investment-disclaimers` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/investment-portfolio` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/investor-propensity/result` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/investors25` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/kakao-inapp` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/live-event/[event-id]` | needs-recheck: not found in prior references; visible public link/ID required |
| `/live-event/[event-id]/[tab]` | needs-recheck: not found in prior references; visible public link/ID required |
| `/login-extend` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/news` | needs-recheck: prior catalog already left public availability unresolved |
| `/open-api/landing` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/open-api/mcp-auth/authorize` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/open-api/pre-apply` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/paper-option-bridge` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/promotions/disclaimers/[id]` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/promotions/reward-stocks/[name]` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/screener` | manifest-observed: existing public family; no live request captured here |
| `/screener/user` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/screener/user/[preset-id]` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/screener/[preset-id]` | manifest-observed: existing public family; no live request captured here |
| `/sector/[tics-id]` | manifest-observed: existing public family; no live request captured here |
| `/security/install` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/settings` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/signin` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/signup` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/status` | excluded: framework/error/service status; not a market-data endpoint |
| `/stocks/[symbol-or-stock-code]` | manifest-observed: existing public stock family; parameter placeholder changed |
| `/stocks/[symbol-or-stock-code]/analytics` | manifest-observed: existing public stock family; parameter placeholder changed |
| `/stocks/[symbol-or-stock-code]/community` | manifest-observed: existing public stock family; parameter placeholder changed |
| `/stocks/[symbol-or-stock-code]/news` | manifest-observed: existing public stock family; parameter placeholder changed |
| `/stocks/[symbol-or-stock-code]/option` | excluded: option/order-adjacent page not investigated |
| `/stocks/[symbol-or-stock-code]/order` | manifest-observed: existing public stock family; parameter placeholder changed |
| `/stocks/[symbol-or-stock-code]/transaction-status` | manifest-observed: existing public stock family; parameter placeholder changed |
| `/test/community` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/test/community/comment-item` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/test/community/info-banner` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |
| `/watchlists` | excluded: account/auth/personal/provision/promotion/legal/test or other non-market route; module not fetched |

## Sector State And Request Evidence

The sector page imports endpoint descriptor module `65079` as `ew`, using `ew.fl` for stocks and `ew.A$` for ETFs, plus module `10031` for other TICS requests. Those descriptor definitions are outside the six chunks inspected. Therefore this audit directly verifies body/query construction and page logic, while the exact method/path/host mapping remains attributed to the existing [TICS catalog](api-catalog.md#dashboard-and-discovery-apis), not freshly proven by request traffic.

| UI state | Current source behavior | Comparison / interpretation |
| --- | --- | --- |
| Header/chart nation | First query `nation` value equals US → US; otherwise KR. Subsequent market selection changes local state. | Header is independent of stock/ETF filter state; route URL need not change. |
| Stock nation | Initialized from first query value only when ALL/KR/US; otherwise ALL. Nation choices ALL/KR/US. | Stock default can differ from header KR. CLI explicit nation choices remain necessary. |
| ETF nation | Local state starts ALL, independently of query/header/stock. | Do not propagate header nation automatically into ETF filters. |
| ETF leverage/inverse | UI hide state starts false. Request sends `includeLeverageInverse: !hideState`; button inverts hide state. | Hide unchecked → include true; hide checked → include false. The bool has opposite sense to the visible label. |
| Stock request body | nation, sortBy, sortOrder, page. Default sort MARKET_CAP/DESC. | Consistent with `sector.py` builder; no size field sent by this UI. |
| ETF request body | nation, sortBy, sortOrder, includeLeverageInverse, page. Default TRADING_VALUE/DESC. | Consistent with `sector.py` builder; no size field sent by this UI. |
| Stock/ETF paging | Initial page 1. Page count `max(1, ceil(totalCount/10))`. Nation/sort changes reset page 1; ETF hide toggle also resets page 1. | Static proof of one-based state and 10-row UI page calculation, not server maximum or a live response. |
| News paging | Initial page 1; query `{number: page}`. UI derives page size from `pagingParam.size`, falling back to current body length. | Previous live size 5 remains historical; current source does not hardcode size 5 for page count. |
| Trending sidebar | Slices full tics list with `(page-1)*10 .. 10*page`; nation change resets 1. | Client-side paging; do not invent a server page parameter. |
| Refresh | Stock/ETF query sets 10 seconds, no background refetch, no window-focus refetch. | Code configuration, not a measured runtime interval or permission for aggressive polling. |
| Empty ETF section | When ALL, hide=false, loaded, and totalCount=0, the component returns null. Otherwise its empty state can show. | A missing ETF section can be data-dependent, not endpoint deletion. |
| Comparison chart | Shared public module sends nation (default KR), securitiesType=STOCK, indicatorCode. | Four labels S&P 500/Nasdaq/KOSPI/KOSDAQ use imported constants; exact code strings are not resolved by the inspected chunk. |

The exact body constructors agree with existing [sector.py](../scripts/sector.py). ETF sort controls are TRADING_VALUE and EXPENSE_RATIO; stock sort controls use MARKET_CAP, TRADING_VALUE, VOLUME and ANALYST. This pass found no justified endpoint or CLI-contract replacement.

Selected exact code fragments below are evidence locators in the hashed source. Offsets are zero-based Unicode character positions after UTF-8 decoding, not byte offsets or line numbers. Module names are deployment-specific. They are evidence references, not a proposed implementation dependency.

`sector` character 13597:

```javascript
eQ={sortBy:"TRADING_VALUE",sortOrder:"DESC"}
```

`sector` character 13642:

```javascript
eZ=e=>{let{ticsId:a}=e,[t,l]=(0,r.useState)("ALL"),[o,d]=(0,r.useState)(eQ),[s,c]=(0,r.useState)(!1),[m,u]=(0,r.useState)(1),{data:p,isLoading:g,dataUpdatedAt:b}=(e=>{let{ticsId:a,nation:t,sortBy:n,sortOrder:l,includeLeverage
```

`sector` character 14192:

```javascript
includeLeverageInverse:!s,page:m
```

`sector` character 15730:

```javascript
onClick:()=>{c(e=>!e),u(1)}
```

`sector` character 30831:

```javascript
aD=e=>{let a=Array.isArray(e)?e[0]:e;return null!=a&&aR(a)?a:"ALL"};var ax=t(98499),aL=t(81709);t(99591);let aF={KR:"국내",US:"해외"},
```

`sector` character 34992:

```javascript
aK=e=>"US"===(Array.isArray(e)?e[0]:e)?"US":"KR",aU=e=>{let{ticsId:a,nation:t,on
```

`sector` character 18367:

```javascript
m=d?.pagingParam.size??c.length,u=m>0?Math.ceil((d?.totalCount??0)/m):1;return i||0!==c.length?(0,n.FD)("
```

`sector-shared` character 1775:

```javascript
queryParams:{nation:d,securitiesType:"STOCK",indicatorCode:a}
```

## Other Public Chunks

| Chunk | Findings | Evidence status |
| --- | --- | --- |
| bonds | GET builder for `/api/v1/bond-infos` with `guid`; GET builder for `/api/v1/bond-infos/simple` with repeated `guids` via `arrayFormat:"repeat"`. | Existing catalog contract reconfirmed in code. INFO host is imported, not re-resolved here. No real GUID or response fetched. |
| analytics | Route registers `/stocks/[symbol-or-stock-code]/analytics`; page component delegates to shared layout. | Page wrapper is not the data implementation; zero API literals here does not mean no APIs. |
| transaction-status | Route registers `/stocks/[symbol-or-stock-code]/transaction-status`; shared layout supplies actual content. | Sub-tab endpoint behavior cannot be refreshed from this small wrapper alone. |
| screener-preset | Route registers `/screener/[preset-id]`; delegates to shared screener layout. | Filter metadata/result request code lives in an uninspected dependency. |

Bond builder evidence uses template literals, so an extractor that only finds strings starting with `/api/` would miss it:

```javascript
let o=e=>r.FH.get(`${l.Q.INFO}/api/v1/bond-infos`,{params:{guid:e}}),
i=e=>{let t=(0,n.stringify)({guids:e},{arrayFormat:"repeat",addQueryPrefix:!0});
return r.FH.get(`${l.Q.INFO}/api/v1/bond-infos/simple${t}`)}
```

This is a static description only. The exact host value behind `l.Q.INFO`, response schemas, accessibility and current page integration require separate current evidence. Do not enumerate bond GUIDs or create a client from route presence alone.

## Disposition And Limits

- Confirmed documentation changes: current build/route count, actual stock template placeholder, explicit sector header/stock/ETF state separation and inverted leverage toggle, dynamic news page-size calculation, existing bond repeated-key query construction.
- New public API endpoints proven by these six chunks: **none**. Relevant unresolved page candidate: live-event detail/tab templates; inspect only from an actual visible public link.
- Exact old route changes, sector descriptor method/path/host definitions, stock shared-layout APIs, screener request families, live response shapes and error handling remain unverified by this bounded static pass. Existing live observations elsewhere in the audit must be labeled separately.
- Use source-byte hashes to reproduce this observation. Chunk hashes can change for build/instrumentation reasons without an API contract change; no old chunk source was available here to establish a semantic code diff.
- Only this dated report was edited by the bundle audit. Temporary downloaded public assets and metadata were confined to `.codex/web-audit-*`; they contain no runtime tokens, cookies, account responses or HAR data. The parent task may recycle these temporary files after consolidating evidence.

## Community Identifier Follow-Up

The parent task reported an empty anonymous direct response for `subjectId=A005930` / `commentSortType=RECENT`, while a public browser stock-community page displayed popular posts. Those are parent-observed API/UI facts, not calls performed by this audit. Differing sort and identifier values initially prevented a deletion conclusion.

Four additional chunks were selected from the already observed current community manifest dependencies. Only public community caller/list-hook code was inspected; no API request or profile investigation was performed.

| Source | Retrieved UTC | Bytes | SHA-256 |
| --- | --- | --- | --- |
| [community-page](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/stocks/%5Bsymbol-or-stock-code%5D/community-be0a0156eb979906.js) | 2026-09-06T23:56:48+00:00 | 2764 | `573c447bc60a1f7d02c9fa3e4a094a6b37abddef9ae10dded56448da960cf238` |
| [stock-layout](https://www.tossinvest.com/assets/v2/_next/static/chunks/3035-85e5999deade0135.js) | 2026-09-06T23:56:48+00:00 | 652424 | `a93f77ec6260ca5f77d1b65469852fa74f859281bf2f0cc8ab1759433647ba3c` |
| [community-shared](https://www.tossinvest.com/assets/v2/_next/static/chunks/3901-34357442c55d3371.js) | 2026-09-06T23:57:37+00:00 | 18208 | `02e2ca78c68b442395f133cd849b91be6fc78b7e6b118452269db2db9440a742` |
| [community-common](https://www.tossinvest.com/assets/v2/_next/static/chunks/1901-57e0f96ccea3440d.js) | 2026-09-06T23:58:10+00:00 | 175153 | `c4f2865bdb2e0fa1b6c9e038279563657476f83040c223ca92eeb3a7956af75c` |

### Findings

The current **rendered stock-community list receives `stockInfo.guid` as subjectId**, not `stockInfo.code` or the input URL symbol. The SEO caller independently passes metadata guid into the same comments hook. Subsequent bounded public verification confirmed `A005930` resolving to `KR7005930003`, with advancing comment continuation and no overlap in the sampled first/next pages; the client correction is complete. See the [update audit](update-audit-2026-09-07.md#direct-public-requests) for that separate API evidence. The metadata resolver itself is outside this four-chunk set, so the bundle evidence alone does not establish which endpoint provides guid or guarantee its presence for every product.

- Module `90094` maps popular to `POPULAR` and recent to `RECENT`; no changed sort enum was found.
- Module `77727` calls descriptor `40785["/api/v4/comments"]` with query fields `subjectType`, `subjectId`, `commentSortType`, and `lastCommentId`.
- Continuation is returned `key` when `hasNext` is true, forwarded as next `lastCommentId`. No numeric page is calculated.
- Stock-layout module `63035` passes metadata guid to the actual list component `83776.J`; that component imports the same `77727.s` list hook. This is rendered-list evidence, not only SEO behavior.
- The community-page SEO callback independently passes metadata guid to `77727.s`, using the popular enum.
- The stock subject-type enum definition (`19876.PQ`) and descriptor host/method definition (`40785`) are outside the inspected four chunks. Exact backing subject-type value, HTTP host/method and live response require existing catalog or parent verification.
- Helper chunk `3901` contained none of the target hook, enum or query-field strings; it provided no positive evidence.
- No v5 replacement route or other endpoint replacement was established. Empty results for an incompatible subjectId must not be called endpoint deletion.

### Exact Source Evidence

Offsets are zero-based Unicode character positions after UTF-8 decoding. These are static code excerpts, not account/profile response data.

`community-page` character 1992:

```javascript
(0,r.Y)(l,{subjectId:t.guid,topic:t.name})
```

`stock-layout` character 468375:

```javascript
(0,a.Y)(bA.J,{subjectName:e.name,subjectImageUrl:i,subjectId:e.guid,subjectType:bP.PQ.종목,scrollRef:t,hideEditor:!0,className:"wy26a77",rende
```

`community-common` character 161433:

```javascript
90094:(e,t,a)=>{a.d(t,{f:()=>r,p:()=>n});let n={인기순:"POPULAR",최신순:"RECENT"},r={최신순:"NEWEST",등록순:"OLDEST",인기순:"POPULAR"}},93274:(e,t,a)=>{a.d(t,{h:()=>
```

`community-common` character 148480:

```javascript
return await o.u.callApi(i["/api/v4/comments"],{queryParams:{subjectType:e,subjectId:t,commentSortType:a,lastCommentId:r}})},initialPageParam:void 0,getNextPageParam:e=>{if(e.hasNext)return e.key},refetchOnMount:!1,refetchOnWindowFocus:!1,placeholderData:l.rX,meta:{scope:"community"}}),b=h?.pages.at
```

### Update Implications

Resolve current metadata before stock-comment calls and use its guid for subjectId while preserving the caller-visible product identity separately. Missing guid is an identifier-resolution failure, not empty community content. Keep lounge and post/reply identifiers separate. Retain the sanitizer and bounded paging rules. Compare POPULAR and RECENT with the same resolved guid before concluding that content is absent or a sort is unsupported.

This source evidence supports a concrete fix investigation but is not a live compatibility test. The parent task owns code changes and public verification. Temporary follow-up assets are limited to `.codex/web-community-*.js` and `.codex/web-community-metadata.json`; no runtime credentials or raw response payloads were stored.
