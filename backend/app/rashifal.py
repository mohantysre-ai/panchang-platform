import json
import re
import urllib.error
import urllib.parse
import urllib.request
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

# 0-based Vedic rashi metadata (Mesha … Meena)
RASHI_META = [
    {"sign": "aries", "planet": "Mars", "element": "Fire"},
    {"sign": "taurus", "planet": "Venus", "element": "Earth"},
    {"sign": "gemini", "planet": "Mercury", "element": "Air"},
    {"sign": "cancer", "planet": "Moon", "element": "Water"},
    {"sign": "leo", "planet": "Sun", "element": "Fire"},
    {"sign": "virgo", "planet": "Mercury", "element": "Earth"},
    {"sign": "libra", "planet": "Venus", "element": "Air"},
    {"sign": "scorpio", "planet": "Mars", "element": "Water"},
    {"sign": "sagittarius", "planet": "Jupiter", "element": "Fire"},
    {"sign": "capricorn", "planet": "Saturn", "element": "Earth"},
    {"sign": "aquarius", "planet": "Saturn", "element": "Air"},
    {"sign": "pisces", "planet": "Jupiter", "element": "Water"},
]

_TERMS_PATH = Path(__file__).resolve().parents[1] / "scripts" / "terms.json"
_TERMS = json.loads(_TERMS_PATH.read_text(encoding="utf-8"))

HOROSCOPE_URL = "https://freehoroscopeapi.com/api/v1/get-horoscope/daily"
HOROSCOPE_WEEKLY_URL = "https://freehoroscopeapi.com/api/v1/get-horoscope/weekly"
HOROSCOPE_MONTHLY_URL = "https://freehoroscopeapi.com/api/v1/get-horoscope/monthly"

