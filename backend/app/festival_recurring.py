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

AMAVASYA = [
    ("Amavasya", "अमावस्या"),
] * 12

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
        out.append(_tithi_vrata(
            f"amavasya_{month}", 30, "Krishna", month,
            {"en": f"{mname} Amavasya", "hi": AMAVASYA[month - 1][1], "or": "ଅମାବସ୍ୟା"},
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
