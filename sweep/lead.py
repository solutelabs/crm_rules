# usage: lead.py spec.json (run inside the workdir) -> classify a person as a lead: optional company create/patch, person PATCH, one task. Appends to apply.log.
# spec: {"id","name","relationship","importance":1-5,"description"?, "company"?: {"id"} | {"name","domain"?}, "account_type"?, "task"?: {"content","deadline","assignee"}}
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from migrate_v05 import api
IMP = {1: "7c83e1e7-d165-4fc5-953a-2a224c72391f", 2: "0c753323-cf38-446a-944f-ed855f8f2bde", 3: "284d2c25-a1cb-41cc-a809-5162cd90049b", 4: "13ade9ba-1e65-4d1a-a0ee-8db5392a5475", 5: "74a0d9b1-50cf-43c3-a82a-f07ee1d7a329"}
KARAN = "860ac1d4-dd8c-47fb-a881-82836abada57"
s = json.load(open(sys.argv[1]))
log = open("apply.log", "a")
def w(line): print(line); log.write(line + "\n"); log.flush()
vals = {"relationship": s["relationship"], "importance": IMP[s["importance"]]}
if s.get("description"): vals["description"] = s["description"]
if s.get("name_fix"): vals["name"] = [{"first_name": s["name_fix"][0], "last_name": s["name_fix"][1], "full_name": " ".join(s["name_fix"])}]
if s.get("location"):  # {"locality","region"?,"country_code"}; Attio wants every key present
    vals["primary_location"] = {k: None for k in ("line_1", "line_2", "line_3", "line_4", "locality", "region", "postcode", "country_code", "latitude", "longitude")} | s["location"]
c = s.get("company")
if c:
    if "id" not in c:
        cv = {"name": c["name"]}
        if c.get("domain"): cv["domains"] = [{"domain": c["domain"]}]
        c["id"] = api("POST", "/objects/companies/records", {"data": {"values": cv}})["data"]["id"]["record_id"]
        w(f"companies {c['id']} {c['name']} created")
    if s.get("account_type"):
        api("PATCH", f"/objects/companies/records/{c['id']}", {"data": {"values": {"account_type": s["account_type"]}}})
        w(f"companies {c['id']} {c.get('name')} {{'account_type': '{s['account_type']}'}}")
    vals["company"] = [{"target_object": "companies", "target_record_id": c["id"]}]
api("PATCH", f"/objects/people/records/{s['id']}", {"data": {"values": vals}})
w(f"people {s['id']} {s['name']} {vals}")
t = s.get("task")
if t:
    r = api("POST", "/tasks", {"data": {"content": t["content"], "format": "plaintext", "deadline_at": t["deadline"] + "T09:00:00.000Z",
            "is_completed": False, "linked_records": [{"target_object": "people", "target_record_id": s["id"]}],
            "assignees": [{"referenced_actor_type": "workspace-member", "referenced_actor_id": t.get("assignee", KARAN)}]}})
    w(f"tasks {r['data']['id']['task_id']} {s['name']} {t['content']!r} due {t['deadline']}")
