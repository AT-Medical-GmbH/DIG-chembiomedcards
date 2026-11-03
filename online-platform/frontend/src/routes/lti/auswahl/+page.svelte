<script lang="ts">
  // Deep Linking: Lehrende wählen Lernsets oder einzelne freigegebene Karten als Moodle-Aktivität.
  import { tick } from 'svelte';
  import { api, post, type CardSummary } from '#lib/api.ts';
  import { session } from '#lib/session.svelte.ts';

  type Item = { type: 'set' | 'card'; id: string; label: string };
  let sets = $state<{ slug: string; name: string }[]>([]);
  let cards = $state<CardSummary[]>([]);
  let q = $state('');
  let chosen = $state<Item[]>([]);
  let busy = $state(false);
  let error = $state<string | null>(null);
  let form = $state<HTMLFormElement>();
  let jwtValue = $state('');
  let returnUrl = $state('');

  api<{ content_sets: { slug: string; name: string }[] }>('/api/sets').then((s) => (sets = s.content_sets)).catch((e) => (error = e.message));
  api<{ cards: CardSummary[] }>('/api/cards').then((c) => (cards = c.cards)).catch(() => {});

  let filtered = $derived(q.trim().length < 2 ? [] : cards.filter((c) =>
    (c.title + ' ' + c.card_id).toLowerCase().includes(q.trim().toLowerCase())).slice(0, 20));
  const has = (it: Item) => chosen.some((c) => c.type === it.type && c.id === it.id);
  function toggle(it: Item) { chosen = has(it) ? chosen.filter((c) => !(c.type === it.type && c.id === it.id)) : [...chosen, it]; }

  async function submit() {
    busy = true; error = null;
    try {
      const r = await post<{ return_url: string; jwt: string }>('/api/lti/deep-link',
        { items: chosen.map(({ type, id }) => ({ type, id })) });
      returnUrl = r.return_url; jwtValue = r.jwt;
      await tick();                                    // action/JWT im DOM, dann POST zurück zu Moodle
      form?.submit();
    } catch (e) { error = (e as Error).message; busy = false; }
  }
</script>

<h1>Inhalt für Moodle auswählen</h1>
{#if session.me?.role !== 'teacher'}
  <p class="banner" role="alert">Die Auswahl ist nur für Lehrende aus Moodle heraus möglich.</p>
{:else}
  <p class="muted">Ausgewählte Lernsets oder Karten erscheinen im Moodle-Kurs als Aktivität. Lernende sehen nur fachlich freigegebene Karten.</p>
  {#if error}<p class="banner" role="alert">{error}</p>{/if}

  <h2>Lernsets</h2>
  <div class="grid cols-auto">
    {#each sets as s (s.slug)}
      {@const it = { type: 'set' as const, id: s.slug, label: s.name }}
      <button class="panel pick" type="button" aria-pressed={has(it)} onclick={() => toggle(it)}>{s.name}</button>
    {/each}
  </div>

  <h2>Einzelne Karte</h2>
  <label class="small muted" for="kq">Suche (Titel oder Nummer)</label>
  <input id="kq" type="search" bind:value={q} placeholder="z. B. Naloxon oder ph_100" />
  <ul class="results">
    {#each filtered as c (c.card_id)}
      {@const it = { type: 'card' as const, id: c.card_id, label: c.title }}
      <li><button class="btn small" type="button" aria-pressed={has(it)} onclick={() => toggle(it)}>
        {c.card_id} · {c.title}</button></li>
    {/each}
  </ul>

  <div class="panel summary">
    <strong>Ausgewählt ({chosen.length})</strong>
    <ul>{#each chosen as c}<li>{c.type === 'set' ? 'Lernset' : 'Karte'}: {c.label}</li>{/each}</ul>
    <button class="btn primary" type="button" disabled={!chosen.length || busy} onclick={submit}>
      {busy ? 'Wird an Moodle übergeben …' : 'In Moodle übernehmen'}</button>
  </div>
  <form bind:this={form} method="POST" action={returnUrl} hidden>
    <input type="hidden" name="JWT" value={jwtValue} />
  </form>
{/if}

<style>
  .pick { text-align: left; font-weight: 600; cursor: pointer; }
  .pick[aria-pressed='true'] { border-color: var(--app-primary); box-shadow: inset 0 0 0 2px var(--app-primary); }
  .results { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 6px; margin-top: 8px; }
  .results .btn[aria-pressed='true'] { border-color: var(--app-primary); }
  .summary { margin-top: var(--sp-4); }
  h2 { margin-top: var(--sp-4); }
</style>
