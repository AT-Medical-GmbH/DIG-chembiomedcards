<script lang="ts">
  // Zeigt eine Karte aus den strukturierten Daten.
  // - Ab Tablet-Breite: druckgetreue Karte. Der Server rendert sie mit demselben Renderer wie Druck
  //   und Moodle; sie landet isoliert im Shadow DOM und wird auf die verfügbare Breite skaliert.
  // - Auf schmalen Bildschirmen wäre die skalierte A6-Karte unlesbar klein. Dort entsteht aus
  //   denselben Feldern eine responsive Leseansicht mit normaler Schriftgröße und gleichen Farbrollen.
  import { api, cardCss, warnLabel, type CardDetail } from './api';

  let { cardId, flipped = false, onflip }: { cardId: string; flipped?: boolean; onflip?: () => void } = $props();

  const CARD_W = (148 * 96) / 25.4;   // 148 mm in CSS-Pixeln
  const CARD_H = (105 * 96) / 25.4;
  const COMPACT_BELOW = 600;          // darunter: Leseansicht statt Druckkarte
  let width = $state(0);
  let compact = $derived(width > 0 && width < COMPACT_BELOW);
  let scale = $derived(width ? Math.min(1.35, width / CARD_W) : 1);
  let html = $state<{ front: string; back: string } | null>(null);
  let data = $state<CardDetail | null>(null);
  let error = $state<string | null>(null);

  $effect(() => {
    const id = cardId;
    html = null; data = null; error = null;
    Promise.all([
      api<{ html: string }>(`/api/cards/${id}/render?side=front`),
      api<{ html: string }>(`/api/cards/${id}/render?side=back`),
      api<CardDetail>(`/api/cards/${id}`)
    ]).then(([f, b, d]) => { if (id === cardId) { html = { front: f.html, back: b.html }; data = d; } })
      .catch((e) => (error = e.message));
  });

  function shadow(node: HTMLElement, markup: string) {
    const root = node.attachShadow({ mode: 'open' });
    const render = async (m: string) => {
      root.innerHTML = `<style>${await cardCss()} .card{margin:0;box-shadow:none}</style>${m}`;
    };
    render(markup);
    return { update: render };
  }

  // Leseansicht: Zeilen mit "- " als Liste, sonst Absätze (Text wird von Svelte escaped)
  const blocks = (t: string) => {
    const lines = t.split('\n').map((l) => l.trim()).filter(Boolean);
    return lines.length && lines.every((l) => l.startsWith('- '))
      ? { list: lines.map((l) => l.slice(2)) } : { text: lines };
  };
  const TABS = ['Allgemein', 'PK/PD', 'Wirkstoff', 'Klinik', 'Tox', 'Antidot', 'Interaktion'];
  const ACTIVE: Record<string, string> = { overview: 'Allgemein', substance: 'Wirkstoff', mechanism: 'PK/PD',
    toxidrome: 'Tox', antidote: 'Antidot', interaction: 'Interaktion', case: 'Klinik' };
  let prompt = $derived(data ? (data.front_content?.prompt ?? data.front_content?.question ?? data.substance_name ?? data.title) : '');
</script>

