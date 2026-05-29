import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

// TODO TypeError: routerHistory.createHref is not a function


createApp(App).use(router).mount('#app')