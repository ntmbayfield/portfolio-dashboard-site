"""Build synthetic gift-level data for the five weekly dashboards + FYTD rollups."""
import datetime as dt
from collections import OrderedDict
from fakedata import rng, name_pool, OFFICERS, CAMPAIGN_DESC, FUNDS, APPEALS

WEEKS = [
    # key, start, end, business days used, gift count
    ("jul1-5",    "2026-07-01", "2026-07-04", ["2026-07-01", "2026-07-02", "2026-07-04"], 18),
    ("jul6-12",   "2026-07-06", "2026-07-10", ["2026-07-06", "2026-07-07", "2026-07-08",
                                               "2026-07-09", "2026-07-10"], 74),
    ("jul13-19",  "2026-07-13", "2026-07-17", ["2026-07-13", "2026-07-14", "2026-07-16",
                                               "2026-07-17"], 29),
    ("jul20-26",  "2026-07-20", "2026-07-25", ["2026-07-20", "2026-07-21", "2026-07-23",
                                               "2026-07-24", "2026-07-25"], 63),
    ("jul27-aug2", "2026-07-27", "2026-08-02", ["2026-07-27", "2026-07-28", "2026-07-29",
                                                "2026-07-30", "2026-07-31", "2026-08-02"], 34),
]

# (campaign, fund, appeal, gift_type, weight, amount-band)
MIX = [
    ("Direct Marketing", "Priority Needs Fund", "Summer Camp Print Mail Appeal", "Cash", 20, "small"),
    ("Direct Marketing", "Recreation Program Fund", "Summer Camp Print Mail Appeal", "Cash", 12, "small"),
    ("Direct Marketing", "Priority Needs Fund", "Monthly Donor Program", "Recurring Gift Pay Cash", 16, "tiny"),
    ("Direct Marketing", "Priority Needs Fund", "Monthly Donor Program", "Recurring Gift Master Card/Visa", 6, "tiny"),
    ("Direct Marketing", "General Contributions - unrestricted - no connection to Events",
     "White Envelope With No Form", "Cash", 7, "mid"),
    ("Direct Marketing", "Priority Needs Fund", "Website", "Cash", 5, "small"),
    ("Direct Marketing", "Mental Health Services Fund", "Summer Camp Print Mail Appeal", "Cash", 3, "small"),
    ("Direct Marketing", "Residential and Vocational Education", "Summer Camp Print Mail Appeal", "Cash", 3, "small"),
    ("Direct Marketing", "General Scholarship", "Monthly Donor Program", "Recurring Gift Master Card/Visa", 2, "small"),
    ("Direct Marketing", "Priority Needs Fund",
     "Donors who use the remit envelope with no selection - gifts restricted to R-006", "Cash", 3, "small"),
    ("Direct Marketing", "Recreation Program Fund", "2026 Gala Print Mail Appeal", "Cash", 2, "small"),
    ("General Contribution", "General Contributions - unrestricted - no connection to Events",
     "White Envelope With No Form", "Cash", 3, "small"),
    ("General Contribution", "Priority Needs Fund", "Memorial & Tribute Giving", "Cash", 2, "small"),
    ("Northgate Academy", "Northgate Academy Fund", "2026 Northgate Academy Benefit Dinner", "Cash", 2, "event"),
    ("Northgate Academy", "Northgate Academy Fund", "Website", "Cash", 1, "small"),
    ("Event Income", "Event Income unrestricted", "2026 Golf Tournament", "Cash", 1, "event"),
    ("Major Gifts", "General Contributions - unrestricted - no connection to Events",
     "White Envelope With No Form", "Stock/Property", 1, "major"),
]

BANDS = {
    "tiny":  [5, 10, 15, 18, 20, 23, 25, 25, 28.99, 30, 35, 36, 40, 50],
    "small": [10, 20, 25, 25, 30, 40, 50, 50, 50, 60, 65, 75, 90, 100, 100, 125, 150],
    "mid":   [50, 75, 100, 125, 150, 200, 250, 300, 500, 750, 1000],
    "event": [500, 750, 1000, 1500, 2500, 2500, 3000],
    "major": [1000, 2500, 5000, 7500, 10000],
}


def pick(r, weights):
    total = sum(w for *_, w, _ in weights)
    x = r.uniform(0, total)
    acc = 0
    for row in weights:
        acc += row[4]
        if x <= acc:
            return row
    return weights[-1]


