#!/usr/bin/env bash
# Phase 4 – Repository samt Issues, Pull Requests, Labels, Meilensteinen und Releases von GitHub
# nach Forgejo übernehmen (Forgejo-Migrations-API) und den Stand prüfen.
#
#   FORGEJO_URL=https://git.at-medical.de \
#   FORGEJO_TOKEN_FILE=~/.secrets/forgejo-admin-token \
#   GITHUB_TOKEN_FILE=~/.secrets/github-readonly-token \
#   bash deploy/scripts/10-migrate-from-github.sh
#
# Tokens werden nur aus Dateien gelesen, nie ausgegeben und nicht gespeichert.
# GitHub-Token: fein granuliert, NUR Lesezugriff (Contents, Issues, Pull requests, Metadata) auf
# dieses eine Repository; nach erfolgreicher Prüfung auf GitHub widerrufen.
# Das Skript ändert auf GitHub nichts. Ein vorhandenes Ziel-Repository wird nicht überschrieben.
set -euo pipefail

FORGEJO_URL="${FORGEJO_URL:?FORGEJO_URL fehlt}"
OWNER="${FORGEJO_OWNER:-AT-Medical-GmbH}"
REPO="${REPO:-DIG-chembiomedcards}"
SRC="${GITHUB_REPO_URL:-https://github.com/AT-Medical-GmbH/DIG-chembiomedcards.git}"
FT="$(tr -d '\r\n' < "${FORGEJO_TOKEN_FILE:?FORGEJO_TOKEN_FILE fehlt}")"
GT="$(tr -d '\r\n' < "${GITHUB_TOKEN_FILE:?GITHUB_TOKEN_FILE fehlt}")"
api() { curl -fsS -H "Authorization: token $FT" -H 'Content-Type: application/json' "$@"; }

echo "1/4 Ziel prüfen: $FORGEJO_URL/$OWNER/$REPO"
if api -o /dev/null "$FORGEJO_URL/api/v1/repos/$OWNER/$REPO" 2>/dev/null; then
  echo "Abbruch: $OWNER/$REPO existiert bereits in Forgejo – nichts verändert." >&2; exit 1
fi
api -o /dev/null "$FORGEJO_URL/api/v1/orgs/$OWNER" 2>/dev/null || {
  echo "   Organisation $OWNER anlegen (privat)"
  api -o /dev/null -X POST "$FORGEJO_URL/api/v1/orgs" \
      -d "{\"username\":\"$OWNER\",\"full_name\":\"AT Medical GmbH\",\"visibility\":\"private\"}"
}

echo "2/4 Migration starten (kann einige Minuten dauern)"
body=$(python3 - "$SRC" "$OWNER" "$REPO" "$GT" <<'PY'
import json, sys
src, owner, repo, token = sys.argv[1:]
print(json.dumps({"clone_addr": src, "service": "github", "auth_token": token,
                  "repo_owner": owner, "repo_name": repo, "private": True, "mirror": False,
                  "wiki": True, "issues": True, "labels": True, "milestones": True,
                  "pull_requests": True, "releases": True, "lfs": False}))
PY
)
api -o /dev/null -X POST "$FORGEJO_URL/api/v1/repos/migrate" --max-time 1800 -d "$body"
unset body GT

echo "3/4 Branches und Tags vergleichen (GitHub ↔ Forgejo)"
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
gh_auth="$(printf 'x-access-token:%s' "$(tr -d '\r\n' < "$GITHUB_TOKEN_FILE")" | base64 | tr -d '\n')"
fj_auth="$(printf 'migration:%s' "$FT" | base64 | tr -d '\n')"
git -c http.extraHeader="Authorization: Basic $gh_auth" ls-remote --heads --tags "$SRC" \
  | grep -v '\^{}' | sort -k2 > "$tmp/github"
git -c http.extraHeader="Authorization: Basic $fj_auth" ls-remote --heads --tags "$FORGEJO_URL/$OWNER/$REPO.git" \
  | grep -v '\^{}' | sort -k2 > "$tmp/forgejo"
if diff -u "$tmp/github" "$tmp/forgejo"; then
  echo "   identisch: $(wc -l < "$tmp/github") Branches/Tags"
else
  echo "Abweichung zwischen GitHub und Forgejo (siehe oben) – Gate G4 nicht erfüllt." >&2; exit 1
fi

echo "4/4 Übernommene Inhalte"
api "$FORGEJO_URL/api/v1/repos/$OWNER/$REPO" | python3 -c \
  'import json,sys; r=json.load(sys.stdin); print(f"   {r[\"full_name\"]}: privat={r[\"private\"]}, Issues={r[\"open_issues_count\"]}, PRs={r[\"open_pr_counter\"]}, Releases={r[\"release_counter\"]}")'
echo "✓ Migration abgeschlossen. Weiter mit Runbook Phase 4, Schritt „Push-Spiegel nach GitHub“."
