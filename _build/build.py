"""Build the de-identified portfolio version of the dashboard site.

Reads the originals from /mnt/user-data/uploads, swaps every piece of employer
branding and every real data payload for synthetic equivalents, and writes a
deployable static site to ./site.
"""
import datetime as dt
import json
import os
import re
import shutil

from fakedata import rng, name_pool, ORG
import gen_weekly

SRC = "/mnt/user-data/uploads"
OUT = "site"

# ---------------------------------------------------------------- branding ---
# Longest first so the substrings don't get clipped early.
TERMS = [
    ("Hanna Academy Classroom Renovation", "Northgate Academy Classroom Renovation"),
    ("Hanna Academy Program Fund", "Northgate Academy Program Fund"),
    ("Hanna Academy Crab Feed", "Northgate Academy Benefit Dinner"),
    ("Hanna Academy Donations", "Northgate Academy Fund"),
    ("Hanna Priority Needs Funds", "Priority Needs Fund"),
    ("Hanna Recreation Program Funds", "Recreation Program Fund"),
    ("Hanna Center Dashboards", "Fundraising Analytics Portfolio"),
    ("Hanna Center", ORG),
    ("Hanna Academy", "Northgate Academy"),
    ("Mental Health Hub Fund", "Mental Health Services Fund"),
    ("Guardian Angel Society Gift", "Guardian Circle Leadership Gift"),
    ("Guardian Angel", "Guardian Circle"),
    # Staff names that appear as fundraisers / officers.
    ("Madison Watkins", "Alexis Moreau"),
    ("Dennis Crandall", "Grant Whitfield"),
    ("Heather Hall", "Renee Castellano"),
    ("Marissa LaBrecque", "Priya Raghavan"),
    ("Mitch Massey", "Trevor Nakashima"),
    ("Susan Anderson", "Dana Whitlock"),
]

FILES = [
    "campaign-revenue.html", "dashboard-reference.html",
    "fundraising-performance-fy26.html", "fy26-progress-to-goal.html",
    "july-giving-yoy.html", "officer-performance.html",
    "weekly-giving-jul1-5.html", "weekly-giving-jul6-12.html",
    "weekly-giving-jul13-19.html", "weekly-giving-jul20-26.html",
    "weekly-giving-jul27-aug2.html",
]


def apply_terms(s):
    for a, b in TERMS:
        s = s.replace(a, b)
    return s


def strip_gate(s):
    """Remove the password gate include; the portfolio version is public."""
    s = s.replace('<script src="../assets/gate.js"></script>\n', "")
    s = s.replace("<script>requireAuth('../index.html');</script>\n", "")
    s = s.replace('<meta name="robots" content="noindex, nofollow">\n', "")
    return s


def replace_json(s, block_id, payload):
    pat = re.compile(
        r'(<script id="%s" type="application/json">).*?(</script>)' % re.escape(block_id),
        re.S)
    new = json.dumps(payload, separators=(",", ":"))
    out, n = pat.subn(lambda m: m.group(1) + new + m.group(2), s, count=1)
    assert n == 1, f"payload {block_id} not replaced"
    return out


SAMPLE_BANNER = """<div style="max-width:1180px;margin:0 auto 22px;padding:11px 16px;border:1px solid #E3B8B8;background:#F9ECEC;border-radius:9px;font-family:'Inter',sans-serif;font-size:12.5px;line-height:1.5;color:#7A2E2E;">
<strong>Portfolio sample.</strong> Every donor name, gift, fund and figure on this page is randomly generated for demonstration. No real constituent or organizational data is shown.
</div>
"""


def add_banner(s):
    """Drop a sample-data notice just inside the first content wrapper."""
    m = re.search(r"</header>", s)
    if not m:
        return s
    idx = m.end()
    return s[:idx] + "\n\n" + SAMPLE_BANNER + s[idx:]


