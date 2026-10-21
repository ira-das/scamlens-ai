# ScamLens AI

ScamLens AI is a beginner-friendly prototype for verifying suspicious internship and job offers.

## Run locally

Use Python 3.12.10 and install the pinned runtime dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item backend/.env.example backend/.env
$env:PORT = "8000"
uvicorn backend.app.main:app --host 0.0.0.0 --port $env:PORT --reload
```

The app does not require a `.env` file to start. The backend reads environment variables directly; copy the example only if you want to set local overrides. Keep real keys in your local environment and never commit them.

To run tests, install `requirements-dev.txt` and run `python -m pytest backend/tests -q`.

## Deploy

For Render, use the repository root as the backend root directory, set the build command to:

```text
pip install -r requirements.txt
```

Set the start command to:

```text
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

Configure these environment variables in Render. `PORT` is provided by Render; `ALLOWED_ORIGIN_REGEX` is optional.

| Variable | Purpose |
| --- | --- |
| `USE_MOCKS` | Set `true` for simulated lookups; defaults to `true`. |
| `TINYFISH_API_KEY` | TinyFish credentials when real lookups are enabled. |
| `GEMINI_API_KEY` | Gemini credentials if Gemini extraction is enabled. |
| `GEMINI_MODEL` | Gemini model name; defaults to `gemini-2.5-flash`. |
| `ALLOWED_ORIGINS` | Comma-separated frontend origins, including the deployed Vercel URL. |
| `ALLOWED_ORIGIN_REGEX` | Optional regex for Vercel preview origins. |
| `PORT` | Render-provided server port. |

For Vercel, set `NEXT_PUBLIC_API_URL` to the deployed Render service URL.