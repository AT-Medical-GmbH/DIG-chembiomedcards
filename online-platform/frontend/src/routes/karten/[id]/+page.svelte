<script lang="ts">
  // Kartendetail: Karte (Flip), Einordnung, Lernziele, verwandte Karten, Notiz, Downloads.
  // Für Fachreview-Rollen zusätzlich Review-Protokoll und Änderungsverlauf.
  import { page } from '$app/state';
  import CardView from '$lib/CardView.svelte';
  import NotesPanel from '$lib/NotesPanel.svelte';
  import { api, download, post, statusLabel, warnLabel, type CardDetail } from '$lib/api';
  import { session } from '$lib/session.svelte';

  type Review = { id: number; review_type: string; status: string; card_version: string; notes: string | null; reviewer: string; role: string; at: string };
  type Version = { version: string; content_hash: string; changed_by: string; change_note: string | null; at: string };

  const id = page.params.id as string;
  let card = $state<CardDetail | null>(null);
  let flipped = $state(false);
  let error = $state<string | null>(null);
  let reviews = $state<Review[]>([]);
  let versions = $state<Version[]>([]);
  let rType = $state('pharmacology');
  let rStatus = $state('reviewed');
  let rNotes = $state('');
  let rMsg = $state<string | null>(null);

  api<CardDetail>(`/api/cards/${id}`).then((c) => (card = c)).catch((e) => (error = e.message));
  function loadReview() {
    if (!session.me?.can_review) return;
    api<{ reviews: Review[] }>(`/api/cards/${id}/reviews`).then((r) => (reviews = r.reviews));
    api<{ versions: Version[] }>(`/api/cards/${id}/versions`).then((r) => (versions = r.versions));
  }
  loadReview();

  async function submitReview(e: SubmitEvent) {
    e.preventDefault();
    rMsg = null;
    try {
      const r = await post<{ hinweis: string }>(`/api/cards/${id}/reviews`, { review_type: rType, status: rStatus, notes: rNotes });
      rMsg = r.hinweis; rNotes = '';
      loadReview();
    } catch (err) { rMsg = (err as Error).message; }
  }

  const fmt = (iso: string) => new Date(iso).toLocaleString('de-DE', { dateStyle: 'short', timeStyle: 'short' });
  async function dl(side: string, format: string) {
    try { await download(`/api/cards/${id}/download?side=${side}&format=${format}`, `${id}.${format}`); }
    catch (e) { error = (e as Error).message; }
  }
</script>

