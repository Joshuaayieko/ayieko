# Deploying Orbes

The repo is pre-configured for one-connect deployment. You'll do the final step
(connecting your account) — that part can't be automated because it needs your
login on the hosting platform.

After deploying you get a public URL like `https://orbes-backend.onrender.com`.
Open **`<that URL>/app`** in any browser — phone or laptop — to use Orbes.

---

## Option A — Render (recommended, free)

1. Push this repo to GitHub (already done on your branch).
2. Go to <https://dashboard.render.com> and sign up / log in (free).
3. Click **New +** → **Blueprint**.
4. Connect your GitHub and pick this repository + branch
   `claude/ai-assistant-mobile-app-ml4jgi`.
5. Render detects `render.yaml` and shows the `orbes-backend` service. It will
   ask you to fill in the secret env vars:
   - `ORBES_ADMIN_EMAIL` → `ayiekojoshua775@gmail.com`
   - `ORBES_ADMIN_PASSWORD` → your password
   - `ANTHROPIC_API_KEY` → your key from <https://console.anthropic.com>
     (needed for real AI replies; leave blank to run in offline mode)
   - `ORBES_SECRET_KEY` is generated automatically.
6. Click **Apply**. First build takes a few minutes.
7. Open `https://<your-service>.onrender.com/app` and sign in.

> Free tier notes: the service sleeps after ~15 min idle (first request after
> sleep is slow), and the SQLite disk is ephemeral — the admin account is
> re-seeded on every deploy, but conversation history resets. For persistent
> data, add a database (below).

### Persistent database (optional)

Use any free Postgres (Render Postgres, [Neon](https://neon.tech),
[Supabase](https://supabase.com)). Copy its connection string and set:

```
ORBES_DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DBNAME
```

Then add `psycopg2-binary` to `backend/requirements.txt` and redeploy.

---

## Option B — Railway (free trial credit)

1. Go to <https://railway.app> and log in.
2. **New Project** → **Deploy from GitHub repo** → pick this repo.
3. In **Settings**, set the root directory to `backend` (it reads the `Procfile`).
4. Under **Variables**, add: `ORBES_ADMIN_EMAIL`, `ORBES_ADMIN_PASSWORD`,
   `ANTHROPIC_API_KEY`, and a long random `ORBES_SECRET_KEY`.
5. Railway assigns a public domain — open `<domain>/app`.

---

## Option C — Docker (any host / your own server)

```bash
cd backend
docker build -t orbes .
docker run -p 8000:8000 \
  -e ORBES_ADMIN_EMAIL=ayiekojoshua775@gmail.com \
  -e ORBES_ADMIN_PASSWORD='your-password' \
  -e ORBES_SECRET_KEY='a-long-random-string' \
  -e ANTHROPIC_API_KEY='sk-ant-...' \
  orbes
```

Open <http://localhost:8000/app>.

---

## After deploying

- Web UI: `<public-url>/app`
- API docs: `<public-url>/docs`
- Health check: `<public-url>/health`
- Point the Flutter app at it:
  `flutter run --dart-define=API_BASE_URL=https://<public-url>`