<div class="stage" class:compact bind:clientWidth={width} style:height={compact ? 'auto' : `${CARD_H * scale}px`}>
  {#if error}
    <p class="muted">Karte konnte nicht geladen werden: {error}</p>
  {:else if compact && data}
    <button type="button" class="reader" onclick={() => onflip?.()}
      aria-label={flipped ? 'Vorderseite zeigen' : 'Rückseite zeigen'}>
      <span class="r-tabs" aria-hidden="true">
        <span class="r-tab">{ACTIVE[data.card_type] ?? TABS[0]}</span>
        <span class="r-side">{flipped ? 'Rückseite' : 'Vorderseite'}</span>
      </span>
      <span class="r-head">
        <span class="r-title">{data.title}</span>
        {#if data.warning_level === 'high' || data.warning_level === 'critical'}
          <span class="chip {data.warning_level}">{warnLabel[data.warning_level]}</span>
        {/if}
      </span>
      {#if data.subtitle}<span class="r-sub muted">{data.subtitle}</span>{/if}
      {#if !flipped}
        <span class="r-prompt">{prompt}</span>
        <span class="r-hint muted small">Tippen zum Umdrehen</span>
      {:else}
        {#each data.back_sections as s (s.key)}
          {@const b = blocks(s.text)}
          <span class="r-box role-{s.color_role}">
            <span class="r-label">{s.label}</span>
            {#if b.list}
              <span class="r-list">{#each b.list as item}<span class="r-li">{item}</span>{/each}</span>
            {:else}
              {#each b.text ?? [] as line}<span class="r-p">{line}</span>{/each}
            {/if}
          </span>
        {/each}
        <span class="r-foot muted small">{data.card_id} · {data.disclaimer}</span>
      {/if}
    </button>
  {:else if html}
    <button
      type="button"
      class="flipper"
      class:flipped
      onclick={() => onflip?.()}
      aria-label={flipped ? 'Karte umdrehen: Vorderseite zeigen' : 'Karte umdrehen: Rückseite zeigen'}
      style:width="{CARD_W}px"
      style:height="{CARD_H}px"
      style:transform="scale({scale})"
    >
      <span class="face front" aria-hidden={flipped} use:shadow={html.front}></span>
      <span class="face back" aria-hidden={!flipped} use:shadow={html.back}></span>
    </button>
  {:else}
    <div class="skeleton" style:width="{Math.min(width, CARD_W * scale)}px" style:height="{CARD_H * scale}px"></div>
  {/if}
</div>

<style>
  .stage { position: relative; width: 100%; display: flex; justify-content: center; perspective: 2400px; }
  .flipper {
    all: unset; position: absolute; top: 0; transform-origin: top center; cursor: pointer;
    display: block;
  }
  .flipper:focus-visible, .reader:focus-visible { outline: 3px solid var(--app-focus); outline-offset: 4px; border-radius: 6px; }
  .face {
    position: absolute; inset: 0; display: block; backface-visibility: hidden;
    border-radius: 6px; overflow: hidden; background: #fff;
    box-shadow: 0 2px 6px rgba(16, 24, 32, .08), 0 12px 32px rgba(16, 24, 32, .10);
    transition: transform .45s cubic-bezier(.2, .7, .2, 1);
  }
  .face.back { transform: rotateY(180deg); }
  .flipped .face.front { transform: rotateY(-180deg); }
  .flipped .face.back { transform: rotateY(0deg); }
  .skeleton { border-radius: 6px; background: linear-gradient(90deg, #eef1f3, #f7f9fa, #eef1f3); }

  /* Leseansicht (schmale Bildschirme) */
  .reader {
    all: unset; box-sizing: border-box; display: flex; flex-direction: column; gap: 10px; width: 100%;
    background: #fff; border-radius: 10px; padding: 16px; cursor: pointer;
    border-top: 6px solid var(--app-primary);
    box-shadow: 0 2px 6px rgba(16, 24, 32, .08), 0 12px 32px rgba(16, 24, 32, .10);
    font-size: 1rem; line-height: 1.5; color: var(--app-text);
  }
  .r-tabs { display: flex; justify-content: space-between; align-items: center; }
  .r-tab { font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em;
    color: #fff; background: var(--app-primary); padding: 3px 8px; border-radius: 4px; }
  .r-side { font-size: .8rem; color: var(--app-text-soft); }
  .r-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 8px; }
  .r-title { font-size: 1.35rem; font-weight: 700; line-height: 1.2; }
  .r-sub { margin-top: -6px; }
  .r-prompt { display: block; font-size: 1.15rem; font-weight: 600; text-align: center; padding: 28px 4px; }
  .r-hint { text-align: center; }
  .r-box { display: block; border: 1px solid #dfe5e8; border-left: 4px solid #37474f; border-radius: 8px; padding: 10px 12px; }
  .r-label { display: block; font-size: .75rem; font-weight: 700; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 4px; }
  .r-p { display: block; }
  .r-list { display: block; padding-left: 18px; }
  .r-li { display: list-item; }
  .r-foot { display: block; }
  .role-base { border-left-color: #37474f; } .role-base .r-label { color: #37474f; }
  .role-pkpd { border-left-color: #1e88e5; } .role-pkpd .r-label { color: #1565c0; }
  .role-clinic { border-left-color: #43a047; } .role-clinic .r-label { color: #2e7d32; }
  .role-risk { border-left-color: #e53935; } .role-risk .r-label { color: #c62828; }
  .role-interaction { border-left-color: #fb8c00; } .role-interaction .r-label { color: #b25d00; }
  .role-antidote { border-left-color: #8e24aa; background: #faf6fc; } .role-antidote .r-label { color: #7b1fa2; }

  @media (prefers-reduced-motion: reduce) { .face { transition: none; } }
</style>
