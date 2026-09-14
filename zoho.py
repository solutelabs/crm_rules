#!/usr/bin/python3
"""Zoho REST helper. Reads credentials from the env file next to this file:

ZOHO_CLIENT_ID=      # Zoho API console -> Self Client
ZOHO_CLIENT_SECRET=
ZOHO_REFRESH_TOKEN=  # generated once from the Self Client "Generate Code" flow
ZOHO_DC=in           # data centre: in, com, eu, com.au ...
ZOHO_ORG_IDS=        # comma-separated Books organisation ids (filled by bootstrap)

Usage: from zoho import api, orgs
  for oid, name in orgs(): api("books", "/invoices?status=unpaid", org=oid)
"""
import json, os, sys, time, urllib.parse, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(HERE, ".env")
BASES = {  # product -> api host + prefix, {dc} filled from ZOHO_DC
    "books": "https://www.zohoapis.{dc}/books/v3",
    "invoice": "https://www.zohoapis.{dc}/invoice/v3",
    "crm": "https://www.zohoapis.{dc}/crm/v7",
    "mail": "https://mail.zoho.{dc}/api",
}
_token = {"value": None, "exp": 0}


def env():
    out = {}
    with open(ENV_FILE) as f:
        for line in f:
            k, _, v = line.strip().partition("=")
            if k.startswith("ZOHO_"):
                out[k] = v.split("#")[0].strip().strip('"')
    missing = [k for k in ("ZOHO_CLIENT_ID", "ZOHO_CLIENT_SECRET", "ZOHO_REFRESH_TOKEN", "ZOHO_DC") if not out.get(k)]
    if missing:
        sys.exit(f"missing in env file: {', '.join(missing)}")
    return out


def token():
    if _token["value"] and time.time() < _token["exp"]:
        return _token["value"]
    e = env()
    data = urllib.parse.urlencode({"grant_type": "refresh_token", "client_id": e["ZOHO_CLIENT_ID"],
                                   "client_secret": e["ZOHO_CLIENT_SECRET"], "refresh_token": e["ZOHO_REFRESH_TOKEN"]}).encode()
    with urllib.request.urlopen(f"https://accounts.zoho.{e['ZOHO_DC']}/oauth/v2/token", data=data, timeout=30) as r:
        j = json.load(r)
    if "access_token" not in j:
        sys.exit(f"zoho token error: {j}")
    _token.update(value=j["access_token"], exp=time.time() + j.get("expires_in", 3600) - 60)
    return _token["value"]


def orgs():
    """[(organization_id, name), ...] for every Books org the token can see."""
    return [(o["organization_id"], o["name"]) for o in api("books", "/organizations")["organizations"]]


def api(product, path, method="GET", body=None, org=None):
    e = env()
    url = BASES[product].format(dc=e["ZOHO_DC"]) + path
    if org:
        url += ("&" if "?" in url else "?") + "organization_id=" + str(org)
    req = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                 headers={"Authorization": f"Zoho-oauthtoken {token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as err:
        sys.exit(f"{method} {url} -> {err.code}: {err.read().decode()[:400]}")


def bootstrap(code):
    """One-time: exchange a Self Client grant code for a refresh token, store it and the Books org id."""
    e = {}
    with open(ENV_FILE) as f:
        for line in f:
            k, _, v = line.strip().partition("=")
            if k.startswith("ZOHO_"):
                e[k] = v.split("#")[0].strip()
    data = urllib.parse.urlencode({"grant_type": "authorization_code", "code": code, "client_id": e["ZOHO_CLIENT_ID"],
                                   "client_secret": e["ZOHO_CLIENT_SECRET"]}).encode()
    with urllib.request.urlopen(f"https://accounts.zoho.{e['ZOHO_DC']}/oauth/v2/token", data=data, timeout=30) as r:
        j = json.load(r)
    if "refresh_token" not in j:
        sys.exit(f"bootstrap failed: {j}")
    _set_env("ZOHO_REFRESH_TOKEN", j["refresh_token"])
    found = api("books", "/organizations")["organizations"]
    for o in found:
        print(f"org {o['organization_id']}: {o['name']} ({o.get('currency_code')})")
    _set_env("ZOHO_ORG_IDS", ",".join(o["organization_id"] for o in found))
    print(f"ZOHO_ORG_IDS set ({len(found)} orgs)")


def _set_env(key, value):
    lines = open(ENV_FILE).read().splitlines()
    lines = [f"{key}={value}" if l.startswith(key + "=") else l for l in lines]
    open(ENV_FILE, "w").write("\n".join(lines) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "bootstrap":   # /usr/bin/python3 zoho.py bootstrap <grant code>
        bootstrap(sys.argv[2])
    else:                                                    # smoke test: /usr/bin/python3 zoho.py books
        p = sys.argv[1] if len(sys.argv) > 1 else "books"
        if p == "books":
            for oid, name in orgs():
                print(oid, name)
        else:
            probe = {"invoice": "/organizations", "crm": "/org", "mail": "/accounts"}[p]
            print(json.dumps(api(p, probe), indent=1)[:800])
