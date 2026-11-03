# Pharma Cards API (FastAPI). Build-Kontext ist das Repository-Root, weil die API die
# Kartendaten (cards/PH), die Scope-Konfiguration und den gemeinsamen Renderer braucht:
#   docker build -f online-platform/backend/Dockerfile -t pharma-api .
FROM python:3.12-slim

ARG WITH_PLAYWRIGHT=1
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright

WORKDIR /srv/pharma
COPY online-platform/backend/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
 && if [ "$WITH_PLAYWRIGHT" = "1" ]; then \
      pip install playwright==1.56.0 && playwright install --with-deps chromium \
      && chmod -R a+rX /opt/ms-playwright; \
    fi

# Layout wie im Repository, damit die Standardpfade in app/config.py gelten
COPY scripts/pharma/ scripts/pharma/
COPY cards/PH/metadata/ cards/PH/metadata/
COPY cards/PH/scope/ cards/PH/scope/
COPY card-system/templates/pharma/card.css card-system/templates/pharma/card.css
COPY online-platform/backend/ online-platform/backend/

RUN useradd --system --uid 10001 --home /srv/pharma pharma \
 && chmod +x online-platform/backend/docker-entrypoint.sh
USER pharma
WORKDIR /srv/pharma/online-platform/backend
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"
ENTRYPOINT ["./docker-entrypoint.sh"]
