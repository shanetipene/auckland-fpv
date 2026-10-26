#!/usr/bin/env bash
# Deploy the Auckland FPV site to Cloudflare Pages.
# Token is read from a local file so it never appears in chat or shell history.
set -euo pipefail

SITE_DIR="$HOME/.hermes/workspace/fpv-auckland"
TOKEN_FILE="${CLOUDFLARE_TOKEN_FILE:-$HOME/.config/wrangler/pages-token}"
PROJECT="${CF_PAGES_PROJECT:-auckland-fpv}"
export PATH="$HOME/.npm-global/bin:$PATH"

if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "No token found at $TOKEN_FILE"
  echo "Create a Cloudflare API token with: Account > Cloudflare Pages > Edit, and Account > Account Settings > Read"
  echo "Then:  install -m 600 /dev/null $TOKEN_FILE  &&  printf '%s' 'YOUR_TOKEN' > $TOKEN_FILE"
  exit 1
fi

# fail loudly if the file is world-readable
perms=$(stat -c '%a' "$TOKEN_FILE")
if [[ "$perms" != "600" && "$perms" != "400" ]]; then
  echo "Refusing to use $TOKEN_FILE: permissions are $perms, expected 600. Run: chmod 600 $TOKEN_FILE"
  exit 1
fi

export CLOUDFLARE_API_TOKEN="$(tr -d '[:space:]' < "$TOKEN_FILE")"

if [[ -z "$CLOUDFLARE_API_TOKEN" ]]; then
  echo "Token file is empty."
  exit 1
fi

cd "$SITE_DIR"
rm -rf dist && mkdir -p dist
cp index.html central.html east.html north.html west.html south.html .nojekyll dist/
cp -r assets dist/

echo "Verifying token..."
wrangler whoami

echo "Deploying dist/ to Cloudflare Pages ($PROJECT)..."
wrangler pages deploy --project-name="$PROJECT" --branch=main --commit-dirty=true

echo
echo "Live at: https://$PROJECT.pages.dev"
