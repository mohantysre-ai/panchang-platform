"""Recurring tithi vratas (Ekadashi, Pradosh, Purnima, Amavasya, Masik Shivaratri)."""

from __future__ import annotations

SHUKLA_EKADASHI = [
    ("Kamada Ekadashi", "कामदा एकादशी"),
    ("Mohini Ekadashi", "मोहिनी एकादशी"),
    ("Nirjala Ekadashi", "निर्जला एकादशी"),
    ("Devshayani Ekadashi", "देवशयनी एकादशी"),
    ("Putrada Ekadashi", "पुत्रदा एकादशी"),
    ("Parsva Ekadashi", "परिवर्तिनी एकादशी"),
    ("Indira Ekadashi", "इंदिरा एकादशी"),
    ("Devutthana Ekadashi", "देवुत्थान एकादशी"),
    ("Mokshada Ekadashi", "मोक्षदा एकादशी"),
    ("Saphala Ekadashi", "सफला एकादशी"),
    ("Shattila Ekadashi", "षटतिला एकादशी"),
    ("Amalaki Ekadashi", "आमलकी एकादशी"),
]

KRISHNA_EKADASHI = [
    ("Papamochani Ekadashi", "पापमोचनी एकादशी"),
    ("Varuthini Ekadashi", "वरुथिनी एकादशी"),
    ("Apara Ekadashi", "अपरा एकादशी"),
    ("Yogini Ekadashi", "योगिनी एकादशी"),
    ("Kamika Ekadashi", "कामिका एकादशी"),
    ("Aja Ekadashi", "अजा एकादशी"),
    ("Devshayani Ekadashi", "देवशयनी एकादशी"),
    ("Utpanna Ekadashi", "उत्पन्ना एकादशी"),
    ("Safala Ekadashi", "सफला एकादशी"),
    ("Pausha Putrada Ekadashi", "पौष पुत्रदा एकादशी"),
    ("Shattila Ekadashi", "षटतिला एकादशी"),
    ("Vijaya Ekadashi", "विजया एकादशी"),
]

PRADOSH = [
    ("Pradosh Vrat", "प्रदोष व्रत"),
] * 12

MASIK_SHIVARATRI = [
    ("Masik Shivaratri", "मासिक शिवरात्रि"),
] * 12

AMAVASYA = [("Amavasya", "अमावस्या")] * 12
AMAVASYA[5] = ("Mahalaya Amavasya", "महालय अमावस्या")

PURNIMA = [
    ("Purnima", "पूर्णिमा"),
] * 12

LUNAR_MONTH_EN = [
    "Chaitra", "Vaishakha", "Jyeshtha", "Ashadha", "Shravana", "Bhadrapada",
    "Ashwin", "Kartika", "Margashirsha", "Pausha", "Magha", "Phalguna",
]


def _tithi_vrata(vrata_id: str, tithi: int, paksha: str, month: int, names: dict, *, tithi_alt: list[int] | None = None) -> dict:
    rule: dict = {"type": "tithi", "tithi": tithi, "paksha": paksha, "lunar_month": month}
    if tithi_alt:
        rule["tithi_alt"] = tithi_alt
    return {
        "id": vrata_id,
        "rule": rule,
        "calendar_system": "Amanta",
        "states": ["ALL"],
        "category": "vrata",
        "accuracy": "astronomical-rule",
        "names": names,
        "vrata_slot": vrata_id.rsplit("_", 1)[0] if vrata_id.rsplit("_", 1)[-1].isdigit() else vrata_id,
    }


def _generic_tithi_vrata(vrata_id: str, tithi: int, paksha: str, names: dict, *, tithi_alt: list[int] | None = None) -> dict:
    rule: dict = {"type": "tithi", "tithi": tithi, "paksha": paksha}
    if tithi_alt:
        rule["tithi_alt"] = tithi_alt
    return {
        "id": vrata_id,
        "rule": rule,
        "calendar_system": "Amanta",
        "states": ["ALL"],
        "category": "vrata",
        "accuracy": "astronomical-rule",
        "names": names,
        "vrata_slot": vrata_id.removeprefix("vrata_"),
    }


