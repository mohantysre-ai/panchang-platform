"""
0–100 Auspiciousness Score Vector Calculator
Synthesizes discrete muhurat slots into a continuous 24-hour time series.
"""

from datetime import datetime, time, timedelta
from typing import Dict, List, Any


def time_to_minutes(t_str: str) -> int:
    """Converts 'HH:MM' (24hr) string to minutes from midnight."""
    h, m = map(int, t_str.split(":"))
    return h * 60 + m


def minutes_to_time_str(minutes: int) -> str:
    """Converts minutes from midnight to 'HH:MM' string."""
    h = (minutes // 60) % 24
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def compute_auspiciousness_timeline(panchang: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Computes 96 discrete 15-minute slots across a 24-hour day.
    Base Score: 50 (Neutral)
    Modifiers:
      +35 : Abhijit Muhurat
      +25 : Amrit / Labh / Shubh Choghadiya
      -45 : Rahu Kalam
      -35 : Durmuhurtham / Yamagandam
      -25 : Varjyam / Rog / Udveg / Kaal Choghadiya
    """
    # Extract timing intervals in minutes from midnight
    rahu_start = time_to_minutes(panchang.get("rahu_kalam", {}).get("start", "00:00"))
    rahu_end = time_to_minutes(panchang.get("rahu_kalam", {}).get("end", "00:00"))
    
    abhijit_start = time_to_minutes(panchang.get("abhijit_muhurat", {}).get("start", "00:00"))
    abhijit_end = time_to_minutes(panchang.get("abhijit_muhurat", {}).get("end", "00:00"))

    durmuhurtham_start = time_to_minutes(panchang.get("durmuhurtham", {}).get("start", "00:00"))
    durmuhurtham_end = time_to_minutes(panchang.get("durmuhurtham", {}).get("end", "00:00"))

    timeline = []

    # 96 intervals x 15 minutes = 1440 minutes (24 hours)
    for slot in range(96):
        start_min = slot * 15
        end_min = start_min + 15
        mid_min = start_min + 7  # Midpoint evaluation

        score = 50  # Base neutral score
        active_factors = []

        # Positive Influences
        if abhijit_start <= mid_min < abhijit_end and abhijit_start != abhijit_end:
            score += 35
            active_factors.append({"name": "Abhijit Muhurat", "type": "POSITIVE", "impact": +35})

        # Negative Influences (Penalties)
        if rahu_start <= mid_min < rahu_end and rahu_start != rahu_end:
            score -= 45
            active_factors.append({"name": "Rahu Kalam", "type": "NEGATIVE", "impact": -45})

        if durmuhurtham_start <= mid_min < durmuhurtham_end and durmuhurtham_start != durmuhurtham_end:
            score -= 30
            active_factors.append({"name": "Durmuhurtham", "type": "NEGATIVE", "impact": -30})

        # Clamp Score between 0 and 100
        score = max(0, min(100, score))

        # Classification
        if score >= 80:
            classification = "EXCELLENT"
            color_code = "#2E7D32"  # Deep Green
        elif score >= 60:
            classification = "GOOD"
            color_code = "#4CAF50"  # Light Green
        elif score >= 40:
            classification = "NEUTRAL"
            color_code = "#FFC107"  # Amber
        elif score >= 20:
            classification = "CAUTION"
            color_code = "#FF9800"  # Orange
        else:
            classification = "AVOID"
            color_code = "#D32F2F"  # Red

        timeline.append({
            "slot_index": slot,
            "time_start": minutes_to_time_str(start_min),
            "time_end": minutes_to_time_str(end_min),
            "score": score,
            "classification": classification,
            "color_code": color_code,
            "active_factors": active_factors
        })

    return timeline