# --------------------------------------------------------- yearly campaign ---
AFTER = {
    "FY24": {"Direct Marketing": 481250, "Event Income": 312400, "Northgate Academy": 0,
             "Major Gifts": 398600, "Other": 561900, "Planned Giving": 1040000},
    "FY25": {"Direct Marketing": 212800, "Event Income": 468300, "Northgate Academy": 15200,
             "Major Gifts": 762400, "Other": 61500, "Planned Giving": 1845000},
    "FY26": {"Direct Marketing": 463900, "Event Income": 481700, "Northgate Academy": 2150,
             "Major Gifts": 941300, "Other": 47800, "Planned Giving": 348000},
}
BEFORE = {
    "FY24": {"Direct Marketing": 712400, "Event Income": 288100, "Northgate Academy": 0,
             "Major Gifts": 260500, "Other": 541900, "Planned Giving": 991250},
    "FY25": {"Direct Marketing": 1180600, "Event Income": 425800, "Northgate Academy": 48300,
             "Major Gifts": 0, "Other": 20000, "Planned Giving": 1690500},
    "FY26": {"Direct Marketing": 289400, "Event Income": 477900, "Northgate Academy": 6200,
             "Major Gifts": 1115550, "Other": 48000, "Planned Giving": 347800},
}
FY_TOTAL = {fy: sum(v.values()) for fy, v in AFTER.items()}


def js_year_block(name, table):
    lines = [f"const {name} = {{"]
    for fy in ("FY24", "FY25", "FY26"):
        parts = ", ".join(f"'{c}':{table[fy][c]}" for c in
                          ["Direct Marketing", "Event Income", "Northgate Academy",
                           "Major Gifts", "Other", "Planned Giving"])
        lines.append(f"  {fy}:{{ {parts} }},")
    lines[-1] = lines[-1].rstrip(",")
    lines.append("};")
    return "\n".join(lines)


def build_campaign_revenue(s):
    s = re.sub(r"const BEFORE = \{.*?\n\};", js_year_block("BEFORE", BEFORE), s, flags=re.S)
    s = re.sub(r"const AFTER = \{.*?\n\};", js_year_block("AFTER", AFTER), s, flags=re.S)
    s = s.replace(
        "// Source: Reclassification_Impact_Data_for_Dashboard.xlsx (tabs FY23-24 / FY24-25 / FY25-26, \"Revenue - Original Classification\").",
        "// Portfolio sample: synthetic figures, not real organizational revenue.")
    s = s.replace(
        "// Source: Reclassification_Impact_Data_for_Dashboard.xlsx (tabs FY23-24 / FY24-25 / FY25-26, \"Revenue - Revised Classification\").",
        "// Portfolio sample: synthetic figures, not real organizational revenue.")
    return s


# ------------------------------------------------------------ progress/goal ---
GOALS = [
    {"name": "Major Gifts", "raised": AFTER["FY26"]["Major Gifts"], "goal": 880000},
    {"name": "Event Income", "raised": AFTER["FY26"]["Event Income"], "goal": 540000},
    {"name": "Direct Marketing", "raised": AFTER["FY26"]["Direct Marketing"], "goal": 600000},
    {"name": "Planned Giving", "raised": AFTER["FY26"]["Planned Giving"], "goal": 1600000,
     "isBequest": True},
]
OTHER_REVENUE = AFTER["FY26"]["Other"] + AFTER["FY26"]["Northgate Academy"]

PROSE = [
    ("Total revenue fell from $3.98M in FY25 to $2.90M in FY26 — a 27% drop.",
     "Total revenue fell from $3.37M in FY25 to $2.28M in FY26 — a 32% drop."),
    ("Planned Giving swung from $1.96M in FY25 down to $372K in FY26 — a $1.6M drop, -81%",
     "Planned Giving swung from $1.85M in FY25 down to $348K in FY26 — a $1.5M drop, -81%"),
    ("grew 25% this year, from $2.02M to $2.53M",
     "grew 27% this year, from $1.52M to $1.94M"),
    ("Revenue grew from $548K to $1.04M to $1.28M over three years — +133% cumulative.",
     "Revenue grew from $399K to $762K to $941K over three years — +136% cumulative."),
    ("Revenue moved from $422K to $639K to $650K — steady growth of +54% cumulative",
     "Revenue moved from $312K to $468K to $482K — steady growth of +54% cumulative"),
    ("It dropped 56% in FY25, then rebounded 127% in FY26",
     "It dropped 56% in FY25, then rebounded 118% in FY26"),
    ("show a drop from $776K to $80K to $54K over three years",
     "show a drop from $562K to $62K to $48K over three years"),
    ("Note: Other ($53,500) and Northgate Academy ($2,360) included in total raised but have no goal amounts.",
     "Note: Other ($47,800) and Northgate Academy ($2,150) included in total raised but have no goal amounts."),
    ("included in total raised (Other: $53,500 + Northgate Academy: $2,360)",
     "included in total raised (Other: $47,800 + Northgate Academy: $2,150)"),
]


