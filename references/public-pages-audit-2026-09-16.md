# Public Pages and API Audit — 2026-09-16

The current build has **62 route templates**, all assigned a disposition below.
The audit found and addressed gaps in transaction data, company-news and reply
continuation, search labels and related panels, company identifiers, and
financial statement selectors. Route coverage does not mean every instrument,
news item, community post, date, or filter combination was exercised.

The starting repository commit was `7d2b7611ef9d3e8dab2e07fa6682cccebd319dca`.
The current web build was `FNTsN5Z21hJmsl3Sh71hB`. Compared with the complete
63-route inventory in the [September 7 bundle audit](web-bundle-audit-2026-09-07.md),
there were **no additions** and one removal, `/investors25`. This removed route
was outside the public market-data scope. The public market route set did not
gain a new template. [Source: current manifest][manifest].

## Contents

- [Evidence and coverage boundaries](#evidence-and-coverage-boundaries)
- [Complete route disposition](#complete-route-disposition)
- [Browser observations](#browser-observations)
- [Paging and link contracts](#paging-and-link-contracts)
- [Direct request ledger](#direct-request-ledger)
- [Verified contracts and implemented fixes](#verified-contracts-and-implemented-fixes)
- [Remaining limits](#remaining-limits)
- [Validation](#validation)
- [Source evidence](#source-evidence)

## Evidence and coverage boundaries

Three evidence types are kept separate throughout this report:

| Label | What it establishes | What it does not establish |
| --- | --- | --- |
| UI | Logged-out page rendering and direct interaction with visible tabs, links, filters and page controls | The exact HTTP request sent by that interaction |
| Static | Request builders, response-field accesses, routing and continuation in the deployed public JavaScript | Successful current server response or logged-out accessibility by itself |
| Direct | A separately executed public read-only API request and its returned structure | That the browser made precisely that request, every supported combination, or future stability |

The browser tool did not expose network capture. This report does not describe
independent API calls as captured browser traffic. Public scripts were downloaded
as text and never executed. Direct checks were bounded and sequential, at least
one second apart within each batch, with no cookies, authentication headers,
redirect-following, or retries. Only public market identifiers, field names,
types, selected option metadata, counts, and sanitized social metadata were
retained; raw account, session, HAR, or community-content archives were not made.

The inventory classifies **16 public content templates**, **2 aliases**,
**4 unresolved/gated candidates**, **2 explicitly member-gated live-event
templates**, **5 framework/status routes**, and **33 excluded routes**. These
sum to 62. All 16 public templates were visited through representative instances,
including the earlier transaction-status visit. “Public” is the scope
classification, not a claim that all instances or controls passed. Current UI
evidence and partial results are enumerated separately below.

## Complete route disposition

This table accounts for every `sortedPages` entry in the current manifest.
Its final column defines the applicable checks or the reason for exclusion;
the browser and direct-request sections record which checks actually ran.
No authenticated workflow is implied by route presence.

| Current route | Disposition | Applicable checks or exclusion |
| --- | --- | --- |
| `/` | public | Home: KR/US, all ranking families/durations, search, focused stock/industry, visible index/calendar/news links. |
| `/404` | framework | Framework/error/service-status route; no market-data coverage claim. |
| `/_app` | framework | Framework/error/service-status route; no market-data coverage claim. |
| `/_error` | framework | Framework/error/service-status route; no market-data coverage claim. |
| `/account/[[...menu]]` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/account-open` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/ai-campaign` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/asap` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/asset-trend` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/bonds/[guid]` | unresolved | Current metadata builders/UI statically verified, but no real public GUID/link found in this audit. Never enumerate IDs or click app notification/trade action. |
| `/calendar` | public | Month/date/nation/category controls; visible event details and economic-indicator links; stop at login gates. |
| `/calendar/economic-indicator` | public | Follow real event query from calendar; chart periods, historical observations, AI text and back-link. |
| `/cheetah` | unresolved | Historically blank/feature gated. Revisit only current public entry/link; stop at login/blank gate. |
| `/cheetah/[code]` | unresolved | Historically blank/feature gated. No proof of a distinct public market-data surface. |
| `/community/events/profile-event` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/community/lounges/[subjectId]` | public | Follow a visible lounge link; POPULAR/RECENT, one continuation, selected public post/reply; sanitize output. |
| `/community/posts/[post-id]` | public | Follow visible post permalink; bounded replies and next cursor; no profile exploration or posting. |
| `/community/profile/[profile-id]` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/device-register` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/disclaimer/day-market-resume` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/disclaimer/sor-introduction` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/downtime` | framework | Framework/error/service-status route; no market-data coverage claim. |
| `/feed/[[...menu]]` | public | Recommended and news; selected public news types and public post links. Following/personalized sections excluded. |
| `/growth/luckybox/delivery` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/guides/kyc/special-finance-information` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/indices/exchange-rate` | public | Public price/chart/quote controls and related currencies; exchange buy/sell routes excluded. |
| `/indices/[index-code]` | public | One representative per visible KR/US/index/commodity/futures/bond/crypto family; relevant chart, daily paging and news. |
| `/investment-disclaimers` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/investment-portfolio` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/investor-propensity/result` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/kakao-inapp` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/live-event/[event-id]` | member-gated | Current shared layout starts with member gate before event data. Tabs are analysis/transcript/ir. Excluded from anonymous API coverage; only visible link/gate observation is permissible. |
| `/live-event/[event-id]/[tab]` | member-gated | Same member-gated shared layout; must not promote API builders in shared chunks to public endpoints. |
| `/login-extend` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/news` | alias | Current source explicitly replaces with `/feed${asPath}`; browse alias once then cover /feed/news. |
| `/open-api/landing` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/open-api/mcp-auth/authorize` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/open-api/pre-apply` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/paper-option-bridge` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/promotions/disclaimers/[id]` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/promotions/reward-stocks/[name]` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/screener` | public | KR/US, filter picker, public preset links, sort and first/next result page; no saved-user-preset operations. |
| `/screener/user` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/screener/user/[preset-id]` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/screener/[preset-id]` | public | Follow public common preset ID; same result APIs; verify preset filter/sort/nation and one next page. |
| `/sector/[tics-id]` | public | Header chart, stock/ETF nations and sorts, leverage hide, separate stock/ETF/news paging, related industries and breadcrumb links. |
| `/security/install` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/settings` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/signin` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/signup` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/status` | framework | Framework/error/service-status route; no market-data coverage claim. |
| `/stocks/[symbol-or-stock-code]` | alias | Prior public root resolves to /order; verify current alias and visible five detail tabs. |
| `/stocks/[symbol-or-stock-code]/analytics` | public | KR/US/ETF differences; company, financial statement/period/currency, dividends, analyst links and related industries. |
| `/stocks/[symbol-or-stock-code]/community` | public | Stock GUID resolution, two list sorts, next cursor, post/related lounge links; bounded sanitized social data. |
| `/stocks/[symbol-or-stock-code]/news` | public | News/disclosure tabs; latest/relevance and paging; modal/detail and related stock links. |
| `/stocks/[symbol-or-stock-code]/option` | unresolved | Historically gated/order adjacent. Observe visible availability only; no option trading requests or actions. |
| `/stocks/[symbol-or-stock-code]/order` | public | Public quote/chart UI only: intervals, history paging, daily/tick, venue and summary controls. Exclude trade widgets and actions. |
| `/stocks/[symbol-or-stock-code]/transaction-status` | public | Already audited 2026-09-16; retain credit, provisional investor flags and cursor corrections in consolidated result. |
| `/test/community` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/test/community/comment-item` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/test/community/info-banner` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |
| `/watchlists` | excluded | Account/auth/personal/profile/provision/marketing/legal/test/user-preset surface; no actions or endpoint harvesting. |

## Browser observations

Representative route instances were followed from observed public links,
already verified page URLs, or an observed public post ID with its known route
template. The table records completed browser work; unavailable controls and
unproven continuations are explicitly qualified.
It includes the earlier dedicated transaction-status inspection.

| Instance / surface | Directly observed controls and links | Boundary |
| --- | --- | --- |
| `/` | Six amount/volume/rise/fall ranking radios; realtime/1d/1w/1m/3m/6m/1y menu; all/KR/US selectors; industry and investor tabs; investor buy/sell; industry nation, change/amount and 1d/1w/1m/3m/1y | Selected UI states often retained `/`; URL state alone does not identify every active filter |
| Home related links | KOSPI, KOSDAQ, FX, VIX, Nasdaq futures, Nasdaq, S&P 500, SOX, BTC, gold, calendar, stocks, sectors | Link discovery is not verification of every destination or market stream |
| `/sector/87?nation=US` | Stock, ETF, news and trending-sidebar page 2 clicked independently; changed content and previous controls; comparison index menu and Nasdaq selection; separate stock/ETF nation controls; related sector/news links | Four paging groups have independent state; the sidebar is client-only paging |
| `/stocks/A005930/news?menu=news` | Latest/relevant sorts; more news revealed by scrolling; disclosure tab changed `menu=disclosure`; visible KIND filing opened in overlay with source-document link | Original external document link was observed; external destination availability is not asserted |
| `/stocks/A005930/analytics` | Six section tabs: 주요 정보, 재무, 실적, 배당, 동종 업계 비교, 애널리스트 분석; income/balance/cash-flow radios; 3년/분기 controls; quarter/annual menu and annual selection | Snapshot after annual selection did not prove a changed table; annual success is direct-API evidence. All factor/range/currency combinations were not traversed |
| `/stocks/A005930/order` | Public price/chart/quote UI; daily/weekly/monthly chart buttons; realtime/daily trade views; daily date/close/change/volume/value/open/high/low columns | No order controls operated; technical studies remain separate from server APIs |
| `/stocks/A005930/community` | Latest/popular selection and visible comment expansion | Browser evidence does not establish a multi-page reply cursor; direct reply check below returned a terminal first page |
| `/stocks/A010170/transaction-status` | Investor/program/credit/lending/short-selling/CFD views, both credit subtypes, investor-detail table | See [dedicated audit](transaction-status-audit-2026-09-16.md) for exact values and fields |
| Global search | All/product/industry/news/index sections for 삼성전자; related-stock links; 반도체 industry and SOX links; real alphanumeric product links | “More” can reveal already returned items; no generic server page parameter was inferred |
| `/indices/KGG01P` | Investor-daily and daily-quote tables independently advanced; investor week/month/year; index/FX, bond, commodity, crypto sidebar tabs | Visible bond links were `/indices/KR1BENCH*` and `/indices/ROB.US*YT-RR`, not bond-product GUID pages |
| `/indices/VWAP.KRW-BTC` | Daily-quote page 2 displayed older dates including weekends; related news/ETF links visible | This does not reverify WebSocket delivery |
| `/indices/exchange-rate` | Public quote/news/ETF content rendered; screenshot confirmed a chart spinner | Chart iframe remained `about:blank`; period controls unavailable. The FX data API succeeded independently |
| `/indices/SPX.CBI` | Public S&P 500 quote/news/related ETFs and daily-table page controls | Page 2 was not clicked on this instance |
| `/indices/KR1BENCH0010?tab=채권` | Actual Korean 10-year government-bond sidebar link rendered quote, news and related ETFs | Bond index, not `/bonds/{guid}` |
| Gold commodity link | Actual `RFU.GCv1` sidebar link was clicked and redirected to sign-in | Stopped at sign-in; no commodity data request or other commodity/futures instance verification |
| `/calendar` | Economic/overseas/monthly; previous month August and next September; earnings/domestic | Month navigation changes date selection, not server cursor; member-gated earning-call data excluded |
| `/calendar/economic-indicator?date=2026-09-01&ric=USPMI%3DECI` | Actual calendar link followed; announcement, AI analysis, history table and calendar backlink rendered | Independent detail API succeeded; separate AI API not called without exact announcement datetime |
| `/stocks/US19990122001/news?menu=news` | NVIDIA four main tabs; news and disclosure tabs; SEC/earnings items with companyCode NAS00208X-E0 | KR-only transaction-status tab absent; not every US tab combination tested |
| `/screener` | Continuous-rise public preset rendered; selected undervalued-growth | Default public entry visited; no user preset saved |
| `/screener/4` | Sales-growth/PER/net-income-growth filters; nation changed to overseas with US results; basic/financial/price/technical filter tabs including RSI/Bollinger metadata; scroll revealed rank 38 | Scroll did not prove a second server page; source and direct two-page check are separate. Sort/filter combinations not exhaustive |
| `/feed/recommended` | Public cards, stock links and eight lounge links rendered | Bounded browser scroll did not prove next page; direct continuation separately succeeded |
| `/feed/news` | Popular/main/latest/rising categories selected; popular page 2 changed article links and enabled previous; actual article overlay with source/related stocks/major news | External article bodies not retained; not every category paged |
| `/community/lounges/LOUNGE_193404` | Actual recommended-feed discussion link followed; popular/recent toggle and expansion | Browser reply/list continuation not established; direct RECENT list continuation separately succeeded |
| `/community/posts/{observed-post-id}` | Known permalink with an ID from a currently rendered card opened the public post and lounge backlink | Share button did not establish permalink navigation; no sharing, profile navigation or social mutation |
| `/news` and `/stocks/A005930` aliases | Resolved to `/feed/news` and `/stocks/A005930/order` respectively | News-query preservation is source evidence, not an independently tested query variant |

## Paging and link contracts

| Family | Continuation or local state | Evidence and current result |
| --- | --- | --- |
| Company news | Send returned `pagingParam.number` and optional `key`; preserve code, size and orderBy; stop on `lastPage` | Static sends both fields. Two live latest pages had null keys and no ID overlap; non-null key behavior remains source-verified |
| Filings | Same response-provided number/key model, deployed UI size 20 | Live size-2 first/next pages succeeded; no extra increment of returned next number |
| Sector stocks / ETFs | Independent one-based `page`; current size 10 | UI page changes and direct page 1/2 agree |
| Sector news | `number`; page-count denominator is `pagingParam.size`, falling back to body length | Live size 5; UI page 2 worked |
| Sector trending sidebar | Slice `(page-1)*10 .. page*10` from an existing list | Static and UI; no server cursor |
| Screener | `{pagingParam:{number,size},filters,sort,nation}`; deployed UI size 50, initial number 1; next is **response.page + 1** iff not lastPage | Two direct size-2 pages succeeded; virtualized visible rows do not measure server page size |
| Recent investor / program / MDS histories | Returned `pagingParam` number/key with `lastPage` | Current CLI now accepts recent history cursors; a short/empty body alone is not end of history |
| Stock / index daily candles | Pass `nextDateTime` unchanged as `from`; stop on null | KOSPI/BTC pairs had no date overlap; earlier stock check is separately dated |
| Stock / lounge comments | `hasNext`, `key` forwarded as `lastCommentId`; bounded page/row limits | Lounge RECENT live first/next pages returned 11 + 11 rows, zero sampled identity overlap, still hasNext; other boards/sorts not covered by this pair |
| V2 replies | `replySortType`; continuation combines returned key as `lastCommentId` and last raw reply's `statistic.likeCount` as `lastLikeCount` | Static plus local regression tests; one live first page returned two replies and `hasNext=false` |
| V1 post replies | Separate `lastReplyId` contract | Keep distinct from v2 sorted replies |
| Recommended feed | Key plus **nonempty raw feeds** required to continue; returned key.lastRecommendId becomes lastRecommendId | Fixed a source-confirmed empty-page mismatch; direct first/next pages returned 24/20 raw entries and 20/20 sanitized comments, zero sampled overlap |
| Search | Main sections and related subsections; `--limit` is local output truncation | No generic page/key contract established; related panels are distinct same-endpoint requests |
| Calendar | Month/date navigation; offset/limit applied locally to filtered events | Not a server cursor |
| Financial tables / dividends | Factor/period/range or years selection returns one selected dataset | No numbered table pagination established |

Related-page identifiers are endpoint-specific. Stock route input, displayed
symbol, product code, metadata companyCode, community GUID, industry ID, news
ID and filing report ID must not be substituted for one another. Actual
alphanumeric KR and US company lookups demonstrated why prefix stripping alone
is insufficient. Current search explicitly supports the verified related-topic,
company-tics, tics-product and market-index-description subsections. The source
also contains other subsection labels; those were not automatically enabled.

## Direct request ledger

This expanded pass contains **49 successful direct requests** in the seven
batches below. The earlier transaction-status pass adds **15** requests across
12 paths, for **64 requests across the two explicitly separated passes**.
Static-file downloads and browser-generated traffic are excluded from these
counts. No blanket availability claim is inferred from these samples.

| Batch | Calls | UTC window on 2026-09-16 | Scope and outcome |
| --- | ---: | --- | --- |
| News and main search | 4 | 02:54:30–02:54:34 | Samsung latest news pages 1/2; 삼성전자 main search; 반도체 TICS search |
| Financials and dividends | 8 | 02:58:56–02:59:04 | Four statement selections; comprehensive default/explicit selection; dividend default/3-year selection |
| V2 community replies | 1 | 03:02:34 | One UI-selected public comment, POPULAR; two sanitized replies, hasNext false |
| Related search | 7 | 03:02:59–03:03:06 | Three source-identifier lookups, then four related-section requests |
| Broad market pages | 23 | 03:06:31–03:07:28 | Filings, sector, KOSPI, BTC, FX, screener, calendar, metadata, US quotes, economic-indicator detail |
| Resolved company IDs | 2 | 03:09:06–03:09:07 | NVIDIA news and alphanumeric KR ETF filings using returned companyCode |
| Public social lists | 4 | 03:21:14–03:21:17 | Recommended feed and lounge RECENT list, one returned-cursor continuation each |

Exact successful bounded market shapes:

| Request family | Parameters / selected identity | Result |
| --- | --- | --- |
| `/api/v2/news/companies/005930` | latest, size 2, initial then returned number 2; key null | 2 + 2 rows; zero ID overlap; next numbers 2 then 3 |
| `/api/v1/stock-detail/companies/005930/filings` | size 2, initial number 1 then returned number 2 | 2 + 2; zero overlap; keys null |
| `/api/v2/dashboard/wts/overview/tics/87/stocks` | POST US, MARKET_CAP/DESC, page 1/2 | 10 + 10; totalCount 498; zero code overlap |
| `/api/v2/dashboard/wts/overview/tics/87/etfs` | POST US, TRADING_VALUE/DESC, includeLeverageInverse true, page 1/2 | 10 + 10; totalCount 353; zero code overlap |
| `/api/v2/dashboard/wts/overview/tics/87/news` | number 1/2 | 5 + 5; totalCount 250; zero identity overlap |
| `/api/v2/index-infos/KGG01P` and `/VWAP.KRW-BTC` | Exact visible codes | Metadata objects |
| `/api/v1/c-chart/kr-s/KGG01P/day:1` | count 3, useAdjustedRate true, then returned from | 3 + 3; zero date overlap |
| `/api/v1/c-chart/crypto/VWAP.KRW-BTC/day:1` | Same bounded continuation | 3 + 3; zero date overlap |
| `/api/v1/dashboard/wts/overview/exchange-rates` | GET | Two exchange-rate entries |
| `/api/v1/r-chart/fx/EXCHANGE_RATE/1d/min:5` | last false, useAdjustedRate true, currency USD | 38 candles; separate from the UI spinner |
| Cert `/api/v2/screener/screen` | POST filters [], nation kr, size 2, number 1/2 | 2 + 2 stocks; totalCount 2479; response page 1/2, lastPage false; zero code overlap |
| Cert `/api/v4/calendar/monthly/2026-09` | POST `{}` | 45 events |
| Cert `/api/v1/calendar/economic-indicators/USPMI=ECI` | announceDate 2026-09-01 | 33 historical rows, 0 related news, 1 related article, 2 upcoming indicators |
| `/api/v2/stock-infos/code-or-symbol/A0162Z0` | Actual search-linked KR ETF | symbol 0162Z0; companyCode **EFKSP0162Z0**, KSP |
| `/api/v2/stock-infos/code-or-symbol/US19990122001` | Actual NVIDIA link | symbol NVDA; companyCode **NAS00208X-E0**, NSQ |
| `/api/v3/stock-prices/US19990122001/quotes` | No optional query overrides | Ten offer/bid levels on each side |
| `/api/v2/news/companies/NAS00208X-E0` | size 2 | Two rows; confirms the resolved US company route |
| `/api/v1/stock-detail/companies/EFKSP0162Z0/filings` | number 1, size 2 | Two rows; confirms the resolved alphanumeric KR company route |
| Cert `/api/v4/feed/recommend/ranking-posts` | Initial then returned lastRecommendId | Raw 24 + 20; sanitized comments 20 + 20; zero comment-identity overlap; both pages retain continuation |
| Cert `/api/v4/comments` | LOUNGE, same observed subject, RECENT, initial then returned lastCommentId | 11 + 11 rows/comments; zero identity overlap; both pages hasNext true |

The seven paired comparisons in the broad batch all had zero sampled identity
overlap. The separate company-news, recommended-feed and lounge pairs also had
zero overlap. These are bounded
observations of moving datasets, not a guarantee against later inserts or
reordering. The helpers expose successful parsed results rather than a separate
numeric HTTP-status field; no unobserved transport details are asserted.

## Verified contracts and implemented fixes

### Transaction-status follow-up

The [dedicated transaction audit](transaction-status-audit-2026-09-16.md)
records the earlier baseline defects and precise field/unit mappings. The
follow-up adds `margin-loan` and exactly spelled `securities-landing`, retaining
legacy `credit`; supports recent investor/program continuation; and preserves
availability flags, intraday state and timing in normalized output. Unavailable
individual data no longer appears as an observed zero. Grouped intraday fields
remain separate and retain their original semantic uncertainty.

The CFD size-3 response was empty but not terminal; size 50 returned 25 rows.
Recent and fixed-date foreign-investor values differed for the same date, so
their provenance must be retained. These observations do not prove why the
series differ. [Source and direct evidence: transaction audit](transaction-status-audit-2026-09-16.md).

### Company news, filings and identifier resolution

The deployed company-news caller sends number, size 20, key and orderBy and
continues with both returned paging fields. The CLI now accepts an encoded
opaque `--key` without deriving a date or incrementing the returned number.
The direct sample exercised null keys; non-null key propagation is supported
by source and regression tests, not a live non-null example. [Source: layout][layout].

News and filing lookup now resolve all product-code/symbol inputs through
public metadata, including numeric KR inputs. This adds a metadata request;
`--company-code` bypasses it for an already confirmed company identifier.
A0162Z0 is not equivalent
to company 0162Z0, and NVIDIA's company key is not its product code or ticker.
The two resolved company requests above both returned data. Existing six-digit
KR behavior is preserved in pure path builders; runtime lookup resolves metadata
for all product/symbol inputs. Related helpers use validated path segments;
no identifier broadening authorizes authenticated or arbitrary paths.

### Search labels and related panels

Main search now preserves PRODUCT `keyword` and TICS `title`. The live TICS 169
sample contained title without name, confirming why the previous sanitizer
lost its visible label. Main search preserves `subSectionQuery` strings;
related modes require the matching identifier. The four verified
subsections use the same POST `/api/v3/search-all/wts-auto-complete` family:

| Section | Exact option | Direct result |
| --- | --- | --- |
| RELATED_TOPIC | productCode A005930 | 22 related products |
| COMPANY_TICS | companyCode 005930 | Industry metadata id 553/title and 3 products |
| TICS_PRODUCT | ticsId 169 | 562 returned products; emitted output remains locally bounded |
| MARKET_INDEX_DESCRIPTION | code KGG01P | One description item |

Queries came from selected result `subSectionQuery` or its displayed name;
identifiers were resolved by three preceding main-search calls. Unknown social,
personal, saved-user and unverified subsection types remain excluded. The server
returned the TICS list in one response; this was not 562 individual requests.
[Source: shared query/UI code][query].

### Reply and recommendation continuation

V2 reply output now retains sort and two-part continuation metadata and guards
missing/repeated cursors. Review found and fixed incomplete validation of explicit
resume inputs: both lastCommentId and lastLikeCount are now required together;
the like count must be a nonnegative integer. Replies continue through the
existing sanitizer.
The separate v1 post reader keeps its `lastReplyId` contract. The one live v2
sample had `hasNext=false`; multi-page behavior is source-derived and tested
offline, and is not described as a successful live second page.
[Source: community query bundle][community].

Recommendation continuation now follows the deployed condition: a cursor and a
nonempty **raw** feed page are both required. A nonempty raw page whose entries
are filtered from sanitized output can still continue. No raw post/profile
payload was added to output. [Source: community query bundle][community].

The direct recommended-feed and RECENT-lounge checks each followed one returned
cursor successfully. Both second pages still advertised continuation; neither
check established the end of history. Only counts, field names, cursor-presence
flags and overlap counts were retained, without social identities or text.

### Financial statement tabs and ranges

The actual financial body constructors were in lazy chunks, not the small route
wrapper. The runtime mapping resolved their exact public asset names without
executing code. Records use POST
`/api/v2/companies/{productCode}/financial-statement-records`:

| CLI statement / UI | factorCode | Verified selection |
| --- | --- | --- |
| income / 손익계산서 | INC | Q |
| balance / 재무상태표 | BAL | Q |
| cash-flow / 현금흐름표 | CAS | Q and Y |

Each live check returned the requested selected codes and ten table periods.
`--kind records --statement cash-flow --period year` builds the verified body
`{"factorCode":"CAS","period":"Y"}` without custom-body opt-in. Named
selectors reject other endpoint kinds and simultaneous body files, including
body files containing `{}`. One supplied selector defaults the other to
income/quarter; neither selector leaves the original `{}` default unchanged.

Comprehensive is a separate stability-indicator chart. Its default sample and
explicit selection both used
`{"factorCode":"LIABILITY_RATIO","period":"Q","range":3}`. The response
offered LIABILITY_RATIO, CURRENT_RATIO, INTEREST_COVERAGE_RATIO; Q/Y periods;
and ranges 1, 3, 5, 2147483647 (전체). The three statement codes must not be sent
as comprehensive factor codes. Other available options remain response-driven.
[Source: finance lazy chunk][finance].

Current estimate, revenue/net-profit and operating-income callers send
`{period,range}`. Peer comparison additionally sends comparisonStockCodes,
factorCode and ticsId, forcing Q when range is zero. These constructors were
read, but not all combinations were called; the existing custom-body guard
remains for those cases. Dividend years uses `?years={selectedRange.code}`;
default and years=3 each returned 14 histories, with the same four range options.
This is range selection, not pagination. Analyst/dividend chunks reconfirmed
existing endpoint families without a justified new route.

### Route and source interpretation corrections

The `/news` component explicitly replaces its URL with `/feed${asPath}`; it is
an alias of `/feed/news`, not a new news API. The live-event shared layout begins
with an `isMember` gate and redirects nonmembers before rendering event content;
analysis/transcript/ir tab names do not make those APIs public. [News source][news-alias],
[live-event source][live-event].

Bond metadata builders remain GET `/api/v1/bond-infos?guid=...` and
`/api/v1/bond-infos/simple?guids=...` with repeated guids. The page checks
`incorporated`, displays yield/maturity metadata and an app handoff notice.
Its app button sends a notification mutation and was not used. No real bond
GUID was discovered, so no bond-product API result is claimed. [Source: bond page][bonds].

Query-cache keys are not HTTP evidence: the stock main-session cache key
contains `/product/`, but its actual builder remains
`/api/v1/stock-prices/mainsession`; the sales-composition cache key says v2,
but its builder remains `/api/v1/companies/{companyCode}/sales-compositions`.
The actual candle builder defaults useAdjustedRate to true, forwards optional
count/from/session/investMode/currency, and uses the endpoint-specific
securities type. No replacement API was inferred from cache names.
[Sources: layout][layout], [shared app][app].

## Remaining limits

- Full route-template accounting is complete; every stock, news item, post,
  event, parameter combination and authenticated page was not traversed.
- FX chart UI remained a spinner despite successful independent data checks.
- The actual gold index link led to sign-in. Other commodity/futures instances
  were not individually rechecked; no commodity success is claimed.
- Bond-product GUID pages lacked a current public identifier. Visible bond-index
  links do not fill that gap. Cheetah and option public availability remain
  unverified or gated; no trading workflow was attempted.
- Live-event member gating was established in source. No member session or
  event API was used to get around it.
- The live news samples had null keys; v2 reply sample was terminal. Their
  non-null/multi-page contracts have static and offline-test evidence only.
- Screener/feed/lounge browser scrolling did not prove server continuation.
  Separate direct checks verified one continuation each; screener sort/filter
  combinations and all lounge orderings were not exhaustively exercised.
- Annual financial-table rendering was not established after the UI selection;
  the selected annual request body succeeded in the separate direct check.
- No bulk comment/reply harvest, raw social content retention, following feed,
  personal screener mutation, notification action, order or account request ran.
- No new WebSocket delivery test was part of this pass. Existing observations
  retain their own dates in the [WebSocket reference](websocket-api-reference.md).
- Economic-indicator AI analysis was not called without its exact announced
  datetime. Related external links were not all followed.
- Empty/null data, a short page, a lazy wrapper without endpoint strings, and a
  changed bundle hash do not independently establish API removal.

## Validation

The consolidated suite passed **328 tests** with `PYTHONUTF8=1`. Ruff lint and
format checks passed for 26 Python files; compilation and CLI help checks passed
for 21 scripts, and three JSON artifacts validated. Skill quick validation and
installed-package Agent Skills validation passed. The explicit reply-resume fix
was also included in a focused 39-test run. No extra live requests were needed
to run these regressions. These checks validate the repository implementation;
they do not remove the browser/API limitations recorded above.

## Source evidence

The 17 new assets below comprise one manifest and 16 JavaScript files. Manifest,
home and runtime URLs came from the current browser DOM. Page/shared dependencies
came from the exact manifest; the five analytics lazy files came from literal
runtime `t.u` mappings. The mapping uses a dot before these lazy hashes.
All were fetched without redirect/retry and read as text. CSS was not fetched.
SHA-256 values cover response bytes; timestamps are UTC.

| Source | Retrieved UTC | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| [manifest.js](https://www.tossinvest.com/assets/v2/_next/static/FNTsN5Z21hJmsl3Sh71hB/_buildManifest.js) | 2026-09-16T02:48:20.979966+00:00 | 12651 | `7eb20fc8f750c41628579caaf4fd97e73603e25cfe4386385700549d90cc2884` |
| [home.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/index-4411bbc1669cc108.js) | 2026-09-16T02:48:21.909257+00:00 | 57097 | `dfd321838e7cffee883d0f25df6110cf0c948f2b800f486d304a06a9517dd54f` |
| [news.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/news-31b1fb720a1a30e9.js) | 2026-09-16T02:49:40.081546+00:00 | 1157 | `57b2888fc73ce1cae225de5cfc62cc2a10ace8355285b5d95702f42e416e7d04` |
| [bonds.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/bonds/%5Bguid%5D-c04f9581b8094d03.js) | 2026-09-16T02:49:41.009865+00:00 | 15248 | `825abc2faf01c9d391efa26a5b39805704a8e66dd9d3b344464e9d0e87af151c` |
| [live-event-tab.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/live-event/%5Bevent-id%5D/%5Btab%5D-1ebae4733bc18437.js) | 2026-09-16T02:49:41.891284+00:00 | 1063 | `b92ea27aa6dd84a042e846caee0f23141f8795ad154127da56e5fe3391de7bf2` |
| [live-event-shared.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/5871-299120f7185a6d9c.js) | 2026-09-16T02:49:42.908775+00:00 | 27659 | `8126f041fd6b03a886a1c3f9bf70cf061a4536c5bdd6f3e3c981e2b1e40c34aa` |
| [screener.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/screener-8b2802ea9ccbd2f9.js) | 2026-09-16T02:49:43.791681+00:00 | 1260 | `877e9d271de39843f19605693fb0116564b1be4912c4d741b1660ca3999f2a06` |
| [screener-shared.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/9817-35f617234db968e5.js) | 2026-09-16T02:49:44.704026+00:00 | 194510 | `4ff08aa3df3df5fe813aef2161a1fd79f80ce6e896f51c46059dfafccdcbb101` |
| [live-event-layout.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/5577-f2ecb4f8cfc4c5ca.js) | 2026-09-16T02:50:19.638961+00:00 | 63339 | `62ef36b96f05b6d38ce926b43ab2aa61abf088a93e52491b221b9cd50f2cc506` |
| [feed.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/feed/%5B%5B...menu%5D%5D-61cacaaba4bf5818.js) | 2026-09-16T02:50:20.538887+00:00 | 46151 | `0983546e7669c08d4769015f966102b1dd799f207b8bd0a4e938d34781f6815d` |
| [sector.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/sector/%5Btics-id%5D-087427febd52c662.js) | 2026-09-16T02:50:21.508524+00:00 | 38869 | `80c7211a79e6f26d02555084bcf9b490a403fc156a09b51b21336c182f0908e1` |
| [webpack.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/webpack-9fc8b464ab5ca3c5.js) | 2026-09-16T02:56:51.845515+00:00 | 11741 | `0eeee8a185156edd27f241ada79154f23b603fcd5ce8aaaa9fe6e2f8222809ef` |
| [finance.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/7530.738000823fae817d.js) | 2026-09-16T02:57:24.633730+00:00 | 42640 | `2546d63531a78e5187c9559d7a7be980392f38a663cb912f72a040cc2bb061fd` |
| [estimates.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/5282.cb8136d12b63ab89.js) | 2026-09-16T02:57:25.635542+00:00 | 27606 | `ce19df6c824fb88bd506b4c27226d88fe1b253f051bd79ca69d55e961c76b598` |
| [dividends.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/2109.2355e7a646a85cf0.js) | 2026-09-16T02:57:26.662910+00:00 | 4162 | `c1b8350cc10feb14a9f4dcc8151894541931faa7a8b5d837bf3191c0f06144a4` |
| [analyst.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/8532.a217b7c73adbc579.js) | 2026-09-16T02:57:27.708250+00:00 | 15152 | `f50b1825db6fc9b0e92fa3e55a675813aab6f38cd8a450440a0f656edf2d3f52` |
| [peer-comparison.js](https://www.tossinvest.com/assets/v2/_next/static/chunks/3219.3d13d5e64d6e27fd.js) | 2026-09-16T02:57:28.884464+00:00 | 28922 | `76e7a899327d2973a428f15884b997050c8d00ca595a75e5b64a72b4671b3f6f` |

Previously downloaded current stock layout, shared query, community and app
sources were reused. The layout and query hashes are also recorded in the
[transaction audit](transaction-status-audit-2026-09-16.md). Exact source locators
for the main changes are decoded Unicode character positions, not byte offsets:

- Layout ~597000: company news number/key continuation; ~469400: filings.
- Layout ~448050: finance/estimate/dividend/comparison/analyst lazy imports.
- Finance ~6250: record body; ~7966: INC/BAL/CAS labels; ~11674: INC/Q default;
  ~39419: comprehensive factor/period/range.
- Screener shared ~148003: size 50, number 1, returned page + 1.
- Sector ~14192: inverse leverage hide flag; ~18372: news size; ~31163: local slices.
- Live-event layout module 19157: member boundary; module 77494: tab labels.

Temporary metadata and public source files are under
`.codex/public-pages-audit-2026-09-16/` and
`.codex/transaction-status-2026-09-16/`. The durable tables above retain the
reviewable conclusions and request shapes without committing those raw bundles
or public social payloads. Owning contracts are maintained in
[stock APIs](api-stock.md), [market APIs](api-market.md),
[community APIs](api-community.md), and [response notes](response-notes.md).

[manifest]: https://www.tossinvest.com/assets/v2/_next/static/FNTsN5Z21hJmsl3Sh71hB/_buildManifest.js
[layout]: https://www.tossinvest.com/assets/v2/_next/static/chunks/3035-9aab83074d3fb73e.js
[query]: https://www.tossinvest.com/assets/v2/_next/static/chunks/9196-5e2fc6fb74a48df3.js
[community]: https://www.tossinvest.com/assets/v2/_next/static/chunks/1901-e370805f386c219f.js
[app]: https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/_app-8afa85118f1bdd97.js
[finance]: https://www.tossinvest.com/assets/v2/_next/static/chunks/7530.738000823fae817d.js
[news-alias]: https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/news-31b1fb720a1a30e9.js
[live-event]: https://www.tossinvest.com/assets/v2/_next/static/chunks/5577-f2ecb4f8cfc4c5ca.js
[bonds]: https://www.tossinvest.com/assets/v2/_next/static/chunks/pages/bonds/%5Bguid%5D-c04f9581b8094d03.js
