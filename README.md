# FilmDB — webová aplikace

Referenční projekt pro předmět **Webové technologie** na Gymnáziu Arabská
(školní rok 2025/2026). Slouží jako ukázka jednoduché, ale úplné aplikace
postavené nad Django frameworkem — od datového modelu přes views a šablony
až po REST API.

---

## Co aplikace umí

FilmDB je miniaturní filmová databáze ve stylu ČSFD / IMDb:

- 🎬 **Seznam filmů** s filtrováním podle žánru, roku, režiséra a herce
  a s fulltextovým vyhledáváním v názvu.
- 👤 **Detail filmu** — popis, žánry, režisér, obsazení, průměrné hodnocení.
- ⭐ **Hodnocení 1–10** — přihlášený uživatel může každý film ohodnotit
  (jedno hodnocení na uživatele a film, dá se přepsat).
- 💬 **Komentáře** — přihlášený uživatel může psát komentáře pod filmy.
- 🎭 **Profily herců a režisérů** s filmografií.
- 🔐 **Registrace, přihlášení a odhlášení** uživatele.
- 🛠️ **Django administrace** pro editaci dat.
- 🌐 **REST API** (django-ninja) s automaticky generovanou dokumentací
  na `/api/docs`.
- ⚡ **Alternativní Vue SPA frontend** ve složce [frontend/](frontend/),
  který stejné API konzumuje z JavaScriptu (příprava na rozdělení do
  Docker kontejnerů).

---

## Datový model (E-R diagram)

Vztahy mezi tabulkami v `app/models.py`. `PK` = primary key,
`FK` = foreign key. `User` je vestavěný model z `django.contrib.auth`.

```
   ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
   │    Genre     │        │     User     │        │    Actor     │
   ├──────────────┤        │ (django.auth)│        ├──────────────┤
   │ id     (PK)  │        ├──────────────┤        │ id     (PK)  │
   │ name         │        │ id     (PK)  │        │ name         │
   └──────┬───────┘        │ username     │        │ birth_year   │
          │                │ password     │        │ nationality  │
          │                │ email        │        │ bio          │
          │                │ ...          │        │ photo_url    │
          │                └──────┬───────┘        └──────┬───────┘
          │                       │                       │
          │ M:N                   │ 1:N                   │ M:N
          │              ┌────────┴────────┐              │
          │              │                 │              │
          │         ┌────▼─────┐     ┌─────▼────┐         │
          │         │ Comment  │     │  Rating  │         │
          │         ├──────────┤     ├──────────┤         │
          │         │ id  (PK) │     │ id  (PK) │         │
          │         │ user (FK)│     │ user (FK)│         │
          │         │ movie(FK)│     │ movie(FK)│         │
          │         │ text     │     │ value    │         │
          │         │ created  │     │ (1–10)   │         │
          │         └────┬─────┘     └─────┬────┘         │
          │              │ N:1             │ N:1          │
          │              ▼                 ▼              │
          │         ┌────────────────────────────┐        │
          └────────►│           Movie            │◄───────┘
                    ├────────────────────────────┤
                    │ id              (PK)       │
                    │ title                      │
                    │ original_title             │
                    │ year                       │
                    │ duration_minutes           │
                    │ country                    │
                    │ description                │
                    │ poster_url                 │
                    │ director_id     (FK)       │
                    └─────────────┬──────────────┘
                                  │ N:1
                                  ▼
                           ┌──────────────┐
                           │   Director   │
                           ├──────────────┤
                           │ id     (PK)  │
                           │ name         │
                           │ birth_year   │
                           │ nationality  │
                           │ bio          │
                           │ photo_url    │
                           └──────────────┘
```

Vztahy slovem:

| Vztah                  | Typ | Realizace v Djangu                         |
|------------------------|-----|--------------------------------------------|
| Movie ↔ Director       | N:1 | `ForeignKey` (jeden film = jeden režisér)  |
| Movie ↔ Actor          | M:N | `ManyToManyField` (film má víc herců)      |
| Movie ↔ Genre          | M:N | `ManyToManyField` (film má víc žánrů)      |
| Movie ↔ Comment        | 1:N | `ForeignKey` na Movie                      |
| Movie ↔ Rating         | 1:N | `ForeignKey` + `unique_together(movie,user)` |
| User ↔ Comment, Rating | 1:N | `ForeignKey` na vestavěného `User`         |

