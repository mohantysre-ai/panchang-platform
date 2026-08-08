from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from .ephemeris import sidereal_longitudes, rise_set

TITHI_NAMES = [
"Shukla Pratipada","Shukla Dwitiya","Shukla Tritiya","Shukla Chaturthi",
"Shukla Panchami","Shukla Shashti","Shukla Saptami","Shukla Ashtami",
"Shukla Navami","Shukla Dashami","Shukla Ekadashi","Shukla Dwadashi",
"Shukla Trayodashi","Shukla Chaturdashi","Purnima",
"Krishna Pratipada","Krishna Dwitiya","Krishna Tritiya","Krishna Chaturthi",
"Krishna Panchami","Krishna Shashti","Krishna Saptami","Krishna Ashtami",
"Krishna Navami","Krishna Dashami","Krishna Ekadashi","Krishna Dwadashi",
"Krishna Trayodashi","Krishna Chaturdashi","Amavasya"
]
NAKSHATRAS = [
"Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
"Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
"Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
"Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
"Uttara Bhadrapada","Revati"
]
VAAR = ["Ravivara","Somavara","Mangalavara","Budhavara","Guruvara","Shukravara","Shanivara"]
YOGA_NAMES = [
"Vishkumbha","Preeti","Ayushman","Saubhagya","Shobhana","Atiganda",
"Sukarma","Dhriti","Shoola","Ganda","Vriddhi","Dhruva","Vyaghata",
"Harshana","Vajra","Siddhi","Vyatipata","Variyana","Parigha","Shiva",
"Siddha","Sadhya","Shubha","Shukla","Brahma","Indra","Vaidhriti"
]
RAHU_PARTS = {0:7,1:1,2:6,3:4,4:5,5:3,6:2}

def fmt(dt):
    return dt.strftime("%I:%M:%S %p") if dt else None

def tithi(sun, moon):
    diff = (moon - sun) % 360
    i = int(diff // 12)
    return {
        "index": i + 1,
        "name": TITHI_NAMES[i],
        "paksha": "Shukla" if i < 15 else "Krishna",
        "progress_percent": round((diff % 12) / 12 * 100, 2)
    }

def nakshatra(moon):
    span = 360 / 27
    i = int(moon // span)
    pada = int((moon % span) / (span / 4)) + 1
    return {"index": i + 1, "name": NAKSHATRAS[i], "pada": min(pada, 4)}

def yoga(sun, moon):
    i = int(((sun + moon) % 360) // (360 / 27))
    return {"index": i + 1, "name": YOGA_NAMES[i]}

def karana(diff):
    i = int((diff % 360) // 6)
    if i == 0:
        name = "Kimstughna"
    elif i >= 57:
        name = ["Shakuni","Chatushpada","Naga"][i - 57]
    else:
        names = ["Bava","Balava","Kaulava","Taitila","Garaja","Vanija","Vishti"]
        name = names[(i - 1) % 7]
    return {"index": i + 1, "name": name}

def calculate_panchang(target_date, lat, lon, timezone_name, state_code):
    tz = ZoneInfo(timezone_name)
    noon = datetime(
        target_date.year, target_date.month, target_date.day,
        12, 0, tzinfo=tz
    )
    sun, moon = sidereal_longitudes(noon)
    sunrise, sunset = rise_set(target_date, lat, lon, timezone_name)
    diff = (moon - sun) % 360
    weekday = (target_date.weekday() + 1) % 7

    rahu = None
    abhijit = None
    if sunrise and sunset:
        duration = (sunset - sunrise) / 8
        rstart = sunrise + duration * (RAHU_PARTS[weekday] - 1)
        rahu = f"{fmt(rstart)} - {fmt(rstart + duration)}"
        midday = sunrise + (sunset - sunrise) / 2
        abhijit = f"{fmt(midday-timedelta(minutes=24))} - {fmt(midday+timedelta(minutes=24))}"

    return {
        "date": target_date.isoformat(),
        "state_code": state_code.upper(),
        "location": {"latitude":lat,"longitude":lon,"timezone":timezone_name},
        "panchang": {
            "tithi": tithi(sun, moon),
            "nakshatra": nakshatra(moon),
            "yoga": yoga(sun, moon),
            "karana": karana(diff),
            "vaar": {"index":weekday,"name":VAAR[weekday]},
            "sunrise": fmt(sunrise),
            "sunset": fmt(sunset)
        },
        "auspicious_timings": {"abhijit_muhurat": abhijit},
        "inauspicious_timings": {"rahu_kalam": rahu},
        "astronomy": {
            "sun_sidereal_longitude": round(sun,6),
            "moon_sidereal_longitude": round(moon,6)
        }
    }
