# miniproject6KyleHorn

INF601 - Advanced Programming in Python<br>
Kyle Horn<br>
Mini Project 6

## Master Catch: A Personal-Best Fishing Log

A Django web app where anglers keep **one record per fish species: their biggest one.** Log a longer fish and it replaces your old record. Log one that's the same size or smaller and it isn't saved.

## Description

Most fishing apps log every fish you catch. I wanted something simpler: a quick list of my personal bests. Master Catch keeps one record per species for each user, so the My Records page is always a short table of your biggest fish.

**How the "biggest only" rule works:**

1. **First fish of a species:** saved as your record ("First Walleye logged!").
2. **Same length or shorter than your record:** not saved, and the form shows "Not a new record. Your best Walleye is 24.00 in…"
3. **Longer than your record:** it replaces the old record ("New personal best Walleye!"). You still have only one record for that species.

The database also has a unique constraint on (user, species), so two records of the same species can't exist even if the form is bypassed.

**Pages (7 total, all extend one `base.html` template):**

| Page | URL | Login required |
|---|---|---|
| Home (with a "How it works" Bootstrap modal) | `/` | No |
| About | `/about/` | No |
| Sign up | `/register/` | No |
| Log in | `/login/` | No |
| My Records (table of your biggest fish) | `/records/` | Yes |
| Log a Catch (the form) | `/records/new/` | Yes |
| Catch Detail (with a delete confirmation modal) | `/records/<id>/` | Yes |

**Other features:**

* **Register and login system** using Django's built-in authentication (sign up, log in, log out).
* **Django admin** styled for the Catch model: list columns, filters, search, a date drill-down and grouped form sections.
* **Bootstrap 5** throughout, with two modals ("How it works" and "Delete this record?").
* **51 fish species** to choose from a dropdown, so spelling is always consistent.
* **Each user only sees their own records.** Changing the record number in the URL returns "404 Not Found" instead of someone else's data.
* **17 automated tests** for the biggest-only rule, access control and sign up.

## Getting Started

### Dependencies

* Python 3.12 or newer (Django 6.1 requires it)
* `pip` (comes with Python)
* Git
* All Python packages are listed in `requirements.txt`:
  * `Django` – the web framework
  * `python-dotenv` – loads the secret key from a `.env` file
  * `whitenoise` – serves the admin's CSS/JS when `DEBUG` is off
  * `asgiref`, `sqlparse` – required by Django

Works on Windows and Linux. Commands for both are shown where they differ.

### Installing

1. Clone the repository:

   ```
   git clone https://github.com/kchorn0/miniproject6KyleHorn.git
   cd miniproject6KyleHorn
   ```

2. Create a virtual environment:

   Windows (PowerShell):
   ```
   python -m venv venv
   ```
   Linux (bash):
   ```
   python3 -m venv venv
   ```

3. Activate the virtual environment:

   Windows (PowerShell):
   ```
   .\venv\Scripts\Activate.ps1
   ```
   Linux (bash):
   ```
   source venv/bin/activate
   ```
   You'll see `(venv)` at the start of your prompt. All commands below assume the venv is active.

4. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

