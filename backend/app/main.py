from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from .cache import cache
from .config import settings
from .database import init_db
from .festivals import festivals_for_date, festivals_for_month, lunar_month_for_date
from .panchang import calculate_panchang, month_calendar
from .rashifal import LANGUAGES, build_rashi_detail, enrich_rows_detailed, fetch_daily_horoscope, generate_rashifal
from .regional_v2 import available_states, regional_month_name, regional_timings, state_style
from .storage import ensure_dirs, get_or_create

FRONTEND = Path(__file__).resolve().parents[2] / "frontend"
DIST = FRONTEND / "dist"
REACT_ASSETS = DIST / "_app"

app = FastAPI(title=settings.app_name, version="3.2.1")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    ensure_dirs()
    init_db()


def current_date(tz):
    return datetime.now(ZoneInfo(tz)).date()


@app.get("/api/v1/health")
def health():
    return {
        "status": "ok",
        "service": settings.app_name,
        "cache": cache.status(),
        "json_storage": settings.json_storage_enabled,
        "postgres": settings.postgres_enabled,
        "gemini_configured": bool(settings.gemini_api_key),
        "release": "classic-first",
        "react_build": DIST.joinpath("index.html").exists(),
    }


@app.get("/api/v1/states")
def states():
    return {"states": available_states(), "languages": LANGUAGES}


