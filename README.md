# Fundraising Dashboard Portfolio — Static Site

A build of a nonprofit fundraising dashboard suite: ten
self-contained HTML dashboards plus a landing page.

Deployed at:  https://ntmbayfield.github.io/portfolio-dashboard-site/

---

## Project Overview

This site duplicates a recent project I completed to produce a set of
executive-level reporting dashboards built on top of an extensive cleanup of the last three fiscal years of
fundraising data.

What's reproduced here, and what isn't:

- **All donor and gift data displayed is dummy data.** Every name, constituent
  ID, gift amount, date, campaign, appeal, fund, and revenue figure rendered on
  these dashboards was randomly generated for this build. No real constituent
  records or organizational financials appear anywhere on the site.
- **The dashboard visualizations are the same ones used in the production
  dashboards** — same charts, same tables, same metrics, same interactions. Only
  the data behind them was swapped.
- **The process used to preserve legacy data and store the cleaned gift data is
  real.** The parallel normalized-attribute approach, the comment field
  recording the basis for each attribution, and the flagging of judgment-based
  calls are all as implemented.
- **The automation is real.** The scheduled pull from Raiser's Edge, the
  triggered build of each new weekly and monthly gift report dashboard, and the
  automatic update to `index.html` adding a card for the new report all reflect
  the processes actually put in place as part of this project.
- **The figures cited in this overview** — records reviewed, revenue
  reattributed, records reclassified and backfilled — describe the real
  engagement.

In short: the data is invented, the methodology and the machinery are not.

### The problem

Fundraising revenue was reported out of Raiser's Edge NXT, but the campaign,
appeal, and fund values behind those numbers had accumulated years of
inconsistent attribution. Gifts of the same type were coded to different
campaigns across fiscal years, some records were missing campaign, appeal, or
fund entirely, and some coding actively misrepresented the gift — an event
ticket purchase credited against a monthly recurring giving commitment, for
example.

The practical consequence: any year-over-year revenue comparison was measuring
coding drift as much as fundraising performance. Leadership couldn't tell
whether a campaign had grown or whether its gifts had simply been categorized
differently that year — which made it impossible to answer the questions they
actually needed answered about budget, program return, and staffing.

### Scope

Two deliverables, in sequence:

1. **A governed campaign structure**, approved across the organization and
   adopted at the start of FY27 — the campaign list, a written definition of
   each campaign, the attribution rules governing which campaign a gift belongs
   to, and a hierarchy resolving cases where a gift could reasonably fall into
   more than one.
2. **Three fiscal years of normalized historical data** reconciled against that
   structure, and a dashboard suite built on it for the CEO and Board of
   Directors — annual fundraising performance, year-over-year campaign revenue,
   progress to goal, and weekly gift reporting.

### Process

**Establishing the rules first.** The cleanup couldn't begin until there was
agreement on what "correct" meant. I secured sign-off on the campaign
definitions and gift attribution rules from the CEO, the Director of
Development, the Gift Processor, and the Accounting and Finance team — the four
parties whose work depends on those definitions holding: strategy, frontline
fundraising, data entry, and financial reporting. Without that alignment,
normalization would have been one person's opinion applied retroactively to
three years of records, and it would have drifted again within a year.

The most consequential rule was how Major Gifts is defined. Under the FY27
rules, a gift is not attributed to Major Gifts because of its dollar amount. It
is attributed to Major Gifts when it is the product of a development officer's
work — a submitted proposal to fund a capital project, a verbal ask for
scholarship support, a gift made during or following a campus tour led by the
officer — and the CRM should show prior engagement with that constituent to
support the attribution. That single change reframes Major Gifts from a size
bucket into a measure of relationship-driven fundraising, which is what makes
officer performance and portfolio return measurable at all.

**Establishing a control dataset.** I exported every gift recorded across the
last five fiscal years from Raiser's Edge — approximately 60,000 rows. This
untouched export served as the baseline for control checks, so every downstream
aggregate could be verified against it to confirm that normalization moved gifts
between categories without adding, dropping, or altering revenue.

**Segmenting by fiscal year.** Each fiscal year was split into its own working
file. Attribution practice had changed over time, so reviewing year by year made
year-specific patterns legible rather than averaging them into noise.

