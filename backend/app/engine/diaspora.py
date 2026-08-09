"""
Diaspora Rule Engine
Decouples local horizon astronomy from regional state rule configurations.
"""

from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import Any, Dict, List, Optional
import pytz


@dataclass
class LocalHorizonContext:
    latitude: float
    longitude: float
    timezone_str: str
    target_date: str  # YYYY-MM-DD
    local_sunrise_utc: datetime
    local_sunset_utc: datetime


@dataclass
class StateRuleConfig:
    state_name: str
    month_system: str  # "AMANTA" or "PURNIMANTA"
    tithi_rule: str    # "SUNRISE_TITHI" or "EXACT_MOMENT"
    solar_calendar: bool  # True for Tamil/Malayalam solar calendar modes


STATE_RULE_REGISTRY: Dict[str, StateRuleConfig] = {
    "Odisha": StateRuleConfig("Odisha", "PURNIMANTA", "SUNRISE_TITHI", False),
    "Tamil Nadu": StateRuleConfig("Tamil Nadu", "AMANTA", "SUNRISE_TITHI", True),
    "Maharashtra": StateRuleConfig("Maharashtra", "AMANTA", "SUNRISE_TITHI", False),
    "Uttar Pradesh": StateRuleConfig("Uttar Pradesh", "PURNIMANTA", "SUNRISE_TITHI", False),
    "Kerala": StateRuleConfig("Kerala", "AMANTA", "SUNRISE_TITHI", True),
}


def get_state_config(state_name: str) -> StateRuleConfig:
    """Fallback to default Purnimanta system if state not registered."""
    return STATE_RULE_REGISTRY.get(
        state_name, 
        StateRuleConfig(state_name, "PURNIMANTA", "SUNRISE_TITHI", False)
    )


def calculate_diaspora_panchang(
    origin_state: str,
    current_lat: float,
    current_lon: float,
    timezone_str: str,
    target_date: str,
    raw_astronomy_provider: Any
) -> Dict[str, Any]:
    """
    Computes precise regional panchang for users located outside their native state/country.
    
    1. Computes local horizon events (Sunrise, Sunset) at current_lat/current_lon.
    2. Evaluates Tithi and Muhurat using origin state cultural rules.
    """
    local_tz = pytz.timezone(timezone_str)
    
    # Calculate astronomical events relative to user's local horizon
    astro_data = raw_astronomy_provider.get_ephemeris_for_location(
        lat=current_lat,
        lon=current_lon,
        date_str=target_date,
        tz=timezone_str
    )
    
    rule_config = get_state_config(origin_state)
    
    # Local horizon timestamps converted to local timezone string display
    sunrise_local = astro_data["sunrise_utc"].astimezone(local_tz)
    sunset_local = astro_data["sunset_utc"].astimezone(local_tz)
    
    # Resolve tithi at local sunrise moment using origin state rule
    sunrise_tithi = astro_data["tithi_at_sunrise"]
    
    # Determine local festival eligibility based on origin state system
    festival_resolved = None
    if rule_config.month_system == "AMANTA" and astro_data.get("amanta_festival"):
        festival_resolved = astro_data["amanta_festival"]
    elif rule_config.month_system == "PURNIMANTA" and astro_data.get("purnimanta_festival"):
        festival_resolved = astro_data["purnimanta_festival"]

    return {
        "metadata": {
            "applied_rule_system": origin_state,
            "month_system": rule_config.month_system,
            "user_location": {
                "latitude": current_lat,
                "longitude": current_lon,
                "timezone": timezone_str
            }
        },
        "local_astronomy": {
            "date": target_date,
            "sunrise": sunrise_local.strftime("%I:%M:%S %p"),
            "sunset": sunset_local.strftime("%I:%M:%S %p"),
            "day_duration_hours": round((sunset_local - sunrise_local).total_seconds() / 3600, 2)
        },
        "regional_panchang": {
            "tithi": sunrise_tithi,
            "nakshatra": astro_data.get("nakshatra"),
            "yoga": astro_data.get("yoga"),
            "karana": astro_data.get("karana"),
            "festival": festival_resolved
        },
        "diaspora_note": f"Astronomy evaluated for local coordinates ({current_lat:.2f}, {current_lon:.2f}) using {origin_state} calendar rules."
    }