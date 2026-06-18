<script setup>
import { ref, onMounted, watch } from 'vue'

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const movie = ref(null)
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  error.value = null
  movie.value = null
  try {
    const res = await fetch(`/api/movie/${props.id}`)
    if (res.status === 404) {
      error.value = 'Film nebyl nalezen.'
      return
    }
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    movie.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(() => props.id, load)
</script>

<template>
  <p><RouterLink to="/">← zpět na filmy</RouterLink></p>

  <p v-if="loading">Načítám…</p>
  <p v-else-if="error">{{ error }}</p>

  <template v-else-if="movie">
    <h2>{{ movie.title }}</h2>
    <p>
      <span v-if="movie.original_title">{{ movie.original_title }} · </span>
      <span v-if="movie.year">{{ movie.year }}</span>
      <span v-if="movie.country"> · {{ movie.country }}</span>
      <span v-if="movie.duration_minutes"> · {{ movie.duration_minutes }} min</span>
    </p>

    <p v-if="movie.genres.length">
      <strong>Žánry:</strong>
      <span v-for="(g, i) in movie.genres" :key="g.id">{{ g.name }}{{ i < movie.genres.length - 1 ? ', ' : '' }}</span>
    </p>

    <p v-if="movie.director"><strong>Režie:</strong> {{ movie.director.name }}</p>

    <p v-if="movie.average_rating !== null">
      <strong>Hodnocení:</strong> ★ {{ movie.average_rating.toFixed(1) }} / 10
    </p>

    <p v-if="movie.description">{{ movie.description }}</p>

    <h3 v-if="movie.actors.length">Obsazení</h3>
    <ul v-if="movie.actors.length">
      <li v-for="a in movie.actors" :key="a.id">{{ a.name }}</li>
    </ul>
  </template>
</template>
