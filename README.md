# State-Adaptive Regional Panchang & Rashifal

Complete VS Code runnable FastAPI project based on the supplied specification.

Features:
- Swiss Ephemeris calculations
- Location-aware sunrise/sunset
- Tithi, Nakshatra, Yoga, Karana and Vaar
- Rahu Kalam and Abhijit Muhurat
- Regional Choghadiya / Gowri Panchangam
- JSON file storage as the primary zero-cost store
- Optional Redis cache
- Optional PostgreSQL audit/persistence
- Optional Gemini Rashifal
- Browser frontend served by FastAPI
- Docker Compose

## Run in VS Code

Windows PowerShell:
```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Linux/macOS:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 and http://localhost:8000/docs.

## Optional services

Redis:
```env
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

PostgreSQL:
```env
POSTGRES_ENABLED=true
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/panchang
```

Gemini:
```env
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-2.5-flash
```

Without Gemini, deterministic fallback Rashifal is returned.

## Docker

```bash
docker compose up --build
```

API:
- GET /api/v1/health
- GET /api/v1/states
- GET /api/v1/panchang
- GET /api/v1/rashifal
- GET /api/v1/festivals
