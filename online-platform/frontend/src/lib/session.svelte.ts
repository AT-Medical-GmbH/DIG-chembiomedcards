// Sitzungszustand der SPA (Svelte-5-Runes). Im lokalen Entwicklungsmodus lässt sich eine
// Test-Identität wählen; sie wird nur im Browser gespeichert (localStorage, mit Fallback).
// Im OIDC-Modus hält `authConfig` die öffentliche Anmeldekonfiguration (aus /api/auth/config).
import type { AuthConfig } from './oidc';

export type DevUser = { subject: string; role: string; label: string };

export const DEV_USERS: DevUser[] = [
  { subject: 'lernende@example.org', role: 'learner', label: 'Lernende' },
  { subject: 'dozent@example.org', role: 'teacher', label: 'Dozent' },
  { subject: 'reviewer-pharm@example.org', role: 'reviewer_pharm', label: 'Fachreview Pharmakologie' },
  { subject: 'reviewer-tox@example.org', role: 'reviewer_tox', label: 'Fachreview Toxikologie' },
  { subject: 'admin@example.org', role: 'admin', label: 'Admin' }
];
const KEY = 'pc_dev_user';

function stored(): DevUser {
  try {
    const s = localStorage.getItem(KEY);
    const found = DEV_USERS.find((u) => u.subject === s);
    if (found) return found;
  } catch { /* privater Modus o. Ä. */ }
  return DEV_USERS[0];
}

class Session {
  authMode = $state<'local' | 'oidc' | 'unknown'>('unknown');
  user = $state<DevUser>(stored());
  authConfig = $state<AuthConfig | null>(null);
  needsLogin = $state(false);
  ltiExpired = $state(false);
  viaLti = $state(false);                 // Sitzung stammt aus einem Moodle-Start
  ltiCourse = $state<string | null>(null);
  me = $state<{ role: string; can_review: boolean; sees_unreviewed: boolean; dev_show_unreviewed: boolean; disclaimer: string } | null>(null);
  version = $state(0);  // erhöht sich beim Identitätswechsel -> Seiten laden neu

  setUser(u: DevUser) {
    this.user = u;
    try { localStorage.setItem(KEY, u.subject); } catch { /* */ }
    this.version += 1;
  }
}

export const session = new Session();
