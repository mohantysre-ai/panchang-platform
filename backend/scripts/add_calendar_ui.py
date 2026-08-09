"""Add calendar UI strings to frontend/i18n.js (ASCII escapes only)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "frontend" / "i18n.js"

EXTRA = {
    "hi": {
        "calendar": "\u092a\u0902\u091a\u093e\u0902\u0917 \u092a\u091e\u094d\u091c\u093f\u0915\u093e",
        "today": "\u0906\u091c",
        "prev_month": "\u092a\u093f\u091b\u0932\u093e \u092e\u093e\u0939",
        "next_month": "\u0905\u0917\u0932\u093e \u092e\u093e\u0939",
        "select_day": "\u0926\u093f\u0928 \u091a\u0941\u0928\u0947\u0902",
        "day_detail": "\u0926\u093f\u0928 \u0935\u093f\u0935\u0930\u0923",
        "celestial": "\u0917\u094d\u0930\u0939 \u0915\u093e\u0932",
    },
    "kn": {
        "calendar": "\u0caa\u0c82\u0c9a\u0cbe\u0c82\u0c97 \u0caa\u0c9e\u0ccd\u0c9c\u0cbf\u0c95",
        "today": "\u0c87\u0c82\u0ca6\u0cc1",
        "prev_month": "\u0cb9\u0cbf\u0c82\u0ca6\u0cbf\u0ca8 \u0ca4\u0cbf\u0c82\u0c97\u0cb3\u0cc1",
        "next_month": "\u0cae\u0cc1\u0c82\u0ca6\u0cbf\u0ca8 \u0ca4\u0cbf\u0c82\u0c97\u0cb3\u0cc1",
        "select_day": "\u0ca6\u0cbf\u0ca8\u0cbe\u0c82\u0c95\u0cc6 \u0c86\u0caf\u0ccd\u0c95\u0cc6\u0cae\u0cbe\u0ca1\u0cbf",
        "day_detail": "\u0ca6\u0cbf\u0ca8\u0ca6 \u0cb5\u0cbf\u0cb5\u0cb0",
        "celestial": "\u0c97\u0ccd\u0cb0\u0cb9 \u0c95\u0cbe\u0cb2",
    },
    "ta": {
        "calendar": "\u0baa\u0b9e\u0bcd\u0b9a\u0bbe\u0b99\u0bcd\u0b95 \u0ba8\u0bbe\u0bb3\u0bcd\u0b95\u0bbe\u0b9f\u0bcd\u0b9f\u0bbf",
        "today": "\u0b87\u0ba9\u0bcd\u0bb1\u0bc1",
        "prev_month": "\u0bae\u0bc1\u0ba8\u0bcd\u0ba4\u0bc8\u0baf \u0bae\u0bbe\u0ba4\u0bae\u0bcd",
        "next_month": "\u0b85\u0b9f\u0bc1\u0ba4\u0bcd\u0ba4 \u0bae\u0bbe\u0ba4\u0bae\u0bcd",
        "select_day": "\u0ba8\u0bbe\u0bb3\u0bc8\u0ba4\u0bcd \u0ba4\u0bc7\u0bb0\u0bcd\u0bb5\u0bc1 \u0b9a\u0bc6\u0baf\u0bcd\u0baf\u0bb5\u0bc1\u0bae\u0bcd",
        "day_detail": "\u0ba8\u0bbe\u0bb3\u0bcd \u0bb5\u0bbf\u0bb5\u0bb0\u0bae\u0bcd",
        "celestial": "\u0b95\u0b95\u0bcd\u0b95 \u0ba8\u0bc7\u0bb0\u0bae\u0bcd",
    },
    "te": {
        "calendar": "\u0c2a\u0c02\u0c1a\u0c3e\u0c02\u0c17 \u0c15\u0c4d\u0c2f\u0c3e\u0c32\u0c46\u0c02\u0c21\u0c30\u0c4d",
        "today": "\u0c28\u0c47\u0c21\u0c41",
        "prev_month": "\u0c2e\u0c41\u0c28\u0c41\u0c2a\u0c1f\u0c3f \u0c28\u0c46\u0c32",
        "next_month": "\u0c24\u0c30\u0c41\u0c35\u0c3e\u0c24\u0c3f \u0c28\u0c46\u0c32",
        "select_day": "\u0c30\u0c4b\u0c1c\u0c41 \u0c0e\u0c02\u0c1a\u0c41\u0c15\u0c4b\u0c02\u0c21\u0c3f",
        "day_detail": "\u0c30\u0c4b\u0c1c\u0c41 \u0c35\u0c3f\u0c35\u0c30\u0c3e\u0c32\u0c41",
        "celestial": "\u0c17\u0c4d\u0c30\u0c39 \u0c15\u0c3e\u0c32\u0c02",
    },
    "or": {
        "calendar": "\u0b2a\u0b1e\u0b4d\u0b1a\u0b3e\u0b19\u0b4d\u0b17 \u0b15\u0b4d\u0b5f\u0b3e\u0b32\u0b47\u0b23\u0b4d\u0b21\u0b30\u0b4d",
        "today": "\u0b06\u0b1c\u0b3f",
        "prev_month": "\u0b2a\u0b42\u0b30\u0b4d\u0b2c\u0b3e\u0b2a\u0b30 \u0b2e\u0b3e\u0b38",
        "next_month": "\u0b2a\u0b30\u0b2c\u0b30\u0b4d\u0b24\u0b40 \u0b2e\u0b3e\u0b38",
        "select_day": "\u0b26\u0b3f\u0b28 \u0b1a\u0b5f\u0b28\u0b4d\u0b24\u0b41",
        "day_detail": "\u0b26\u0b3f\u0b28 \u0b2c\u0b3f\u0b2c\u0b30\u0b23",
        "celestial": "\u0b17\u0b4d\u0b30\u0b39 \u0b15\u0b3e\u0b33",
    },
    "mr": {
        "calendar": "\u092a\u0902\u091a\u093e\u0902\u0917 \u092a\u0902\u091a\u0915",
        "today": "\u0906\u091c",
        "prev_month": "\u092e\u093e\u0917\u0940\u0932 \u092e\u0939\u093f\u0928\u093e",
        "next_month": "\u092a\u0941\u0922\u0940\u0932 \u092e\u0939\u093f\u0928\u093e",
        "select_day": "\u0926\u093f\u0935\u0938 \u0928\u093f\u0935\u0921\u093e",
        "day_detail": "\u0926\u093f\u0935\u0938 \u0935\u093f\u0935\u0930",
        "celestial": "\u0917\u094d\u0930\u0939 \u0915\u093e\u0933",
    },
}


def main() -> None:
    text = I18N.read_text(encoding="utf-8")
    m = re.search(r"window\.I18N\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not m:
        raise SystemExit("Could not parse I18N object")
    data = json.loads(m.group(1))
    for lang, extras in EXTRA.items():
        if lang not in data["ui"]:
            continue
        data["ui"][lang].update(extras)
    out = "window.I18N = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    I18N.write_text(out, encoding="utf-8")
    print("Updated", I18N)


if __name__ == "__main__":
    main()
