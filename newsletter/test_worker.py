import json, urllib.request, urllib.error, os

f = open(os.path.expanduser("~/cf_api_token.txt"))
TOKEN=*** = {"Authorization": "Bearer " + TOKEN}

# Check bindings
url = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/scripts/daily-ai-digest-newsletter/bindings"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
        if data:
            result = json.loads(data)
            print("Bindings:", json.dumps(result, indent=2)[:500])
        else:
            print("Empty response")
except urllib.error.HTTPError as e:
    print("Error " + str(e.code) + ": " + e.read().decode()[:200])

# Test worker health
print("")
print("=== Testing worker ===")
import urllib.request as ur
try:
    req2 = ur.Request("https://daily-ai-digest-newsletter." + ACCOUNT_ID[:8] + ".workers.dev/api/health")
    with ur.urlopen(req2, timeout=15) as resp:
        print("Health:", resp.read().decode()[:200])
except Exception as e:
    print("Health check error:", str(e)[:200])
