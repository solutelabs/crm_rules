# usage: apply.py ops.json (run inside the workdir) -> PATCHes people/companies, appends to apply.log, skips ids already logged. ops: [{"id","name","obj"?:"companies", ...attribute values}]; importance as 1-5
import os, sys, json, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from migrate_v05 import api
IMP = {1: "7c83e1e7-d165-4fc5-953a-2a224c72391f", 2: "0c753323-cf38-446a-944f-ed855f8f2bde", 3: "284d2c25-a1cb-41cc-a809-5162cd90049b", 4: "13ade9ba-1e65-4d1a-a0ee-8db5392a5475", 5: "74a0d9b1-50cf-43c3-a82a-f07ee1d7a329"}
ops = json.load(open(sys.argv[1]))
done = {l.split()[1] for l in open("apply.log")} if __import__("os").path.exists("apply.log") else set()
log = open("apply.log", "a")
for o in ops:
    obj = o.get("obj", "people")
    vals = {k: v for k, v in o.items() if k not in ("id", "obj", "name")}
    if "importance" in vals: vals["importance"] = IMP[vals["importance"]]
    if o["id"] in done: continue
    api("PATCH", f"/objects/{obj}/records/{o['id']}", {"data": {"values": vals}})
    line = f"{obj} {o['id']} {o.get('name')} {vals}"
    print(line); log.write(line + "\n"); log.flush()
    time.sleep(0.05)
print("done", len(ops))
