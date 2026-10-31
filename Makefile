# ChemBioMed Cards / Pharma Cards — Build-Orchestrierung
# Alle Ziele rufen dieselben Skripte auf, die auch in CI laufen (reproduzierbar).

PY        ?= python3
PH_CARDS  ?= cards/PH/metadata
PH_SCOPE  ?= cards/PH/scope
REGISTRY  ?= cards/registry/cards.master.csv
HTML_OUT  ?= exports/web/ph/html
PNG_OUT   ?= exports/preview/ph
# Python mit Playwright (+ qrcode) für Rendering, Druck, Moodle-Bilder, Layoutprüfung
PYR       ?= $(PY)

.PHONY: help ph-validate ph-registry ph-registry-check ph-render ph-render-png \
        ph-output-check ph-release-check ph-review-report ph-layout-check \
        ph-moodle ph-moodle-preview ph-print ph-print-preview ph-test ph-all registry-validate \
        app-test app-web app-e2e

help:
	@echo "Pharma Cards (PH) Ziele:"
	@echo "  make ph-validate        - PH-Kartendaten gegen Schema + Scope prüfen"
	@echo "  make ph-registry        - ph_*-Zeilen in $(REGISTRY) aus YAML aktualisieren"
	@echo "  make ph-registry-check  - prüft, ob die Registry aktuell ist (CI-Gate)"
	@echo "  make ph-render          - Vorder-/Rückseiten als HTML erzeugen"
	@echo "  make ph-render-png      - zusätzlich PNG/PDF (braucht Playwright+Chromium)"
	@echo "  make ph-output-check    - erzeugte Ausgabe + Export-Gating prüfen"
	@echo "  make ph-release-check   - Export-Gating hart (nur approved/reviewed) erzwingen"
	@echo "  make ph-review-report   - Liste offener Reviews mit Prüfschwerpunkten erzeugen"
	@echo "  make ph-layout-check    - Überlauf + Sicherheitszone in Chromium messen (Report)"
	@echo "  make ph-moodle          - Moodle-Pakete, nur freigegebene Karten -> dist/moodle"
	@echo "  make ph-moodle-preview  - Moodle-Vorschau inkl. Karten im Review -> dist/preview"
	@echo "  make ph-print           - Druckpakete, nur freigegebene Karten -> dist/print"
	@echo "  make ph-print-preview   - Druckvorschau mit ENTWURF-Wasserzeichen -> dist/preview"
	@echo "  make ph-test            - Tests der Pharma-Pipeline (pytest)"
	@echo "  make ph-all             - validate -> registry -> render -> output-check"
	@echo "  make registry-validate  - bestehender Registry-CSV-Validator (alle Module)"
	@echo "  make app-test           - Tests der Online-API (pytest, SQLite)"
	@echo "  make app-web            - Frontend prüfen und bauen (svelte-check, vite build)"
	@echo "  make app-e2e URL=...    - Browser-Smoke-Test gegen laufende Instanz"

ph-validate:
	$(PY) scripts/pharma/validate_ph_cards.py --cards $(PH_CARDS) --scope $(PH_SCOPE)

ph-registry:
	$(PY) scripts/pharma/build_registry.py --cards $(PH_CARDS) --csv $(REGISTRY)

ph-registry-check:
	$(PY) scripts/pharma/build_registry.py --cards $(PH_CARDS) --csv $(REGISTRY) --check

ph-render:
	$(PY) scripts/pharma/render_cards.py --cards $(PH_CARDS) --scope $(PH_SCOPE) --out $(HTML_OUT)

ph-render-png:
	$(PY) scripts/pharma/render_cards.py --cards $(PH_CARDS) --scope $(PH_SCOPE) \
		--out $(HTML_OUT) --png --pdf --png-out $(PNG_OUT)

ph-output-check:
	$(PY) scripts/pharma/validate_output.py --cards $(PH_CARDS) --html $(HTML_OUT)

ph-release-check:
	$(PY) scripts/pharma/validate_output.py --cards $(PH_CARDS) --html $(HTML_OUT) --require-exportable

ph-review-report:
	$(PY) scripts/pharma/review_report.py --cards $(PH_CARDS) --out docs/pharma-cards/reports/cards_review_needed.md

ph-layout-check:
	$(PYR) scripts/pharma/check_layout.py --cards $(PH_CARDS) --strict

ph-moodle:
	$(PYR) scripts/pharma/generate_moodle_import.py --cards $(PH_CARDS)

ph-moodle-preview:
	$(PYR) scripts/pharma/generate_moodle_import.py --cards $(PH_CARDS) --preview

ph-print: ph-layout-check
	$(PYR) scripts/pharma/generate_print_sheets.py --cards $(PH_CARDS)

ph-print-preview:
	$(PYR) scripts/pharma/generate_print_sheets.py --cards $(PH_CARDS) --preview

ph-test:
	$(PYR) -m pytest scripts/pharma/tests -q

registry-validate:
	$(PY) scripts/validate_card_metadata.py --csv $(REGISTRY)

ph-all: ph-validate ph-registry ph-render ph-output-check ph-review-report registry-validate
	@echo "Pharma-Cards-Pipeline durchlaufen."

# ---- Online-Lernsystem (online-platform/) ----
URL ?= http://127.0.0.1:8000

app-test:
	cd online-platform/backend && $(PYR) -m pytest tests -q

app-web:
	cd online-platform/frontend && npm ci && npm run check && npm run build

app-e2e:
	$(PYR) online-platform/e2e/smoke.py --url $(URL)
