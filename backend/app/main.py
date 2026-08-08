from datetime import date,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from .config import settings
from .cache import cache
from .database import init_db
from .panchang import calculate_panchang
from .regional import regional_timings,available_states
from .rashifal import LANGUAGES,generate_rashifal
from .storage import get_or_create,ensure_dirs

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"

app=FastAPI(title=settings.app_name,version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

@app.on_event("startup")
def startup():
    ensure_dirs()
    init_db()

def current_date(tz):
    return datetime.now(ZoneInfo(tz)).date()

@app.get("/api/v1/health")
def health():
    return {
        "status":"ok",
        "service":settings.app_name,
        "cache":cache.status(),
        "json_storage":settings.json_storage_enabled,
        "postgres":settings.postgres_enabled,
        "gemini_configured":bool(settings.gemini_api_key)
    }

@app.get("/api/v1/states")
def states():
    return {"states":available_states(),"languages":LANGUAGES}

@app.get("/api/v1/panchang")
def panchang(
    state_code:str=Query("KA"),
    lat:float=Query(settings.default_lat),
    lon:float=Query(settings.default_lon),
    timezone:str=Query(settings.default_timezone),
    date_str:str|None=Query(None)
):
    try: ZoneInfo(timezone)
    except Exception: timezone=settings.default_timezone
    target=date.fromisoformat(date_str) if date_str else current_date(timezone)
    state_code=state_code.upper()
    key=f"panchang:{target}:{state_code}:{lat:.5f}:{lon:.5f}:{timezone}"

    def generate():
        data=calculate_panchang(target,lat,lon,timezone,state_code)
        s=data["panchang"]["sunrise"]; e=data["panchang"]["sunset"]
        sunrise=sunset=None
        if s and e:
            tz=ZoneInfo(timezone)
            sunrise=datetime.strptime(f"{target} {s}","%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
            sunset=datetime.strptime(f"{target} {e}","%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
        data["regional"]=regional_timings(sunrise,sunset,(target.weekday()+1)%7,state_code)
        data["metadata"]={"engine":"Swiss Ephemeris","sidereal_mode":"Lahiri","cache_key":key}
        return data
    return get_or_create(key,"panchang",generate)

@app.get("/api/v1/rashifal")
def rashifal(lang:str=Query("kn"),date_str:str|None=Query(None)):
    lang=lang.lower()
    if lang not in LANGUAGES: lang="kn"
    target=date.fromisoformat(date_str) if date_str else current_date(settings.default_timezone)
    return get_or_create(
        f"rashifal:{target}:{lang}",
        "rashifal",
        lambda:generate_rashifal(lang,target)
    )

@app.get("/api/v1/festivals")
def festivals(state_code:str="KA",date_str:str|None=None):
    target=date.fromisoformat(date_str) if date_str else current_date(settings.default_timezone)
    return {"date":target.isoformat(),"state_code":state_code.upper(),"events":[]}

@app.get("/")
def home():
    return FileResponse(FRONTEND / "index.html")

@app.get("/i18n.js")
def i18n_js():
    return FileResponse(FRONTEND / "i18n.js", media_type="application/javascript")