# Longer area write-ups (index-cycled) for expand panels — regional scripts.
_DETAIL_AREAS = {
    "hi": {
        "work": [
            "कार्यक्षेत्र में आज योजनाबद्ध कदम उठाएँ; जल्दबाज़ी से बचें और सहयोगियों से स्पष्ट संवाद रखें।",
            "दफ़्तर या व्यवसाय में धैर्य फलदायी रहेगा। छोटी जिम्मेदारियाँ पूरी कर बड़े लक्ष्य की नींव मज़बूत करें।",
            "नए प्रस्ताव पर दो बार सोचें। अनुभवी सलाह से निर्णय सरल हो सकते हैं।",
        ],
        "family": [
            "परिवार में सामंजस्य बनाए रखने के लिए सुनने का अभ्यास करें; छोटे विवादों को शांत स्वर में सुलझाएँ।",
            "घर के सदस्यों के साथ समय निकालना मानसिक शांति देगा। घरेलू व्यवस्था में सुधार शुभ।",
            "बुज़ुर्गों का आशीर्वाद लें। पारिवारिक निर्णयों में सबकी राय लें।",
        ],
        "health": [
            "नियमित जलपान, हल्की व्यायाम और पर्याप्त विश्राम स्वास्थ्य बनाए रखने में सहायक।",
            "तनाव कम करने के लिए श्वास-अभ्यास या छोटी सैर लाभदायक रहेगी।",
            "अति भोजन और देर रात जागने से बचें; शरीर की थकान पर ध्यान दें।",
        ],
        "remedy": [
            "स्वंय के राशि स्वामी की कृपा हेतु सात्विक आहार और दान-पुण्य का संकल्प रखें।",
            "सूर्योदय के बाद कुछ क्षण शांत ध्यान या प्रार्थना दिन का स्वर स्थिर कर सकती है।",
            "जल से तुलसी या पीपल के समीप कृतज्ञता व्यक्त करना पारंपरिक रूप से शुभ माना जाता है।",
        ],
        "state_note": "इस राज्य की पंचांग परंपरा {system} कैलेंडर और {muhurat} मुहूर्त पद्धति पर आधारित है। आज का नक्षत्र {nakshatra}, तिथि {tithi}।",
    },
    "ml": {
        "work": [
            "ജോലിയിൽ ഇന്ന് ക്രമീകൃതമായ നടപടികൾ സ്വീകരിക്കുക; തിടുക്കം ഒഴിവാക്കി സഹപ്രവർത്തകരുമായി വ്യക്തമായി സംസാരിക്കുക.",
            "ക്ഷമയോടെയുള്ള ശ്രമങ്ങൾ ഫലം ചെയ്യും. ചെറിയ ജോലികൾ പൂർത്തിയാക്കി വലിയ ലക്ഷ്യത്തിന് അടിത്തറയിടുക.",
            "പുതിയ ഓഫറുകൾ രണ്ടുതവണ ആലോചിച്ച ശേഷം തീരുമാനിക്കുക. പരിചയസമ്പന്നരുടെ ഉപദേശം സഹായകമാകും.",
        ],
        "family": [
            "കുടുംബത്തിൽ ഐക്യം നിലനിർത്താൻ ശ്രദ്ധയോടെ കേൾക്കുക; ചെറിയ തർക്കങ്ങൾ ശാന്തമായി പരിഹരിക്കുക.",
            "വീട്ടുകാരുമായി സമയം ചിലവഴിക്കുന്നത് മനസ്സിന് ആശ്വാസം നൽകും.",
            "മുതിർന്നവരുടെ അനുഗ്രഹം തേടുക. കുടുംബ തീരുമാനങ്ങളിൽ എല്ലാവരുടെയും അഭിപ്രായം പരിഗണിക്കുക.",
        ],
        "health": [
            "വെള്ളം കുടിക്കുക, ലഘുവായ വ്യായാമം, മതിയായ വിശ്രമം എന്നിവ ആരോഗ്യത്തിന് അനുകൂലം.",
            "സമ്മർദ്ദം കുറയ്ക്കാൻ ശ്വാസവ്യായാമം അല്ലെങ്കിൽ ചെറിയ നടത്തം സഹായകം.",
            "അമിതഭക്ഷണവും രാത്രി വൈകിയുള്ള ഉണർവും ഒഴിവാക്കുക.",
        ],
        "remedy": [
            "രാശ്യധിപന്റെ അനുഗ്രഹത്തിനായി സാത്വിക ഭക്ഷണവും ദാനവും സ്വീകരിക്കുക.",
            "സൂര്യോദയത്തിന് ശേഷം ചെറിയ ധ്യാനം അല്ലെങ്കിൽ പ്രാർത്ഥന ദിനം സ്ഥിരപ്പെടുത്തും.",
            "നന്ദിയോടെയുള്ള ചെറിയ പൂജാകർമ്മങ്ങൾ പരമ്പരാഗതമായി ശുഭമായി കണക്കാക്കപ്പെടുന്നു.",
        ],
        "state_note": "ഈ സംസ്ഥാനത്തെ പഞ്ചാംഗ പാരമ്പര്യം {system} കലണ്ടറും {muhurat} മുഹൂർത്ത രീതിയും അടിസ്ഥാനമാക്കിയതാണ്. ഇന്നത്തെ നക്ഷത്രം {nakshatra}, തിഥി {tithi}.",
    },
    "ta": {
        "work": [
            "பணியில் இன்று திட்டமிட்ட நடவடிக்கை எடுங்கள்; அவசரத்தை தவிர்த்து தெளிவாக பேசுங்கள்.",
            "பொறுமையுடன் செயல்பட்டால் பலன் கிடைக்கும். சிறு பணிகளை முடித்து பெரிய இலக்குக்கு அடித்தளம் அமைக்கவும்.",
            "புதிய வாய்ப்புகளை இருமுறை சிந்தித்து முடிவு செய்யுங்கள்.",
        ],
        "family": [
            "குடும்பத்தில் இணக்கத்திற்கு கவனமாகக் கேளுங்கள்; சிறு தகராறுகளை அமைதியாக தீர்க்கவும்.",
            "குடும்பத்தினருடன் நேரம் செலவிடுவது மன அமைதி தரும்.",
            "மூத்தோர் ஆசியைப் பெறுங்கள். குடும்ப முடிவுகளில் அனைவரின் கருத்தும் கேளுங்கள்.",
        ],
        "health": [
            "நீர் அருந்துதல், இலகு உடற்பயிற்சி, போதிய ஓய்வு ஆரோக்கியத்திற்கு உதவும்.",
            "மன அழுத்தத்தைக் குறைக்க மூச்சுப் பயிற்சி அல்லது நடைபயிற்சி நல்லது.",
            "அதிக உணவு மற்றும் தாமத உறக்கத்தைத் தவிர்க்கவும்.",
        ],
        "remedy": [
            "ராசி அதிபதி அருளுக்கு சாத்விக உணவும் தானமும் உதவும்.",
            "சூரிய உதயத்திற்குப் பின் சிறு தியானம் நாளை நிலைப்படுத்தும்.",
            "நன்றியுடன் செய்யும் சிறு வழிபாடு பாரம்பரியமாக நல்லதாகக் கருதப்படுகிறது.",
        ],
        "state_note": "இம்மாநில பஞ்சாங்க மரபு {system} நாட்காட்டி மற்றும் {muhurat} முகூர்த்த முறையை அடிப்படையாகக் கொண்டது. இன்றைய நட்சத்திரம் {nakshatra}, திதி {tithi}.",
    },
    "kn": {
        "work": [
            "ಕೆಲಸದಲ್ಲಿ ಇಂದು ಯೋಜಿತ ಹೆಜ್ಜೆಗಳನ್ನು ಇಡಿ; ಆತುರ ತಪ್ಪಿಸಿ ಸ್ಪಷ್ಟ ಸಂವಾದ ಇರಲಿ.",
            "ತಾಳ್ಮೆಯಿಂದ ಕೆಲಸ ಮಾಡಿದರೆ ಫಲ ಸಿಗುತ್ತದೆ. ಸಣ್ಣ ಕಾರ್ಯಗಳನ್ನು ಪೂರೈಸಿ ದೊಡ್ಡ ಗುರಿಗೆ ಅಡಿಪಾಯ ಹಾಕಿ.",
            "ಹೊಸ ಪ್ರಸ್ತಾವನೆಗಳನ್ನು ಎರಡು ಬಾರಿ ಯೋಚಿಸಿ ನಿರ್ಧರಿಸಿ.",
        ],
        "family": [
            "ಕುಟುಂಬದಲ್ಲಿ ಸಾಮರಸ್ಯಕ್ಕಾಗಿ ಗಮನವಿಟ್ಟು ಕೇಳಿ; ಸಣ್ಣ ವಿವಾದಗಳನ್ನು ಶಾಂತವಾಗಿ ಬಗೆಹರಿಸಿ.",
            "ಮನೆಯವರೊಂದಿಗೆ ಸಮಯ ಕಳೆಯುವುದು ಮನಶ್ಶಾಂತಿ ನೀಡುತ್ತದೆ.",
            "ಹಿರಿಯರ ಆಶೀರ್ವಾದ ಪಡೆಯಿರಿ. ಕುಟುಂಬ ನಿರ್ಧಾರಗಳಲ್ಲಿ ಎಲ್ಲರ ಅಭಿಪ್ರಾಯ ಪಡೆಯಿರಿ.",
        ],
        "health": [
            "ನೀರು ಕುಡಿಯುವುದು, ಹಗುರ ವ್ಯಾಯಾಮ, ಸಾಕಷ್ಟು ವಿಶ್ರಾಂತಿ ಆರೋಗ್ಯಕ್ಕೆ ಸಹಾಯಕ.",
            "ಒತ್ತಡ ಕಡಿಮೆ ಮಾಡಲು ಉಸಿರಾಟ ಅಭ್ಯಾಸ ಅಥವಾ ನಡಿಗೆ ಉತ್ತಮ.",
            "ಅತಿಯಾದ ಆಹಾರ ಮತ್ತು ರಾತ್ರಿ ತಡವಾಗಿ ಎಚ್ಚರವಿರುವುದನ್ನು ತಪ್ಪಿಸಿ.",
        ],
        "remedy": [
            "ರಾಶ್ಯಧಿಪತಿ ಅನುಗ್ರಹಕ್ಕಾಗಿ ಸಾತ್ವಿಕ ಆಹಾರ ಮತ್ತು ದಾನ ಅಭ್ಯಾಸ ಮಾಡಿ.",
            "ಸೂರ್ಯೋದಯದ ನಂತರ ಸಣ್ಣ ಧ್ಯಾನ ದಿನವನ್ನು ಸ್ಥಿರಗೊಳಿಸಬಹುದು.",
            "ಕೃತಜ್ಞತೆಯ ಸಣ್ಣ ಪೂಜಾ ಕಾರ್ಯಗಳು ಪಾರಂಪರಿಕವಾಗಿ ಶುಭ.",
        ],
        "state_note": "ಈ ರಾಜ್ಯದ ಪಂಚಾಂಗ ಪರಂಪರೆ {system} ಕ್ಯಾಲೆಂಡರ್ ಮತ್ತು {muhurat} ಮುಹೂರ್ತ ವಿಧಾನವನ್ನು ಆಧರಿಸಿದೆ. ಇಂದಿನ ನಕ್ಷತ್ರ {nakshatra}, ತಿಥಿ {tithi}.",
    },
}