def build_progress(s):
    s = replace_json(s, "dashboard-data",
                     {"allCampaigns": GOALS, "otherRevenue": OTHER_REVENUE})
    for a, b in PROSE:
        assert a in s, f"prose not found: {a[:50]}"
        s = s.replace(a, b)
    return s


# ------------------------------------------------------------- FY26 overview ---
QUARTERLY = {
    "FY24": {"Q1": 512300, "Q2": 986400, "Q3": 641250, "Q4": 654200},
    "FY25": {"Q1": 604800, "Q2": 1412700, "Q3": 728400, "Q4": 619300},
    "FY26": {"Q1": 438600, "Q2": 812450, "Q3": 574900, "Q4": 458900},
}
GIFT_COUNTS = {"FY24": 4220, "FY25": 2340, "FY26": 2110}
DONOR_COUNTS = {"FY24": 3180, "FY25": 1240, "FY26": 1090}

FY_WINDOW = {
    "FY24": ("2023-07-01", "2024-06-30"),
    "FY25": ("2024-07-01", "2025-06-30"),
    "FY26": ("2025-07-01", "2026-06-30"),
}


def rand_date(r, fy):
    a, b = (dt.date.fromisoformat(x) for x in FY_WINDOW[fy])
    return (a + dt.timedelta(days=r.randint(0, (b - a).days))).isoformat()


def rand_amount(r):
    roll = r.random()
    if roll < 0.0015:
        return round(r.uniform(60000, 240000), 2)
    if roll < 0.015:
        return round(r.uniform(8000, 55000), 2)
    if roll < 0.09:
        return round(r.uniform(900, 7500), 2)
    if roll < 0.38:
        return round(r.uniform(100, 850), 2)
    return float(r.choice([10, 15, 20, 25, 25, 30, 35, 50, 50, 60, 75, 100]))


def roster(names, fy, tag):
    r = rng("roster:" + tag)
    rows = [[n, rand_date(r, fy), rand_amount(r)] for n in names]
    rows.sort(key=lambda x: -x[2])
    return rows