def recurring_festival_definitions() -> list[dict]:
    out: list[dict] = []
    for month in range(1, 13):
        mname = LUNAR_MONTH_EN[month - 1]
        en, hi = SHUKLA_EKADASHI[month - 1]
        out.append(_tithi_vrata(
            f"shukla_ekadashi_{month}", 11, "Shukla", month,
            {"en": en, "hi": hi, "or": f"{mname} ଏକାଦଶୀ"},
        ))
        en, hi = KRISHNA_EKADASHI[month - 1]
        out.append(_tithi_vrata(
            f"krishna_ekadashi_{month}", 11, "Krishna", month,
            {"en": en, "hi": hi, "or": f"{mname} କୃଷ୍ଣ ଏକାଦଶୀ"},
        ))
        out.append(_tithi_vrata(
            f"pradosh_{month}", 13, "Krishna", month,
            {"en": f"{mname} Pradosh", "hi": PRADOSH[month - 1][1], "or": "ପ୍ରଦୋଷ"},
        ))
        out.append(_tithi_vrata(
            f"masik_shivaratri_{month}", 14, "Krishna", month,
            {"en": f"{mname} Masik Shivaratri", "hi": MASIK_SHIVARATRI[month - 1][1], "or": "ମାସିକ ଶିବରାତ୍ରି"},
        ))
        am_en, am_hi = AMAVASYA[month - 1]
        out.append(_tithi_vrata(
            f"amavasya_{month}", 30, "Krishna", month,
            {"en": f"{mname} {am_en}", "hi": am_hi, "or": "ମହାଲୟ ଅମାବସ୍ୟା" if month == 6 else "ଅମାବସ୍ୟା"},
            tithi_alt=[29],
        ))
        out.append(_tithi_vrata(
            f"purnima_{month}", 15, "Shukla", month,
            {"en": f"{mname} Purnima", "hi": PURNIMA[month - 1][1], "or": "ପୂର୍ଣ୍ଣିମା"},
        ))
        out.append(_tithi_vrata(
            f"sankashti_{month}", 4, "Krishna", month,
            {"en": f"{mname} Sankashti Chaturthi", "hi": "संकष्टी चतुर्थी", "or": "ସଙ୍କଷ୍ଟୀ ଚତୁର୍ଥୀ"},
        ))
        out.append(_tithi_vrata(
            f"vinayaka_chaturthi_{month}", 4, "Shukla", month,
            {"en": f"{mname} Vinayaka Chaturthi", "hi": "विनायक चतुर्थी", "or": "ବିନାୟକ ଚତୁର୍ଥୀ"},
        ))
    return out


