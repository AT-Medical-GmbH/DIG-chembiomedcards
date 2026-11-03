"""Konfiguration der Pharma Cards API (ausschließlich über Umgebungsvariablen).

Sicherheitsregeln werden beim Start erzwungen (`validate`):
- In Produktion ist der lokale Header-Login (AUTH_MODE=local) verboten.
- In Produktion dürfen ungeprüfte Karten nicht für Lernende sichtbar sein.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

ROLES = ("learner", "teacher", "reviewer_pharm", "reviewer_tox", "editor", "admin")
REVIEW_ROLES = {"reviewer_pharm", "reviewer_tox", "editor", "admin"}


def _bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name)
    return default if v is None else v.strip().lower() in {"1", "true", "yes", "on"}


def _path(name: str, default: Path) -> Path:
    v = os.environ.get(name)
    return Path(v) if v else default


def _role_map(raw: str) -> dict[str, str]:
    """'pharma-admin:admin,pharma-reviewer-tox:reviewer_tox' -> {gruppe: rolle}."""
    out = {}
    for pair in filter(None, (p.strip() for p in raw.split(","))):
        group, _, role = pair.partition(":")
        if role in ROLES:
            out[group.strip()] = role
    return out


@dataclass(frozen=True)
class Settings:
    env: str = "development"
    database_url: str = "sqlite:///./pharma_cards.db"
    auth_mode: str = "local"                     # local | oidc
    show_unreviewed: bool = False                # nur Entwicklung: Entwürfe für alle sichtbar
    bootstrap_admin: str | None = None           # E-Mail, die im lokalen Modus Admin wird
    daily_goal: int = 20
    cards_dir: Path = REPO_ROOT / "cards/PH/metadata"
    scope_dir: Path = REPO_ROOT / "cards/PH/scope"
    css_path: Path = REPO_ROOT / "card-system/templates/pharma/card.css"
    pipeline_dir: Path = REPO_ROOT / "scripts/pharma"
    frontend_dist: Path | None = None
    cors_origins: tuple[str, ...] = ()
    oidc_issuer: str | None = None
    oidc_audience: str | None = None
    oidc_jwks_url: str | None = None
    oidc_role_claim: str = "groups"
    oidc_role_map: dict[str, str] = field(default_factory=dict)
    # Browser-Anmeldung der SPA (Authorization Code + PKCE, öffentlicher Client ohne Secret)
    oidc_client_id: str | None = None
    oidc_redirect_uri: str | None = None         # https://<host>/auth/callback
    oidc_post_logout_uri: str | None = None      # https://<host>/
    oidc_scopes: str = "openid profile email offline_access"
    oidc_discovery_url: str | None = None        # Standard: <issuer>/.well-known/openid-configuration
    # Moodle LTI 1.3 (Launch + Deep Linking)
    public_url: str | None = None                # https://pharma.at-medical.de (ohne / am Ende)
    lti_enabled: bool = False
    lti_platforms: tuple[dict, ...] = ()         # [{issuer, client_id, deployment_ids, auth_login_url, jwks_url}]
    lti_key_file: Path | None = None             # privater RSA-Schlüssel des Tools (PEM, Secret-Mount)
    lti_kid: str = "pharma-cards-lti-1"
    lti_session_hours: int = 4

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    def validate(self) -> None:
        if self.auth_mode not in {"local", "oidc"}:
            raise RuntimeError(f"AUTH_MODE muss 'local' oder 'oidc' sein, nicht {self.auth_mode!r}")
        if self.is_production and self.auth_mode == "local":
            raise RuntimeError("AUTH_MODE=local ist in Produktion verboten (Header-Login ohne Prüfung).")
        if self.is_production and self.show_unreviewed:
            raise RuntimeError("PHARMA_SHOW_UNREVIEWED ist in Produktion verboten "
                               "(ungeprüfte medizinische Inhalte).")
        if self.auth_mode == "oidc" and not (self.oidc_issuer and self.oidc_jwks_url):
            raise RuntimeError("AUTH_MODE=oidc braucht OIDC_ISSUER und OIDC_JWKS_URL.")
        if self.auth_mode == "oidc" and not (self.oidc_client_id and self.oidc_redirect_uri):
            raise RuntimeError("AUTH_MODE=oidc braucht OIDC_CLIENT_ID und OIDC_REDIRECT_URI "
                               "(Browser-Anmeldung).")
        if self.is_production and self.oidc_redirect_uri and \
                not self.oidc_redirect_uri.startswith("https://"):
            raise RuntimeError("OIDC_REDIRECT_URI muss in Produktion https verwenden.")

        if self.lti_enabled:
            self._validate_lti()

    LTI_PLATFORM_KEYS = ("issuer", "client_id", "deployment_ids", "auth_login_url", "jwks_url")

    def _validate_lti(self) -> None:
        if not self.public_url:
            raise RuntimeError("LTI braucht PHARMA_PUBLIC_URL.")
        if self.is_production and not self.public_url.startswith("https://"):
            raise RuntimeError("PHARMA_PUBLIC_URL muss in Produktion https verwenden.")
        if not self.lti_key_file or not Path(self.lti_key_file).is_file():
            raise RuntimeError("LTI braucht LTI_KEY_FILE (privater Tool-Schlüssel, PEM).")
        if not self.lti_platforms:
            raise RuntimeError("LTI braucht mindestens eine Plattform in LTI_PLATFORMS.")
        for p in self.lti_platforms:
            missing = [k for k in self.LTI_PLATFORM_KEYS if not p.get(k)]
            if missing:
                raise RuntimeError(f"LTI-Plattform unvollständig: {', '.join(missing)}")

    @property
    def lti_issuer(self) -> str:
        """Aussteller der App-Sitzungstoken nach einem LTI-Start."""
        return f"{(self.public_url or '').rstrip('/')}/lti"

    @property
    def discovery_url(self) -> str | None:
        if self.oidc_discovery_url:
            return self.oidc_discovery_url
        if not self.oidc_issuer:
            return None
        return self.oidc_issuer.rstrip("/") + "/.well-known/openid-configuration"


def load_settings() -> Settings:
    dist = os.environ.get("PHARMA_FRONTEND_DIST")
    return Settings(
        env=os.environ.get("PHARMA_ENV", "development"),
        database_url=os.environ.get("DATABASE_URL", "sqlite:///./pharma_cards.db"),
        auth_mode=os.environ.get("AUTH_MODE", "local"),
        show_unreviewed=_bool("PHARMA_SHOW_UNREVIEWED"),
        bootstrap_admin=os.environ.get("PHARMA_BOOTSTRAP_ADMIN") or None,
        daily_goal=int(os.environ.get("PHARMA_DAILY_GOAL", "20")),
        cards_dir=_path("PHARMA_CARDS_DIR", REPO_ROOT / "cards/PH/metadata"),
        scope_dir=_path("PHARMA_SCOPE_DIR", REPO_ROOT / "cards/PH/scope"),
        css_path=_path("PHARMA_CSS_PATH", REPO_ROOT / "card-system/templates/pharma/card.css"),
        pipeline_dir=_path("PHARMA_PIPELINE_DIR", REPO_ROOT / "scripts/pharma"),
        frontend_dist=Path(dist) if dist else None,
        cors_origins=tuple(o for o in os.environ.get("CORS_ORIGINS", "").split(",") if o),
        oidc_issuer=os.environ.get("OIDC_ISSUER") or None,
        oidc_audience=os.environ.get("OIDC_AUDIENCE") or None,
        oidc_jwks_url=os.environ.get("OIDC_JWKS_URL") or None,
        oidc_role_claim=os.environ.get("OIDC_ROLE_CLAIM", "groups"),
        oidc_role_map=_role_map(os.environ.get("OIDC_ROLE_MAP", "")),
        oidc_client_id=os.environ.get("OIDC_CLIENT_ID") or None,
        oidc_redirect_uri=os.environ.get("OIDC_REDIRECT_URI") or None,
        oidc_post_logout_uri=os.environ.get("OIDC_POST_LOGOUT_URI") or None,
        oidc_scopes=os.environ.get("OIDC_SCOPES", "openid profile email offline_access"),
        oidc_discovery_url=os.environ.get("OIDC_DISCOVERY_URL") or None,
        public_url=(os.environ.get("PHARMA_PUBLIC_URL") or "").rstrip("/") or None,
        lti_enabled=_bool("LTI_ENABLED"),
        lti_platforms=tuple(json.loads(os.environ.get("LTI_PLATFORMS") or "[]")),
        lti_key_file=Path(os.environ["LTI_KEY_FILE"]) if os.environ.get("LTI_KEY_FILE") else None,
        lti_kid=os.environ.get("LTI_KID", "pharma-cards-lti-1"),
        lti_session_hours=int(os.environ.get("LTI_SESSION_HOURS", "4")),
    )
