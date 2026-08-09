"""Expand states, stateLang, stateStyle in frontend/i18n.js."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
I18N = ROOT / "frontend" / "i18n.js"

STATE_LANG = {
    "KA": "kn", "TN": "ta", "AP": "te", "TS": "te", "MH": "mr",
    "GJ": "hi", "UP": "hi", "RJ": "hi", "KL": "ta", "WB": "hi",
    "OD": "or", "AS": "hi", "PB": "hi", "BR": "hi", "MP": "hi",
    "CG": "hi", "JH": "hi", "UK": "hi", "HP": "hi", "JK": "hi",
    "GA": "mr", "DL": "hi", "HR": "hi",
}

STATE_STYLE = {
    "KA": "kannada", "TN": "tamil", "AP": "telugu", "TS": "telugu",
    "MH": "marathi", "GJ": "gujarati", "UP": "hindu", "RJ": "rajasthani",
    "KL": "malayalam", "WB": "bengali", "OD": "odia", "AS": "assamese",
    "PB": "punjabi", "BR": "maithili", "MP": "hindi", "CG": "hindi",
    "JH": "tribal", "UK": "himalayan", "HP": "himachali", "JK": "kashmiri",
    "GA": "konkani", "DL": "hindu", "HR": "punjabi",
}

# Unicode-escaped names so this file stays ASCII-safe on Windows.
STATES = {
    "hi": {
        "KA": "\u0915\u0930\u094d\u0928\u093e\u091f\u0915",
        "TN": "\u0924\u092e\u093f\u0932\u0928\u093e\u0921\u0941",
        "AP": "\u0906\u0902\u0927\u094d\u0930 \u092a\u094d\u0930\u0926\u0947\u0936",
        "TS": "\u0924\u0947\u0932\u0902\u0917\u093e\u0928\u093e",
        "MH": "\u092e\u0939\u093e\u0930\u093e\u0937\u094d\u091f\u094d\u0930",
        "GJ": "\u0917\u0941\u091c\u0930\u093e\u0924",
        "UP": "\u0909\u0924\u094d\u0924\u0930 \u092a\u094d\u0930\u0926\u0947\u0936",
        "RJ": "\u0930\u093e\u091c\u0938\u094d\u0925\u093e\u0928",
        "KL": "\u0915\u0947\u0930\u0932",
        "WB": "\u092a\u0936\u094d\u091a\u093f\u092e \u092c\u0902\u0917\u093e\u0932",
        "OD": "\u0913\u0921\u093c\u093f\u0936\u093e",
        "AS": "\u0905\u0938\u092e",
        "PB": "\u092a\u0902\u091c\u093e\u092c",
        "BR": "\u092c\u093f\u0939\u093e\u0930",
        "MP": "\u092e\u0927\u094d\u092f \u092a\u094d\u0930\u0926\u0947\u0936",
        "CG": "\u091b\u0924\u094d\u0924\u0940\u0938\u0917\u0922\u093c",
        "JH": "\u091d\u093e\u0930\u0916\u0923\u094d\u0921",
        "UK": "\u0909\u0924\u094d\u0924\u0930\u093e\u0916\u0923\u094d\u0921",
        "HP": "\u0939\u093f\u092e\u093e\u091a\u0932 \u092a\u094d\u0930\u0926\u0947\u0936",
        "JK": "\u091c\u092e\u094d\u092e\u0942 \u0914\u0930 \u0915\u0936\u094d\u092e\u0940\u0930",
        "GA": "\u0917\u094b\u0935\u093e",
        "DL": "\u0926\u093f\u0932\u094d\u0932\u0940",
        "HR": "\u0939\u0930\u093f\u092f\u093e\u0923\u093e",
    },
    "kn": {
        "KA": "\u0c95\u0cb0\u0ccd\u0ca8\u0cbe\u0c9f\u0c95",
        "TN": "\u0ca4\u0cae\u0cbf\u0cb3\u0cc1\u0ca8\u0cbe\u0ca1\u0cc1",
        "AP": "\u0c86\u0c82\u0ca7\u0ccd\u0cb0 \u0caa\u0ccd\u0cb0\u0ca6\u0cc7\u0cb6",
        "TS": "\u0ca4\u0cc6\u0cb2\u0c82\u0c97\u0cbe\u0ca3",
        "MH": "\u0cae\u0cb9\u0cbe\u0cb0\u0cbe\u0cb7\u0ccd\u0c9f\u0ccd\u0cb0",
        "GJ": "\u0c97\u0cc1\u0c9c\u0cb0\u0cbe\u0ca4",
        "UP": "\u0c89\u0ca4\u0ccd\u0ca4\u0cb0 \u0caa\u0ccd\u0cb0\u0ca6\u0cc7\u0cb6",
        "RJ": "\u0cb0\u0cbe\u0c9c\u0cb8\u0ccd\u0ca5\u0cbe\u0ca8",
        "KL": "\u0c95\u0cc7\u0cb0\u0cb3",
        "WB": "\u0caa\u0cb6\u0ccd\u0c9a\u0cbf\u0cae \u0cac\u0c82\u0c97\u0cbe\u0cb3",
        "OD": "\u0c92\u0ca1\u0cbf\u0cb6\u0cbe",
        "AS": "\u0c85\u0cb8\u0ccd\u0cb8\u0cbe\u0cae",
        "PB": "\u0caa\u0c82\u0c9c\u0cbe\u0cac",
        "BR": "\u0cac\u0cbf\u0cb9\u0cbe\u0cb0",
        "MP": "\u0cae\u0ca7\u0ccd\u0caf \u0caa\u0ccd\u0cb0\u0ca6\u0cc7\u0cb6",
        "CG": "\u0c9b\u0ca4\u0ccd\u0ca4\u0cc0\u0cb8\u0c97\u0ca2\u0cbc",
        "JH": "\u0c9d\u0cbe\u0cb0\u0c96\u0c82\u0ca1",
        "UK": "\u0c89\u0ca4\u0ccd\u0ca4\u0cb0\u0cbe\u0c96\u0c82\u0ca1",
        "HP": "\u0cb9\u0cbf\u0cae\u0cbe\u0c9a\u0cb2 \u0caa\u0ccd\u0cb0\u0ca6\u0cc7\u0cb6",
        "JK": "\u0c9c\u0cae\u0ccd\u0cae\u0cc1 \u0cae\u0ca4\u0ccd\u0ca4\u0cc1 \u0c95\u0cb6\u0ccd\u0cae\u0cc0\u0cb0",
        "GA": "\u0c97\u0ccb\u0cb5\u0cbe",
        "DL": "\u0ca6\u0cbf\u0cb2\u0ccd\u0cb2\u0cbf",
        "HR": "\u0cb9\u0cb0\u0cbf\u0caf\u0cbe\u0ca3",
    },
}

# For remaining langs, reuse Hindi names as base then override script-specific where we have them.
for lang in ("ta", "te", "mr", "or"):
    STATES[lang] = dict(STATES["hi"])

STATES["ta"].update({
    "KA": "\u0b95\u0bb0\u0bcd\u0ba8\u0bbe\u0b9f\u0b95\u0bbe",
    "TN": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd\u0ba8\u0bbe\u0b9f\u0bc1",
    "AP": "\u0b86\u0ba8\u0bcd\u0ba4\u0bbf\u0bb0\u0baa\u0bcd \u0baa\u0bbf\u0bb0\u0ba4\u0bc7\u0b9a\u0bae\u0bcd",
    "TS": "\u0ba4\u0bc6\u0bb2\u0bc1\u0b99\u0bcd\u0b95\u0bbe\u0ba9\u0bbe",
    "MH": "\u0bae\u0b95\u0bbe\u0bb0\u0bbe\u0bb7\u0bcd\u0b9f\u0bbf\u0bb0\u0bbe",
    "KL": "\u0b95\u0bc7\u0bb0\u0bb3\u0bbe",
    "WB": "\u0bae\u0bc7\u0bb1\u0bcd\u0b95\u0bc1 \u0bb5\u0b99\u0bcd\u0b95\u0bbe\u0bb3\u0bae\u0bcd",
    "OD": "\u0b92\u0b9f\u0bbf\u0b9a\u0bbe",
})
STATES["te"].update({
    "KA": "\u0c15\u0c30\u0c4d\u0c23\u0c3e\u0c1f\u0c15",
    "TN": "\u0c24\u0c2e\u0c3f\u0c33\u0c28\u0c3e\u0c21\u0c41",
    "AP": "\u0c06\u0c02\u0c27\u0c4d\u0c30 \u0c2a\u0c4d\u0c30\u0c26\u0c47\u0c36\u0c4d",
    "TS": "\u0c24\u0c46\u0c32\u0c02\u0c17\u0c3e\u0c23",
    "MH": "\u0c2e\u0c39\u0c3e\u0c30\u0c3e\u0c37\u0c4d\u0c1f\u0c4d\u0c30",
    "KL": "\u0c15\u0c47\u0c30\u0c33",
    "OD": "\u0c12\u0c21\u0c3f\u0c36\u0c3e",
})
STATES["or"].update({
    "KA": "\u0b15\u0b30\u0b4d\u0b23\u0b3e\u0b1f\u0b15",
    "TN": "\u0b24\u0b2e\u0b3f\u0b33\u0b28\u0b3e\u0b21\u0b41",
    "AP": "\u0b06\u0b28\u0b4d\u0b27\u0b4d\u0b30 \u0b2a\u0b4d\u0b30\u0b26\u0b47\u0b36",
    "TS": "\u0b24\u0b47\u0b32\u0b47\u0b19\u0b4d\u0b17\u0b3e\u0b23\u0b3e",
    "MH": "\u0b2e\u0b39\u0b3e\u0b30\u0b3e\u0b37\u0b4d\u0b1f\u0b4d\u0b30",
    "KL": "\u0b15\u0b47\u0b30\u0b33",
    "WB": "\u0b2a\u0b36\u0b4d\u0b1a\u0b3f\u0b2e\u0b2c\u0b19\u0b4d\u0b17",
    "OD": "\u0b13\u0b21\u0b3c\u0b3f\u0b36\u0b3e",
    "AS": "\u0b05\u0b38\u0b2e",
    "PB": "\u0b2a\u0b1e\u0b4d\u0b1c\u0b3e\u0b2c",
    "BR": "\u0b2c\u0b3f\u0b39\u0b3e\u0b30",
    "GA": "\u0b17\u0b4b\u0b06",
})
STATES["mr"].update({
    "MH": "\u092e\u0939\u093e\u0930\u093e\u0937\u094d\u091f\u094d\u0930",
    "GA": "\u0917\u094b\u0935\u093e",
    "KL": "\u0915\u0947\u0930\u0933",
})


def main() -> None:
    text = I18N.read_text(encoding="utf-8")
    m = re.search(r"window\.I18N\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not m:
        raise SystemExit("parse failed")
    data = json.loads(m.group(1))
    data["stateLang"] = STATE_LANG
    data["stateStyle"] = STATE_STYLE
    data["states"] = STATES
    I18N.write_text("window.I18N = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print("states:", len(STATE_LANG), "styles:", len(set(STATE_STYLE.values())))


if __name__ == "__main__":
    main()
