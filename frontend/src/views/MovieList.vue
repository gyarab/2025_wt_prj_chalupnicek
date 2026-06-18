<script setup>
import { ref, onMounted } from 'vue'

const movies = ref([])
const count = ref(0)
const loading = ref(false)
const error = ref(null)

const q = ref('')
const year = ref('')

async function load() {
  loading.value = true
  error.value = null
  try {
    // /api se v dev režimu proxuje na Django :8000 (viz vite.config.js)
    const url = new URL('/api/movie', window.location.origin)
    if (q.value) url.searchParams.set('q', q.value)
    if (year.value) url.searchParams.set('year', year.value)

    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    movies.value = data.results
    count.value = data.count
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <h2>Filmy</h2>

  <form @submit.prevent="load">
    <input v-model="q" type="text" placeholder="Hledat v názvu" />
    <input v-model="year" type="number" placeholder="Rok" />
    <button type="submit">Filtrovat</button>
  </form>

  <p v-if="loading">Načítám…</p>
  <p v-else-if="error">Chyba: {{ error }}</p>
  <p v-else>Nalezeno {{ count }} filmů</p>

  <ul v-if="!loading && !error">
    <li v-for="movie in movies" :key="movie.id">
      <RouterLink :to="{ name: 'movie-detail', params: { id: movie.id } }">
        {{ movie.title }}
      </RouterLink>
      <span v-if="movie.year"> ({{ movie.year }})</span>
      <span v-if="movie.director"> – {{ movie.director }}</span>
      <span v-if="movie.average_rating !== null"> – ★ {{ movie.average_rating.toFixed(1) }}</span>
    </li>
  </ul>
</template>
