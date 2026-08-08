from datetime import datetime
from zoneinfo import ZoneInfo
import swisseph as swe

FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL

def julian_day(dt):
    utc = dt.astimezone(ZoneInfo("UTC"))
    return swe.julday(
        utc.year, utc.month, utc.day,
        utc.hour + utc.minute / 60 + utc.second / 3600
    )

def sidereal_longitudes(dt):
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    jd = julian_day(dt)
    sun, _ = swe.calc_ut(jd, swe.SUN, FLAGS)
    moon, _ = swe.calc_ut(jd, swe.MOON, FLAGS)
    return sun[0] % 360, moon[0] % 360

def rise_set(target_date, lat, lon, timezone_name):
    tz = ZoneInfo(timezone_name)
    midnight = datetime(
        target_date.year, target_date.month, target_date.day,
        tzinfo=tz
    )
    jd = julian_day(midnight)
    geopos = (lon, lat, 0.0)

    def event(rising):
        rsmi = swe.CALC_RISE if rising else swe.CALC_SET
        result = swe.rise_trans(
            jd, swe.SUN, rsmi, geopos, 0.0, 10.0
        )
        event_jd = result[1][0]
        year, month, day, hour = swe.revjul(event_jd, swe.GREG_CAL)
        h = int(hour)
        minute_float = (hour - h) * 60
        minute = int(minute_float)
        second = int(round((minute_float - minute) * 60))
        if second >= 60:
            second = 0
            minute += 1
        if minute >= 60:
            minute = 0
            h += 1
        return datetime(
            year, month, day, h, minute, second,
            tzinfo=ZoneInfo("UTC")
        ).astimezone(tz)

    try:
        return event(True), event(False)
    except Exception:
        return None, None
