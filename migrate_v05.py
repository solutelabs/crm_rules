#!/usr/bin/env python3
"""Rulebook v0.5 migration: role-only person.relationship + company.account_type.

Usage:
  python3 migrate_v05.py migration.csv            # dry run: prints what would change
  python3 migrate_v05.py migration.csv --apply    # writes to Attio
  python3 migrate_v05.py --archive-old --apply    # step 2, after verifying counts

Reads ATTIO_API_KEY from the env file next to this file. Only touches
`relationship` on people and `account_type` on companies. Never changes
ignore/importance; rows with flags are listed so Karan can decide.
"""
import csv, json, os, sys, time, urllib.request, urllib.error

BASE = "https://api.attio.com/v2"
NEW = ["Decision Maker", "POC", "Partner", "Referrer", "Vendor"]
OLD = ["Client - Founder / Owner", "Client POC", "Vendor POC", "Past Client",
       "Future Prospect", "Past Lead", "Past client POC", "CWX POC"]  # Referrer is reused
HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, ".env")


def token():
    with open(ENV_FILE) as f:
        for line in f:
            k, _, v = line.strip().partition("=")
            if k == "ATTIO_API_KEY" and v:
                return v.strip().strip('"')
    sys.exit("ATTIO_API_KEY missing in env file")


def api(method, path, body=None):
    req = urllib.request.Request(BASE + path, method=method,
                                 data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Bearer {token()}",
                                          "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"{method} {path} -> {e.code}: {e.read().decode()[:400]}")


def options():
    return {o["title"]: o for o in api("GET", "/objects/people/attributes/relationship/options?show_archived=true")["data"]}


def ensure_options(apply):
    have = options()
    for title in NEW:
        if title in have:
            print(f"option exists: {title}")
        elif apply:
            api("POST", "/objects/people/attributes/relationship/options", {"data": {"title": title}})
            print(f"option created: {title}")
        else:
            print(f"would create option: {title}")


def migrate(csv_path, apply):
    rows = list(csv.DictReader(open(csv_path)))
    people = [r for r in rows if r["proposed_relationship"] and r["proposed_relationship"] != r["current_relationship"]]
    companies = {r["company_id"]: r["proposed_account_type"] for r in rows if r["company_id"] and r["proposed_account_type"]}
    print(f"{len(rows)} rows; {len(people)} people to re-tag; {len(companies)} companies to set account_type")
    for r in people:
        print(f"  person {r['name']!r}: {r['current_relationship']} -> {r['proposed_relationship']}")
        if apply:
            api("PATCH", f"/objects/people/records/{r['record_id']}",
                {"data": {"values": {"relationship": r["proposed_relationship"]}}})
            time.sleep(0.05)
    for cid, at in companies.items():
        print(f"  company {cid}: account_type -> {at}")
        if apply:
            api("PATCH", f"/objects/companies/records/{cid}", {"data": {"values": {"account_type": at}}})
            time.sleep(0.05)
    flagged = [r for r in rows if r["flags"]]
    print(f"\n{len(flagged)} rows carry flags (not changed by this script):")
    for r in flagged:
        print(f"  {r['name']} | {r['company_name']} | {r['flags']}")


def archive_old(apply):
    have = options()
    for title in OLD:
        o = have.get(title)
        if not o or o.get("is_archived"):
            continue
        n = api("POST", "/objects/people/records/query",
                {"filter": {"relationship": title}, "limit": 1})["data"]
        if n:
            print(f"NOT archiving {title}: records still use it")
            continue
        if apply:
            api("PATCH", f"/objects/people/attributes/relationship/options/{o['id']['option_id']}",
                {"data": {"is_archived": True}})
            print(f"archived: {title}")
        else:
            print(f"would archive: {title}")


if __name__ == "__main__":
    apply = "--apply" in sys.argv
    if "--archive-old" in sys.argv:
        archive_old(apply)
    else:
        ensure_options(apply)
        migrate(sys.argv[1], apply)
    if not apply:
        print("\nDRY RUN: add --apply to write.")
