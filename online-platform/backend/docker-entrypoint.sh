#!/bin/sh
# Start der API: Migrationen -> Kartendaten seeden (idempotent) -> Server.
set -eu
# Zuerst Konfiguration prüfen: Eine unsichere Einstellung (z. B. Header-Login in Produktion) muss
# den Container sofort beenden. Uvicorn mit mehreren Workern würde abgestürzte Worker sonst
# endlos neu starten, und der Fehlstart bliebe für Docker/Orchestrierung unsichtbar.
echo "[pharma-api] Konfiguration prüfen ..."
python -c "from app.config import load_settings; load_settings().validate()"
echo "[pharma-api] Migrationen ..."
alembic upgrade head
echo "[pharma-api] Seed (Scope + Karten) ..."
python -m app.seed
echo "[pharma-api] Start (Umgebung: ${PHARMA_ENV:-development}, Auth: ${AUTH_MODE:-local})"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 \
  --workers "${UVICORN_WORKERS:-2}" --proxy-headers --forwarded-allow-ips "*"
