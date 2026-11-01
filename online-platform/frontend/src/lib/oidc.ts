// Browser-Anmeldung über Authentik: OAuth 2.0 Authorization Code + PKCE (S256), öffentlicher Client.
//
// Ablauf: login() erzeugt code_verifier, state und nonce (sessionStorage) und leitet zum
// authorization_endpoint. /auth/callback ruft handleCallback(): state prüfen, Code über die API
// (/api/auth/token) tauschen, nonce im id_token prüfen, Tokens in sessionStorage ablegen.
// Tokens liegen nur in sessionStorage (pro Tab, endet mit dem Tab) – nie in localStorage.
// Die Signaturprüfung der Tokens übernimmt die API bei jedem Aufruf (JWKS).

export type AuthConfig = {
  mode: 'oidc'; client_id: string; redirect_uri: string; post_logout_redirect_uri: string | null;
  scope: string; authorization_endpoint: string; end_session_endpoint: string | null;
};
type Tokens = { access_token: string; id_token?: string; refresh_token?: string; expires_at: number };

const K_TOKENS = 'pc_oidc_tokens';
const K_FLOW = 'pc_oidc_flow';

function store(): Storage | null {
  try { return window.sessionStorage; } catch { return null; }
}

function b64url(bytes: Uint8Array): string {
  let s = '';
  bytes.forEach((b) => (s += String.fromCharCode(b)));
  return btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function random(n = 32): string {
  const a = new Uint8Array(n);
  crypto.getRandomValues(a);
  return b64url(a);
}

async function challenge(verifier: string): Promise<string> {
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(verifier));
  return b64url(new Uint8Array(digest));
}

function claims(jwt: string | undefined): Record<string, unknown> {
  if (!jwt) return {};
  try {
    const part = jwt.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    return JSON.parse(decodeURIComponent(escape(atob(part))));
  } catch { return {}; }
}

export function loadTokens(): Tokens | null {
  try {
    const raw = store()?.getItem(K_TOKENS);
    return raw ? (JSON.parse(raw) as Tokens) : null;
  } catch { return null; }
}

function saveTokens(t: { access_token: string; id_token?: string; refresh_token?: string; expires_in?: number }, prev?: Tokens | null) {
  const tokens: Tokens = {
    access_token: t.access_token,
    id_token: t.id_token ?? prev?.id_token,
    refresh_token: t.refresh_token ?? prev?.refresh_token,
    expires_at: Date.now() + (t.expires_in ?? 300) * 1000
  };
  store()?.setItem(K_TOKENS, JSON.stringify(tokens));
  return tokens;
}

export function clearTokens() { store()?.removeItem(K_TOKENS); }

/** Zur Anmeldung weiterleiten; `returnTo` ist der Pfad, zu dem es danach zurückgeht. */
export async function login(cfg: AuthConfig, returnTo = '/') {
  const verifier = random(48);
  const flow = { verifier, state: random(), nonce: random(), returnTo: returnTo.startsWith('/') ? returnTo : '/' };
  store()?.setItem(K_FLOW, JSON.stringify(flow));
  const p = new URLSearchParams({
    response_type: 'code', client_id: cfg.client_id, redirect_uri: cfg.redirect_uri, scope: cfg.scope,
    state: flow.state, nonce: flow.nonce, code_challenge: await challenge(verifier), code_challenge_method: 'S256'
  });
  window.location.assign(`${cfg.authorization_endpoint}?${p}`);
}

async function tokenRequest(body: Record<string, string>) {
  const res = await fetch('/api/auth/token', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
  });
  const j = await res.json().catch(() => ({}));
  if (!res.ok || !j.access_token) throw new Error(j.error ? `Anmeldung fehlgeschlagen (${j.error})` : `Anmeldung fehlgeschlagen (${res.status})`);
  return j;
}

/** Auf /auth/callback: Code tauschen. Gibt den Rücksprungpfad zurück. */
export async function handleCallback(cfg: AuthConfig, url: URL): Promise<string> {
  const raw = store()?.getItem(K_FLOW);
  store()?.removeItem(K_FLOW);                       // Flow ist einmalig
  const flow = raw ? JSON.parse(raw) as { verifier: string; state: string; nonce: string; returnTo: string } : null;
  const err = url.searchParams.get('error');
  if (err) throw new Error(`Anmeldung abgebrochen (${err})`);
  if (!flow || url.searchParams.get('state') !== flow.state) throw new Error('Anmeldung ungültig (state). Bitte erneut anmelden.');
  const code = url.searchParams.get('code');
  if (!code) throw new Error('Anmeldung ungültig (kein Code).');
  const t = await tokenRequest({ grant_type: 'authorization_code', code, code_verifier: flow.verifier, redirect_uri: cfg.redirect_uri });
  if (claims(t.id_token).nonce !== flow.nonce) throw new Error('Anmeldung ungültig (nonce). Bitte erneut anmelden.');
  saveTokens(t);
  return flow.returnTo;
}

let refreshing: Promise<Tokens | null> | null = null;

/** Gültiges Access-Token (bei Bedarf per Refresh-Token erneuert) oder null. */
export async function accessToken(): Promise<string | null> {
  const t = loadTokens();
  if (!t) return null;
  if (t.expires_at - Date.now() > 30_000) return t.access_token;
  if (!t.refresh_token) return null;
  refreshing ??= tokenRequest({ grant_type: 'refresh_token', refresh_token: t.refresh_token })
    .then((n) => saveTokens(n, t))
    .catch(() => { clearTokens(); return null; })
    .finally(() => { refreshing = null; });
  return (await refreshing)?.access_token ?? null;
}

export function displayName(): string | null {
  const c = claims(loadTokens()?.id_token);
  return (c.name as string) || (c.preferred_username as string) || (c.email as string) || null;
}

export function logout(cfg: AuthConfig) {
  const idToken = loadTokens()?.id_token;
  clearTokens();
  if (cfg.end_session_endpoint) {
    const p = new URLSearchParams({ client_id: cfg.client_id });
    if (idToken) p.set('id_token_hint', idToken);
    if (cfg.post_logout_redirect_uri) p.set('post_logout_redirect_uri', cfg.post_logout_redirect_uri);
    window.location.assign(`${cfg.end_session_endpoint}?${p}`);
  } else {
    window.location.assign('/');
  }
}