@app.get("/api/v1/panchang")
def panchang(
    state_code: str = Query("KA"),
    lat: float = Query(settings.default_lat),
    lon: float = Query(settings.default_lon),
    timezone: str = Query(settings.default_timezone),
    date_str: str | None = Query(None),
):
    try:
        ZoneInfo(timezone)
    except Exception:
        timezone = settings.default_timezone
    target = date.fromisoformat(date_str) if date_str else current_date(timezone)
    state_code = state_code.upper()
    key = f"panchang:{target}:{state_code}:{lat:.5f}:{lon:.5f}:{timezone}"

    def generate():
        data = calculate_panchang(target, lat, lon, timezone, state_code)
        s = data["panchang"]["sunrise"]
        e = data["panchang"]["sunset"]
        sunrise = sunset = None
        if s and e:
            tz = ZoneInfo(timezone)
            sunrise = datetime.strptime(f"{target} {s}", "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
            sunset = datetime.strptime(f"{target} {e}", "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
        data["regional"] = regional_timings(sunrise, sunset, (target.weekday() + 1) % 7, state_code)
        data["metadata"] = {"engine": "Swiss Ephemeris", "sidereal_mode": "Lahiri", "cache_key": key}
        return data

    data = get_or_create(key, "panchang", generate)
    # Backfill rashi indices for older cache entries
    ast = data.get("astronomy") or {}
    if "moon_rashi_index" not in ast and "moon_sidereal_longitude" in ast:
        moon = float(ast["moon_sidereal_longitude"])
        sun = float(ast.get("sun_sidereal_longitude") or 0)
        ast = {
            **ast,
            "moon_rashi_index": int(moon // 30) + 1,
            "sun_rashi_index": int(sun // 30) + 1,
        }
        data = {**data, "astronomy": ast}
    return data


@app.get("/api/v1/rashifal")
def rashifal(lang: str = Query("kn"), date_str: str | None = Query(None)):
    lang = lang.lower()
    lang = lang if lang in LANGUAGES else "kn"
    target = date.fromisoformat(date_str) if date_str else current_date(settings.default_timezone)
    data = get_or_create(f"rashifal:{target}:{lang}", "rashifal", lambda: generate_rashifal(lang, target))
    rows = enrich_rows_detailed(list(data.get("rashifal") or []), lang)
    return {**data, "rashifal": rows}


@app.get("/api/v1/rashifal/detail")
def rashifal_detail(
    sign: str = Query("aries"),
    lang: str = Query("kn"),
    state_code: str = Query("KA"),
    date_str: str | None = Query(None),
    lat: float = Query(settings.default_lat),
    lon: float = Query(settings.default_lon),
    timezone: str = Query(settings.default_timezone),
):
    """Expanded write-up for one rashi: regional sections + state context + daily/weekly/monthly."""
    lang = lang.lower()
    lang = lang if lang in LANGUAGES else "kn"
    state_code = state_code.upper()
    try:
        ZoneInfo(timezone)
    except Exception:
        timezone = settings.default_timezone
    target = date.fromisoformat(date_str) if date_str else current_date(timezone)

    bundle = get_or_create(f"rashifal:{target}:{lang}", "rashifal", lambda: generate_rashifal(lang, target))
    rows = enrich_rows_detailed(list(bundle.get("rashifal") or []), lang)
    sign_key = (sign or "aries").strip().lower()
    row = next((r for r in rows if (r.get("sign") or "").lower() == sign_key), None)
    if row is None and rows:
        # fall back by index order of RASHI_META
        from .rashifal import RASHI_META
        idx = next((i for i, m in enumerate(RASHI_META) if m["sign"] == sign_key), 0)
        row = rows[idx] if idx < len(rows) else rows[0]

    pan_key = f"panchang:{target}:{state_code}:{lat:.5f}:{lon:.5f}:{timezone}"

    def gen_pan():
        data = calculate_panchang(target, lat, lon, timezone, state_code)
        s = data["panchang"]["sunrise"]
        e = data["panchang"]["sunset"]
        sunrise = sunset = None
        if s and e:
            tz = ZoneInfo(timezone)
            sunrise = datetime.strptime(f"{target} {s}", "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
            sunset = datetime.strptime(f"{target} {e}", "%Y-%m-%d %I:%M:%S %p").replace(tzinfo=tz)
        data["regional"] = regional_timings(sunrise, sunset, (target.weekday() + 1) % 7, state_code)
        data["metadata"] = {"engine": "Swiss Ephemeris", "sidereal_mode": "Lahiri", "cache_key": pan_key}
        return data

    panchang = get_or_create(pan_key, "panchang", gen_pan)
    ast = panchang.get("astronomy") or {}
    if "moon_rashi_index" not in ast and "moon_sidereal_longitude" in ast:
        moon = float(ast["moon_sidereal_longitude"])
        sun = float(ast.get("sun_sidereal_longitude") or 0)
        panchang = {
            **panchang,
            "astronomy": {
                **ast,
                "moon_rashi_index": int(moon // 30) + 1,
                "sun_rashi_index": int(sun // 30) + 1,
            },
        }

    return build_rashi_detail(sign_key, lang, state_code, target, row=row, panchang=panchang)


@app.get("/api/v1/horoscope/daily")
def daily_horoscope(sign: str = Query("aries")):
    """Proxy daily sun-sign horoscope (English) with ruling planet metadata."""
    return fetch_daily_horoscope(sign)

@app.get("/api/v1/festivals")
def festivals(
    state_code: str = Query("KA"),
    lat: float = Query(settings.default_lat),
    lon: float = Query(settings.default_lon),
    timezone: str = Query(settings.default_timezone),
    date_str: str | None = Query(None),
    year: int | None = Query(None),
    month: int | None = Query(None),
):
    try:
        ZoneInfo(timezone)
    except Exception:
        timezone = settings.default_timezone
    state_code = state_code.upper()
    if year is not None or month is not None:
        today = current_date(timezone)
        y = year or today.year
        m = month or today.month
        m = m if 1 <= m <= 12 else today.month
        return festivals_for_month(y, m, state_code, lat, lon, timezone)
    target = date.fromisoformat(date_str) if date_str else current_date(timezone)
    return festivals_for_date(target, state_code, lat, lon, timezone)


@app.get("/api/v1/lunar-month")
def lunar_month(
    state_code: str = Query("KA"),
    date_str: str | None = Query(None),
    timezone: str = Query(settings.default_timezone),
    lat: float = Query(settings.default_lat),
    lon: float = Query(settings.default_lon),
):
    try:
        ZoneInfo(timezone)
    except Exception:
        timezone = settings.default_timezone
    target = date.fromisoformat(date_str) if date_str else current_date(timezone)
    return lunar_month_for_date(target, state_code, lat, lon, timezone)


@app.get("/api/v1/calendar/month")
def calendar_month(
    state_code: str = Query("KA"),
    year: int | None = Query(None),
    month: int | None = Query(None),
    timezone: str = Query(settings.default_timezone),
):
    try:
        ZoneInfo(timezone)
    except Exception:
        timezone = settings.default_timezone
    today = current_date(timezone)
    year = year or today.year
    month = month or today.month
    month = month if 1 <= month <= 12 else today.month
    state_code = state_code.upper()
    key = f"calmonth:{year}:{month}:{state_code}:{timezone}"

    def generate():
        data = month_calendar(year, month, timezone, state_code)
        data["calendar_style"] = state_style(state_code)
        data["regional_month_name"] = regional_month_name(state_code, month)
        data["regional_accent"] = available_states()[state_code]["accent"]
        data["priority_fields"] = available_states()[state_code]["priority_fields"]
        data["layout"] = (
            "row_weekday" if state_style(state_code) in {"odia", "malayalam", "assamese"} else "col_weekday"
        )
        return data

    return get_or_create(key, "panchang", generate)


def _inject_classic(html: str) -> str:
    inject = (
        '<link rel="manifest" href="/manifest.webmanifest">'
        '<meta http-equiv="Cache-Control" content="no-cache">'
        '<link rel="stylesheet" href="/regional-ui.css?v=10">'
        '<link rel="stylesheet" href="/app-shell.css?v=9">'
        '<script defer src="/share-card.js?v=1"></script>'
        '<script defer src="/live-activity.js?v=1"></script>'
        '<script defer src="/classic-extras.js?v=1"></script>'
        '<script defer src="/regional-ui.js?v=10"></script>'
        '<script defer src="/app-shell.js?v=9"></script>'
        '<script defer src="/launch-enhancements.js?v=5"></script>'
    )
    return html.replace("</head>", inject + "</head>")


def _classic_html() -> HTMLResponse:
    html = (FRONTEND / "classic.html").read_text(encoding="utf-8")
    return HTMLResponse(_inject_classic(html))


@app.get("/")
def home():
    """Classic regional panji is the primary experience."""
    return _classic_html()


@app.get("/classic")
def classic_home():
    return _classic_html()


@app.get("/app")
def react_app():
    dist_index = DIST / "index.html"
    if dist_index.exists():
        return FileResponse(dist_index)
    return HTMLResponse(
        "<p>React dashboard not built. Run <code>npm run build</code> in frontend/.</p>"
        '<p><a href="/">Back to classic</a></p>',
        status_code=503,
    )


@app.get("/regional-ui.css")
def regional_css():
    return FileResponse(FRONTEND / "regional-ui.css", media_type="text/css")


@app.get("/regional-ui.js")
def regional_js():
    return FileResponse(FRONTEND / "regional-ui.js", media_type="application/javascript")


@app.get("/state-options.js")
def state_options_js():
    return FileResponse(FRONTEND / "state-options.js", media_type="application/javascript")


@app.get("/app-shell.css")
def app_shell_css():
    return FileResponse(FRONTEND / "app-shell.css", media_type="text/css")


@app.get("/app-shell.js")
def app_shell_js():
    return FileResponse(FRONTEND / "app-shell.js", media_type="application/javascript")


@app.get("/launch-enhancements.js")
def launch_enhancements_js():
    return FileResponse(FRONTEND / "launch-enhancements.js", media_type="application/javascript")


@app.get("/share-card.js")
def share_card_js():
    return FileResponse(FRONTEND / "share-card.js", media_type="application/javascript")


@app.get("/live-activity.js")
def live_activity_js():
    return FileResponse(FRONTEND / "live-activity.js", media_type="application/javascript")


@app.get("/classic-extras.js")
def classic_extras_js():
    return FileResponse(FRONTEND / "classic-extras.js", media_type="application/javascript")


@app.get("/locale-extras.js")
def locale_extras_js():
    return FileResponse(FRONTEND / "locale-extras.js", media_type="application/javascript")


@app.get("/manifest.webmanifest")
def manifest():
    return FileResponse(FRONTEND / "manifest.webmanifest", media_type="application/manifest+json")


@app.get("/sw.js")
def service_worker():
    return FileResponse(FRONTEND / "sw.js", media_type="application/javascript")


@app.get("/i18n.js")
def i18n_js():
    return FileResponse(FRONTEND / "i18n.js", media_type="application/javascript")


@app.get("/fonts.css")
def fonts_css():
    return FileResponse(FRONTEND / "fonts.css", media_type="text/css")


app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")
REACT_ASSETS.mkdir(parents=True, exist_ok=True)
app.mount("/_app", StaticFiles(directory=REACT_ASSETS), name="react_assets")