**Flagging gaps.** Within each file, I marked every record missing campaign,
appeal, or fund data in yellow, producing an explicit, visible backfill queue
rather than a set of silent nulls.

**Reverse-engineering the rules in force.** For each fiscal year, I worked
through the data to identify the patterns revealing how gifts had actually been
attributed that year — what had driven a gift to Major Gifts versus Annual
Giving versus Events in practice, as distinct from what policy said.

**Documenting findings per year.** I wrote up my assessment of the attribution
rules operating in each fiscal year, along with every inconsistency and
data-integrity issue surfaced during review. This became the audit trail
explaining why any given gift was reclassified.

**Normalizing without overwriting.** Rather than editing values in place, I
created three parallel custom attributes — *Normalized Campaign*, *Normalized
Appeal*, and *Normalized Fund*. Each holds either the original value where
attribution was already correct, or the value the gift belongs to under the FY27
definitions and attribution rules. This carried good data forward, backfilled
what was missing, and corrected misattribution, all while leaving the original
legacy values intact — which kept the reclassification fully reversible and
auditable, and made it possible to quantify the effect of the cleanup itself.
The "before and after" view on the Year-over-Year Fundraising dashboard is built
directly on that pairing.

**Recording the reasoning, gift by gift.** Each normalized attribute carries a
comment field documenting the basis for its value: the appeal code, fund
designation, gift date and type, batch context, or documented officer engagement
that supported the attribution. Where the evidence didn't resolve the question,
the record was marked *"unresolved — attribution based on best judgement"*
rather than silently absorbed into the dataset.

**Making the uncertainty a decision, not an assumption.** Classifying every
record — including the unresolved ones — was a deliberate choice made with
leadership, who wanted a complete dataset to plan from rather than a partial one
with holes. That came with an agreed tolerance: because a subset of records
rests on judgment calls, fiscal-year fundraising figures may vary by ±2%.
Surfacing that margin up front meant leadership knew the precision of the
numbers they were making decisions on, and the flagged records remain
identifiable for future review.

### Automating the reporting cycle

The cleanup fixed the historical data. The reporting pipeline was built so the
same problem wouldn't recur — and so that reporting stopped being reactive.

Before FY27, gift reports were pulled on request. That meant last-minute asks
landing on the database manager's desk, inconsistent date ranges depending on
who asked and when, and no guarantee that two reports pulled a week apart used
the same logic. Reporting was a service request rather than a standing
deliverable.

Starting in FY27, weekly and monthly gift reporting runs on a schedule with no
manual step:

1. **A scheduled Power Automate flow** runs once a week, queries the gift data
   for the reporting period, and writes the resulting file to a designated
   SharePoint folder.
2. **The arrival of that file triggers a second automation.** It reads the new
   week's gift records, builds a complete weekly gift report dashboard from
   them, and adds a card for that report to the FY27 Fundraising section of the
   site index — so the new dashboard is published and linked without anyone
   touching the HTML.
3. **Fiscal-year-to-date totals recalculate on each run**, concatenating the
   current week's gift rows with every prior week in the fiscal year and
   re-aggregating by campaign, appeal, and fund. There is no running database to
   drift out of sync; each build is derived fresh from the source files.

The design goal was schedule over request. Leadership gets a consistent report
on a predictable cadence, built the same way every week against the same
attribution rules, rather than a bespoke pull whose comparability to the last
one depends on who ran it. It also removed a recurring interrupt from the
database manager's week — the reports that used to be urgent asks now simply
exist by Monday.

Because the second automation keys off a file appearing in the SharePoint folder
rather than off the query itself, the pipeline degrades gracefully. A documented
manual export procedure covers the two cases the schedule doesn't: a failed or
skipped run, and off-cycle requests for a non-standard date range. Following it
produces a file identical in shape and naming to the automated output, dropped
in the same folder, which triggers the same downstream build. The manual path is
a fallback into the same pipeline, not a parallel one — so a report produced by
hand is indistinguishable from a scheduled one, and the SOP is written to be
executable by someone other than its author. That procedure is documented in
full on the [Dashboard Reference](dashboards/dashboard-reference.html) page.