def fmt_display(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%a %b %d, %Y")


def short_display(iso):
    d = dt.date.fromisoformat(iso)
    return d.strftime("%a %m/%d")


def build_week(key, start, end, days, count, donors, cid_iter):
    r = rng("week:" + key)
    gifts = []
    for i in range(count):
        campaign, fund, appeal, gtype, _w, band = pick(r, MIX)
        amt = r.choice(BANDS[band])
        if band in ("event", "major") and r.random() < 0.5:
            amt = round(amt + r.uniform(-0.4, 0.4) * amt / 4, 2)
        elif r.random() < 0.12:
            amt = round(amt + r.uniform(0.01, 0.99), 2)
        day = r.choice(days)
        if gifts and r.random() < 0.05:
            # A donor occasionally gives twice inside the same reporting week.
            prev = r.choice(gifts)
            name, cid = prev["donor_name"], prev["constituent_id"]
        else:
            name = donors.pop()
            cid = next(cid_iter)
        fundraiser = r.choice(OFFICERS[:4]) if r.random() < 0.28 else ""
        gifts.append({
            "date": day,
            "date_display": fmt_display(day),
            "amount": round(float(amt), 2),
            "gift_type": gtype,
            "campaign": campaign,
            "campaign_desc": CAMPAIGN_DESC[campaign],
            "fund": fund,
            "fund_id": FUNDS[fund],
            "appeal": appeal,
            "appeal_id": APPEALS[appeal],
            "constituent_id": str(cid),
            "fundraiser": fundraiser,
            "soft_credit": "No",
            "donor_name": name,
            "gift_link": "",
            "cons_link": "",
        })
    gifts.sort(key=lambda g: (g["date"], g["donor_name"]))
    return gifts


def group(gifts, field, total):
    agg = OrderedDict()
    for g in gifts:
        row = agg.setdefault(g[field], {"label": g[field], "count": 0, "amount": 0.0})
        row["count"] += 1
        row["amount"] += g["amount"]
    out = sorted(agg.values(), key=lambda x: -x["amount"])
    for row in out:
        row["amount"] = round(row["amount"], 2)
        row["pct"] = round(row["amount"] / total * 100, 1) if total else 0.0
    return out


def daily(gifts):
    agg = OrderedDict()
    for g in sorted(gifts, key=lambda x: x["date"]):
        row = agg.setdefault(g["date"], {"date": g["date"],
                                         "date_display": short_display(g["date"]),
                                         "count": 0, "amount": 0.0})
        row["count"] += 1
        row["amount"] += g["amount"]
    out = list(agg.values())
    for row in out:
        row["amount"] = round(row["amount"], 2)
    return out


def build_all():
    total_needed = sum(w[4] for w in WEEKS)
    donors = name_pool("weekly-donors", total_needed + 20, org_share=0.05)
    cid_r = rng("weekly-cids")
    used = set()

    def cids():
        while True:
            c = cid_r.randint(100000, 699999)
            if c not in used:
                used.add(c)
                yield c

    cid_iter = cids()

    results = {}
    running = []
    for key, start, end, days, count in WEEKS:
        gifts = build_week(key, start, end, days, count, donors, cid_iter)
        total = round(sum(g["amount"] for g in gifts), 2)
        uniq = len({g["constituent_id"] for g in gifts})
        data = {
            "meta": {
                "date_start": start,
                "date_end": max(days),
                "total_gifts": len(gifts),
                "total_amount": total,
                "avg_gift": round(total / len(gifts), 2),
                "unique_donors": uniq,
            },
            "by_campaign": group(gifts, "campaign", total),
            "by_appeal": group(gifts, "appeal", total),
            "by_fund": group(gifts, "fund", total),
            "daily": daily(gifts),
            "gifts": gifts,
        }
        running.extend(gifts)
        ftotal = round(sum(g["amount"] for g in running), 2)
        fytd = {
            "fy_start": "2026-07-01",
            "through_date": max(days),
            "total_gifts": len(running),
            "total_amount": ftotal,
            "unique_donors": len({g["constituent_id"] for g in running}),
            "by_campaign": group(running, "campaign", ftotal),
            "by_appeal": group(running, "appeal", ftotal),
            "by_fund": group(running, "fund", ftotal),
        }
        results[key] = (data, fytd, list(running))
    return results


if __name__ == "__main__":
    res = build_all()
    for k, (d, f, _) in res.items():
        print(k, d["meta"], "| FYTD", f["total_gifts"], f["total_amount"])
