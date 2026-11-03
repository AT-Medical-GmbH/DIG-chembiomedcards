<script lang="ts">
  // Toxikologie-/Antidot-Schnellübersicht: Antidot ↔ Zielintoxikation und Toxidrome auf einen Blick.
  import { api, warnLabel, type CardDetail, type CardSummary } from '#lib/api.ts';

  let antidotes = $state<CardDetail[]>([]);
  let toxidromes = $state<CardDetail[]>([]);
  let loaded = $state(false);
  let error = $state<string | null>(null);

  async function load() {
    try {
      const [a, t] = await Promise.all([
        api<{ cards: CardSummary[] }>('/api/cards?card_type=antidote'),
        api<{ cards: CardSummary[] }>('/api/cards?card_type=toxidrome')
      ]);
      const details = (list: CardSummary[]) => Promise.all(list.map((c) => api<CardDetail>(`/api/cards/${c.card_id}`)));
      [antidotes, toxidromes] = await Promise.all([details(a.cards), details(t.cards)]);
    } catch (e) { error = (e as Error).message; } finally { loaded = true; }
  }
  load();

  const section = (c: CardDetail, key: string) => c.back_sections.find((s) => s.key === key)?.text ?? '–';
</script>

<h1>Antidote &amp; Toxidrome</h1>
<p class="muted">Schnellübersicht zum Wiederholen. Für Details und Quellen die jeweilige Karte öffnen.</p>
{#if error}<p class="banner" role="alert">{error}</p>{/if}
{#if loaded && !antidotes.length && !toxidromes.length}
  <p class="muted">Noch keine freigegebenen Antidot- oder Toxidromkarten.</p>
{/if}

{#if antidotes.length}
  <h2>Antidote</h2>
  <div class="panel scroll">
    <table>
      <thead><tr><th scope="col">Antidot</th><th scope="col">Zielintoxikation</th><th scope="col">Wirkprinzip</th><th scope="col">Warnlevel</th></tr></thead>
      <tbody>
        {#each antidotes as c (c.card_id)}
          <tr>
            <th scope="row"><a href="/karten/{c.card_id}">{c.title}</a>{#if c.draft} <span class="chip draft">Entwurf</span>{/if}</th>
            <td>{section(c, 'zielintoxikation')}</td>
            <td>{section(c, 'wirkprinzip')}</td>
            <td><span class="chip {c.warning_level}">{warnLabel[c.warning_level]}</span></td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

{#if toxidromes.length}
  <h2 class="h">Toxidrome und Intoxikationen</h2>
  <div class="panel scroll">
    <table>
      <thead><tr><th scope="col">Toxidrom</th><th scope="col">Leitsymptome</th><th scope="col">Antidot</th></tr></thead>
      <tbody>
        {#each toxidromes as c (c.card_id)}
          <tr>
            <th scope="row"><a href="/karten/{c.card_id}">{c.title}</a>{#if c.draft} <span class="chip draft">Entwurf</span>{/if}</th>
            <td class="pre">{section(c, 'leitsymptome')}</td>
            <td>{c.antidote ?? 'kein spezifisches'}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>
{/if}

<style>
  .h { margin-top: var(--sp-4); }
  .scroll { overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; min-width: 640px; }
  th, td { text-align: left; vertical-align: top; padding: 10px 8px; border-bottom: 1px solid var(--app-line); font-size: .95rem; }
  thead th { font-size: .8rem; color: var(--app-text-soft); text-transform: uppercase; letter-spacing: .03em; }
  .pre { white-space: pre-line; }
</style>
