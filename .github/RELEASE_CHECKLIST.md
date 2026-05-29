# Release Checklist

Use this checklist before tagging a public release or asking others to install the
skill from GitHub.

## Skill Surface

- `SKILL.md` frontmatter has the canonical `name: tossinvest-web-api`.
- `SKILL.md` description starts with `Use` and describes trigger conditions,
  not implementation steps.
- `agents/openai.yaml` has localized display metadata consistent with `SKILL.md`
  and the core lookup workflow.
- Public prompt examples use `$tossinvest-web-api`, not aliases.

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

## Verification

Run these commands from the repository root:

```bash
python3 -m unittest discover -s tests -v
ruff format --check .
ruff check .
for f in scripts/*.py; do python3 -m py_compile "$f" || exit 1; done
for f in scripts/*.py; do python3 "$f" --help >/dev/null || exit 1; done
for f in examples/filters/*.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
```

Run the skill layout smoke test:

```bash
skill_dir="$(mktemp -d)/tossinvest-web-api"
mkdir -p "$skill_dir"
cp -R SKILL.md README.md LICENSE SECURITY.md agents examples references scripts "$skill_dir"/
test -f "$skill_dir/SKILL.md"
test -f "$skill_dir/agents/openai.yaml"
test -f "$skill_dir/references/api-catalog.md"
python3 "$skill_dir/scripts/stock_summary.py" --help >/dev/null
```

## Documentation

- README first screen explains what the skill does, what it does not do, and the
  canonical trigger.
- `references/api-catalog.md` status labels remain conservative:
  `script-backed`, `observed`, `needs-recheck`, or `excluded`.
- `references/eval-prompts.md` covers lookup, discovery, and refusal scenarios.
- `SECURITY.md` points sensitive reports to private vulnerability reporting.

## GitHub

- CI is green on the target branch.
- No generated caches, virtualenvs, build outputs, credentials, HAR files, or
  local result files are staged.
- Release notes mention that TossInvest web APIs are unofficial, undocumented,
  and subject to change.
