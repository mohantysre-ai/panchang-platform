import json
import re
from pathlib import Path

from .config import settings

LANGUAGES = {
    "hi": "\u0939\u093f\u0928\u094d\u0926\u0940",
    "kn": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1",
    "ta": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",
    "te": "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41",
    "mr": "\u092e\u0930\u093e\u0920\u0940",
    "or": "\u0b13\u0b21\u0b3c\u0b3f\u0b06",
    "bn": "\u09ac\u09be\u0982\u09b2\u09be",
    "as": "\u0985\u09b8\u09ae\u09c0\u09af\u09bc\u09be",
    "pa": "\u0a2a\u0a70\u0a1c\u0a3e\u0a2c\u0a40",
    "gu": "\u0a97\u0ac1\u0a9c\u0ab0\u0abe\u0aa4\u0ac0",
    "ml": "\u0d2e\u0d32\u0d2f\u0d3e\u0d33\u0d02",
}

_TERMS_PATH = Path(__file__).resolve().parents[1] / "scripts" / "terms.json"
_TERMS = json.loads(_TERMS_PATH.read_text(encoding="utf-8"))


def _normalize_lang(language: str) -> str:
    code = (language or "kn").lower()
    if code == "en" or code not in LANGUAGES:
        return "kn"
    return code


def fallback(language: str, target_date):
    lang = _normalize_lang(language)
    colors = _TERMS["colors"][lang]
    preds = _TERMS["predictions"][lang]
    rashis = _TERMS["rashi"][lang]
    rows = []
    for i, name in enumerate(rashis):
        rows.append({
            "rashi": name,
            "prediction": preds[i % len(preds)],
            "lucky_number": str((i + target_date.day) % 9 + 1),
            "lucky_color": colors[i % len(colors)],
        })
    return {
        "date": target_date.isoformat(),
        "language": LANGUAGES[lang],
        "lang": lang,
        "provider": "deterministic-fallback",
        "rashifal": rows,
    }


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
    text = re.sub(r"```$", "", text).strip()
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("No JSON found")
    return json.loads(m.group(0))


def generate_rashifal(language, target_date):
    lang = _normalize_lang(language)
    if not settings.gemini_api_key:
        return fallback(lang, target_date)
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        lang_name = LANGUAGES[lang]
        prompt = (
            "Generate a culturally respectful daily Vedic astrology-style Rashifal. "
            f"Date: {target_date.isoformat()}. Write entirely in {lang_name} script. "
            "Do not use English words. Generate all 12 Rashis with native names. "
            "Each prediction must be 1-2 concise sentences. "
            'Return ONLY JSON in the form {"rashifal":[{"rashi":"...",'
            '"prediction":"...","lucky_number":"7","lucky_color":"..."}]}. '
            "lucky_color must also be in the same regional language. "
            "Do not use markdown. Do not make medical, legal, financial, or guaranteed outcome claims."
        )
        response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
        data = extract_json(response.text)
        if not isinstance(data.get("rashifal"), list):
            raise ValueError("Invalid JSON")
        return {
            "date": target_date.isoformat(),
            "language": lang_name,
            "lang": lang,
            "provider": f"gemini:{settings.gemini_model}",
            "rashifal": data["rashifal"],
        }
    except Exception:
        return fallback(lang, target_date)
