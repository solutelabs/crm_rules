#!/usr/bin/python3
"""Read-only: compare Zoho Books invoices with Attio company status. Proposes, never writes.

  /usr/bin/python3 books_reconcile.py            # prints the diff table, writes books_reconcile.csv next to it
"""
import csv, datetime, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zoho
from migrate_v05 import api

TODAY = datetime.date.today()
CUTOFF = (TODAY - datetime.timedelta(days=182)).isoformat()
PER_USD = {"USD": 1.0, "INR": 85.0, "AUD": 1.55, "GBP": 0.79, "CAD": 1.37}  # ponytail: fixed rates, good enough for spend buckets
INTERNAL = ("solute",)  # invoices between our own entities
BUCKETS = [(10_000, "$0 - $10k"), (50_000, "$10k - $50k"), (100_000, "$50k - $100k"), (250_000, "$100k - $250k"),
           (500_000, "$250k - $500k"), (float("inf"), "$500k+")]


def bucket(usd):
    return next(label for lim, label in BUCKETS if usd < lim)


def invoices(org):
    page, out = 1, []
    while True:
        d = zoho.api("books", f"/invoices?per_page=200&page={page}", org=org)
        out += d.get("invoices", [])
        if not d.get("page_context", {}).get("has_more_page"):
            return out
        page += 1


def domains_for(org, contact_id):
    c = zoho.api("books", f"/contacts/{contact_id}", org=org)["contact"]
    emails = {p.get("email", "") for p in c.get("contact_persons", [])} | {c.get("email", "")}
    doms = {e.split("@")[1].lower() for e in emails if "@" in e}
    if c.get("website"):
        doms.add(c["website"].replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0].lower())
    return {d for d in doms if not any(k in d for k in INTERNAL) and d not in ("gmail.com", "outlook.com", "hotmail.com", "yahoo.com")}


OVERRIDES = {}  # Books customer name -> Attio company id, confirmed by Karan (books_overrides.json)
try:
    import json
    OVERRIDES = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "books_overrides.json")))
except FileNotFoundError:
    pass


def attio_company(doms, name):
    if name in OVERRIDES:
        return api("GET", f"/objects/companies/records/{OVERRIDES[name]}")["data"]
    for d in sorted(doms):
        hits = api("POST", "/objects/companies/records/query", {"filter": {"domains": {"domain": {"$contains": d}}}, "limit": 2})["data"]
        if hits:
            return hits[0]
    key = name.split()[0]
    hits = api("POST", "/objects/companies/records/query", {"filter": {"name": {"$contains": key}}, "limit": 2})["data"]
    return hits[0] if len(hits) == 1 else None


# 1. aggregate invoices per Books customer across orgs
agg = {}
for oid, oname in zoho.orgs():
    for i in invoices(oid):
        cur = i.get("currency_code", "USD")
        if any(k in i["customer_name"].lower() for k in INTERNAL):
            continue
        a = agg.setdefault(i["customer_id"], {"name": i["customer_name"], "org": oid, "entity": oname, "n": 0, "usd": 0.0,
                                               "first": i["date"], "last": i["date"], "unpaid": 0.0})
        a["n"] += 1
        rate = PER_USD.get(cur, 1.0)
        a["usd"] += float(i.get("total", 0)) / rate
        a["unpaid"] += float(i.get("balance", 0)) / rate
        a["first"], a["last"] = min(a["first"], i["date"]), max(a["last"], i["date"])

# 2. match to Attio and diff
rows = []
for cid, a in sorted(agg.values() and agg.items(), key=lambda kv: -kv[1]["usd"]):
    doms = domains_for(a["org"], cid)
    co = attio_company(doms, a["name"])
    proposed = "Customer" if a["last"] >= CUTOFF else "Past Customer"
    row = {"books_customer": a["name"], "entity": a["entity"].replace("Solute TechnoLabs ", "").replace("SoluteLabs ", ""),
           "invoices": a["n"], "usd_total": round(a["usd"]), "unpaid_usd": round(a["unpaid"]), "first": a["first"], "last": a["last"],
           "proposed_type": proposed, "proposed_spend": bucket(a["usd"]), "attio_company": "", "attio_id": "", "attio_type": "",
           "attio_since": "", "attio_end": "", "attio_spend": "", "diff": ""}
    if co:
        v = co["values"]
        g = lambda k: (v.get(k) or [{}])[0]
        row.update(attio_company=g("name").get("value", "") or ",".join(x.get("domain", "") for x in v.get("domains") or []),
                   attio_id=co["id"]["record_id"], attio_type=g("account_type").get("option", {}).get("title", ""),
                   attio_since=g("customer_since").get("value", ""), attio_end=g("engagement_end_date").get("value", ""),
                   attio_spend=g("total_spend_range").get("option", {}).get("title", ""))
        d = []
        if row["attio_type"] != proposed: d.append(f"type {row['attio_type'] or 'blank'} -> {proposed}")
        if not row["attio_since"]: d.append(f"since -> {a['first']}")
        if proposed == "Past Customer" and not row["attio_end"]: d.append(f"end -> {a['last']}")
        if row["attio_spend"] != row["proposed_spend"]: d.append(f"spend {row['attio_spend'] or 'blank'} -> {row['proposed_spend']}")
        row["diff"] = "; ".join(d)
    else:
        row["diff"] = "NOT IN ATTIO (domains: " + ", ".join(sorted(doms)) + ")"
    rows.append(row)

# 3. merge rows that hit the same Attio company (billed from several entities)
merged = {}
for r in rows:
    k = r["attio_id"] or ("books:" + r["books_customer"])
    if k in merged:
        m = merged[k]
        m["books_customer"] += " + " + r["books_customer"]; m["entity"] += "+" + r["entity"]
        m["invoices"] += r["invoices"]; m["usd_total"] += r["usd_total"]; m["unpaid_usd"] += r["unpaid_usd"]
        m["first"], m["last"] = min(m["first"], r["first"]), max(m["last"], r["last"])
    else:
        merged[k] = dict(r)
rows = list(merged.values())
for r in rows:
    r["proposed_type"] = "Customer" if r["last"] >= CUTOFF else "Past Customer"
    r["proposed_spend"] = bucket(r["usd_total"])
    if r["attio_id"]:
        d = []
        keep = r["attio_type"] in ("Partner", "Vendor") or (r["attio_type"] == "Past Customer" and r["attio_end"])  # Karan's call stands
        if r["attio_type"] != r["proposed_type"] and not keep: d.append(f"type {r['attio_type'] or 'blank'} -> {r['proposed_type']}")
        if not r["attio_since"]: d.append(f"since -> {r['first']}")
        if r["proposed_type"] == "Past Customer" and not r["attio_end"] and not keep: d.append(f"end -> {r['last']}")
        order = [b for _, b in BUCKETS]
        if r["attio_spend"] != r["proposed_spend"] and (not r["attio_spend"] or order.index(r["proposed_spend"]) > order.index(r["attio_spend"])):
            d.append(f"spend {r['attio_spend'] or 'blank'} -> {r['proposed_spend']}")  # fill or raise, never lower: Books history starts 2019
        r["diff"] = "; ".join(d)
rows.sort(key=lambda r: -r["usd_total"])

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "books_reconcile.csv")
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"{len(rows)} Books customers, cutoff {CUTOFF}; csv -> {out}\n")
for r in rows:
    if r["diff"]:
        print(f"{r['books_customer']} [{r['entity']}] | {r['invoices']} inv | ${r['usd_total']:,} | last {r['last']} | Attio: {r['attio_company'] or '-'} ({r['attio_type'] or 'blank'}) | {r['diff']}")
