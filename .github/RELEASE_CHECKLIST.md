# Release Checklist

Use this checklist before tagging a public release or asking others to install the
skill from GitHub.

## Skill Surface

- `SKILL.md` frontmatter has the canonical `name: tossinvest-web-api`.
- `SKILL.md` description starts with `Use` and describes trigger conditions,
  not implementation steps.
- `agents/openai.yaml` has localized display metadata consistent with `SKILL.md`
  and the core lookup workflow.
- Antigravity CLI installation examples place the skill at
  `.agents/skills/tossinvest-web-api/SKILL.md`.
- Public prompt examples use natural TossInvest/토스증권 language and do not
  depend on `$...` skill selectors or aliases.

## Safety

- No script accepts cookies, authorization headers, account identifiers, raw HAR
  files, or browser storage state.
- `scripts/tossinvest_api.py` blocks unapproved hosts, account/order/login
  markers, sensitive query/body keys, encoded path separators, backslashes, and
  dot segments.
- `wts-cert-api` endpoints use an exact allowlist for public-looking metadata
  and are documented with sensitive-host caution.
- Order, account, login, certificate mutation, and orderable-amount endpoints are
  excluded from scripts and cataloged only as out-of-scope notes when needed.
- Ephemeral WebSocket guest metadata, complete STOMP `CONNECT` or `MESSAGE`
  frames, raw frame dumps, and guest-bootstrap responses are absent from the
  release contents and verification logs.
- Any standalone public read-only WebSocket client acquires anonymous guest
  metadata at runtime, keeps it memory-only, redacts logs, bounds reconnects,
  and never reaches an order/account destination.
- The standalone WebSocket client keeps its one-process lock, canonical
  destination allowlist, 20-subscription/400-ms pacing, 256-KiB frame cap,
  1-MiB inbound message cap, bounded JSONL flushes, and graceful disconnect
  receipt timeout.
- `requirements-websocket.txt` pins the optional binary package exactly and
  verifies its published SHA-256 hash; dependency audit results are reviewed.
- Any top100 stream uses one shared connection, at most 100 deduplicated product
  destinations for one view, and the observed 10-second HTTP ranking refresh.

## Verification

Run these commands from the repository root with Python 3.12 (`python3` below).
Install the locked optional WebSocket dependency so the full suite exercises its
library integration test:

```bash
python3 -m pip install -r requirements-websocket.txt
python3 -m unittest discover -s tests -v
ruff format --check .
ruff check .
for f in scripts/*.py; do python3 -m py_compile "$f" || exit 1; done
for f in scripts/*.py; do python3 "$f" --help >/dev/null || exit 1; done
for f in examples/filters/*.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
dependency_dir="$(mktemp -d)"
python3 -m pip download --dest "$dependency_dir" -r requirements-websocket.txt
```

Run the skill layout smoke test:

```bash
workspace="$(mktemp -d)"
skill_dir="$workspace/.agents/skills/tossinvest-web-api"
mkdir -p "$skill_dir"
cp -R SKILL.md README.md LICENSE SECURITY.md agents examples references scripts "$skill_dir"/
cp requirements-websocket.txt "$skill_dir"/
test -f "$skill_dir/SKILL.md"
test -f "$skill_dir/agents/openai.yaml"
test -f "$skill_dir/references/api-catalog.md"
test -f "$skill_dir/references/websocket-api-reference.md"
test -f "$skill_dir/requirements-websocket.txt"
test -f "$skill_dir/scripts/websocket_prices.py"
python3 "$skill_dir/scripts/stock_summary.py" --help >/dev/null
python3 "$skill_dir/scripts/websocket_prices.py" --help >/dev/null
```

## Documentation

- README first screen explains what the skill does, what it does not do, and the
  canonical trigger.
- README defines the stable repository interface covered by semantic versioning
  and excludes unofficial upstream endpoints and response fields from that
  compatibility promise.
- README and release notes identify Python 3.12 as the only supported runtime;
  the release adopting this policy records the end of Python 3.10 support.
- `references/api-catalog.md` status labels remain conservative; keep its
  Verification Status table authoritative (`script-backed`, `observed`,
  `observed-drift`, `needs-recheck`, `excluded`, `public-social-sensitive`).
- `references/websocket-api-reference.md` remains browser-observed,
  unofficial, and unstable; its evidence labels distinguish protocol standards
  from TossInvest-specific observations and state whether a client is bundled.
- `references/eval-prompts.md` covers lookup, discovery, and refusal scenarios.
- `SECURITY.md` points sensitive reports to private vulnerability reporting.

## GitHub

- CI is green on the target branch.
- No generated caches, virtualenvs, build outputs, credentials, HAR files, or
  local result files are staged.
- The release tag and GitHub release describe the skill contents for local
  `.agents/skills/tossinvest-web-api` installation and mention the Antigravity
  layout.
- Release notes mention that TossInvest web APIs are unofficial, undocumented,
  and subject to change.
- For `v1.0.0` and later, release notes distinguish the stable repository
  interface from the unstable upstream TossInvest web interfaces.
- Release notes describe the WebSocket interface as browser-observed and
  unofficial, and repeat the memory-only guest-metadata, bounded subscription,
  no-order, and no-account requirements.
