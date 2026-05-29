<script setup>
    import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
    <header>
        <RouterLink to="/">
            <h1>FilmDB (vue)</h1>
        </RouterLink>
    </header>
    <main>
        <RouterView />
    </main>

</template>