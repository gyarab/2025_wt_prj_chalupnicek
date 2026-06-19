import { createRouter, createWebHistory } from 'vue-router'
import MovieList from '../views/MovieList.vue'
import MovieDetail from '../views/MovieDetail.vue'

const router = createRouter({
  // BASE_URL = hodnota `base` z vite.config.js ('/' v dev, '/app/' v produkci),
  // aby klientské routování fungovalo i když SPA neběží v kořeni domény.
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: MovieList },
    { path: '/movie/:id', name: 'movie-detail', component: MovieDetail, props: true },
  ],
})

export default router