def build_overview(s):
    # Donor universe, sliced so every movement bucket reconciles.
    fy24_donors = name_pool("fy24", DONOR_COUNTS["FY24"], org_share=0.04, estate_share=0.004)
    r = rng("slice")
    r.shuffle(fy24_donors)
    retained_25 = fy24_donors[:720]
    fy24_only = fy24_donors[720:]                     # 2,460 lapsed after FY24
    new_25 = name_pool("new25", 520, org_share=0.05, estate_share=0.01)

    fy25_donors = retained_25 + new_25                # 1,240
    r2 = rng("slice2")
    r2.shuffle(fy25_donors)
    retained_26 = fy25_donors[:640]
    lybunt_26 = fy25_donors[640:]                     # 600
    recaptured_26 = fy24_only[:140]
    lost_26 = fy24_only[140:]                         # 2,320
    new_26 = name_pool("new26", 310, org_share=0.05, estate_share=0.01)

    metrics, movement = {}, {}
    for fy in ("FY24", "FY25", "FY26"):
        rev = FY_TOTAL[fy]
        metrics[fy] = {
            "total_revenue": float(rev),
            "total_gifts": GIFT_COUNTS[fy],
            "unique_donors": DONOR_COUNTS[fy],
            "avg_gift": round(rev / GIFT_COUNTS[fy], 2),
            "avg_gifts_per_donor": round(GIFT_COUNTS[fy] / DONOR_COUNTS[fy], 2),
            "quarterly": {k: float(v) for k, v in QUARTERLY[fy].items()},
        }

    movement["FY24"] = {
        "new": DONOR_COUNTS["FY24"], "retained": None, "recaptured": None,
        "lapsing_lybunt": None, "lost": None, "sybunt": None,
        "note": "Baseline year in this dataset — no earlier giving history to compare against.",
    }
    movement["FY25"] = {
        "new": len(new_25), "retained": len(retained_25), "recaptured": None,
        "lapsing_lybunt": len(fy24_only), "lost": None, "sybunt": len(fy24_only),
        "note": ("Only one prior year (FY24) is available, so Recaptured and Lost "
                 "(which need 2+ prior years) cannot be computed, and SYBUNT equals LYBUNT."),
    }
    movement["FY26"] = {
        "new": len(new_26), "retained": len(retained_26), "recaptured": len(recaptured_26),
        "lapsing_lybunt": len(lybunt_26), "lost": len(lost_26),
        "sybunt": len(lybunt_26) + len(lost_26), "note": None,
    }

    lyb_rows = roster(lybunt_26, "FY25", "lyb26")
    lost_rows = roster(lost_26, "FY24", "lost26")
    syb_rows = sorted(lyb_rows + lost_rows, key=lambda x: -x[2])

    details = {
        "FY25": {
            "new": roster(new_25, "FY25", "new25"),
            "lybunt_sybunt": roster(fy24_only, "FY24", "lyb25"),
        },
        "FY26": {
            "new": roster(new_26, "FY26", "new26"),
            "recaptured": roster(recaptured_26, "FY26", "rec26"),
            "lybunt": lyb_rows,
            "lost": lost_rows,
            "sybunt": syb_rows,
        },
    }
    return replace_json(s, "dashboard-data",
                        {"metrics": metrics, "movement": movement, "details": details})


# ----------------------------------------------------------------- July YoY ---
def build_july(s, july_gifts):
    days = [0.0] * 31
    camp = {}
    for g in july_gifts:
        d = dt.date.fromisoformat(g["date"])
        days[d.day - 1] += g["amount"]
        c = camp.setdefault(g["campaign"], {"count": 0, "amount": 0.0})
        c["count"] += 1
        c["amount"] += g["amount"]
    days = [round(x, 2) for x in days]
    total26 = round(sum(days), 2)
    gifts26 = len(july_gifts)
    donors26 = len({g["constituent_id"] for g in july_gifts})
    for v in camp.values():
        v["amount"] = round(v["amount"], 2)
        v["pct"] = round(v["amount"] / total26 * 100, 1)

    # Prior-year July: same shape, independently generated.
    r = rng("july2025")
    camp25 = {
        "Direct Marketing": {"count": 148, "amount": 11840.25},
        "Event Income": {"count": 5, "amount": 14260.00},
        "Major Gifts": {"count": 2, "amount": 6500.00},
        "General Contribution": {"count": 9, "amount": 1129.40},
    }
    total25 = round(sum(v["amount"] for v in camp25.values()), 2)
    gifts25 = sum(v["count"] for v in camp25.values())
    for v in camp25.values():
        v["pct"] = round(v["amount"] / total25 * 100, 1)

    weights = [r.random() ** 2 for _ in range(31)]
    for i in (5, 6, 12, 19, 26):
        weights[i] *= 0.15
    wsum = sum(weights)
    days25 = [round(total25 * w / wsum, 2) for w in weights]
    days25[-1] = round(total25 - sum(days25[:-1]), 2)

    payload = {
        "meta2026": {"total_gifts": gifts26, "total_amount": total26,
                     "unique_donors": donors26,
                     "avg_gift": round(total26 / gifts26, 2),
                     "daily_avg": round(total26 / 31, 2)},
        "meta2025": {"total_gifts": gifts25, "total_amount": total25,
                     "unique_donors": gifts25 - 4,
                     "avg_gift": round(total25 / gifts25, 2),
                     "daily_avg": round(total25 / 31, 2)},
        "daily2026": days,
        "daily2025": days25,
        "campaigns": sorted(set(camp) | set(camp25)),
        "camp2026": camp,
        "camp2025": camp25,
    }
    return replace_json(s, "dashboard-data", payload)


