"""Lightweight free translation helpers (Google Translate via deep-translator, MyMemory fallback)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .config import settings

# App language codes → Google Translate / MyMemory codes
_LANG_MAP = {
    "hi": "hi",
    "kn": "kn",
    "ta": "ta",
    "te": "te",
    "mr": "mr",
    "or": "or",
    "bn": "bn",
    "as": "as",
    "pa": "pa",
    "gu": "gu",
    "ml": "ml",
    "en": "en",
}

_LATIN_RE = re.compile(r"[A-Za-z]")
_CACHE_DIR = settings.absolute_data_dir / "translations"
_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def looks_english(text: str) -> bool:
    """True when the string is mostly Latin letters (English leftover)."""
    if not text or not str(text).strip():
        return False
    s = str(text).strip()
    letters = _LATIN_RE.findall(s)
    if len(letters) < 4:
        return False
    # Reject if a major Indic script is already present
    for lo, hi in (
        (0x0900, 0x097F),
        (0x0980, 0x09FF),
        (0x0A00, 0x0A7F),
        (0x0A80, 0x0AFF),
        (0x0B00, 0x0B7F),
        (0x0B80, 0x0BFF),
        (0x0C00, 0x0C7F),
        (0x0C80, 0x0CFF),
        (0x0D00, 0x0D7F),
    ):
        if any(lo <= ord(ch) <= hi for ch in s):
            return False
    return len(letters) >= max(4, int(len(re.sub(r"\s+", "", s)) * 0.5))


def _cache_path(text: str, target: str) -> Path:
    digest = hashlib.sha1(f"{target}\n{text}".encode("utf-8")).hexdigest()
    return _CACHE_DIR / f"{target}_{digest}.json"


def _cache_get(text: str, target: str) -> str | None:
    path = _cache_path(text, target)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        out = (data.get("text") or "").strip()
        return out or None
    except Exception:
        return None


def _cache_set(text: str, target: str, translated: str) -> None:
    path = _cache_path(text, target)
    path.write_text(
        json.dumps({"source": text, "target": target, "text": translated}, ensure_ascii=False),
        encoding="utf-8",
    )


def translate_to(text: str, lang: str, source: str = "en") -> str:
    """Translate text into app language. Returns original on failure / English target."""
    raw = (text or "").strip()
    if not raw:
        return ""
    target = _LANG_MAP.get((lang or "").lower())
    if not target or target == "en" or target == source:
        return raw
    if not looks_english(raw) and source == "en":
        return raw

    cached = _cache_get(raw, target)
    if cached:
        return cached

    # Prefer Google Translate (unofficial free endpoint via deep-translator).
    try:
        from deep_translator import GoogleTranslator

        out = GoogleTranslator(source=source, target=target).translate(raw)
        out = (out or "").strip()
        if out:
            _cache_set(raw, target, out)
            return out
    except Exception:
        pass

    # Open MyMemory fallback (free, rate-limited).
    try:
        from deep_translator import MyMemoryTranslator

        out = MyMemoryTranslator(source=source, target=target).translate(raw)
        out = (out or "").strip()
        if out:
            _cache_set(raw, target, out)
            return out
    except Exception:
        pass

    return raw


def translate_if_english(text: str, lang: str) -> str:
    if looks_english(text):
        return translate_to(text, lang, source="en")
    return (text or "").strip()
