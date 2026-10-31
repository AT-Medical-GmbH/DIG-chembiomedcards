// API-Client der Pharma Cards SPA. Im lokalen Entwicklungsmodus wird die gewählte Test-Identität
// als X-User/X-Role mitgeschickt; im Betrieb (OIDC) ein Bearer-Token (bei Bedarf erneuert).
import { accessToken, clearTokens } from './oidc';
import { session } from './session.svelte';

export type Progress = {
  status: string; flags: string[]; leitner_box: number; ease_factor: number;
  interval_days: number; repetitions: number; lapses: number;
  next_due_at: string | null; last_reviewed_at: string | null; last_rating: string | null;
};
export type CardSummary = {
  card_id: string; title: string; subtitle: string | null; card_type: string;
  warning_level: 'low' | 'moderate' | 'high' | 'critical'; review_status: string; draft: boolean;
  version: string; primary_category: string | null; drug_class: string | null; tags: string[];
  progress: Progress | null;
};
export type BackSection = { key: string; label: string; color_role: string; text: string };
export type CardDetail = CardSummary & {
  front_type: string; front_content: Record<string, string>; back_sections: BackSection[];
  secondary_categories: string[]; substance_name: string | null; antidote: string | null;
  toxidrome: string | null; related_cards: string[]; learning_objectives: string[]; disclaimer: string;
};
export type Note = {
  id: number; card_id: string; note_text: string; annotation_data: unknown; visibility: string;
  own: boolean; created_at: string; updated_at: string; title?: string;
};
export type Rating = 'again' | 'hard' | 'good' | 'easy';

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function headers(extra: Record<string, string> = {}): Promise<Record<string, string>> {
  const h: Record<string, string> = { ...extra };
  if (session.authMode === 'local') {
    h['X-User'] = session.user.subject;
    h['X-Role'] = session.user.role;
  } else if (session.authMode === 'oidc') {
    const t = await accessToken();
    if (t) h['Authorization'] = `Bearer ${t}`;
  }
  return h;
}

/** 401 im OIDC-Modus: Sitzung abgelaufen -> Tokens verwerfen, Layout bietet Anmeldung an. */
function unauthorized(res: Response) {
  if (res.status === 401 && session.authMode === 'oidc') {
    clearTokens();
    session.needsLogin = true;
  }
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: await headers({ ...(init.body ? { 'Content-Type': 'application/json' } : {}),
                             ...(init.headers as Record<string, string> | undefined) })
  });
  unauthorized(res);
  if (!res.ok) {
    let msg = `${res.status} ${res.statusText}`;
    try { const j = await res.json(); if (j?.detail) msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail); } catch { /* kein JSON */ }
    throw new ApiError(res.status, msg);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const post = <T>(path: string, body: unknown) => api<T>(path, { method: 'POST', body: JSON.stringify(body) });
export const put = <T>(path: string, body: unknown) => api<T>(path, { method: 'PUT', body: JSON.stringify(body) });
export const del = (path: string) => api<void>(path, { method: 'DELETE' });

/** Download mit Auth-Headern (ein normaler Link könnte die Header nicht mitsenden). */
export async function download(path: string, fallbackName: string): Promise<void> {
  const res = await fetch(path, { headers: await headers() });
  unauthorized(res);
  if (!res.ok) {
    let msg = `${res.status}`;
    try { msg = (await res.json()).detail ?? msg; } catch { /* */ }
    throw new ApiError(res.status, msg);
  }
  const disp = res.headers.get('Content-Disposition') ?? '';
  const name = /filename="([^"]+)"/.exec(disp)?.[1] ?? fallbackName;
  const url = URL.createObjectURL(await res.blob());
  const a = Object.assign(document.createElement('a'), { href: url, download: name });
  document.body.append(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

let cssCache: Promise<string> | null = null;
/** Karten-CSS (dieselbe Datei wie Druck/Moodle), für das Shadow DOM aufbereitet. */
export function cardCss(): Promise<string> {
  cssCache ??= fetch('/api/assets/card.css').then((r) => r.text())
    .then((css) => css.replaceAll(':root', ':host'));
  return cssCache;
}

export const ratingLabel: Record<Rating, string> = {
  again: 'Wiederholen', hard: 'Unsicher', good: 'Gelernt', easy: 'Beherrscht'
};
export const statusLabel: Record<string, string> = {
  new: 'neu', learning: 'gelernt', unsure: 'unsicher', repeat: 'wiederholen', mastered: 'beherrscht'
};
export const flagLabel: Record<string, string> = {
  favorit: 'Favorit', klinisch_wichtig: 'Klinisch wichtig', pruefungsrelevant: 'Prüfungsrelevant', spaeter: 'Später'
};
export const warnLabel: Record<string, string> = {
  low: 'niedrig', moderate: 'mittel', high: 'hoch', critical: 'kritisch'
};
