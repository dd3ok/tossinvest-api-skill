# Capture Workflow

Use this workflow when adding or verifying TossInvest web API endpoints.

1. Open the target `tossinvest.com` page in a real browser, Playwright, or CDP-connected browser.
2. Record network requests after initial page load.
3. Scroll the page to trigger lazy-loaded sections.
4. Filter requests:
   - Include `wts-info-api.tossinvest.com`.
   - Include selected `wts-api.tossinvest.com` bootstrapping calls when needed for context.
   - Include selected `wts-cert-api.tossinvest.com` only when the endpoint is visible page metadata.
   - Exclude logs, Sentry, CDN refresh checks, static assets, and images.
5. Normalize endpoint paths:
   - Replace stock/product codes with `{productCode}`.
   - Replace company codes with `{companyCode}`.
   - Replace long comma-separated code lists with `{codes}`.
   - Replace dynamic dates with `{YYYY-MM-DD}`.
   - Replace tab ids or deployment ids with placeholders.
6. Record method, path, query params, source page, observed purpose, and response top-level shape.
7. Store only sanitized notes. Do not store raw HAR files, cookies, tokens, storage state, account numbers, or personally identifying financial data.

For POST endpoints, capture whether the browser sends a body. If a manual check is needed, try `Content-Type: application/json` with `{}` only for read-only endpoints.

