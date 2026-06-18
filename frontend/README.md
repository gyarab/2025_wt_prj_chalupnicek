# FilmDB – Vue frontend

Alternativní **frontend** k Django aplikaci ve složce [../prj/](../prj/).
Komunikuje s ní jen přes REST API (`/api/...`).

Tahle složka je samostatný JavaScriptový projekt. Backend (Django) o ní nic neví –
běží na jiném portu a v budoucnu poběží v jiném Docker kontejneru. Vue frontend
si všechna data tahá z API přes `fetch()`.

---

## Co je v této složce

```
frontend/
├── package.json          # seznam závislostí + npm skripty (dev, build, preview)
├── vite.config.js        # konfigurace Vite dev serveru (port, proxy na /api)
├── index.html            # vstupní HTML stránka (jediná! je to SPA)
└── src/
    ├── main.js           # bootstrap aplikace – createApp().mount()
    ├── App.vue           # kořenová komponenta (layout: hlavička, RouterView, patička)
    ├── style.css         # globální CSS
    ├── router/index.js   # mapování URL → Vue komponenty (vue-router)
    └── views/
        ├── MovieList.vue   # `/`           – seznam filmů, volá GET /api/movie
        └── MovieDetail.vue # `/movie/:id`  – detail filmu, volá GET /api/movie/{id}
```

> **Není tu** `node_modules/` ani `dist/` – ty se generují (a jsou v `.gitignore`).
> Stejně jako u Pythonu nikdy necommituješ `venv/`, tak v JS necommituješ `node_modules/`.

---

## Co je Node.js, npm, Vite a Vue?

Pro porozumění frontendovému workflow musíš znát čtyři kousky:

### Node.js
- JavaScriptový **runtime** pro spouštění JS mimo prohlížeč (server, CLI nástroje, build skripty).
- Frontend kód běží nakonec v prohlížeči, ale **build nástroje** (Vite, eslint, …) běží v Node.
- Verzi zjistíš `node --version`. Tento projekt potřebuje Node 18+.

### npm
- **Package manager** pro Node – ekvivalent `pip` ve světě Pythonu.
- `package.json` ≈ `requirements.txt` (deklaruje závislosti a skripty).
- `node_modules/` ≈ obsah `venv/lib/python*/site-packages/` (sem se instalují balíčky).
- `package-lock.json` ≈ lock soubor s přesnými verzemi – commituje se.

### Vite
- **Build tool** a **dev server** pro moderní frontend (Vue, React, Svelte…).
- V dev režimu (`npm run dev`) drží otevřený malý webový server, který:
  - servíruje `index.html` a JS moduly,
  - umí *hot module replacement* (HMR) – po Ctrl-S v editoru se stránka okamžitě
    aktualizuje bez ztráty stavu,
  - **proxuje** vybrané cesty na backend (u nás `/api` → Django na `:8000`,
    viz [vite.config.js](vite.config.js)).
- V produkci (`npm run build`) vyrobí ve složce `dist/` statické soubory
  (jeden HTML, několik JS/CSS bundlů s hash v názvu, optimalizované, minifikované).
  Tahle `dist/` se pak servíruje z nginx kontejneru.

### Vue
- **Framework** pro stavbu reaktivních uživatelských rozhraní.
- Komponenta = jeden `.vue` soubor obsahující tři bloky:
  - `<script setup>` – JavaScript logika (stav, funkce)
  - `<template>` – HTML s direktivami (`v-if`, `v-for`, `@click`, `:href`, `{{ var }}`)
  - `<style>` – CSS (volitelně `scoped`, aby platilo jen pro tuhle komponentu)
- **Reaktivita**: stav drženy v `ref(...)` se sám propíše do šablony – nemusíš
  ručně dělat `document.getElementById(...).textContent = ...`, jak by ses musel/a
  ve vanilla JS.
- **vue-router** přidává klientské routování – URL ↔ komponenta. URL se přepíná
  bez reloadu stránky (SPA = Single-Page Application).

---

## Lokální spuštění

> **Pozor:** Aby Vue frontend fungoval, musí současně běžet i Django backend
> na portu 8000. Vite proxuje `/api/...` tam (viz vite.config.js).

### 1. Nainstaluj závislosti (jen poprvé, nebo po `git pull` který mění package.json)

```bash
cd frontend
npm install
```

Toto vytvoří složku `node_modules/` (~70 MB, je v `.gitignore`).

### 2. Spusť dev server

```bash
npm run dev
```

Otevři `http://localhost:5173/`. Vite tě informuje o portu i v terminálu.

V druhém terminálu nech běžet Django backend:

```bash
cd prj
source ../venv/bin/activate
./manage.py runserver
```

### 3. Build pro produkci (později k Dockeru)

```bash
npm run build       # vyrobí frontend/dist/
npm run preview     # lokálně si dist/ vyzkoušej
```

V produkci by `dist/` servíroval nginx a Vite by už neběžel.

---

## Jak Vue konzumuje Django API

Klíčové místo je [src/views/MovieList.vue](src/views/MovieList.vue) – tady je
základní vzorec, který se opakuje pro každý API endpoint:

```vue
<script setup>
import { ref, onMounted } from 'vue'

const movies = ref([])         // reactive state
const loading = ref(false)
const error = ref(null)

async function load() {
  loading.value = true
  try {
    const res = await fetch('/api/movie')   // → proxy → Django :8000
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const data = await res.json()
    movies.value = data.results              // přiřazení → Vue překreslí šablonu
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(load)   // zavolej load() při prvním vykreslení komponenty
</script>

<template>
  <p v-if="loading">Načítám…</p>
  <p v-else-if="error">Chyba: {{ error }}</p>
  <ul v-else>
    <li v-for="m in movies" :key="m.id">{{ m.title }}</li>
  </ul>
</template>
```

Tři věci, které si z toho odnes:

1. **`ref()`** dělá hodnotu reaktivní. Když změníš `movies.value = ...`, Vue automaticky
   překreslí všechny části šablony, které ji používají.
2. **`fetch()`** je vestavěná funkce prohlížeče. Vrací `Promise`, takže používáme `await`.
3. **`/api/movie`** je relativní URL. Pokud bys napsal/a `http://localhost:8000/api/movie`,
   prohlížeč by request zablokoval kvůli CORS (jiný origin než `localhost:5173`).
   Proxy z `vite.config.js` přepošle request na Django, ale prohlížeč si myslí,
   že komunikuje se stejným serverem – CORS problém odpadá.

---

## Příprava na kontejnery

V další lekci se aplikace rozdělí na dva Docker kontejnery:

```
┌──────────────────┐         ┌──────────────────┐
│  nginx (frontend)│         │  gunicorn (django)│
│  servíruje dist/ │ ──/api──┤  REST API + admin │
│  port 80         │         │  port 8000        │
└──────────────────┘         └──────────────────┘
```

Tahle adresářová struktura (`/frontend` a `/prj` vedle sebe, každý se svým
buildem/závislostmi) je přesně to, co kontejnerizace potřebuje – každý kontejner
si zkopíruje jen svou složku.
