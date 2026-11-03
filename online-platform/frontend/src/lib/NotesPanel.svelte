<script lang="ts">
  // Notizen unter der Karte: einklappbar, automatische Speicherung (1 s nach der letzten Eingabe),
  // Zeitstempel. Kursnotizen von Dozierenden werden zusätzlich angezeigt (nur lesend).
  import { api, del, post, put, type Note } from './api';

  let { cardId, open = $bindable(false) }: { cardId: string; open?: boolean } = $props();

  let notes = $state<Note[]>([]);
  let draft = $state('');
  let ownId = $state<number | null>(null);
  let saved = $state<string | null>(null);
  let saving = $state(false);
  let error = $state<string | null>(null);
  let timer: ReturnType<typeof setTimeout> | undefined;

  $effect(() => {
    const id = cardId;
    clearTimeout(timer);
    notes = []; draft = ''; ownId = null; saved = null; error = null;
    api<{ notes: Note[] }>(`/api/cards/${id}/notes`).then((r) => {
      if (id !== cardId) return;
      notes = r.notes;
      const own = r.notes.find((n) => n.own && n.visibility === 'private');
      if (own) { draft = own.note_text; ownId = own.id; saved = own.updated_at; }
    }).catch((e) => (error = e.message));
  });

  async function save() {
    saving = true; error = null;
    try {
      if (ownId === null) {
        if (!draft.trim()) return;
        const n = await post<Note>(`/api/cards/${cardId}/notes`, { note_text: draft });
        ownId = n.id; saved = n.updated_at;
      } else if (!draft.trim()) {
        await del(`/api/notes/${ownId}`);
        ownId = null; saved = null;
      } else {
        const n = await put<Note>(`/api/notes/${ownId}`, { note_text: draft });
        saved = n.updated_at;
      }
    } catch (e) {
      error = (e as Error).message;
    } finally {
      saving = false;
    }
  }

  function onInput() {
    clearTimeout(timer);
    timer = setTimeout(save, 1000);
  }

  const fmt = (iso: string) => new Date(iso).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' });
  let courseNotes = $derived(notes.filter((n) => n.visibility === 'course'));
</script>

<section class="notes panel" aria-labelledby="notes-h">
  <button class="toggle" type="button" aria-expanded={open} onclick={() => (open = !open)}>
    <h2 id="notes-h">Meine Notiz</h2>
    <span class="muted small">
      {#if saving}speichert …{:else if saved}gespeichert {fmt(saved)}{:else}noch keine Notiz{/if}
    </span>
    <span aria-hidden="true">{open ? '▾' : '▸'}</span>
  </button>
  {#if open}
    <label class="sr-only" for="note-text">Notiz zu dieser Karte</label>
    <textarea id="note-text" bind:value={draft} oninput={onInput} onblur={() => { clearTimeout(timer); save(); }}
      placeholder="Eigene Gedanken, Eselsbrücken, Fragen an die Dozierenden … (wird automatisch gespeichert)"></textarea>
    {#if error}<p class="error small" role="alert">Speichern fehlgeschlagen: {error}</p>{/if}
    {#if courseNotes.length}
      <h3 class="course-h">Hinweise der Dozierenden</h3>
      {#each courseNotes as n (n.id)}
        <blockquote>{n.note_text}<footer class="muted small">{fmt(n.updated_at)}</footer></blockquote>
      {/each}
    {/if}
  {/if}
</section>

<style>
  .notes { margin-top: var(--sp-3); }
  .toggle { all: unset; display: flex; align-items: baseline; gap: var(--sp-2); width: 100%; cursor: pointer; }
  .toggle h2 { margin: 0; font-size: 1rem; }
  .toggle .muted { margin-left: auto; }
  textarea { margin-top: var(--sp-2); }
  .error { color: var(--app-critical); }
  .course-h { margin-top: var(--sp-3); font-size: .95rem; }
  blockquote { margin: 0 0 var(--sp-2); padding: 8px 12px; border-left: 3px solid var(--app-primary);
    background: var(--app-surface-2); border-radius: 0 var(--radius) var(--radius) 0; white-space: pre-wrap; }
</style>
