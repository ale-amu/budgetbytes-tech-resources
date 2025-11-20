 #!/usr/bin/env bash
set -euo pipefail

BASE=http://localhost:8080

echo "Running smoke test..."

# 1. Health
echo "Checking /health..."
curl -fsS "${BASE}/health" | jq . || { echo "Health check failed"; exit 1; }

# 2. Create a tiny file and upload
TMPFILE=$(mktemp /tmp/ait-XXXX.txt)
echo "Test Resource $(date --iso-8601=seconds)" > "$TMPFILE"

echo "Uploading test file..."
RESP=$(curl -s -w "\n%{http_code}" -X POST "${BASE}/api/v1/upload" -F "file=@${TMPFILE}")
BODY=$(echo "$RESP" | sed '$d')
CODE=$(echo "$RESP" | tail -n1)
echo "Status: $CODE"
echo "Response: $BODY"

if [ "$CODE" != "200" ]; then
  echo "Upload failed (code $CODE): $BODY"
  exit 1
fi

URL=$(echo "$BODY" | jq -r '.url')
if [ -z "$URL" ] || [ "$URL" == "null" ]; then
  echo "No URL returned from upload"
  exit 1
fi
echo "Uploaded to $URL"

# 3. Gallery
echo "Checking gallery..."
curl -fsS "${BASE}/api/v1/gallery" | jq . || { echo "Gallery check failed"; exit 1; }

echo "Smoke test passed!"
