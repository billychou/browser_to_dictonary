# Repository Guidelines

This monorepo contains a Chrome extension, its WeChat mini-program companion, and their shared API backend for collecting words from web pages into a personal vocabulary book.

## Project Structure & Module Organization

- `vocabulary-book/` — Plasmo-based Chrome extension (Manifest V3, React + TypeScript + Tailwind).
  - `popup.tsx` (popup UI), `background.ts` (service worker), `contents/` (content scripts, e.g. `highlight.ts`, `notification.tsx`), `assets/` (icons).
  - Extension manifest (permissions, host permissions) is declared in `package.json` under `manifest`.
- `wechat-mini/` — WeChat mini-program client (native WXML/WXSS/JS, no build step).
  - Shares the backend account & data with the extension; pages under `pages/` (`login`, `words`, `study`, `profile`), shared logic in `utils/`, server address in `config/api.js`. See `wechat-mini/README.md`.
- `vocabulary_book_backend/` — Flask API (Python ≥3.9).
  - Source: flat layout directly under `vocabulary_book_backend/` (`app.py`, `app_factory.py`, `wsgi.py` at the root) with layers `controllers/` (Flask-RESTful resources under `/api/...`), `services/` (business logic), `models/` (SQLAlchemy), `configs/` (pydantic-settings), `extensions/`, `libs/`, `fields/`, `migrations/` (Alembic via Flask-Migrate).
  - Tests: `vocabulary_book_backend/tests/`.
  - API reference (endpoints, auth, conventions): `docs/api.md`.

## Build, Test, and Development Commands

**Extension** (`vocabulary-book/`, pnpm):
- `pnpm dev` — dev build with hot reload; load `build/chrome-mv3-dev` in Chrome.
- `pnpm build` — production bundle (`build/chrome-mv3-prod`).
- `pnpm package` — zip the build for store submission.

**Mini-program** (`wechat-mini/`):
- No build step. Import the directory into WeChat DevTools (test AppID works); enable "不校验合法域名" for local development against `http://127.0.0.1:7001`.

**Full local setup without Docker** (Homebrew MySQL/Redis, all three clients): `docs/local-development.md`.

**Backend** (`vocabulary_book_backend/`, uv preferred; `poetry.lock` also present):
- `./dev.sh` — one-command local startup: ensures MySQL/Redis are running (brew), generates `.env` on first run, syncs deps, migrates, starts port 7001.
- `uv sync` — install dependencies into `.venv`.
- `uv run python app.py` — run locally on port 7001.
- `uv run pytest tests/` — run tests from `vocabulary_book_backend/`.
- `upgrade-db` (registered CLI command) — apply database migrations.
- `gunicorn -c deploy/gunicorn.conf.py wsgi:app` — production server (WSGI entry `wsgi.py` at the backend root).

## Coding Style & Naming Conventions

- Extension: 2-space indent, no semicolons, double quotes, no trailing commas (Prettier, see `vocabulary-book/.prettierrc.mjs`; imports auto-sorted). TypeScript `~/*` alias maps to project root.
- Mini-program: 2-space indent, double quotes, no semicolons (same conventions as the extension); pages keep WXML/WXSS/JS/JSON quartets named after the page folder.
- Backend: PEP 8, 4-space indent, `snake_case` functions/variables, `PascalCase` classes, type hints expected. Keep controllers thin; business logic belongs in `services/`.
- Python files start with a docstring header (`File:`, `Author:`, `Date:`).

## Testing Guidelines

- Framework: pytest. Test files live in `tests/test_services/` mirroring the source layer, named `test_*.py` with `test_*` functions.
- Two flavors: mocked unit tests (`test_sms_code_guard.py`, `TestCode2Session` in `test_wechat_login.py` — mock Redis/HTTP, run anywhere) and integration tests that build the real app (`create_app()`) and need MySQL (schema via `tests/setup_schema.py`). Prefer mocking external dependencies in new tests; CI provides MySQL/Redis services.

## Commit & Pull Request Guidelines

- Commit messages follow Conventional Commits: `type(scope): summary` — e.g. `feat(user): ...`, `fix(vocabulary_service): ...`, `chore(popup): ...`. Scopes are usually a module name (`user`, `word`, `config`, `vocabulary-book`).
- PRs: describe what/why, link related issues, and include screenshots for UI changes. Keep each PR focused on one change.

## CI & Deployment

- Workflows live at the repo root `.github/workflows/` (never in subdirectories — GitHub ignores them there).
- `backend-ci.yml` — pytest with MySQL/Redis services; schema created via `tests/setup_schema.py`.
- `frontend-ci.yml` — `tsc --noEmit`, Prettier check, `pnpm build`, `pnpm package` (uploads zip artifact).
- `submit.yml` — manual web-store submission (needs `SUBMIT_KEYS` secret).
- Production deployment (Docker Compose / systemd / Nginx TLS): see `docs/deployment.md`. pnpm version is pinned via the `packageManager` field in `vocabulary-book/package.json`.

## Security & Configuration Tips

- Backend configuration is loaded from a local `.env` file (pydantic-settings: `DB_*`, Redis, JWT, Aliyun SMS keys). Never commit `.env` or hardcode credentials in `configs/` defaults.
- The extension talks to the backend only through the CORS-allowed origin configured in `app_factory.py`; keep API URLs and permissions minimal.
