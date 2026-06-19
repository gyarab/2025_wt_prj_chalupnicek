# Nasazení FilmDB (deployment)

Tahle složka přidává **nasazení aplikace na reálný server** (`gawt.dtcloud.cz`).
Navazuje na lekci o Dockeru: aplikaci zabalíme do kontejnerů a pošleme ji na server
přes **Ansible**, celé to spouští **GitHub Actions**.

> Lokální vývoj se nemění — dál platí `./manage.py runserver` + `npm run dev`
> z hlavního [README](../README.md). Tady je řeč jen o produkci.

## Jak to vypadá na serveru

```
                         ┌──────────────── server gawt.dtcloud.cz ────────────────┐
   návštěvník  ──:80──►  │  frontend (nginx)                                        │
                         │   /app/     →  Vue SPA (build z frontend/)               │
                         │   /static/  →  statika Djanga   (volume static_data)     │
                         │   /media/   →  média            (volume media_data)      │
                         │   /…        →  proxy ──►  web (gunicorn :8000)            │
                         │                          Django: /, /movies, /admin, /api │
                         │                          SQLite (volume db_data)          │
                         └──────────────────────────────────────────────────────────┘
```

Dvě služby (viz [docker-compose.yml](docker-compose.yml)):

| služba | image | co dělá |
|--------|-------|---------|
| `web` | [../Dockerfile](../Dockerfile) | Django + gunicorn. Při startu pustí `migrate` a `collectstatic` (viz [web-entrypoint.sh](web-entrypoint.sh)). |
| `frontend` | [../frontend/Dockerfile](../frontend/Dockerfile) | nginx = vstupní brána. Postaví Vue SPA a servíruje statiku/média + proxuje na `web`. |

Dva frontendy nad stejným backendem koexistují tak, že **Django zůstává v kořeni**
(`/`, `/movies`, `/admin`, `/api`) a **Vue SPA se přesune pod `/app/`** (build s
`VITE_BASE=/app/`, router používá `import.meta.env.BASE_URL`). Rozcestník `/` na Vue
odkazuje přes `settings.VUE_FRONTEND_URL` (v produkci `/app/`, lokálně `:5173`).

## Konfigurace

- [inventory.ini](inventory.ini) — **verzovaný** seznam serverů. Uprav si tu
  `ansible_host` (kam) a `ansible_user` (jako kdo). `project_dir` je cesta na serveru,
  kam se rozbalí zdroják.
- [config/production.env](config/production.env) — **necitlivé** nastavení (DEBUG,
  ALLOWED_HOSTS, cesty k datům, port). Commitnuté schválně.
- **Jediné tajemství** je SSH klíč v GitHub secrets jako `SSH_PRIVATE_KEY`
  (Settings → Secrets and variables → Actions). Veřejnou půlku klíče přidej do
  `~/.ssh/authorized_keys` uživatele `ansible_user` na serveru. Ten uživatel musí
  umět spouštět `docker`.

> ⚠️ Bezpečnost jsme tu **záměrně zjednodušili** (školní projekt): `SECRET_KEY` i
> ostatní nastavení jsou v gitu, ven jde jen SSH klíč přes secret. Pro ostrý provoz
> by tajemství patřila do secrets / vaultu, ne do repa.

## Nasazení přes GitHub Actions

[.github/workflows/deploy.yml](../.github/workflows/deploy.yml):

- **push do `main`** → automaticky se nasadí nová verze (data zůstanou).
- **ručně** (Actions → *Deploy* → *Run workflow*) → můžeš zaškrtnout **seed** a tím
  databázi znovu naplnit z fixtures.

## Ruční nasazení (bez Actions)

Z této složky (potřebuješ SSH přístup na server + nainstalovaný Ansible):

```bash
pip install ansible-core
ansible-galaxy collection install community.docker

# nasazení (build + up)
ansible-playbook playbooks/deploy.yml

# naplnění daty — POZOR: napřed databázi vyprázdní (flush), pak nahraje fixtures
ansible-playbook playbooks/seed.yml
```

Co playbooky dělají:

- [playbooks/deploy.yml](playbooks/deploy.yml) — `git archive HEAD` zabalí commitnutý
  stav, pošle ho na server do `project_dir`, tam `docker compose up -d --build`.
  Migrace a collectstatic doběhnou z entrypointu kontejneru.
- [playbooks/seed.yml](playbooks/seed.yml) — `manage.py flush` + `loaddata
  /app/fixtures/*.yaml` uvnitř kontejneru `web` (fixtures jsou zabalené v image).

## Spustit celý stack přímo na serveru (debug)

```bash
cd /srv/filmdb/deploy
docker compose --env-file config/production.env -f docker-compose.yml up -d --build
docker compose --env-file config/production.env -f docker-compose.yml logs -f web
```

## Předpoklady na serveru

- Nainstalovaný Docker + plugin `docker compose`.
- `ansible_user` smí používat docker a má v `authorized_keys` veřejný klíč k `SSH_PRIVATE_KEY`.
- Na `HTTP_PORT` (výchozí 80) se dá dostat zvenčí, případně před stack postav reverzní
  proxy a `HTTP_PORT` přesměruj (Django věří hlavičce `X-Forwarded-Proto`).