# --------------------------------------------------------------- reference ---
REF_INTRO_OLD = ("This site bundles five fundraising dashboards. Below: the file structure, "
                 "then for each dashboard,")
REF_INTRO_NEW = ("This site bundles ten fundraising dashboards. Below: the file structure, "
                 "then for each dashboard,")

REF_FIXES = [
    ('├── index.html                          <span class="fyi">← landing page + password gate</span>',
     '├── index.html                          <span class="fyi">← landing page</span>'),
    ('│   └── gate.js                         <span class="fyi">← shared auth logic</span>\n', ''),
    ('├── assets/\n', ''),
    ("Nyiema - Northgate Youth Foundation &gt; Dashboard Exports &gt; Weekly Gift Reports",
     "Shared Drive &gt; Dashboard Exports &gt; Weekly Gift Reports"),
    ("<footer>Northgate Youth Foundation · Internal reporting · Not for public distribution</footer>",
     "<footer>Portfolio sample · All data shown is synthetic</footer>"),
    ("Source files, metric definitions, and data schema for every dashboard in this site.",
     "Source files, metric definitions, and data schema for every dashboard in this site. "
     "In this portfolio build the source workbooks are not included and every figure shown "
     "is randomly generated."),
]

REF_NOTE = """<div style="max-width:900px;margin:0 auto 26px;padding:13px 17px;border:1px solid #E3B8B8;background:#F9ECEC;border-radius:9px;font-family:'Inter',sans-serif;font-size:12.5px;line-height:1.55;color:#7A2E2E;">
<strong>Portfolio note.</strong> This page documents the data model and calculation logic behind the dashboards. The methodology is real; the organization, source files, and every figure rendered on the linked dashboards are synthetic stand-ins created for this portfolio. The RENXT record links present in the production build have been removed here.
</div>
"""


def build_reference(s):
    s = s.replace(REF_INTRO_OLD, REF_INTRO_NEW)
    for a, b in REF_FIXES:
        s = s.replace(a, b)
    s = re.sub(r"(</header>)", r"\1\n\n" + REF_NOTE, s, count=1)
    return s


# --------------------------------------------------------------------- main ---
def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "dashboards"))

    weekly = gen_weekly.build_all()
    july_gifts = [g for g in weekly["jul27-aug2"][2]
                  if g["date"].startswith("2026-07")]

    for fname in FILES:
        s = open(os.path.join(SRC, fname), encoding="utf-8").read()
        s = strip_gate(s)

        if fname == "campaign-revenue.html":
            s = apply_terms(s)
            s = build_campaign_revenue(s)
        elif fname == "fy26-progress-to-goal.html":
            s = apply_terms(s)
            s = build_progress(s)
        elif fname == "fundraising-performance-fy26.html":
            s = apply_terms(s)
            s = build_overview(s)
        elif fname == "july-giving-yoy.html":
            s = apply_terms(s)
            s = build_july(s, july_gifts)
        elif fname.startswith("weekly-giving-"):
            key = fname[len("weekly-giving-"):-len(".html")]
            data, fytd, _ = weekly[key]
            s = apply_terms(s)
            s = replace_json(s, "dashboard-data", data)
            s = replace_json(s, "fytd-data", fytd)
        elif fname == "dashboard-reference.html":
            s = apply_terms(s)
            s = build_reference(s)
        else:
            s = apply_terms(s)

        if fname != "dashboard-reference.html":
            s = add_banner(s)

        with open(os.path.join(OUT, "dashboards", fname), "w", encoding="utf-8") as f:
            f.write(s)
        print("wrote", fname, len(s))

    shutil.copy("index_template.html", os.path.join(OUT, "index.html"))
    print("wrote index.html")


if __name__ == "__main__":
    main()
