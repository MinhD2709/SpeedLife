# Setup

## Local demo

```sh
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e './backend[dev]'
python -m uvicorn app.main:app --app-dir backend --env-file .env --reload --host 127.0.0.1
```

In another terminal:

```sh
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. Demo mode uses the same planner and Scout engine as
live mode, with local substitutes for Zetaris and Nightshift.

## Live mode

1. Complete `data/zetaris/README.md`, keep the Codespace ports private, and keep
   `gh codespace ports forward 3000:3000 8888:8888` running.
2. Install Nightshift, add the NVIDIA key in Providers, seat a Nemotron lane and
   copy the Runtime URL/token/route from Console.
3. Fill the root `.env`, generate a unique `SCOUT_SIGNING_SECRET`, and set
   `METERLESS_NEMOTRON_ROUTE_CONFIRMED=true` only after a redacted Nightshift
   receipt proves the configured route used the Nemotron lane.
4. Set `APP_MODE=live`, restart the API, and open
   `http://127.0.0.1:8000/api/integrations/status`.
5. Require `live_ready: true` before the demo. This gates Zetaris, Nightshift
   health and model discovery, the Nemotron receipt flag, and Scout signing.

## Checks

```sh
PYTHONPATH=backend python -m pytest -q
cd frontend && npm run build
```

For Scout's official harness, clone the Meterless Scout engine separately, install
its dependencies, and set `SCOUT_IMPL` to the absolute path of
`meterless/scout_adapter.mjs` in this repository.