def generic_paksha_vrata_definitions() -> list[dict]:
    """Paksha+tithi vratas without lunar-month binding (Dainik Panchang style)."""
    common = {
        "en": "Ekadashi", "hi": "एकादशी", "or": "ଏକାଦଶୀ",
    }
    return [
        _generic_tithi_vrata("vrata_shukla_ekadashi", 11, "Shukla", common),
        _generic_tithi_vrata("vrata_krishna_ekadashi", 11, "Krishna", {"en": "Ekadashi", "hi": "एकादशी", "or": "ଏକାଦଶୀ"}),
        _generic_tithi_vrata("vrata_pradosh", 13, "Krishna", {"en": "Pradosh Vrat", "hi": "प्रदोष व्रत", "or": "ପ୍ରଦୋଷ ବ୍ରତ"}),
        _generic_tithi_vrata("vrata_masik_shivaratri", 14, "Krishna", {"en": "Masik Shivaratri", "hi": "मासिक शिवरात्रि", "or": "ମାସିକ ଶିବରାତ୍ରି"}),
        _generic_tithi_vrata("vrata_amavasya", 30, "Krishna", {"en": "Amavasya", "hi": "अमावस्या", "or": "ଅମାବସ୍ୟା"}, tithi_alt=[29]),
        _generic_tithi_vrata("vrata_purnima", 15, "Shukla", {"en": "Purnima", "hi": "पूर्णिमा", "or": "ପୂର୍ଣ୍ଣିମା"}),
        _generic_tithi_vrata("vrata_sankashti", 4, "Krishna", {"en": "Sankashti Chaturthi", "hi": "संकष्टी चतुर्थी", "or": "ସଙ୍କଷ୍ଟୀ ଚତୁର୍ଥୀ"}),
        _generic_tithi_vrata("vrata_vinayaka_chaturthi", 4, "Shukla", {"en": "Vinayaka Chaturthi", "hi": "विनायक चतुर्थी", "or": "ବିନାୟକ ଚତୁର୍ଥୀ"}),
        _generic_tithi_vrata("vrata_shukla_ashtami", 8, "Shukla", {"en": "Shukla Ashtami", "hi": "शुक्ल अष्टमी", "or": "ଶୁକ୍ଳ ଅଷ୍ଟମୀ"}),
        _generic_tithi_vrata("vrata_krishna_ashtami", 8, "Krishna", {"en": "Krishna Ashtami", "hi": "कृष्ण अष्टमी", "or": "କୃଷ୍ଣ ଅଷ୍ଟମୀ"}),
        _generic_tithi_vrata("vrata_shukla_navami", 9, "Shukla", {"en": "Shukla Navami", "hi": "शुक्ल नवमी", "or": "ଶୁକ୍ଳ ନବମୀ"}),
        _generic_tithi_vrata("vrata_krishna_navami", 9, "Krishna", {"en": "Krishna Navami", "hi": "कृष्ण नवमी", "or": "କୃଷ୍ଣ ନବମୀ"}),
        _generic_tithi_vrata("vrata_shukla_dwadashi", 12, "Shukla", {"en": "Shukla Dwadashi", "hi": "शुक्ल द्वादशी", "or": "ଶୁକ୍ଳ ଦ୍ୱାଦଶୀ"}),
        _generic_tithi_vrata("vrata_krishna_dwadashi", 12, "Krishna", {"en": "Krishna Dwadashi", "hi": "कृष्ण द्वादशी", "or": "କୃଷ୍ଣ ଦ୍ୱାଦଶୀ"}),
        _generic_tithi_vrata("vrata_shukla_trayodashi", 13, "Shukla", {"en": "Shukla Trayodashi", "hi": "शुक्ल त्रयोदशी", "or": "ଶୁକ୍ଳ ତ୍ରୟୋଦଶୀ"}),
        _generic_tithi_vrata("vrata_krishna_trayodashi", 13, "Krishna", {"en": "Krishna Trayodashi", "hi": "कृष्ण त्रयोदशी", "or": "କୃଷ୍ଣ ତ୍ରୟୋଦଶୀ"}),
        _generic_tithi_vrata("vrata_shukla_panchami", 5, "Shukla", {"en": "Shukla Panchami", "hi": "शुक्ल पंचमी", "or": "ଶୁକ୍ଳ ପଞ୍ଚମୀ"}),
        _generic_tithi_vrata("vrata_krishna_panchami", 5, "Krishna", {"en": "Krishna Panchami", "hi": "कृष्ण पंचमी", "or": "କୃଷ୍ଣ ପଞ୍ଚମୀ"}),
        _generic_tithi_vrata("vrata_shukla_saptami", 7, "Shukla", {"en": "Shukla Saptami", "hi": "शुक्ल सप्तमी", "or": "ଶୁକ୍ଳ ସପ୍ତମୀ"}),
        _generic_tithi_vrata("vrata_krishna_saptami", 7, "Krishna", {"en": "Krishna Saptami", "hi": "कृष्ण सप्तमी", "or": "କୃଷ୍ଣ ସପ୍ତମୀ"}),
        _generic_tithi_vrata("vrata_shukla_dashami", 10, "Shukla", {"en": "Shukla Dashami", "hi": "शुक्ल दशमी", "or": "ଶୁକ୍ଳ ଦଶମୀ"}),
        _generic_tithi_vrata("vrata_krishna_dashami", 10, "Krishna", {"en": "Krishna Dashami", "hi": "कृष्ण दशमी", "or": "କୃଷ୍ଣ ଦଶମୀ"}),
        _generic_tithi_vrata("vrata_shukla_chaturdashi", 14, "Shukla", {"en": "Shukla Chaturdashi", "hi": "शुक्ल चतुर्दशी", "or": "ଶୁକ୍ଳ ଚତୁର୍ଦ୍ଦଶୀ"}),
        _generic_tithi_vrata("vrata_krishna_chaturdashi", 14, "Krishna", {"en": "Krishna Chaturdashi", "hi": "कृष्ण चतुर्दशी", "or": "କୃଷ୍ଣ ଚତୁର୍ଦ୍ଦଶୀ"}),
    ]
