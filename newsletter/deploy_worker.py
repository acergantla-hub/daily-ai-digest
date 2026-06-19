import json, urllib.request, urllib.error, os, sys

f=open(os.path.expanduser("~/cf_api_token.txt"))
TOKEN=f.read().strip()
f.close()
print("Token len:", len(TOKEN))

ACCOUNT_ID = "e227995b424158109fb77a1de35ab083"
DB_ID = "c83aec15-53fd-4107-a763-8da58a8bebb5"
BASE_DIR = "/data/data/com.termux/files/home/daily-ai-digest/newsletter"

worker_code = open(os.path.join(BASE_DIR, "worker.js")).read()
print("Worker code length:", len(worker_code))

metadata = json.dumps({"main_module":"index.js","compatibility_date":"2026-05-30","compatibility_flags":["nodejs_compat"],"usage_model":"bundled"})

boundary = "----Boundary7MA4YWxkTrZu0gW"
CRLF = chr(13) + chr(10)
body = ("--" + boundary + CRLF + "Content-Disposition: form-data; name=\"metadata\"" + CRLF + "Content-Type: application/json" + CRLF + CRLF + metadata + CRLF + "--" + boundary + CRLF + "Content-Disposition: form-data; name=\"index.js\"; filename=\"index.js\"" + CRLF + "Content-Type: application/javascript+module" + CRLF + CRLF).encode() + worker_code.encode() + (CRLF + "--" + boundary + "--" + CRLF).encode()

url = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/scripts/daily-ai-digest-newsletter"
headers = {"Authorization": "Bearer " + TOKEN, "Content-Type": "multipart/form-data; boundary=" + boundary}
req = urllib.request.Request(url, data=body, headers=headers, method="PUT")
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        success = result.get("success", False)
        print("Worker deploy success:", success)
        if success:
            print("Worker deployed!")
        else:
            print("Errors:", json.dumps(result.get("errors", []), indent=2))
except urllib.error.HTTPError as e:
    print("Worker deploy failed " + str(e.code) + ": " + e.read().decode()[:300])
    sys.exit(1)

print("")
print("=== Bindings included in deploy ===")

# Check if D1 binding exists, if not warn
print("")
print("=== Checking D1 binding ===")
url_check = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/scripts/daily-ai-digest-newsletter/bindings"
req_check = urllib.request.Request(url_check, headers={"Authorization": "Bearer " + TOKEN}, method="GET")
try:
    with urllib.request.urlopen(req_check, timeout=30) as resp:
        bresult = json.loads(resp.read())
        bindings = bresult.get("result", [])
        has_d1 = any(b.get("type") == "d1" for b in bindings)
        print("D1 binding:", "OK" if has_d1 else "MISSING - add in dashboard")
        for b in bindings:
            print("  ", b.get("type"), b.get("name"))
except Exception as e:
    print("Check failed:", str(e)[:100])

print("")
print("=== DONE ===")

# Check routes
print("")
print("=== Checking routes ===")
# Enable workers.dev subdomain for this worker
url4 = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/scripts/daily-ai-digest-newsletter/subdomain"
body4 = json.dumps({"enabled": True}).encode()
req4 = urllib.request.Request(url4, data=body4, headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json"}, method="POST")
try:
    with urllib.request.urlopen(req4, timeout=30) as resp:
        result4 = json.loads(resp.read())
        print("Subdomain enable:", json.dumps(result4, indent=2)[:300])
except urllib.error.HTTPError as e:
    print("Subdomain error " + str(e.code) + ": " + e.read().decode()[:200])

# Also check account-level subdomain
print("")
print("=== Account subdomain ===")
url5 = "https://api.cloudflare.com/client/v4/accounts/" + ACCOUNT_ID + "/workers/subdomain"
req5 = urllib.request.Request(url5, headers={"Authorization": "Bearer " + TOKEN})
try:
    with urllib.request.urlopen(req5, timeout=30) as resp:
        result5 = json.loads(resp.read())
        subdomain = result5.get("result", {}).get("subdomain", "unknown")
        print("Subdomain:", subdomain)
        print("Worker URL: https://daily-ai-digest-newsletter." + subdomain + ".workers.dev")
except urllib.error.HTTPError as e:
    print("Error " + str(e.code) + ": " + e.read().decode()[:200])

# Test subscribe
print("")
print("=== Test subscribe ===")
import urllib.request as ur2
try:
    body_test = json.dumps({"email": "test@example.com"}).encode()
    req_test = ur2.Request("https://daily-ai-digest-newsletter." + subdomain + ".workers.dev/api/subscribe", data=body_test, headers={"Content-Type": "application/json"}, method="POST")
    with ur2.urlopen(req_test, timeout=15) as resp:
        print("Subscribe test:", resp.read().decode()[:200])
except Exception as e:
    print("Subscribe test error:", str(e)[:200])
