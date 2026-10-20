# ScamLens AI

ScamLens AI is a beginner-friendly prototype for verifying suspicious internship and job offers.

## Phase 1
This repo currently includes:
- a FastAPI backend skeleton
- a health check endpoint
- environment template
- starter project structure
- a basic health test

## Run locally
```bash
cd "c:\Users\ira23\OneDrive\Desktop\CS\ScamLens AI"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install "fastapi>=0.111,<1" "uvicorn[standard]>=0.30,<1" "httpx>=0.27,<1" "pytest>=8,<9"
pytest backend/tests/test_health.py -q
uvicorn backend.app.main:app --reload