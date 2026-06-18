<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <header>
    <RouterLink to="/"><h1>FilmDB (Vue)</h1></RouterLink>
  </header>
  <main>
    <RouterView />
  </main>
</template>
