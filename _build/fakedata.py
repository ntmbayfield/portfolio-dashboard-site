"""Synthetic fundraising data for the portfolio version of the dashboards.

Nothing in here is derived from any real donor file. Every name, ID, amount and
date is generated from a fixed seed so the numbers are stable between builds.
"""
import random

SEED = 20260812
ORG = "Northgate Youth Foundation"

FIRST = """Alan Alice Amara Andre Angela Anita Arthur Barbara Beatriz Bernard Bianca Blake
Bonnie Brian Bridget Bruce Camille Carl Carla Carmen Cecilia Charles Cheryl Clara Clifford
Colin Corinne Curtis Daniel Danielle Dean Deborah Denise Derek Diane Dolores Donald Doris
Douglas Edith Edward Eileen Elaine Elena Elias Ellen Emanuel Emily Enrique Erica Ernest
Esther Eugene Evelyn Fatima Felix Fiona Frances Frank Gabriel Gail Gerald Gloria Grace
Gregory Gwen Harold Harriet Hector Helen Henry Hilda Hugo Ian Ines Irene Isaac
Ivan Jacob Janet Janice Jasmine Jeffrey Jerome Joan Joel Jonas Josephine Joyce Judith
Julian Karen Katherine Keith Kenneth Krishna Lamar Laura Lawrence Leon Leona Leslie Lidia
Linda Lionel Lorraine Louis Lucia Luther Lydia Mabel Malcolm Marcia Margaret Maria Marion
Marlene Martin Marvin Maureen Maxine Melvin Mercedes Michael Miriam Monica Nadia Nathan
Neil Nelson Nina Noel Norma Olga Oliver Omar Opal Oscar Patricia Paulette Percy Philip
Phyllis Priscilla Rafael Ramona Randall Raquel Raymond Rebecca Regina Renata Reuben Rhonda
Richard Rita Roberta Rodney Roland Rosalind Roy Ruby Rudolph Ruth Salvador Samuel Sandra
Selma Serena Sheila Sidney Silvia Simone Sonia Stanley Stella Stuart Sylvia Tamara Terrence
Thelma Theodore Thomas Tobias Ursula Vera Vernon Veronica Victor Vincent Viola Wallace
Wanda Warren Wendell Wesley Wilfred Wilma Yvonne Zachary Zelda""".split()

LAST = """Abbott Adkins Ainsworth Alcott Almeida Anders Ashford Atwater Baldwin Barlowe Barnhill
Bassett Beauchamp Bellamy Benavidez Beringer Bertrand Blackwood Bogart Bramwell Brennan
Bridgeforth Brockman Cadwell Calloway Cardoza Carrington Castellon Chadwick Chatfield Chenoweth
Colefax Collier Comstock Cordova Cranfield Crenshaw Cromwell Dalrymple Danvers Darnell Delacroix
Denniston Devereaux Dinsmore Dobbins Draycott Dunmore Eastwick Eberhardt Ellingson Elmore Enright
Escalante Fairbanks Falconer Farrington Fenwick Fitzhugh Fontaine Forsythe Galbraith Gallardo
Garnier Gatlin Gilliam Goodwyn Granville Greenlaw Grimsley Hadleigh Halstead Hargrove Harkness
Hathaway Havermeyer Hawthorne Heathcote Hemming Hollister Holbrook Hulburt Ingersoll Isley Jamison
Jarvis Kavanagh Keighley Kendrick Kingsley Kirkwood Lacroix Lambert Langford Larkspur Lattimore
Ledbetter Linford Livingood Lockridge Longstreet Lyman Macomber Maldonado Marchetti Mattingly
Merriweather Middleton Milbourne Montgomery Moorcroft Mulvaney Nakamura Nesbitt Newcomb Norcross
Oakhurst Ogilvie Okonkwo Ormsby Osgood Pemberton Pennington Perrault Pickering Pinkerton Prescott
Quimby Quintanilla Radcliffe Ramsdell Rathbone Redmond Reinhart Rensselaer Ridgeway Rockwell
Rosales Rutherford Sandoval Sargent Satterfield Selwyn Shackleton Sheffield Shepstone Sinclair
Somerville Stanhope Stockbridge Strickland Sutcliffe Swinton Tarrington Thackeray Thorpe Tremaine
Underhill Vandermeer Vasquez Verplanck Vickery Wadsworth Wainwright Waverly Weatherby Westbrook
Whitcomb Whitfield Willoughby Winslow Wolcott Woodbury Wycliffe Yardley Yeardley Zabriskie""".split()

