import json
import re
import urllib.request

base = "http://127.0.0.1:8001"

for path in [
    "/",
    "/fonts.css",
    "/i18n.js",
    "/assets/fonts/noto-devanagari-400.woff2",
    "/assets/fonts/noto-malayalam-700.woff2",
    "/api/v1/calendar/month?state_code=OD&year=2026&month=8",
]:
    r = urllib.request.urlopen(base + path)
    print(path.split("?")[0], r.status)

html = urllib.request.urlopen(base + "/").read().decode("utf-8")
assert "fonts.googleapis" not in html
assert "/fonts.css" in html
assert 'id="lang"' in html
assert "daySheet" in html
assert "class=\"badge\"" not in html
print("html ok")

for st in ["OD", "WB", "AS", "PB", "KL", "GJ", "MH", "KA", "TN", "AP", "UP", "GA"]:
    d = json.load(urllib.request.urlopen(base + f"/api/v1/calendar/month?state_code={st}&year=2026&month=8"))
    print(st, d["calendar_style"], d["layout"], len(d["days"]))

for lang in ["mr", "bn", "ml", "gu", "pa", "as", "or"]:
    d = json.load(urllib.request.urlopen(base + f"/api/v1/rashifal?lang={lang}&date_str=2026-08-08"))
    blob = d["language"] + d["rashifal"][0]["prediction"] + d["rashifal"][0]["lucky_color"]
    has_latin = bool(re.search(r"[A-Za-z]{3,}", blob))
    print("rashifal", lang, "LATIN" if has_latin else "clean", d["lang"])

i18n = json.loads(re.search(r"window\.I18N\s*=\s*(\{.*\})\s*;?\s*$", open("frontend/i18n.js", encoding="utf-8").read(), re.S).group(1))
for code, lang in i18n["stateLang"].items():
    assert lang in i18n["languages"], (code, lang)
    assert lang in i18n["fonts"], lang
print("stateLang lock ok", len(i18n["stateLang"]))
print("DONE")
