"""
FastAPI Router for Diaspora Engine and Auspiciousness Timeline API
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.engine.auspiciousness import compute_auspiciousness_timeline
from app.engine.diaspora import calculate_diaspora_panchang

router = APIRouter(prefix="/api/v1", tags=["Advanced Panchang Engines"])


# Mock provider wrapper for raw ephemeris calculation
class EphemerisProviderMock:
    @staticmethod
    def get_ephemeris_for_location(lat, lon, date_str, tz):
        from datetime import datetime
        import pytz
        local_tz = pytz.timezone(tz)
        return {
            "sunrise_utc": local_tz.localize(datetime.strptime(f"{date_str} 06:15:00", "%Y-%m-%d %H:%M:%S")),
            "sunset_utc": local_tz.localize(datetime.strptime(f"{date_str} 18:30:00", "%Y-%m-%d %H:%M:%S")),
            "tithi_at_sunrise": "Shukla Dwadashi",
            "nakshatra": "Rohini",
            "yoga": "Ayushman",
            "karana": "Bava",
            "amanta_festival": None,
            "purnimanta_festival": "Regional Vrat"
        }


@router.get("/panchang/diaspora")
async def get_diaspora_panchang(
    origin_state: str = Query(..., example="Odisha", description="Native Indian State rule set"),
    latitude: float = Query(..., example=37.7749, description="Current latitude"),
    longitude: float = Query(..., example=-122.4194, description="Current longitude"),
    timezone: str = Query(..., example="America/Los_Angeles", description="Local Timezone string"),
    date: str = Query(..., example="2026-08-10", description="Date in YYYY-MM-DD format")
):
    """
    Calculates panchang using home state cultural rules adapted to overseas/local horizon coordinates.
    """
    try:
        res = calculate_diaspora_panchang(
            origin_state=origin_state,
            current_lat=latitude,
            current_lon=longitude,
            timezone_str=timezone,
            target_date=date,
            raw_astronomy_provider=EphemerisProviderMock()
        )
        return {"status": "success", "data": res}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/panchang/auspiciousness-timeline")
async def get_auspiciousness_timeline(
    date: str = Query(..., example="2026-08-10"),
    latitude: float = Query(..., example=28.6139),
    longitude: float = Query(..., example=77.2090)
):
    """
    Returns a 24-hour (96-slot) continuous Auspiciousness Index array (0-100 score).
    """
    # Sample structured panchang data passed to calculator
    sample_panchang = {
        "rahu_kalam": {"start": "16:30", "end": "18:00"},
        "abhijit_muhurat": {"start": "11:50", "end": "12:40"},
        "durmuhurtham": {"start": "08:30", "end": "09:20"}
    }
    
    timeline = compute_auspiciousness_timeline(sample_panchang)
    
    return {
        "status": "success",
        "date": date,
        "total_slots": len(timeline),
        "timeline": timeline
    }