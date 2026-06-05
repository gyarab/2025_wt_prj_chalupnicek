<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

const movies = ref([])
const router = useRouter()

async function load() {
    const url = new URL('/api/movie', window.location.origin)
    const res = await fetch(url)
    if (!res.ok) throw new Error(`HTTP returned ${res.status}`)
    const data = await res.json()
    movies.value = data.results

}

function selectMovie(movie) {
    router.push(`/movie/${movie.id}`)
}

onMounted(load)
</script>

<template>
    <h2>Movie List</h2>

    <div v-for="movie in movies" @click="selectMovie(movie)" style="cursor: pointer;">
        <h3>{{ movie.title }}</h3>
        <p>{{ movie.director }}</p>
        <img :src="movie.poster_url" style="max-height: 100px">
    </div>

</template>