# Bauumgebung für Lern- und Druckpakete (pharma-deploy content). Wird auf ATMED-core lokal gebaut,
# der Bau selbst läuft danach als unprivilegierter Benutzer (65534) ohne Capabilities.
FROM mcr.microsoft.com/playwright/python:v1.56.0-noble
RUN apt-get update -qq \
 && apt-get install -y -qq --no-install-recommends make python3-venv \
 && rm -rf /var/lib/apt/lists/* \
 && python3 -m venv /opt/v \
 && /opt/v/bin/pip install -q --no-cache-dir pyyaml qrcode pytest playwright==1.56.0 \
 && chmod -R a+rX /opt/v
ENV PATH=/opt/v/bin:$PATH
