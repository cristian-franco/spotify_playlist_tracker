<script>
    import { onMount } from 'svelte';

    let loginSuccess = false;

    onMount(() => {
        const params = new URLSearchParams(window.location.search);
        if (params.get('success')) {
            loginSuccess = true;
        }
    });

    function loginSpotify() {
        window.location.href = 'http://localhost:8001/auth/spotify/login';
    }
</script>

<div class="p-8">
    <h1 class="text-2xl font-bold mb-4">Test Spotify Auth</h1>

    <button
        on:click={loginSpotify}
        class="bg-green-500 text-white px-4 py-2 rounded"
    >
        Login with Spotify
    </button>

    {#if loginSuccess}
        <p class="mt-4 text-green-600">Login successful!</p>
    {/if}
</div>