---

## Struktura projektu

Projekt má dvě nezávislé části, každou ve své vlastní složce. V budoucnu
půjde každou zabalit do samostatného Docker kontejneru.

```
2025_wt_prj_chalupnicek/
├── requirements.txt           # python závislosti (backend)
├── fixtures/                  # ukázková data v YAML (viz níže)
│   ├── actors.yaml
│   ├── comments.yaml
│   ├── directors.yaml
│   ├── genres.yaml
│   ├── movies.yaml
│   ├── ratings.yaml
│   └── users.yaml
├── prj/                       # 🐍 Django backend (API + admin + HTML frontend)
│   ├── manage.py
│   ├── db.sqlite3             # SQLite DB (vznikne po `migrate`)
│   ├── prj/                   # nastavení projektu
│   │   ├── settings.py
│   │   └── urls.py            # root URL conf — namapuje /, /admin, /api
│   └── app/                   # naše hlavní aplikace
│       ├── models.py          # datový model (viz E-R nahoře)
│       ├── views.py           # HTML pohledy (landing, movies, detail, …)
│       ├── api.py             # REST API přes django-ninja
│       ├── forms.py           # formuláře (komentář, hodnocení, registrace)
│       ├── admin.py           # registrace modelů do admin rozhraní
│       ├── migrations/        # automaticky generované migrace
│       ├── static/            # CSS, obrázky
│       └── templates/         # HTML šablony
│           ├── base.html
│           ├── landing.html   # `/` — rozcestník mezi Django a Vue frontendem
│           ├── home.html      # `/movies/` — seznam filmů (Django frontend)
│           ├── movie_detail.html
│           ├── actors.html / actor_detail.html
│           ├── directors.html / director_detail.html
│           └── registration/  # login.html, register.html
└── frontend/                  # ⚡ Vue SPA frontend (alternativa Django šablon)
    ├── README.md              # podrobný popis Node/npm/Vite/Vue
    ├── package.json           # JS závislosti + npm skripty
    ├── vite.config.js         # dev server, proxy /api → :8000
    ├── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── style.css
        ├── router/index.js
        └── views/
            ├── MovieList.vue   # `/`            — volá GET /api/movie
            └── MovieDetail.vue # `/movie/:id`   — volá GET /api/movie/{id}
```

---

## Lokální spuštění

Aplikace používá Python Virtual Environment. Před prvním spuštěním je
potřeba ho vytvořit:

```bash
# Linux / macOS
python3 -m venv venv

# Windows
py -3 -m venv venv
```

Aktivace venv (před každou prací):

```bash
# Linux / macOS
source ./venv/bin/activate

# Windows — Git Bash
source ./venv/Scripts/activate

# Windows — PowerShell
.\venv\Scripts\Activate.ps1
```

Instalace závislostí (Django, PyYAML, django-ninja):

```bash
# (venv)$
pip install -r requirements.txt
```

Inicializace databáze (jen poprvé, nebo po `git pull`, který přidá migrace):

```bash
cd prj
./manage.py migrate
```

Naplnění ukázkovými daty (žánry, filmy, herci, režiséři, uživatelé,
komentáře, hodnocení):

```bash
./manage.py loaddata ../fixtures/*.yaml
```

Vytvoření admin uživatele (pokud nepoužiješ uživatele z fixtures):

```bash
./manage.py createsuperuser
```

> Pro výuku doporučuji jednoduché `admin` / `admin` bez e-mailu —
> Django bude protestovat kvůli slabému heslu, prostě potvrď.

Start vývojového serveru:

```bash
./manage.py runserver
```

A pak v prohlížeči:

| URL                                | Co tam je                                          |
|------------------------------------|----------------------------------------------------|
| http://127.0.0.1:8000/             | rozcestník (Django HTML × Vue SPA frontend)        |
| http://127.0.0.1:8000/movies/      | Django frontend — seznam filmů                     |
| http://127.0.0.1:8000/admin/       | Django administrace                                |
| http://127.0.0.1:8000/api/docs     | interaktivní dokumentace REST API                  |

### Vue frontend (volitelně, ve druhém terminálu)

Vue SPA frontend žije ve složce [frontend/](frontend/) a běží na vlastním
portu. Poprvé nainstaluj JS závislosti, pak nech běžet `npm run dev`:

```bash
cd frontend
npm install         # jen poprvé (vytvoří node_modules/)
npm run dev         # spustí Vite dev server na http://localhost:5173/
```

Vue volá Django API přes `fetch('/api/movie')`. V dev režimu Vite tyhle
requesty proxuje na `http://localhost:8000` (viz [frontend/vite.config.js](frontend/vite.config.js)),
takže nepotřebuješ řešit CORS. Django musí současně běžet.

Podrobnější popis Node.js, npm, Vite a Vue najdeš v [frontend/README.md](frontend/README.md).

### Frontend

```
cd frontend
npm install
npm run dev
```

---

## Workflow při změně modelu

Po **každé** úpravě `app/models.py` je potřeba vygenerovat migraci a
spustit ji proti DB:

```bash
./manage.py makemigrations   # vytvoří soubor v app/migrations/
./manage.py migrate          # aplikuje změny na db.sqlite3
```

> Migrace se commitují do gitu — patří k modelu. Když si je smažeš
> a vygeneruješ znova, ostatní si nebudou rozumět s tvojí DB.

Pokud se DB úplně rozbije (typicky během experimentování), nejjednodušší
fix je smazat `prj/db.sqlite3`, pustit `migrate` a znovu `loaddata`.

---

## REST API

Endpointy jsou definované v [prj/app/api.py](prj/app/api.py) pomocí
knihovny [django-ninja](https://django-ninja.dev/). Interaktivní swagger
dokumentace běží na `/api/docs`.

Příklady:

```bash
# seznam filmů
curl http://127.0.0.1:8000/api/movie

# detail filmu
curl http://127.0.0.1:8000/api/movie/1

# filtrování
curl "http://127.0.0.1:8000/api/movie?genre_id=2&year=1999"
```

`POST`/`PUT`/`DELETE` endpointy vyžadují přihlášení (cookie session
z `/admin/login/`).

---

## Nasazení na server (deployment)

Aplikace běží na reálném serveru na **https://vch.gawt.dtcloud.cz**, zabalená do Docker
kontejnerů. Vše k tomu je ve složce [deploy/](deploy/) a v GitHub Action
[.github/workflows/deploy.yml](.github/workflows/deploy.yml).

Stručně:

- **`web`** (Django + gunicorn) a **`frontend`** (nginx) jsou dvě služby v
  [deploy/docker-compose.yml](deploy/docker-compose.yml). nginx je vstupní brána:
  servíruje nabuildovanou Vue SPA pod `/app/`, statiku (`/static/`) a média
  (`/media/`), zbytek proxuje na Django (`/`, `/movies/`, `/admin/`, `/api/`).
- Provoz zvenčí (HTTPS) pouští na nginx **traefik** běžící na serveru — podle domény,
  přes sdílenou síť `proxy` a traefik štítky na službě `frontend`.
- **Ansible** ([deploy/playbooks/](deploy/playbooks/)) pošle commitnutý zdroják na
  server a postaví + spustí stack. Cílový server a SSH uživatel jsou ve verzovaném
  [deploy/inventory.ini](deploy/inventory.ini).
- **GitHub Actions** deployuje při pushi do `main` (workflow *Deploy*); naplnění
  databáze z [fixtures/](fixtures/) je samostatný ruční workflow *Seed database*.
- Jediné tajemství je SSH klíč v repository secrets jako `SSH_PRIVATE_KEY` —
  bezpečnost je tu pro účely výuky záměrně zjednodušená.

Podrobný návod (konfigurace, ruční spuštění, předpoklady na serveru) je v
[deploy/README.md](deploy/README.md).

> `settings.py` je teď připravené na produkci: `SECRET_KEY`, `DEBUG`,
> `ALLOWED_HOSTS`, cesta k databázi i `STATIC_ROOT`/`MEDIA_ROOT` se dají nastavit
> přes proměnné prostředí. Bez nich (lokálně) platí stejné výchozí hodnoty jako dřív.

---

## Studijní tipy

- Začni u `urls.py` → `views.py` → `templates/` → `models.py`. To je
  cesta jednoho requestu.
- Django shell je tvůj kamarád: `./manage.py shell` ti pustí Python
  s loadnutými modely — ideální na zkoušení ORM dotazů.
- Když něco nefunguje, koukni do terminálu, kde běží `runserver` —
  Django tam píše plný traceback.
