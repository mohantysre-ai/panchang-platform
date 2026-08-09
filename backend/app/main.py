from datetime import date,datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from fastapi import FastAPI,Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.staticfiles import StaticFiles
from .config import settings
from .cache import cache
from .database import init_db
from .panchang import calculate_panchang, month_calendar
from .regional_v2 import regional_timings, available_states, state_style, regional_month_name
from .rashifal import LANGUAGES,generate_rashifal
from .storage import get_or_create,ensure_dirs
from .festivals import festivals_for_date, festivals_for_month, lunar_month_for_date
FRONTEND=Path(__file__).resolve().parents[2]/"frontend"
app=FastAPI(title=settings.app_name,version="3.1.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.on_event("startup")
def startup():ensure_dirs();init_db()
def current_date(tz):return datetime.now(ZoneInfo(tz)).date()
@app.get("/api/v1/health")
def health():return {"status":"ok","service":settings.app_name,"cache":cache.status(),"json_storage":settings.json_storage_enabled,"postgres":settings.postgres_enabled,"gemini_configured":bool(settings.gemini_api_key),"release":"regional-calendar-launch"}
@app.get("/api/v1/states")
def states():return {"states":available_states(),"languages":LANGUAGES}
@app.get("/api/v1/panchang")
def panchang(state_code:str=Query("KA"),lat:float=Query(settings.default_lat),lon:float=Query(settings.default_lon),timezone:str=Query(settings.default_timezone),date_str:str|None=Query(None)):
    try:ZoneInfo(timezone)
    except Exception:timezone=settings.default_timezone
    target=date.fromisoformat(date_str) if date_str else current_date(timezone);state_code=state_code.upper();key=f"panchang:{target}:{state_code}:{lat:.5f}:{lon:.5f}:{timezone}"
    def generate():
        data=calculate_panchang(target,lat,lon,timezone,state_code);s=data["panchang"]["sunrise"];e=data["panchang"]["sunset"];sunrise=sunset=None
        if s and e:
            tz=ZoneInfo(timezone);sunrise=datetime.strptime(f"{target} {s}","%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz);sunset=datetime.strptime(f"{target} {e}","%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
        data["regional"]=regional_timings(sunrise,sunset,(target.weekday()+1)%7,state_code);data["metadata"]={"engine":"Swiss Ephemeris","sidereal_mode":"Lahiri","cache_key":key};return data
    return get_or_create(key,"panchang",generate)
@app.get("/api/v1/rashifal")
def rashifal(lang:str=Query("kn"),date_str:str|None=Query(None)):
    lang=lang.lower();lang=lang if lang in LANGUAGES else "kn";target=date.fromisoformat(date_str) if date_str else current_date(settings.default_timezone);return get_or_create(f"rashifal:{target}:{lang}","rashifal",lambda:generate_rashifal(lang,target))
@app.get("/api/v1/festivals")
def festivals(state_code:str=Query("KA"),lat:float=Query(settings.default_lat),lon:float=Query(settings.default_lon),timezone:str=Query(settings.default_timezone),date_str:str|None=Query(None),year:int|None=Query(None),month:int|None=Query(None)):
    try:ZoneInfo(timezone)
    except Exception:timezone=settings.default_timezone
    state_code=state_code.upper()
    if year is not None or month is not None:
        today=current_date(timezone);y=year or today.year;m=month or today.month;m=m if 1<=m<=12 else today.month;return festivals_for_month(y,m,state_code,lat,lon,timezone)
    target=date.fromisoformat(date_str) if date_str else current_date(timezone);return festivals_for_date(target,state_code,lat,lon,timezone)
@app.get("/api/v1/lunar-month")
def lunar_month(state_code:str=Query("KA"),date_str:str|None=Query(None),timezone:str=Query(settings.default_timezone),lat:float=Query(settings.default_lat),lon:float=Query(settings.default_lon)):
    try:ZoneInfo(timezone)
    except Exception:timezone=settings.default_timezone
    target=date.fromisoformat(date_str) if date_str else current_date(timezone);return lunar_month_for_date(target,state_code,lat,lon,timezone)
@app.get("/api/v1/calendar/month")
def calendar_month(state_code:str=Query("KA"),year:int|None=Query(None),month:int|None=Query(None),timezone:str=Query(settings.default_timezone)):
    try:ZoneInfo(timezone)
    except Exception:timezone=settings.default_timezone
    today=current_date(timezone);year=year or today.year;month=month or today.month;month=month if 1<=month<=12 else today.month;state_code=state_code.upper();key=f"calmonth:{year}:{month}:{state_code}:{timezone}"
    def generate():
        data=month_calendar(year,month,timezone,state_code);data["calendar_style"]=state_style(state_code);data["regional_month_name"]=regional_month_name(state_code,month);data["regional_accent"]=available_states()[state_code]["accent"];data["priority_fields"]=available_states()[state_code]["priority_fields"];data["layout"]="row_weekday" if state_style(state_code) in {"odia","malayalam","assamese"} else "col_weekday";return data
    return get_or_create(key,"panchang",generate)
@app.get("/regional-ui.css")
def regional_css():return FileResponse(FRONTEND/"regional-ui.css",media_type="text/css")
@app.get("/regional-ui.js")
def regional_js():return FileResponse(FRONTEND/"regional-ui.js",media_type="application/javascript")
@app.get("/state-options.js")
def state_options_js():return FileResponse(FRONTEND/"state-options.js",media_type="application/javascript")
@app.get("/app-shell.css")
def app_shell_css():return FileResponse(FRONTEND/"app-shell.css",media_type="text/css")
@app.get("/app-shell.js")
def app_shell_js():return FileResponse(FRONTEND/"app-shell.js",media_type="application/javascript")
@app.get("/launch-enhancements.js")
def launch_enhancements_js():return FileResponse(FRONTEND/"launch-enhancements.js",media_type="application/javascript")
@app.get("/manifest.webmanifest")
def manifest():return FileResponse(FRONTEND/"manifest.webmanifest",media_type="application/manifest+json")
@app.get("/sw.js")
def service_worker():return FileResponse(FRONTEND/"sw.js",media_type="application/javascript")
@app.get("/")
def home():
    html=(FRONTEND/"index.html").read_text(encoding="utf-8")
    inject='<link rel="manifest" href="/manifest.webmanifest"><link rel="stylesheet" href="/regional-ui.css?v=5"><link rel="stylesheet" href="/app-shell.css?v=1"><script src="/state-options.js?v=2"></script><script defer src="/regional-ui.js?v=6"></script><script defer src="/app-shell.js?v=1"></script><script defer src="/launch-enhancements.js?v=1"></script>'
    html=html.replace('</head>',inject+'</head>')
    return HTMLResponse(html)
@app.get("/i18n.js")
def i18n_js():return FileResponse(FRONTEND/"i18n.js",media_type="application/javascript")
@app.get("/fonts.css")
def fonts_css():return FileResponse(FRONTEND/"fonts.css",media_type="text/css")
app.mount("/assets",StaticFiles(directory=FRONTEND/"assets"),name="assets")