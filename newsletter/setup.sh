#!/bin/bash
# Cloudflare Newsletter Setup Script
# Run this to set up everything automatically

# Read token from local file (never commit this!)
CF_ACCOUNT_ID="e227995b424158109fb77a1de35ab083"
CF_API_KEY=$(cat ~/cf_api_token.txt | tr -d '[:space:]')

echo "=== Step 1: Creating D1 database ==="
DB_RESULT=$(curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "newsletter-db"}')

echo "$DB_RESULT"

# Extract database ID
DB_ID=$(echo "$DB_RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['uuid'])" 2>/dev/null)
echo "Database ID: $DB_ID"

if [ -z "$DB_ID" ]; then
  echo "ERROR: Failed to create database"
  exit 1
fi

echo ""
echo "=== Step 2: Running schema ==="
SCHEMA_RESULT=$(curl -s -X POST \
  "https://api.cloudflare.com/client/v4/accounts/$CF_ACCOUNT_ID/d1/database/$DB_ID/query" \
  -H "X-Auth-Key: $CF_API_KEY" \
  -H "Content-Type: application/json" \
  -d @newsletter/schema.json)
echo "$SCHEMA_RESULT"

echo ""
echo "=== Setup complete ==="
echo "Database ID: $DB_ID"
echo "Use this in your wrangler.toml"