def _areas_for(lang: str) -> dict:
    return _DETAIL_AREAS.get(lang) or _DETAIL_AREAS["hi"]


def _normalize_lang(language: str) -> str:
    code = (language or "kn").lower()
    if code == "en" or code not in LANGUAGES:
        return "kn"
    return code


def enrich_rows(rows: list, lang: str) -> list:
    native = _TERMS.get("rashi", {}).get(lang) or _TERMS["rashi"]["hi"]
    out = []
    for i, row in enumerate(rows[:12]):
        meta = RASHI_META[i % 12]
        item = dict(row)
        item["index"] = i + 1
        item["sign"] = meta["sign"]
        item["planet"] = meta["planet"]
        item["element"] = meta["element"]
        if not item.get("rashi") and i < len(native):
            item["rashi"] = native[i]
        out.append(item)
    return out


def expand_row_writeup(row: dict, lang: str, index: int) -> dict:
    """Attach longer multi-section write-up to a single rashi row."""
    areas = _areas_for(lang)
    i = index % 3
    base = (row.get("prediction") or "").strip()
    work = (row.get("work") or "").strip() or areas["work"][i]
    family = (row.get("family") or "").strip() or areas["family"][i]
    health = (row.get("health") or "").strip() or areas["health"][i]
    remedy = (row.get("remedy") or "").strip() or areas["remedy"][i]
    overview = (row.get("overview") or "").strip() or " ".join(x for x in [base, work] if x)
    item = dict(row)
    item["overview"] = overview
    item["work"] = work
    item["family"] = family
    item["health"] = health
    item["remedy"] = remedy
    item["prediction_long"] = " ".join(
        x for x in [overview, family, health, remedy] if x
    )
    return item


