# Local setup

Requirements: Node.js 22+ with npm, Python 3.11+, and two terminals.
Run these from the existing SpeedLife repository root. The original README is unchanged.

```sh
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './backend[dev]'
python -m uvicorn app.main:app --app-dir backend --env-file .env --reload --host 127.0.0.1
```

In the second terminal:

```sh
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. API health: http://127.0.0.1:8000/api/health.
Interactive API docs: http://127.0.0.1:8000/docs.
Vite forwards `/api` requests to the local backend. Production proxy configuration is TODO.

Demo mode requires no keys and makes no external AI calls. Upload 1–5 text PDFs,
at most 100 pages and 15 MB per file, 30 MB combined. The result contains at most
eight source excerpts, page citations, warnings, and a processing trace. It is a
smoke-test workflow, not a complete AI summary of every lecture. Uploaded files
and results remain in request memory; there is no storage or history yet.

## Checks

From the root, with the virtual environment active:

```sh
cd backend
python -m pytest
```

Frontend:

```sh
cd frontend
npm run build
```

Core agent tests can also run without installed packages from the root:

```sh
PYTHONPATH=backend python3 -m unittest discover -s tests/backend -p test_agents.py -v
```

See `tests/frontend/README.md` for browser checks. Test PDFs are generated in memory;
no private lecture materials are included.

Keep `.env` local. All sponsor keys belong on the backend. Do not create `VITE_`
variables for secrets. If `.env` already exists, keep it and add missing variables manually.
No authentication or multi-user isolation is implemented. This scaffold binds to
localhost; add authentication, request limits at the server/proxy, isolated PDF
processing, and persistence controls before hosting it for other users.
