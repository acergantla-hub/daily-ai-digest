import json, urllib.request, urllib.error, os

f = open(os.path.expanduser("~/cf_api_token.txt"))
TOKEN=*** = {"Authorization": "Bearer " + TOKEN}

url = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/scripts/daily-ai-digest-newsletter/bindings"
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())
    for b in result.get("result", []):
        print(b.get("type"), b.get("name"))
