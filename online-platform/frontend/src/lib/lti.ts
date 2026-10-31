// Sitzung aus einem Moodle-Start (LTI 1.3). Die API stellt nach geprüftem Launch ein kurzlebiges
// App-Token aus und übergibt es im URL-Fragment an /lti/start. Es liegt nur in sessionStorage
// (je Tab bzw. je Moodle-iframe) und hat Vorrang vor OIDC und lokalen Test-Identitäten.

const KEY = 'pc_lti_token';

function store(): Storage | null {
  try { return window.sessionStorage; } catch { return null; }
}

function payload(t: string): Record<string, unknown> {
  try { return JSON.parse(atob(t.split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))); } catch { return {}; }
}

export function ltiToken(): string | null {
  const t = store()?.getItem(KEY) ?? null;
  if (t && Number(payload(t).exp ?? 0) * 1000 < Date.now()) { store()?.removeItem(KEY); return null; }
  return t;
}

export function setLtiToken(t: string) { store()?.setItem(KEY, t); }
export function clearLti() { store()?.removeItem(KEY); }

/** Kurstitel aus Moodle (nur Anzeige). */
export function ltiContext(): string | null {
  const t = ltiToken();
  return t ? ((payload(t).ctx as string) ?? null) : null;
}

/** Nur relative, app-interne Ziele zulassen (kein Open Redirect). */
export function safeNext(next: string | null): string {
  return next && next.startsWith('/') && !next.startsWith('//') ? next : '/';
}
