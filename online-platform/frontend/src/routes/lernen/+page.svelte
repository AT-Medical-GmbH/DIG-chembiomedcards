<script lang="ts">
  // Lernmodus: Karte mittig, Flip per Klick/Tap/Leertaste/Wischen, Bewertung 1–4, Markierungen,
  // Notizen, Downloads, Fokusmodus (Vollbild). Bewertung steuert SM-2 bzw. Leitner im Backend.
  import { page } from '$app/state';
  import CardView from '$lib/CardView.svelte';
  import NotesPanel from '$lib/NotesPanel.svelte';
  import { api, download, flagLabel, post, put, ratingLabel, warnLabel,
           type CardDetail, type CardSummary, type Rating } from '$lib/api';

  const setSlug = page.url.searchParams.get('set') ?? 'alle';
  const category = page.url.searchParams.get('category');
  const RATINGS: Rating[] = ['again', 'hard', 'good', 'easy'];
  const FLAGS = ['favorit', 'klinisch_wichtig', 'pruefungsrelevant'];

  let queue = $state<CardSummary[]>([]);
  let total = $state(0);
  let index = $state(0);
  let done = $state(0);
  let flipped = $state(false);
  let detail = $state<CardDetail | null>(null);
  let notesOpen = $state(false);
  let algorithm = $state<'sm2' | 'leitner'>('sm2');
  let busy = $state(false);
  let error = $state<string | null>(null);
  let message = $state<string | null>(null);
  let loaded = $state(false);
  let focus = $state(false);
  let wrap: HTMLElement;

  let current = $derived(queue[index] ?? null);
  let setName = $state(setSlug);
  api<{ content_sets: { slug: string; name: string }[]; user_sets: { slug: string; name: string }[] }>('/api/sets')
    .then((s) => { setName = [...s.content_sets, ...s.user_sets].find((x) => x.slug === setSlug)?.name ?? setSlug; })
    .catch(() => {});

  async function loadQueue() {
    try {
      const q = await api<{ total: number; cards: CardSummary[] }>(
        `/api/learn/queue?set=${setSlug}&limit=50${category ? `&category=${category}` : ''}`);
      queue = q.cards; total = q.total; index = 0; loaded = true;
    } catch (e) { error = (e as Error).message; loaded = true; }
  }
  loadQueue();

  $effect(() => {
    const c = current;
    detail = null; flipped = false;
    if (c) api<CardDetail>(`/api/cards/${c.card_id}`).then((d) => { if (current?.card_id === d.card_id) detail = d; });
  });

  async function rate(r: Rating) {
    if (!current || busy) return;
    busy = true; error = null;
    try {
      await post(`/api/progress/${current.card_id}`, { rating: r, algorithm });
      done += 1;
      index += 1;
    } catch (e) { error = (e as Error).message; } finally { busy = false; }
  }

  async function toggleFlag(f: string) {
    if (!detail) return;
    const flags = new Set(detail.progress?.flags ?? []);
    flags.has(f) ? flags.delete(f) : flags.add(f);
    try {
      const r = await put<{ progress: CardDetail['progress'] }>(`/api/progress/${detail.card_id}/flags`, { flags: [...flags] });
      detail = { ...detail, progress: r.progress };
    } catch (e) { error = (e as Error).message; }
  }

  async function dl(side: 'both' | 'front' | 'back', format: 'pdf' | 'png') {
    if (!current) return;
    message = null; error = null;
    try { await download(`/api/cards/${current.card_id}/download?side=${side}&format=${format}`, `${current.card_id}.${format}`); }
    catch (e) {
      const err = e as Error & { status?: number };
      if (err.status === 503) {
        message = 'PDF/PNG ist auf diesem Server nicht verfügbar – HTML-Version wird geladen.';
        await download(`/api/cards/${current.card_id}/download?side=${side === 'both' ? 'both' : side}&format=html`, `${current.card_id}.html`);
      } else error = err.message;
    }
  }

  async function toggleFocus() {
    focus = !focus;
    try {
      if (focus && !document.fullscreenElement) await wrap.requestFullscreen?.();
      if (!focus && document.fullscreenElement) await document.exitFullscreen();
    } catch { /* Vollbild nicht erlaubt: Fokusmodus funktioniert trotzdem */ }
  }

  function onKey(e: KeyboardEvent) {
    const t = e.target as HTMLElement;
    // In Eingabefeldern nie Kürzel auslösen (Tippen in der Notiz!).
    if (t.closest('textarea, input, select, [contenteditable]') || e.ctrlKey || e.metaKey || e.altKey) return;
    // Auf Buttons/Links behalten Leertaste und Enter ihre normale Funktion; Kürzel 1–4/N/F gelten.
    const onControl = !!t.closest('button, a');
    if ((e.key === ' ' || e.key === 'Enter') && !onControl) { e.preventDefault(); flipped = !flipped; }
    else if (flipped && ['1', '2', '3', '4'].includes(e.key)) rate(RATINGS[Number(e.key) - 1]);
    else if (e.key.toLowerCase() === 'n') notesOpen = !notesOpen;
    else if (e.key.toLowerCase() === 'f') toggleFocus();
  }

  // Wischen: Vorderseite -> umdrehen; Rückseite -> rechts „Gelernt“, links „Wiederholen“
  let startX = 0, startY = 0;
  const down = (e: PointerEvent) => { startX = e.clientX; startY = e.clientY; };
  function up(e: PointerEvent) {
    const dx = e.clientX - startX, dy = e.clientY - startY;
    if (Math.abs(dx) < 60 || Math.abs(dx) < Math.abs(dy)) return;
    if (!flipped) flipped = true;
    else rate(dx > 0 ? 'good' : 'again');
  }
