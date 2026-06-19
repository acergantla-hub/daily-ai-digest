import json, urllib.request, urllib.error, os

f = open(os.path.expanduser("~/cf_api_token.txt"))
TOKEN=*** = {"Authorization": "Bearer " + TOKEN}

# Check worker details
url = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/scripts/daily-ai-digest-newsletter"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        r = result.get("result", {})
        print("Script name:", r.get("id"))
        print("Created:", r.get("created_on"))
        print("Modified:", r.get("modified_on"))
        # Check if there's a compatibility_date
        print("Compat:", r.get("compatibility_date"))
        # Check modules
        modules = r.get("modules", [])
        print("Modules:", len(modules))
        for m in modules:
            print("  -", m.get("name"), m.get("type"))
except urllib.error.HTTPError as e:
    print("Error " + str(e.code) + ": " + e.read().decode()[:200])

# Check routes
print("")
print("=== Routes ===")
url2 = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/routes"
req2 = urllib.request.Request(url2, headers=headers)
try:
    with urllib.request.urlopen(req2, timeout=30) as resp:
        result2 = json.loads(resp.read())
        routes = result2.get("result", [])
        for route in routes:
            if "daily-ai-digest-newsletter" in route.get("script", ""):
                print("Route:", route.get("pattern"), "->", route.get("script"))
        if not any("daily-ai-digest-newsletter" in r.get("script", "") for r in routes):
            print("No routes found for this worker")
            print("Total routes:", len(routes))
except urllib.error.HTTPError as e:
    print("Error " + str(e.code) + ": " + e.read().decode()[:200])