{#if error}
  <p class="banner" role="alert">{error}</p>
  <a href="/karten">Zurück zur Übersicht</a>
{:else if card}
  <p class="muted small"><a href="/karten">Karten</a> / {card.card_id}</p>
  <div class="title-row">
    <h1>{card.title}</h1>
    <span class="chip {card.warning_level}">Warnlevel {warnLabel[card.warning_level]}</span>
    {#if card.draft}<span class="chip draft">Entwurf · {card.review_status}</span>{/if}
    {#if card.progress}<span class="chip">{statusLabel[card.progress.status] ?? card.progress.status}</span>{/if}
  </div>

  <div class="layout">
    <div>
      <CardView cardId={card.card_id} {flipped} onflip={() => (flipped = !flipped)} />
      <div class="actions">
        <button class="btn primary" type="button" onclick={() => (flipped = !flipped)}>{flipped ? 'Vorderseite' : 'Rückseite'} zeigen</button>
        <a class="btn" href="/lernen?set=alle&category={card.primary_category}">Kategorie lernen</a>
      </div>
      <NotesPanel cardId={card.card_id} open />
    </div>

    <aside class="side">
      <section class="panel">
        <h2>Einordnung</h2>
        <dl>
          <dt>Kategorie</dt><dd>{card.primary_category}{#if card.secondary_categories.length} · {card.secondary_categories.join(', ')}{/if}</dd>
          {#if card.drug_class}<dt>Wirkstoffgruppe</dt><dd>{card.drug_class}</dd>{/if}
          {#if card.antidote}<dt>Antidot</dt><dd>{card.antidote}</dd>{/if}
          {#if card.toxidrome}<dt>Toxidrom</dt><dd>{card.toxidrome}</dd>{/if}
          <dt>Version</dt><dd>{card.version}</dd>
          <dt>Tags</dt><dd>{card.tags.join(', ') || '–'}</dd>
        </dl>
      </section>
      {#if card.learning_objectives.length}
        <section class="panel"><h2>Lernziele</h2>
          <ul>{#each card.learning_objectives as o}<li>{o}</li>{/each}</ul></section>
      {/if}
      {#if card.related_cards.length}
        <section class="panel"><h2>Verwandte Karten</h2>
          <p>{#each card.related_cards as r, i}<a href="/karten/{r}" data-sveltekit-reload>{r}</a>{i < card.related_cards.length - 1 ? ', ' : ''}{/each}</p></section>
      {/if}
      <section class="panel"><h2>Download</h2>
        <div class="dl">
          <button class="btn small" type="button" onclick={() => dl('both', 'pdf')}>PDF (beide Seiten)</button>
          <button class="btn small" type="button" onclick={() => dl('front', 'png')}>PNG vorn</button>
          <button class="btn small" type="button" onclick={() => dl('back', 'png')}>PNG hinten</button>
        </div>
      </section>

      {#if session.me?.can_review}
        <section class="panel review">
          <h2>Fachreview</h2>
          <form onsubmit={submitReview}>
            <label><span class="small muted">Prüfart</span>
              <select bind:value={rType}>
                <option value="pharmacology">Pharmakologie</option><option value="toxicology">Toxikologie</option>
                <option value="clinical_safety">Klinische Sicherheit</option><option value="editorial">Redaktion</option>
              </select></label>
            <label><span class="small muted">Ergebnis</span>
              <select bind:value={rStatus}>
                <option value="reviewed">fachlich korrekt (reviewed)</option>
                <option value="approved">Freigabe empfohlen (approved)</option>
                <option value="changes_requested">Korrektur nötig</option>
                <option value="clinical_review_needed">klinische Prüfung nötig</option>
                <option value="toxicology_review_needed">toxikologische Prüfung nötig</option>
                <option value="update_needed">Aktualisierung nötig</option>
              </select></label>
            <label><span class="small muted">Anmerkungen / Quelle</span>
              <textarea bind:value={rNotes} placeholder="Geprüfte Punkte, Korrekturvorschlag, Quelle mit Jahr"></textarea></label>
            <button class="btn primary" type="submit">Prüfung protokollieren</button>
          </form>
          {#if rMsg}<p class="small" role="status">{rMsg}</p>{/if}
          <p class="muted small">Der verbindliche Freigabestatus wird in den Kartendaten im Repository gesetzt.</p>
          {#if reviews.length}
            <h3>Protokoll</h3>
            <ul class="log">{#each reviews as r (r.id)}<li><strong>{r.status}</strong> · {r.review_type} · v{r.card_version}<br />
              <span class="muted small">{r.reviewer} ({r.role}), {fmt(r.at)}</span>{#if r.notes}<br />{r.notes}{/if}</li>{/each}</ul>
          {/if}
          {#if versions.length}
            <h3>Änderungsverlauf</h3>
            <ul class="log">{#each versions as v}<li>v{v.version} · <code>{v.content_hash}</code><br /><span class="muted small">{v.change_note} · {fmt(v.at)}</span></li>{/each}</ul>
          {/if}
        </section>
      {/if}
    </aside>
  </div>
{:else}
  <p class="muted">Lade Karte …</p>
{/if}

<style>
  .title-row { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: var(--sp-3); }
  .title-row h1 { margin: 0 8px 0 0; }
  .layout { display: grid; grid-template-columns: minmax(0, 1fr) 320px; gap: var(--sp-4); align-items: start; }
  @media (max-width: 960px) { .layout { grid-template-columns: 1fr; } }
  .actions { display: flex; gap: 8px; justify-content: center; margin-top: var(--sp-3); flex-wrap: wrap; }
  .side { display: grid; gap: var(--sp-3); }
  dl { display: grid; grid-template-columns: auto 1fr; gap: 4px 12px; margin: 0; }
  dt { color: var(--app-text-soft); font-size: .875rem; }
  dd { margin: 0; overflow-wrap: anywhere; }
  .dl { display: flex; gap: 6px; flex-wrap: wrap; }
  .review form { display: grid; gap: 8px; }
  .review label { display: grid; gap: 4px; }
  .log { padding-left: 18px; margin: 0; display: grid; gap: 8px; }
  ul { margin: 0; padding-left: 18px; }
</style>