def enrich_rows_detailed(rows: list, lang: str) -> list:
    enriched = enrich_rows(rows, lang)
    return [expand_row_writeup(row, lang, i) for i, row in enumerate(enriched)]


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
        "rashifal": enrich_rows_detailed(rows, lang),
    }


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.I).strip()
    text = re.sub(r"```$", "", text).strip()
    m = re.search(r"\{.*\}", text, flags=re.S)
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
            "For each rashi provide: prediction (2-3 sentences overview), "
            "work (1-2 sentences), family (1-2 sentences), health (1-2 sentences), "
            "remedy (1 short traditional tip). "
            'Return ONLY JSON {"rashifal":[{"rashi":"...","prediction":"...",'
            '"work":"...","family":"...","health":"...","remedy":"...",'
            '"lucky_number":"7","lucky_color":"..."}]}. '
            "lucky_color must also be in the same regional language. "
            "Do not use markdown. Do not make medical, legal, financial, or guaranteed outcome claims."
        )
        response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
        data = extract_json(response.text)
        if not isinstance(data.get("rashifal"), list):
            raise ValueError("Invalid JSON")
        rows = enrich_rows(data["rashifal"], lang)
        detailed = []
        for i, row in enumerate(rows):
            if row.get("work") and row.get("family") and row.get("health"):
                row["overview"] = row.get("prediction") or ""
                row["prediction_long"] = " ".join(
                    filter(None, [row.get("prediction"), row.get("work"), row.get("family"), row.get("health"), row.get("remedy")])
                )
                detailed.append(row)
            else:
                detailed.append(expand_row_writeup(row, lang, i))
        return {
            "date": target_date.isoformat(),
            "language": lang_name,
            "lang": lang,
            "provider": f"gemini:{settings.gemini_model}",
            "rashifal": detailed,
        }
    except Exception:
        return fallback(lang, target_date)