The weekly dashboards on this site are the output of that pipeline, and the FYTD
sections demonstrate the cumulative rollup behavior.

### Results

- **~60,000 gift records reviewed** across five fiscal years, with three years
  normalized against the new structure.
- **More than $2 million in revenue reattributed** to a different campaign —
  roughly 17% of the $11.5 million in combined revenue across the three-year
  period.
- **Over 6,000 records reclassified**, with original values preserved.
- **Approximately 3,000 additional records** with missing campaign, appeal, or
  fund data identified and backfilled.
- **Three normalized attributes** (campaign, appeal, fund) each carrying a
  documented rationale, with judgment-based attributions explicitly flagged.
- **A documented campaign structure, definitions, and attribution hierarchy**
  approved by the CEO, Director of Development, Gift Processor, and Accounting
  and Finance, adopted organization-wide at the start of FY27.
- **Weekly and monthly reporting automated** from the start of FY27, with a
  documented manual fallback into the same pipeline.

### Impact

Nearly a fifth of three-year revenue sat in the wrong campaign. That is the
difference between a strategy conversation and a guess — and it explains why
year-over-year reporting had stopped being useful.

The cleanup gave leadership numbers they could act on rather than numbers they
had to caveat. With three years on a consistent basis, the reclassification
effect shown explicitly rather than absorbed silently, and a stated ±2% margin,
the CEO and Board could distinguish real year-over-year movement from recoding
artifacts — and use that to make decisions about budget allocation, return on
annual giving investment, and team staffing: how many people each fundraising
function needs, and in what capacity.

Redefining Major Gifts by officer effort rather than gift size was central to
that. It made the return on a development officer's portfolio measurable for the
first time, which is a staffing question, not a data question.

---

## Site structure

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

## How the sample data was generated

Every figure rendered on every page comes from a fixed random seed, generated
for a fictional organization, **Northgate Youth Foundation**. Specifically:

- **Donor names** are random first/last-name combinations from a synthetic pool.
  Foundation and estate donors are invented names.
- **Constituent IDs** are random six-digit integers with no relationship to any
  real record.
- **Gift amounts, dates, campaigns, appeals, and funds** are generated.
- **Revenue, goal, and donor-count figures** across all three fiscal years are
  invented, including every number quoted in the narrative commentary on the
  dashboards themselves.
- **Development officer names** are invented.
- **CRM record links** (donor profile / gift record deep links) have been
  removed entirely — in the production build these pointed into a live Raiser's
  Edge NXT tenant. Donor names and gift amounts now render as plain text.
- **The password gate** has been removed, since there is nothing here to gate.

### Internal consistency

The synthetic data is generated as one connected dataset rather than
page-by-page, so the dashboards still reconcile against each other the way the
production ones do:

- Each weekly dashboard's FYTD section is a true cumulative rollup of that week
  plus every prior week in the fiscal year.
- The July Monthly Giving dashboard's 2026 column is computed from the five
  weekly gift files covering the month.
- FY26 "Raised" figures on the Progress to Goal dashboard match FY26
  revised-classification revenue on the Year-over-Year dashboard.
- Donor-movement counts reconcile: retained + new + recaptured equals unique
  donors, and LYBUNT ∪ Lost equals SYBUNT, with rosters sliced from the same
  donor universe.


---

## Regenerating or rebranding the data

The `_build/` folder (not deployed) contains the generator:

| File | Purpose |
|---|---|
| `fakedata.py` | Name pools, fund/appeal/campaign vocabulary, fictional org name |
| `gen_weekly.py` | Generates the weekly gift-level data and FYTD rollups |
| `build.py` | Rewrites branding, swaps in every data payload, writes `site/` |
| `index_template.html` | The landing page source |
| `README_source.md` | Source for the deployed `README.md` |
| `smoke.js` | Headless jsdom check that every page renders without JS errors |

To change the fictional organization name, edit `ORG` in `fakedata.py` and the
`TERMS` list in `build.py`, then re-run `python3 build.py`. The scripts read the
originals from `/mnt/user-data/uploads`; point `SRC` at wherever you keep them.
Changing `SEED` in `fakedata.py` reshuffles every donor, gift, and roster.
