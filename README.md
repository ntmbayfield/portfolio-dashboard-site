# Fundraising Dashboard Portfolio — Static Site

A de-identified portfolio build of a nonprofit fundraising dashboard suite:
ten self-contained HTML dashboards plus a landing page. No build step, no
server, no database — drop the folder on GitHub Pages, Netlify, or any static
host and it works.

Available online at:  https://ntmbayfield.github.io/portfolio-dashboard-site/

```
site/
├── index.html                              ← portfolio landing page
├── README.md
└── dashboards/
    ├── fundraising-performance-fy26.html   (Fundraising Overview, FY24–FY26)
    ├── campaign-revenue.html               (Year-over-Year Fundraising)
    ├── fy26-progress-to-goal.html          (FY26 Progress to Goal)
    ├── july-giving-yoy.html                (July Giving: 2026 vs. 2025)
    ├── weekly-giving-jul1-5.html           (Weekly Giving: July 1–5)
    ├── weekly-giving-jul6-12.html          (Weekly Giving: July 6–12)
    ├── weekly-giving-jul13-19.html         (Weekly Giving: July 13–19)
    ├── weekly-giving-jul20-26.html         (Weekly Giving: July 20–26)
    ├── weekly-giving-jul27-aug2.html       (Weekly Giving: July 27–Aug 2)
    ├── officer-performance.html            (Development Officer Performance — prototype)
    └── dashboard-reference.html            (metric definitions, schema, SOP)
```

---

## All data here is fictional

This is a portfolio build. Every figure rendered on every page was generated
from a fixed random seed for a fictional organization, **Northgate Youth
Foundation**. Specifically:

- **Donor names** are random first/last-name combinations from a synthetic pool.
  Foundation and estate donors are invented names.
- **Constituent IDs** are random six-digit integers with no relationship to any
  real record.
- **Gift amounts, dates, campaigns, appeals, and funds** are generated.
- **Revenue, goal, and donor-count figures** across all three fiscal years are
  invented, including every number quoted in the narrative commentary.
- **Development officer names** are invented.
- **CRM record links** (donor profile / gift record deep links) have been
  removed entirely — in the production build these pointed into a live Raiser's
  Edge NXT tenant. Donor names and gift amounts now render as plain text.
- **The password gate** has been removed, since there is nothing here to gate.

What is *not* fictional is the work: the dashboard design, the metric
definitions, the donor-movement logic, the calculation methods, and the
documentation. That is the point of the portfolio.

### Internal consistency

The synthetic data is generated as one connected dataset rather than
page-by-page, so the dashboards still reconcile against each other the way the
originals did:

- Each weekly dashboard's FYTD section is a true cumulative rollup of that week
  plus every prior week in the fiscal year.
- The July year-over-year dashboard's 2026 column is computed from the five
  weekly gift files covering the month.
- FY26 "Raised" figures on the Progress to Goal dashboard match FY26
  revised-classification revenue on the Year-over-Year dashboard.
- Donor-movement counts reconcile: retained + new + recaptured equals unique
  donors, and LYBUNT ∪ Lost equals SYBUNT, with rosters sliced from the same
  donor universe.

---

## Deploying

It's a static site, so any of these work:

- **GitHub Pages** — push the contents of `site/` to a repo, then enable Pages
  on the branch root. Links are all relative, so it works from a project
  subpath (`username.github.io/repo-name/`) without changes.
- **Netlify / Cloudflare Pages** — drag the folder into the dashboard.
- **Local** — open `index.html` directly in a browser.

The only external requests are Google Fonts (Fraunces, Inter, IBM Plex Mono).
Chart.js is bundled inline in each dashboard, so the charts render offline.

---

## Regenerating or rebranding the data

The `_build/` folder (not deployed) contains the generator:

| File | Purpose |
|---|---|
| `fakedata.py` | Name pools, fund/appeal/campaign vocabulary, fictional org name |
| `gen_weekly.py` | Generates the weekly gift-level data and FYTD rollups |
| `build.py` | Rewrites branding, swaps in every data payload, writes `site/` |
| `index_template.html` | The landing page source |
| `smoke.js` | Headless jsdom check that every page renders without JS errors |

To change the fictional organization name, edit `ORG` in `fakedata.py` and the
`TERMS` list in `build.py`, then re-run `python3 build.py`. The scripts read the
originals from `/mnt/user-data/uploads`; point `SRC` at wherever you keep them.
Changing `SEED` in `fakedata.py` reshuffles every donor, gift, and roster.
