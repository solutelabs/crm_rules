# usage: build_batch.py N  -> batchN.json + groupN_{0,1,2}.txt; skips anyone in earlier batch files
import os, sys, json, glob, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from migrate_v05 import api
N = sys.argv[1]
P = json.load(open("unclassified.json"))
done = {x["id"] for f in glob.glob("batch*.json") for x in json.load(open(f))}
ts = collections.Counter(x["li_at"] for x in P if x["li_type"] == "meeting")
out = []
for x in P:
    if x["id"] in done or (x["li_type"] == "meeting" and ts[x["li_at"]] >= 5): continue
    if any(e.split("@")[1].startswith(("solutelab", "solute-lab", "aiwithsolute")) for e in x["emails"]): continue
    r = api("POST", "/objects/people/records/query", {"filter": {"record_id": x["id"]}})["data"]
    if not r: continue  # merged away
    v = r[0]["values"]
    if v["relationship"] or v["importance"] or (v["ignore"] and v["ignore"][0]["value"]): continue
    x["company"] = x["account_type"] = None
    x["company_id"] = v["company"][0]["target_record_id"] if v["company"] else None  # live, not the pull (merges)
    if x["company_id"]:
        c = api("GET", "/objects/companies/records/" + x["company_id"])["data"]["values"]
        x["company"] = (c.get("name") or [{}])[0].get("value")
        at = c.get("account_type") or []
        x["account_type"] = at[0]["option"]["title"] if at else None
    t = api("GET", "/tasks?linked_object=people&linked_record_id=" + x["id"])["data"]
    x["tasks"] = [(k["content_plaintext"][:90], k["is_completed"]) for k in t]
    out.append(x)
    if len(out) == 25: break
json.dump(out, open(f"batch{N}.json", "w"), indent=1)
line = lambda i, x: f"{i+1}. {x['name']} <{x['emails'][0] if x['emails'] else None}> | title: {x['title']} | company: {x['company']} (Attio status: {x['account_type']}) | last {x['li_type']} {(x['li_at'] or '')[:10]} | attio id {x['id']} | tasks: {x['tasks']} | bio: {(x['description'] or '')[:150]}"
for g, (a, b) in enumerate(((0, 9), (9, 17), (17, 25))):
    open(f"group{N}_{g}.txt", "w").write("\n".join(line(i, x) for i, x in enumerate(out) if a <= i < b))
for i, x in enumerate(out): print(line(i, x)[:230])
