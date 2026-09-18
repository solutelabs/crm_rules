import json, sys, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from migrate_v05 import api
S = sys.argv[1]
def v(r, k):
    x = r["values"].get(k) or []
    return x[0] if x else None
out, off = [], 0
while True:
    d = api("POST", "/objects/people/records/query", {"limit": 500, "offset": off,
            "sorts": [{"attribute": "last_interaction", "field": "interacted_at", "direction": "desc"}]})["data"]
    for r in d:
        if v(r, "importance") or v(r, "relationship") or (v(r, "ignore") or {}).get("value"):
            continue
        li = v(r, "last_interaction") or {}
        n = v(r, "name") or {}
        c = v(r, "company") or {}
        out.append({"id": r["id"]["record_id"], "name": n.get("full_name"),
                    "emails": [e["email_address"] for e in r["values"].get("email_addresses", [])],
                    "title": (v(r, "job_title") or {}).get("value"), "company_id": c.get("target_record_id"),
                    "li_at": li.get("interacted_at"), "li_type": li.get("interaction_type"),
                    "description": (v(r, "description") or {}).get("value")})
    off += len(d)
    print(off, len(out), flush=True)
    if len(d) < 500: break
out.sort(key=lambda p: p["li_at"] or "", reverse=True)
json.dump(out, open(S + "/unclassified.json", "w"))
print("unclassified:", len(out))
print(collections.Counter((p["li_at"] or "")[:10] + " " + str(p["li_type"]) for p in out[:400]).most_common(15))
