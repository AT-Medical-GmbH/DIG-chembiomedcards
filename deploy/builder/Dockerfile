# ChemBioMed Cards – Build- und Runner-Image (ADR-024)
#
# Ein Image für beides:
#   1. reproduzierbarer Karten-Build (Python, Playwright/Chromium, RDKit, Schrift Inter)
#   2. Forgejo-Runner im Host-Modus: Jobs laufen direkt in diesem Container.
#      Kein Docker-Socket, kein privilegierter Container auf ATMED-core.
#
# Bauen (im Repo-Wurzelverzeichnis):
#   docker build -f deploy/builder/Dockerfile -t chembiomed-builder:<git-sha> .
# Lokal testen:
#   docker run --rm -v "$PWD":/work -w /work chembiomed-builder:<git-sha> make build
#
# Versionen sind fest gepinnt. Aktualisieren nur zusammen mit einem Testlauf von `make cards-force`.
ARG PLAYWRIGHT_VERSION=1.56.0
FROM mcr.microsoft.com/playwright/python:v${PLAYWRIGHT_VERSION}-noble

ARG FORGEJO_RUNNER_VERSION=13.2.1
# SHA-256 des Runner-Binaries laut Release-Seite (wird beim Bauen geprüft)
ARG FORGEJO_RUNNER_SHA256=bb369fe1ecb50fdc983c0b1d993f19b0920df6e5864511892b3cdbf16d858b34

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    VIRTUAL_ENV=/opt/venv \
    PATH=/opt/venv/bin:$PATH

# Schriften (Inter für die Karten, DejaVu Mono für die Kartennummer), Build-Werkzeuge
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      fonts-inter fonts-dejavu-core fontconfig \
      git make ca-certificates curl rsync python3-venv xz-utils \
 && fc-cache -f \
 && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten in einer eigenen venv (PEP 668)
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv "$VIRTUAL_ENV" \
 && pip install --upgrade pip \
 && pip install -r /tmp/requirements.txt \
 && python -c "import playwright, rdkit, yaml, jsonschema, jinja2, qrcode, pypdf; print('deps ok')"

# Pharma Cards (Modul PH) und Lernplattform (online-platform/): pytest für die PH-Tests,
# eigene venv für die API-Tests, Node 22 LTS für Typprüfung und Build der Web-Oberfläche.
ARG NODE_VERSION=22.23.4
# SHA-256 laut https://nodejs.org/dist/v22.23.4/SHASUMS256.txt (linux-x64.tar.xz)
ARG NODE_SHA256=1805bcd35e6815559bd2eb97db438d3fdb0eb3a5e6a977b7c1badca76337e9ce
COPY online-platform/backend/requirements.txt online-platform/backend/requirements-dev.txt /tmp/api/
RUN pip install pytest==9.0.3 \
 && python3 -m venv /opt/api-venv \
 && /opt/api-venv/bin/pip install -r /tmp/api/requirements-dev.txt \
 && curl -fsSL -o /tmp/node.tar.xz "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-x64.tar.xz" \
 && echo "${NODE_SHA256}  /tmp/node.tar.xz" | sha256sum -c - \
 && tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1 \
      --exclude=CHANGELOG.md --exclude=LICENSE --exclude=README.md \
 && rm -f /tmp/node.tar.xz \
 && node --version && npm --version

# Forgejo-Runner (nur für den Betrieb als CI-Runner nötig)
RUN curl -fsSL -o /usr/local/bin/forgejo-runner \
      "https://code.forgejo.org/forgejo/runner/releases/download/v${FORGEJO_RUNNER_VERSION}/forgejo-runner-${FORGEJO_RUNNER_VERSION}-linux-amd64" \
 && if [ -n "$FORGEJO_RUNNER_SHA256" ]; then echo "$FORGEJO_RUNNER_SHA256  /usr/local/bin/forgejo-runner" | sha256sum -c -; fi \
 && chmod 0755 /usr/local/bin/forgejo-runner \
 && forgejo-runner --version

# Ohne Root arbeiten (pwuser ist im Playwright-Image angelegt)
RUN mkdir -p /data /work && chown pwuser:pwuser /data /work
USER pwuser
WORKDIR /work
