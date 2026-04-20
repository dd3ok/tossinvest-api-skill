# Safety Rules

- Do not use, install, or run `tossctl`.
- Do not use, install, or run `tossinvest-cli`.
- Do not call order placement, cancellation, amendment, account transfer, certificate mutation, login mutation, or other account-impacting endpoints.
- Do not store cookies, authorization headers, account numbers, session files, storage-state files, raw HAR captures, or personal financial data.
- Prefer public read-only stock information endpoints on `wts-info-api.tossinvest.com`.
- Treat `wts-cert-api.tossinvest.com` as sensitive unless the endpoint is clearly public page metadata.
- Re-verify endpoints because TossInvest internal APIs are undocumented and may change without notice.
- Keep output clear that the API is unofficial and not supported by TossInvest as a public developer API.

