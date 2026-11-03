# Pharma Cards Web (SvelteKit, statisch) hinter nginx; /api wird intern an pharma-api gereicht.
#   docker build -t pharma-web online-platform/frontend
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
ENV PHARMA_API_UPSTREAM=pharma-api:8000 \
    FRAME_ANCESTORS="'self'"
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=5s CMD wget -qO- http://127.0.0.1:8080/healthz || exit 1
