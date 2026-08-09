def compute_hourly_auspiciousness(panchang_data: dict) -> list:
    """
    Returns a 24-hour array (15-minute intervals) with calculated scores and status tags.
    """
    timeline = []
    # 96 intervals of 15 mins across 24 hours
    for slot in range(96):
        time_slot = slot_to_time(slot)
        score = 50 # Base neutral score
        
        # Apply Positive Modifiers
        if is_in_range(time_slot, panchang_data["abhijit_muhurat"]):
            score += 35
        if get_choghadiya_nature(time_slot, panchang_data) in ["Amrit", "Shubh", "Labh"]:
            score += 20

        # Apply Negative Modifiers (Hard Penalties)
        if is_in_range(time_slot, panchang_data["rahu_kalam"]):
            score -= 45
        if is_in_range(time_slot, panchang_data["durmuhurtham"]):
            score -= 30

        # Clamp Score between 0 and 100
        score = max(0, min(100, score))
        
        timeline.append({
            "time": time_slot,
            "score": score,
            "status": "EXCELLENT" if score >= 75 else "GOOD" if score >= 55 else "NEUTRAL" if score >= 40 else "AVOID",
            "active_influences": get_influences_at(time_slot, panchang_data)
        })
        
    return timeline