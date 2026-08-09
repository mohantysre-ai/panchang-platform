"""Sync new langs into terms.json + expand rashifal LANGUAGES."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "frontend" / "i18n.js"
TERMS = ROOT / "backend" / "scripts" / "terms.json"
RASHIFAL = ROOT / "backend" / "app" / "rashifal.py"

NEW = ("bn", "as", "pa", "gu", "ml")


def load_i18n() -> dict:
    text = I18N.read_text(encoding="utf-8")
    m = re.search(r"window\.I18N\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not m:
        raise SystemExit("i18n parse fail")
    return json.loads(m.group(1))


def main() -> None:
    i18n = load_i18n()
    terms = json.loads(TERMS.read_text(encoding="utf-8"))
    for section in ("systems", "tithi", "nakshatra", "yoga", "karana", "vaar", "choghadiya", "gowri", "rashi", "colors", "predictions"):
        if section not in terms:
            continue
        src = terms[section]
        for lang in NEW:
            if lang in src:
                continue
            if section in i18n and lang in i18n[section]:
                src[lang] = i18n[section][lang]
            elif "hi" in src:
                src[lang] = src["hi"]
            elif "bn" in src and lang == "as":
                src[lang] = src["bn"]
    TERMS.write_text(json.dumps(terms, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    langs = {
        "hi": "\\u0939\\u093f\\u0928\\u094d\\u0926\\u0940",
        "kn": "\\u0c95\\u0ca8\\u0ccd\\u0ca8\\u0ca1",
        "ta": "\\u0ba4\\u0bae\\u0bbf\\u0bb4\\u0bcd",
        "te": "\\u0c24\\u0c46\\u0c32\\u0c41\\u0c17\\u0c41",
        "mr": "\\u092e\\u0930\\u093e\\u0920\\u0940",
        "or": "\\u0b13\\u0b21\\u0b3c\\u0b3f\\u0b06",
        "bn": "\\u09ac\\u09be\\u0982\\u09b2\\u09be",
        "as": "\\u0985\\u0938\\u092e\\u0940\\u092f\\u093e".replace("\\u0938\\u092e\\u0940\\u092f\\u093e", "\\u09b8\\u09ae\\u09c0\\u09af\\u09bc\\u09be"),  # fix - write properly below
        "pa": "\\u0a2a\\u0a70\\u0a1c\\u0a3e\\u0a2c\\u0a40",
        "gu": "\\u0a97\\u0ac1\\u0a9c\\u0ab0\\u0abe\\u0aa4\\u0ac0",
        "ml": "\\u0d2e\\u0d32\\u0d2f\\u0d3e\\u0d33\\u0d02",
    }
    # Assamese name: অসমীয়া
    langs["as"] = "\\u0985\\u09b8\\u09ae\\u09c0\\u09af\\u09bc\\u09be"

    block = "LANGUAGES = {\n"
    for k, v in langs.items():
        block += f'    "{k}": "{v}",\n'
    block += "}\n"

    text = RASHIFAL.read_text(encoding="utf-8")
    text2, n = re.subn(
        r"LANGUAGES\s*=\s*\{.*?\n\}",
        block.rstrip(),
        text,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"rashifal LANGUAGES replace failed n={n}")
    # Unescape unicode in the written file so Python source has real escapes as literals
    # Actually we wrote \\u which becomes \u in file - good for ASCII Python source
    RASHIFAL.write_text(text2, encoding="utf-8")
    print("terms langs tithi:", list(terms["tithi"].keys()))
    print("rashifal updated")


if __name__ == "__main__":
    main()
