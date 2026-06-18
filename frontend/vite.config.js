import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// Vite dev server config.
// Vue volá API přes relativní cestu /api/... – proxy ji pak v dev režimu
// přesměruje na Django runserver na :8000. V produkci by frontend tekl
// z jiného kontejneru (nginx) a /api by se proxovalo tam.
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // Pozn.: 127.0.0.1 (ne localhost) – Node 18+ jinak preferuje IPv6 a
      // Django runserver defaultně poslouchá jen na IPv4.
      '/api': 'http://127.0.0.1:8000',
      '/admin': 'http://127.0.0.1:8000',
      '/static': 'http://127.0.0.1:8000',
    },
  },
})
