# ChemBioMed Cards – reproduzierbarer Build (docs/concept/06-generation-pipeline.md)
PY ?= python3

.PHONY: help validate cards cards-force reports build clean

help:
	@echo "make validate     – Kartendaten gegen Schema und Projektregeln prüfen"
	@echo "make cards        – geänderte Karten rendern (PNG/PDF/SVG/Vorschau)"
	@echo "make cards-force  – alle Karten neu rendern"
	@echo "make reports      – Review-Bericht erzeugen"
	@echo "make build        – validate + cards + reports"

validate:
	$(PY) scripts/validate_cards.py

cards:
	$(PY) scripts/generate_cards.py

cards-force:
	$(PY) scripts/generate_cards.py --force

reports:
	$(PY) scripts/report_review_status.py
	$(PY) scripts/update_master_directory.py

build: validate cards reports

clean:
	rm -rf generated/individual generated/manifest.json