5. Create the `.env` file. It holds the secret key, so it is **never committed to GitHub** (it's in `.gitignore`). Run the command for where you're running the site:

   **On your own computer (development):** includes `DJANGO_DEBUG=True` so you can log in over plain `http://127.0.0.1`:
   ```
   python -c "import secrets; open('.env','w').write('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50) + '\nDJANGO_DEBUG=True\n')"
   ```

   **On a live server (like the course dev box):** no debug line, so `DEBUG` stays off:
   ```
   python -c "import secrets; open('.env','w').write('DJANGO_SECRET_KEY=' + secrets.token_urlsafe(50) + '\n')"
   ```

6. **Only if you're hosting at a different address:** open `mysite/settings.py` and change the site address in `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` to your own. `localhost` and `127.0.0.1` already work.

### Database Initialization

1. Create migration files for any model changes. The migrations are already in the repo, so this should say `No changes detected`:
   ```
   python manage.py makemigrations
   ```

2. Build the database tables (creates `db.sqlite3`):
   ```
   python manage.py migrate
   ```

3. Create an admin account for the Django admin. It asks for a username, an optional email, and a password typed twice. The password doesn't show while you type.
   ```
   python manage.py createsuperuser
   ```

4. **Live server only** (when `DEBUG` is off): collect the static files so the admin page has its styling:
   ```
   python manage.py collectstatic --noinput
   ```

### Executing program

**On your own computer:**

1. Start the development server:
   ```
   python manage.py runserver
   ```
2. Open **http://127.0.0.1:8000** in your browser.
3. Click **Sign up** to make a regular user, then **Log a Catch** to add your first fish.
4. The admin is at **http://127.0.0.1:8000/admin/**. Log in with the superuser from Database Initialization.
5. Press `Ctrl + C` in the terminal to stop the server.

**On the course dev box (Linux):**

1. Start a tmux session so the site keeps running after you close the browser tab:
   ```
   tmux new -s work
   ```
2. Activate the venv and start the server on all interfaces, port 8000:
   ```
   source venv/bin/activate
   python manage.py runserver 0.0.0.0:8000
   ```
3. Detach from tmux with `Ctrl + b`, then `d`. Reattach later with `tmux attach -t work`.

**Run the automated tests (optional):**
```
python manage.py test
```
It should end with `Ran 17 tests` and `OK`. The tests use a temporary database, so your real data isn't touched.

## Help

* **`KeyError: 'DJANGO_SECRET_KEY'`**: there's no `.env` file in the project folder (next to `manage.py`). Redo step 5 of Installing.
* **`ModuleNotFoundError: No module named 'django'`**: the venv isn't active, or the packages weren't installed. Redo steps 3 and 4 of Installing.
* **`running scripts is disabled on this system` (Windows)**: PowerShell is blocking `Activate.ps1`. Skip activation and run commands with the venv's Python directly, e.g. `.\venv\Scripts\python.exe manage.py runserver`, or allow it once with `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
* **Can't stay logged in on `http://127.0.0.1`**: your `.env` is missing `DJANGO_DEBUG=True`. With debug off, login cookies are only sent over HTTPS. Use the development `.env` command in step 5.
* **400 Bad Request**: the address you're visiting isn't in `ALLOWED_HOSTS` in `mysite/settings.py`.
* **403 Forbidden (CSRF) when logging in or submitting a form on the live site**: `CSRF_TRUSTED_ORIGINS` doesn't match your site address. It must include `https://`.
* **Admin page has no styling on the live site**: run `python manage.py collectstatic --noinput`, then restart the server.
* **502 Bad Gateway on the dev box**: the server isn't running, or it was started without `0.0.0.0:8000`. Start it with `python manage.py runserver 0.0.0.0:8000` inside tmux.
* **Forgot your admin password**: run `python manage.py changepassword <username>`. It doesn't need the old password.

## Authors

Kyle Horn ([kchorn@mail.fhsu.edu](mailto:kchorn@mail.fhsu.edu))

## Acknowledgments

* [Django documentation](https://docs.djangoproject.com/en/stable/)
* [Django authentication views](https://docs.djangoproject.com/en/stable/topics/auth/default/#module-django.contrib.auth.views)
* [Bootstrap 5 documentation](https://getbootstrap.com/docs/5.3/) (modals, navbar, tables, forms)
* [WhiteNoise documentation](https://whitenoise.readthedocs.io/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)

## AI Usage

I used **Claude Code** in VS Code as a helper on this project. I reviewed every file before committing it, made all commits and pushes myself from VS Code, and tested the site myself.

### What AI helped with:

* **Planning:** read the assignment rubric and week notes and turned them into a step-by-step plan and an expected folder layout.
* **Dev box setup:** gave me step-by-step terminal commands for tmux, git, the virtual environment and Django on the course dev box.
* **Django code:** wrote the first drafts of `settings.py`, the admin setup, the forms (including the "biggest only" rule), the views and the URLs.
* **Templates:** drafted the Bootstrap templates for all 7 pages, including both modals.
* **Comments and docstrings:** added comments and docstrings across the code following PEP 8 and PEP 257.
* **Tests:** wrote the 17 automated tests in `tests.py` and explained why they matter for the Week 12 pentest.
* **Security:** suggested keeping the secret key in a `.env` file, turning `DEBUG` off on the live site, and filtering every record lookup by the logged-in user so users can't see each other's records (IDOR protection).
* **README:** drafted this template.

### What I personally did:

* Chose the project idea: a fishing log that keeps only the **biggest fish of each species**, instead of every catch.
* Named the app `Master_Catch`, and explained exactly how the app should function and flow: each process and what each button should do.
* Created the GitHub repository and cloned it to my PC and to the dev box.
* Signed in to the dev box, set up my authenticator app, and ran the setup commands in the terminal.
* Reviewed each group of files and the explanation of what each one does before committing it or changing it.
* Made **every commit and push myself** in VS Code, with my own commit messages.
* Tested the site myself in the browser: signing up, logging in, logging catches, trying smaller and bigger fish, deleting records and using the admin.
* Chose the final list of fish species for the dropdown.
* Deployed and ran the finished site on my dev box.
* Wrote and edited this AI Usage section.

### What AI did that I changed/modified:

* **Working style:** at first the AI built several steps at once and made commits with its own messages. I stopped it, had it undo those commits (keeping the files), and switched to one step at a time, with me reviewing each change and making my own commits.
* **App name:** the AI suggested `catches` as the app name. I named it `Master_Catch` instead.
* **Comments:** I asked for clear comments on each line so I can explain what every part does, following PEP 8 and PEP 257.
* **Fish species list:** the AI started with 15 common Kansas fish. I replaced it with my own list of 48 species, then had Walleye, Saugeye and Wiper added back (51 total).
* **PEP 8 and PEP 257:** adjusted comments and code to keep up with PEP 8 and PEP 257 requirements.
