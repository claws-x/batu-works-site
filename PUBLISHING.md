# Automated BATU WORKS public publishing / 自动官网发布

This public repository is the only source for the public GitHub Pages website. The private company repository must not be made public.

## Pipeline
1. The BATU WORKS AI operator detects a **verified** company change, feature update, product release, or company news from authoritative project evidence.
2. The operator creates an issue in **this public repository** as the repository owner account (currently `claws-x`) with a title starting `[publish] `. No separate manual label is needed.
3. The issue body must consist of **exactly one** JSON fenced code block, using the schema below. This is the machine-readable publication request.
4. GitHub Actions checks the issue's `author_association == OWNER`, validates fields and HTTPS evidence URL, updates `updates.json`, commits it to `main`, and GitHub Pages redeploys the site automatically.
5. The homepage reads `updates.json` on page load and displays the latest updates. No manual website edits are required.

```json
{
  "kind": "product",
  "title": "Element Atlas reaches public beta",
  "summary": "Public beta availability is verified with a live product link. This is an example only; do not publish until verified.",
  "url": "https://github.com/claws-x/batu-works-site",
  "approved": true
}
```

Valid `kind`: `company`, `product`, `release`, `news`. For a `release`, URL must point to a public app store listing or GitHub release. The approval field means the autonomous publisher has checked **public release authorization and evidence**; it is not permission to publish internal or confidential content.

**Safety:** Never publish source code, credentials, internal client names, unannounced OEM projects, private financials, personal data, or unreleased features. Do not claim an app has launched without a verified public listing. Issues authored by non-owners are ignored. GitHub issue text is parsed as data, not executed. All homepage updates are inserted via `textContent` (no HTML injection).

**Current limitations:** The workflow is installed but execution and GitHub Pages redeployment must be confirmed in GitHub Actions. A verified external event still needs an AI operator to submit an issue; this is not a magical connection to the private Mac filesystem. The `workflow_dispatch` event does not publish anything by itself. GitHub Actions may need repository Actions permissions to allow writing `contents`. If GitHub rejects writes, configure Settings → Actions → General → Workflow permissions → Read and write permissions.

## Automatic triggers for agents / AI 员工发布契约
- On **verified company change**: owner AI account creates an issue with `kind: company`.
- On **verified product upgrade**: issue with `kind: product`, evidence link.
- On **public app launch**: issue with `kind: release`, public store/release link.
- On **approved company news**: issue with `kind: news`, public authoritative URL.
- Every issue is deduplicated by issue number; edits update the same item, and feed is capped at 60 entries.

**Important:** Publishing the issue is the integration step the AI operator must implement; do not assume it is already wired to the private company agent.
