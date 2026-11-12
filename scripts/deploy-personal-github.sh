#!/usr/bin/env bash
# One-time: host the site on personal GitHub (sushmita119), then switch back to Alef.
set -euo pipefail

REPO_NAME="${REPO_NAME:-parth-susmita-wedding}"
PERSONAL_USER="${PERSONAL_USER:-sushmita119}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> Active GitHub account:"
gh auth status -h github.com | sed -n '1,4p'

ACTIVE="$(gh api user -q .login 2>/dev/null || true)"
if [[ "$ACTIVE" != "$PERSONAL_USER" ]]; then
  echo ""
  echo "You are logged in as: ${ACTIVE:-unknown}"
  echo "Run this first (browser only — no password in terminal):"
  echo "  gh auth login -h github.com"
  echo "  → GitHub.com → HTTPS → Login with a web browser → add account ${PERSONAL_USER}"
  echo "  gh auth switch -h github.com -u ${PERSONAL_USER}"
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "==> Committing local changes on main..."
  git add -A
  git commit -m "chore: sync site for GitHub Pages"
fi

if ! git remote get-url origin &>/dev/null; then
  echo "==> Creating ${PERSONAL_USER}/${REPO_NAME} and pushing main..."
  gh repo create "$REPO_NAME" \
    --public \
    --source=. \
    --remote=origin \
    --push \
    --description "Wedding invitation site (static)"
else
  echo "==> Pushing to origin main..."
  git push -u origin main
fi

echo "==> Enabling GitHub Pages (GitHub Actions workflow)..."
gh api -X POST "repos/${PERSONAL_USER}/${REPO_NAME}/pages" \
  -f build_type=workflow \
  -f source[branch]=main \
  -f source[path]=/ 2>/dev/null || \
  gh api -X PUT "repos/${PERSONAL_USER}/${REPO_NAME}/pages" \
  -f build_type=workflow || true

echo ""
echo "==> Done. Site will be live after the Pages workflow runs (1–3 min):"
echo "    https://${PERSONAL_USER}.github.io/${REPO_NAME}/"
echo "    Check: gh run list -R ${PERSONAL_USER}/${REPO_NAME}"
echo ""
echo "==> Switch back to Alef (keep personal only on GitHub, not on this Mac):"
echo "    gh auth switch -h github.com -u sushmita-mukherjee-alef"
echo "    gh auth status"