MIDDLE = list("ABCDEFGHJKLMNPRSTVW")

ORG_DONORS = [
    "Alderwood Family Foundation", "Bayline Charitable Trust", "Cedar Hollow Fund",
    "Delmar Community Trust", "Everly Family Foundation", "Fairhaven Giving Circle",
    "Granite Point Foundation", "Harbor Light Charitable Fund", "Ironwood Family Trust",
    "Juniper Ridge Foundation", "Kestrel Family Fund", "Larkmead Charitable Trust",
    "Meridian Hills Foundation", "Northvale Community Fund", "Orchard Gate Foundation",
    "Pinecrest Family Trust", "Quarrystone Foundation", "Rosewater Charitable Fund",
    "Stillwater Family Foundation", "Thornbury Giving Trust", "Umberland Foundation",
    "Vesper Hill Charitable Fund", "Westmarch Family Foundation", "Yarrow Creek Trust",
]

ESTATES = [
    "Estate of Coralie Vandermeer", "Estate of Everett Pemberton", "Estate of Hazel Thackeray",
    "Estate of Lionel Barlowe", "Estate of Marguerite Ellingson", "Estate of Sanford Whitcomb",
]

# Development officers used on the weekly + prototype dashboards.
OFFICERS = ["Alexis Moreau", "Grant Whitfield", "Renee Castellano", "Priya Raghavan",
            "Trevor Nakashima", "Dana Whitlock"]

CAMPAIGNS = ["Direct Marketing", "Event Income", "Northgate Academy", "Major Gifts",
             "Other", "Planned Giving"]

CAMPAIGN_DESC = {
    "Direct Marketing": "Mass appeals",
    "Event Income": "Event Income",
    "Northgate Academy": "Northgate Academy",
    "General Contribution": "General Contribution",
    "Major Gifts": "Major Gifts",
}

FUNDS = {
    "Priority Needs Fund": "R-006",
    "Recreation Program Fund": "R-004",
    "Northgate Academy Fund": "42355",
    "General Contributions - unrestricted - no connection to Events": "42200",
    "Event Income unrestricted": "42400",
    "Residential and Vocational Education": "R-001",
    "Mental Health Services Fund": "R-002",
    "General Scholarship": "F-010",
}

APPEALS = {
    "Summer Camp Print Mail Appeal": "CAMP_m",
    "Monthly Donor Program": "Guardian Circle",
    "White Envelope With No Form": "White Mail",
    "Website": "Website",
    "Memorial & Tribute Giving": "MEM&TRIB",
    "2026 Northgate Academy Benefit Dinner": "BENEFIT-FY26",
    "2026 Golf Tournament": "GOLF-EVNT-FY27",
    "Donors who use the remit envelope with no selection - gifts restricted to R-006": "Remit Envelope",
    "2026 Gala Print Mail Appeal": "GALA_m",
    "Northgate Academy": "Northgate Academy",
}


def rng(tag):
    """Deterministic per-purpose random stream."""
    return random.Random(f"{SEED}:{tag}")


def person_name(r):
    if r.random() < 0.55:
        return f"{r.choice(FIRST)} {r.choice(MIDDLE)}. {r.choice(LAST)}"
    return f"{r.choice(FIRST)} {r.choice(LAST)}"


def name_pool(tag, n, org_share=0.03, estate_share=0.0):
    """A de-duplicated list of n synthetic donor names."""
    r = rng(tag)
    out, seen = [], set()
    guard = 0
    while len(out) < n and guard < n * 60:
        guard += 1
        roll = r.random()
        if roll < estate_share:
            nm = r.choice(ESTATES)
        elif roll < estate_share + org_share:
            nm = r.choice(ORG_DONORS)
        else:
            nm = person_name(r)
        if nm in seen:
            continue
        seen.add(nm)
        out.append(nm)
    return out