def _fetch_horoscope_period(sign: str, period: str) -> dict:
    key = (sign or "aries").strip().lower()
    valid = {m["sign"] for m in RASHI_META}
    if key not in valid:
        key = "aries"
    meta = next(m for m in RASHI_META if m["sign"] == key)
    urls = {
        "daily": HOROSCOPE_URL,
        "weekly": HOROSCOPE_WEEKLY_URL,
        "monthly": HOROSCOPE_MONTHLY_URL,
    }
    url = f"{urls.get(period, HOROSCOPE_URL)}?{urllib.parse.urlencode({'sign': key})}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "panchang-platform/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        data = payload.get("data") or {}
        return {
            "sign": key,
            "planet": meta["planet"],
            "element": meta["element"],
            "date": data.get("date"),
            "period": data.get("period") or period,
            "horoscope": data.get("horoscope") or "",
            "provider": "freehoroscopeapi",
        }
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError) as exc:
        return {
            "sign": key,
            "planet": meta["planet"],
            "element": meta["element"],
            "date": None,
            "period": period,
            "horoscope": "",
            "provider": "unavailable",
            "error": str(exc),
        }


def fetch_daily_horoscope(sign: str) -> dict:
    return _fetch_horoscope_period(sign, "daily")


def build_rashi_detail(
    sign: str,
    lang: str,
    state_code: str,
    target_date,
    row: dict | None = None,
    panchang: dict | None = None,
) -> dict:
    """Full expand payload: regional write-up + state context + daily/weekly/monthly."""
    from .regional_v2 import config

    lang = _normalize_lang(lang)
    key = (sign or "aries").strip().lower()
    idx = next((i for i, m in enumerate(RASHI_META) if m["sign"] == key), 0)
    meta = RASHI_META[idx]
    native = (_TERMS.get("rashi", {}).get(lang) or _TERMS["rashi"]["hi"])[idx]
    base = row or {
        "rashi": native,
        "prediction": (_TERMS["predictions"][lang][idx % len(_TERMS["predictions"][lang])]),
        "lucky_number": str((idx + target_date.day) % 9 + 1),
        "lucky_color": _TERMS["colors"][lang][idx % len(_TERMS["colors"][lang])],
    }
    writeup = expand_row_writeup({**base, **meta, "index": idx + 1, "sign": key, "rashi": base.get("rashi") or native}, lang, idx)

    cfg = config(state_code or "KA")
    pan = (panchang or {}).get("panchang") or {}
    ast = (panchang or {}).get("astronomy") or {}
    moon_i = int(ast.get("moon_rashi_index") or (int(float(ast.get("moon_sidereal_longitude") or 0) // 30) + 1))
    sun_i = int(ast.get("sun_rashi_index") or (int(float(ast.get("sun_sidereal_longitude") or 0) // 30) + 1))
    areas = _areas_for(lang)
    nak = (pan.get("nakshatra") or {}).get("name") or "—"
    tithi = (pan.get("tithi") or {}).get("name") or "—"
    state_note = areas["state_note"].format(
        system=cfg.get("system", "Amanta"),
        muhurat=cfg.get("muhurat", "Choghadiya"),
        nakshatra=nak,
        tithi=tithi,
    )

    daily = _fetch_horoscope_period(key, "daily")
    weekly = _fetch_horoscope_period(key, "weekly")
    monthly = _fetch_horoscope_period(key, "monthly")

    return {
        "date": target_date.isoformat(),
        "lang": lang,
        "sign": key,
        "rashi": writeup.get("rashi") or native,
        "planet": meta["planet"],
        "element": meta["element"],
        "lucky_number": writeup.get("lucky_number"),
        "lucky_color": writeup.get("lucky_color"),
        "overview": writeup.get("overview") or writeup.get("prediction"),
        "work": writeup.get("work"),
        "family": writeup.get("family"),
        "health": writeup.get("health"),
        "remedy": writeup.get("remedy"),
        "prediction_long": writeup.get("prediction_long"),
        "is_moon_sign": moon_i == idx + 1,
        "is_sun_sign": sun_i == idx + 1,
        "state": {
            "code": (state_code or "KA").upper(),
            "system": cfg.get("system"),
            "muhurat": cfg.get("muhurat"),
            "style": cfg.get("style"),
            "accent": cfg.get("accent"),
            "note": state_note,
            "nakshatra": nak,
            "tithi": tithi,
            "vaar": (pan.get("vaar") or {}).get("name"),
        },
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
    }
