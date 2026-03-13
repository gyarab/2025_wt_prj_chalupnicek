# Webová aplikace
Vznikla v předmětu Webové technologie na Gymnáziu Arabská ve školním roce 2025/2026.

## Local development

Aplikace používá Python Virtual Environment, před spuštěním je potřeba vytvořit venv (pokud neexistuje):

```bash
# Linux
python3 -m venv venv

# Windows
py -3 -m venv venv
```

Dále je třeba venv aktivovat:

```bash
# [Linux]
source ./venv/bin/activate

# Windows - Bash
source ./venv/Scripts/activate

# Windows - Power shell
...
```

Je třeba ujistit se, že jsou nainstalovány všechny závislosti:

```bash
# (venv)$
pip install -r requirements.txt
```

Spustit lokalni server

```bash
cd prj
./manage.py runserver
```

Pokud pouštíme projekt poprvé, je třeba inicializovat DB pomocí

```bash
./manage.py migrate
```

Pokud je DB prázdná a chceme mít přístup do Django administrace, vytvoříme si uživatele pomocí

```bash
./manage.py createsuperuser
```

Doporučuji použít username `admin` a heslo `admin`, bez e-mailu.


## Změna `models.py`

Po kazde zmene v models.py je treba pustit skript, ktery vygeneruje zmenu struktury DB.

```bash
./manage.py makemigrations
```

Pote zmenu DB aplikovat na aktualni zivou DB

```bash
./manage.py migrate
```
