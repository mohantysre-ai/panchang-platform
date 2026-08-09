from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from .panchang import calculate_panchang
from .storage import get_or_create

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "festivals.json"


def _load_definitions() -> list[dict]:
    with DATA_FILE.open("r", encoding="utf-8") as fh:
        return json.load(fh)["festivals"]


def _applies(defn: dict, state_code: str) -> bool:
    states = {s.upper() for s in defn.get("states", ["ALL"])}
    return "ALL" in states or state_code.upper() in states


def _tithi_index(target: date, lat: float, lon: float, timezone: str, state: str) -> int:
    return calculate_panchang(target, lat, lon, timezone, state)["panchang"]["tithi"]["index"]


def _matches(defn: dict, target: date, lat: float, lon: float, timezone: str, state: str) -> bool:
    rule = defn["rule"]
    kind = rule.get("type")
    if kind == "fixed":
        return target.month == rule["month"] and target.day == rule["day"]
    if kind == "tithi":
        if target.month not in rule.get("months", []):
            return False
        return _tithi_index(target, lat, lon, timezone, state) == rule["tithi"]
    return False


def _event(defn: dict, target: date) -> dict:
    return {
        "id": defn["id"],
        "date": target.isoformat(),
        "category": defn.get("category", "major"),
        "names": defn.get("names", {}),
    }


def resolve_festivals(
    target: date,
    state_code: str,
    lat: float,
    lon: float,
    timezone: str,
) -> dict:
    definitions = _load_definitions()
    events = []
    for defn in definitions:
        if not _applies(defn, state_code):
            continue
        if _matches(defn, target, lat, lon, timezone, state_code):
            events.append(_event(defn, target))
    events.sort(key=lambda x: (x["category"] != "major", x["id"]))
    return {
        "date": target.isoformat(),
        "state_code": state_code.upper(),
        "timezone": timezone,
        "events": events,
        "engine": "Swiss Ephemeris + regional festival rules",
    }


def festivals_for_date(
    target: date,
    state_code: str,
    lat: float,
    lon: float,
    timezone: str,
) -> dict:
    key = f"festivals:{target}:{state_code.upper()}:{lat:.5f}:{lon:.5f}:{timezone}"
    return get_or_create(
        key,
        "festivals",
        lambda: resolve_festivals(target, state_code, lat, lon, timezone),
    )


def festivals_for_month(
    year: int,
    month: int,
    state_code: str,
    lat: float,
    lon: float,
    timezone: str,
) -> dict:
    start = date(year, month, 1)
    next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
    days = []
    cursor = start
    while cursor < next_month:
        result = festivals_for_date(cursor, state_code, lat, lon, timezone)
        days.extend(result["events"])
        cursor += timedelta(days=1)
    return {
        "year": year,
        "month": month,
        "state_code": state_code.upper(),
        "timezone": timezone,
        "events": days,
    }
