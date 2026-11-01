<script lang="ts">
  import { api, download, type Note } from '#lib/api.ts';

  let notes = $state<Note[]>([]);
  let loaded = $state(false);
  let error = $state<string | null>(null);
  api<{ notes: Note[] }>('/api/notes').then((r) => (notes = r.notes))
    .catch((e) => (error = e.message)).finally(() => (loaded = true));
  const fmt = (iso: string) => new Date(iso).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' });
</script>

<div class="head">
  <h1>Meine Notizen</h1>
  <button class="btn" type="button" disabled={!notes.length}
    onclick={() => download('/api/notes/export', 'pharma-cards-notizen.md').catch((e) => (error = e.message))}>
    Als Markdown exportieren</button>
</div>
{#if error}<p class="banner" role="alert">{error}</p>{/if}
{#if loaded && !notes.length}
  <p class="muted">Noch keine Notizen. Notizen legst du unter jeder Karte an.</p>
{/if}
<ul class="list">
  {#each notes as n (n.id)}
    <li class="panel">
      <a href="/karten/{n.card_id}"><strong>{n.title}</strong> <span class="muted small">{n.card_id}</span></a>
      <p class="text">{n.note_text}</p>
      <p class="muted small">zuletzt geändert {fmt(n.updated_at)}{n.visibility === 'course' ? ' · Kursnotiz' : ''}</p>
    </li>
  {/each}
</ul>

<style>
  .head { display: flex; justify-content: space-between; align-items: center; gap: var(--sp-2); flex-wrap: wrap; margin-bottom: var(--sp-3); }
  .list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
  .text { white-space: pre-wrap; margin: 8px 0; }
  a { text-decoration: none; }
</style>
