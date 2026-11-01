<script lang="ts">
  // Ziel nach dem Moodle-Start: Token aus dem Fragment übernehmen, Fragment entfernen, weiterleiten.
  import { goto } from '$app/navigation';
  import { safeNext, setLtiToken } from '$lib/lti';
  import { session } from '$lib/session.svelte';

  let error = $state<string | null>(null);
  const frag = new URLSearchParams(window.location.hash.slice(1));
  const token = frag.get('token');
  history.replaceState(null, '', '/lti/start');           // Token nicht in Verlauf/Lesezeichen
  if (token) {
    setLtiToken(token);
    session.needsLogin = false;
    goto(safeNext(frag.get('next')), { replaceState: true }).then(() => { session.version += 1; });
  } else {
    error = 'Kein Start-Token gefunden. Bitte die Aktivität in Moodle erneut öffnen.';
  }
</script>

{#if error}
  <div class="panel"><h1>Start aus Moodle</h1><p class="banner" role="alert">{error}</p></div>
{:else}
  <p class="muted">Pharma Cards wird gestartet …</p>
{/if}
