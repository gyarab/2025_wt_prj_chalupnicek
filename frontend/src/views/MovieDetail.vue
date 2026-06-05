<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const movie = ref(null)

async function load() {
    const url = new URL(`/api/movie/${route.params.id}`, window.location.origin)
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP returned ${res.status}`)
    movie.value = await res.json()
}

onMounted(load)
</script>

<template>
    <h2>Movie Detail</h2>
    <div v-if="movie">
        <h3>{{ movie.title }}</h3>
        <p>{{ movie.director.name }} ({{ movie.director.birth_year }})</p>
        <img :src="movie.poster_url" style="max-height: 100px">
    </div>
</template>