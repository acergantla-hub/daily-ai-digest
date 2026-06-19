#!/bin/bash
# Deploy newsletter worker and binding to Cloudflare

set -e

ACCOUNT_ID="e227995b424158109fb77a1de35ab083"
DB_ID="c83aec15-53fd-4107-a763-8da58a8bebb5"
BASE_DIR="/data/data/com.termux/files/home/daily-ai-digest/newsletter"

echo "=== Step 1: Get token ==="
TOKEN=printf '%s' "$TOKEN" | tr -d '[:space:]')
echo "Token length: ${#TOKEN}"

echo ""
echo "=== Step 2: Check D1 database ==="
curl -s "https://api.cloudflare.com/client/v4/accounts/${ACCOUNT_ID}/d1/database/${DB_ID}" \
  -H "Authorization: Bearer ${TOKEN}" | python3 -c "import sys,json; d=json.load(sys.stdin); print('DB:', d.get('result',{}).get('name'), '| tables:', d.get('result',{}).get('num_tables'))"

echo ""
echo "=== Step 3: Deploy Worker ==="
WORKER_CODE=$(cat "${BASE_DIR}/worker.js")
METADATA='{"main_module":"index.js","compatibility_date":"2026-05-30","compatibility_flags":["nodejs_compat"],"usage_model":"bundled"}'

# Build multipart body using python to avoid shell escaping issues
python3 << 'PYEOF'
import json, urllib.request, urllib.error, os, sys

ACCOUNT_ID = "e227995b424158109fb77a1de35ab083"
DB_ID = "c83aec15-53fd-4107-a763-8da58a8bebb5"
BASE_DIR = "/data/data/com.termux/files/home/daily-ai-digest/newsletter"

# Read token - strip whitespace
tok...TOKEN = TOKEN.strip()
print(f"Token: {TOKEN[:10]}... (len={len(TOKEN)})")

worker_code = open(os.path.join(BASE_DIR, "worker.js")).read()

metadata = json.dumps({
    "main_module": "index.js",
    "compatibility_date": "2026-05-30",
    "compatibility_flags": ["nodejs_compat"],
    "usage_model": "bundled"
})

boundary = "----Boundary7MA4YWxkTrZu0gW"
body = (
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="metadata"\r\n'
    f"Content-Type: application/json\r\n\r\n"
    f"{metadata}\r\n"
    f"--{boundary}\r\n"
    f'Content-Disposition: form-data; name="index.js"; filename="index.js"\r\n'
    f"Content-Type: application/javascript\r\n\r\n"
).encode() + worker_code.encode() + f"\r\n--{boundary}--\r\n".encode()

url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/daily-ai-digest-newsletter"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": f"multipart/form-data; boundary={boundary}",
}
req = urllib.request.Request(url, data=body, headers=headers, method="PUT")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        success = result.get("success", False)
        print(f"Worker deploy success: {success}")
        if success:
            print("Worker deployed successfully!")
        else:
            print("Errors:", json.dumps(result.get("errors", []), indent=2))
except urllib.error.HTTPError as e:
    print(f"Worker deploy failed {e.code}: {e.read().decode()[:300]}")
    sys.exit(1)

# Step 4: Add D1 binding
print("\n=== Step 4: Add D1 binding ===")
url2 = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/daily-ai-digest-newsletter/bindings"
body2 = json.dumps([{
    "type": "d1",
    "name": "DB",
    "database_id": DB_ID
}]).encode()
headers2 = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}
req2 = urllib.request.Request(url2, data=body2, headers=headers2, method="PUT")
try:
    with urllib.request.urlopen(req2, timeout=30) as resp:
        result2 = json.loads(resp.read())
        print(f"D1 binding: {json.dumps(result2, indent=2)[:300]}")
except urllib.error.HTTPError as e:
    print(f"D1 binding failed {e.code}: {e.read().decode()[:300]}")

print("\n=== DONE ===")
PYEOF