</script>

<svelte:window onkeydown={onKey} />

<div class="learn" class:focus bind:this={wrap}>
  <div class="head">
    <div>
      <h1>Lernen</h1>
      <p class="muted small">Lernset: <strong>{setName}</strong>{#if category} · Kategorie: {category}{/if}</p>
    </div>
    <div class="tools">
      <label class="small muted">Verfahren
        <select bind:value={algorithm} aria-label="Wiederholungsverfahren">
          <option value="sm2">SM-2</option><option value="leitner">Leitner</option>
        </select>
      </label>
      <button class="btn small" type="button" aria-pressed={focus} onclick={toggleFocus}>Fokusmodus (F)</button>
    </div>
  </div>

  {#if error}<p class="banner" role="alert">{error}</p>{/if}
  {#if message}<p class="banner small" role="status">{message}</p>{/if}

  {#if !loaded}
    <p class="muted">Lade Lernstapel …</p>
  {:else if !current}
    <div class="panel finished">
      {#if done}
        <h2>Geschafft</h2><p>{done} Karte(n) in dieser Sitzung bewertet.</p>
      {:else}
        <h2>Nichts zu lernen</h2><p>In diesem Set gibt es gerade keine fälligen oder neuen Karten.</p>
      {/if}
      <a class="btn primary" href="/">Zur Übersicht</a>
    </div>
  {:else}
    <div class="progress" aria-label="Fortschritt {done} von {Math.min(total, queue.length)}">
      <span style:width="{(done / Math.max(1, Math.min(total, queue.length))) * 100}%"></span></div>
    <p class="muted small count">Karte {index + 1} von {Math.min(total, queue.length)}{total > queue.length ? ` (insgesamt ${total})` : ''}</p>

    {#if detail?.draft}
      <p class="banner small" role="note"><strong>Entwurf:</strong>&nbsp;fachlich noch nicht freigegeben (Status {detail.review_status}).</p>
    {/if}
    {#if detail && (detail.warning_level === 'high' || detail.warning_level === 'critical')}
      <p class="chip {detail.warning_level} risk">Warnlevel {warnLabel[detail.warning_level]} – Hochrisiko-Inhalt</p>
    {/if}

    <div class="stage" role="group" aria-label="Lernkarte" onpointerdown={down} onpointerup={up}>
      <CardView cardId={current.card_id} {flipped} onflip={() => (flipped = !flipped)} />
    </div>

    {#if !flipped}
      <div class="actions">
        <button class="btn primary big" type="button" onclick={() => (flipped = true)}>Karte umdrehen <span class="kbd">Leertaste</span></button>
      </div>
    {:else}
      <div class="actions ratings" role="group" aria-label="Bewertung">
        {#each RATINGS as r, i}
          <button class="btn rate {r}" type="button" disabled={busy} onclick={() => rate(r)}>
            {ratingLabel[r]} <span class="kbd">{i + 1}</span></button>
        {/each}
      </div>
    {/if}

    <div class="secondary">
      <div class="flags" role="group" aria-label="Markierungen">
        {#each FLAGS as f}
          <button class="btn small" type="button" aria-pressed={detail?.progress?.flags?.includes(f) ?? false}
            disabled={!detail} onclick={() => toggleFlag(f)}>{flagLabel[f]}</button>
        {/each}
      </div>
      <div class="dl" role="group" aria-label="Download">
        <button class="btn small" type="button" onclick={() => dl('both', 'pdf')}>PDF</button>
        <button class="btn small" type="button" onclick={() => dl('front', 'png')}>PNG vorn</button>
        <button class="btn small" type="button" onclick={() => dl('back', 'png')}>PNG hinten</button>
        <button class="btn small" type="button" onclick={() => dl('both', 'pdf')}>Drucken</button>
      </div>
    </div>

    <NotesPanel cardId={current.card_id} bind:open={notesOpen} />
    <p class="muted small hint">Tastatur: Leertaste umdrehen · 1–4 bewerten · N Notiz · F Fokus.
      Wischen: auf der Rückseite nach rechts = Gelernt, nach links = Wiederholen.</p>
  {/if}
</div>

<style>
  .learn { max-width: 860px; margin: 0 auto; }
  .learn.focus { background: var(--app-bg); padding: var(--sp-3); }
  .learn.focus .head h1, .learn.focus .hint, .learn.focus .secondary { display: none; }
  .head { display: flex; justify-content: space-between; align-items: flex-end; gap: var(--sp-3); flex-wrap: wrap; margin-bottom: var(--sp-3); }
  .tools { display: flex; gap: var(--sp-2); align-items: center; }
  .tools select { width: auto; min-height: 36px; padding: 4px 8px; margin-left: 4px; }
  .count { margin: 6px 0 var(--sp-2); }
  .risk { margin: 0 0 var(--sp-2); }
  .stage { margin: var(--sp-2) 0 var(--sp-3); touch-action: pan-y; user-select: none; }
  .actions { display: flex; justify-content: center; gap: var(--sp-2); flex-wrap: wrap; }
  .big { min-height: 52px; padding: 0 28px; font-size: 1rem; }
  .ratings .btn { flex: 1 1 140px; min-height: 52px; color: #fff; border: none; }
  .rate.again { background: var(--r-again); } .rate.hard { background: var(--r-hard); }
  .rate.good { background: var(--r-good); } .rate.easy { background: var(--r-easy); }
  .rate:hover { filter: brightness(.95); }
  .kbd { font: 600 .75rem/1 ui-monospace, monospace; padding: 3px 6px; border-radius: 4px; background: rgba(255,255,255,.22); }
  .btn:not(.rate):not(.primary) .kbd { background: var(--app-surface-2); }
  .secondary { display: flex; justify-content: space-between; gap: var(--sp-2); flex-wrap: wrap; margin-top: var(--sp-3); }
  .flags, .dl { display: flex; gap: 6px; flex-wrap: wrap; }
  .finished { text-align: center; padding: var(--sp-4); }
  .hint { margin-top: var(--sp-3); }
</style>
