from __future__ import annotations
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from .ephemeris import sidereal_longitudes, rise_set
from .storage import get_or_create
from .regional_v2 import STATE_CONFIGS
from .festival_recurring import recurring_festival_definitions
DATA_FILE=Path(__file__).resolve().parents[1]/"data"/"festivals.json"
CATEGORY_ORDER={"major":0,"regional":1,"minor":2,"vrata":3}
AMANTA_MONTHS=["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada","Ashwin","Kartika","Margashirsha","Pausha","Magha","Phalguna"]
SOLAR_MONTHS={"tamil":["Chithirai","Vaikasi","Aani","Aadi","Avani","Purattasi","Aippasi","Karthigai","Margazhi","Thai","Maasi","Panguni"],"malayalam":["Medam","Edavam","Mithunam","Karkidakam","Chingam","Kanni","Thulam","Vrischikam","Dhanu","Makaram","Kumbham","Meenam"]}
# Sun sign at Amavasya (Mesha=0 … Meena=11) → Amanta lunar month index (Chaitra=1 …)
_AMAVASYA_SIGN_TO_MONTH=lambda sign:((sign+1)%12)+1
def _load_definitions():
    with DATA_FILE.open("r",encoding="utf-8") as fh:static=json.load(fh)["festivals"]
    return static+recurring_festival_definitions()
def _applies(defn,state_code):
    states={s.upper() for s in defn.get("states",["ALL"])};return "ALL" in states or state_code.upper() in states
def _phase(dt):
    sun,moon=sidereal_longitudes(dt);return (moon-sun)%360,sun
def _cross_phase(dt,phase,forward):
    step=timedelta(hours=6);cur=dt;prev,_=_phase(cur)
    for _ in range(120):
        nxt=cur+(step if forward else -step);angle,_=_phase(nxt);crossed=((prev<180<=angle) if forward else (angle<180<=prev)) if phase==180 else ((prev>300 and angle<60) if forward else (angle>300 and prev<60))
        if crossed:
            a,b=(cur,nxt) if forward else (nxt,cur)
            for _ in range(28):
                mid=a+(b-a)/2;ma,_=_phase(mid)
                if phase==180:
                    if ma>=180:b=mid
                    else:a=mid
                else:
                    if ma>300:a=mid
                    else:b=mid
            return a+(b-a)/2
        cur,prev=nxt,angle
    return None
def _full_moon(dt):
    angle,_=_phase(dt);return _cross_phase(dt,180,angle<180)
def _new_moon(dt,forward=False):return _cross_phase(dt,0,forward)
def _lunar_month(dt,system="Amanta"):
    angle,_=_phase(dt);prev_new=_new_moon(dt,False)
    if not prev_new:return None
    next_new=_new_moon(dt,True);tithi=int(angle//12)+1
    ref=prev_new
    if tithi>15 and tithi>=25 and next_new:ref=next_new
    sun,_=sidereal_longitudes(ref+timedelta(hours=1));month=_AMAVASYA_SIGN_TO_MONTH(int(sun//30))
    if system=="Purnimanta" and tithi>15 and tithi<25:month=(month%12)+1
    adhika=False
    if next_new:
        before=sidereal_longitudes(prev_new+timedelta(hours=1))[0];after=sidereal_longitudes(next_new-timedelta(hours=1))[0];adhika=int(before//30)==int(after//30)
    return {"index":month,"name":AMANTA_MONTHS[month-1],"system":system,"tithi_index":tithi,"paksha":"Shukla" if tithi<=15 else "Krishna","adhika":adhika}
def lunar_month_for_date(target,state_code,lat,lon,timezone):
    cfg=STATE_CONFIGS.get(state_code.upper(),STATE_CONFIGS["KA"]);system=cfg.get("system","Amanta");sunrise,_=rise_set(target,lat,lon,timezone);dt=sunrise or datetime(target.year,target.month,target.day,6,tzinfo=ZoneInfo(timezone));sun,_moon=sidereal_longitudes(dt);sign=int(sun//30)
    if system=="Solar":
        names=SOLAR_MONTHS.get(cfg.get("style","hindu"))
        if names:return {"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone,"system":"Solar","index":sign+1,"name":names[sign],"adhika":False}
    result=_lunar_month(dt,system) or {"index":None,"name":None,"system":system,"adhika":False};result.update({"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone});return result
def _sunrise_tithi(target,lat,lon,timezone):
    sunrise,_=rise_set(target,lat,lon,timezone);dt=sunrise or datetime(target.year,target.month,target.day,6,tzinfo=ZoneInfo(timezone));angle,_=_phase(dt);idx=int(angle//12)+1;return idx,"Shukla" if idx<=15 else "Krishna",dt
def _solar_ingress_date(target,longitude,timezone):
    tz=ZoneInfo(timezone)
    for delta in range(-3,4):
        d=target+timedelta(days=delta);noon=datetime(d.year,d.month,d.day,12,tzinfo=tz);sun_b=sidereal_longitudes(noon-timedelta(hours=12))[0];sun_a=sidereal_longitudes(noon+timedelta(hours=12))[0]
        if longitude==0 and sun_b>330 and sun_a<30:return d
        if longitude and sun_b<=longitude<=sun_a:return d
    return None
def _matches(defn,target,lat,lon,timezone,state):
    rule=defn["rule"];kind=rule.get("type")
    if kind=="solar_ingress":return target==_solar_ingress_date(target,rule["longitude"],timezone)
    if kind=="fixed":return target.month==rule["month"] and target.day==rule["day"]
    if kind!="tithi":return False
    idx,paksha,sunrise=_sunrise_tithi(target,lat,lon,timezone)
    allowed={rule["tithi"],*(rule.get("tithi_alt") or [])}
    if idx not in allowed or (rule.get("paksha") and paksha!=rule["paksha"]):return False
    if rule.get("lunar_month"):
        lm=_lunar_month(sunrise,defn.get("calendar_system","Amanta"))
        if not lm or lm["index"]!=rule["lunar_month"] or (lm.get("adhika") and not rule.get("allow_adhika",False)):return False
    return True
def _event(defn,target):return {"id":defn["id"],"date":target.isoformat(),"category":defn.get("category","major"),"names":defn.get("names",{}),"accuracy":defn.get("accuracy","astronomical-rule"),"source_rule":defn["rule"]["type"]}
def resolve_festivals(target,state_code,lat,lon,timezone):
    events=[_event(d,target) for d in _load_definitions() if _applies(d,state_code) and _matches(d,target,lat,lon,timezone,state_code)];events.sort(key=lambda x:(CATEGORY_ORDER.get(x["category"],9),x["id"]));return {"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone,"events":events,"engine":"Swiss Ephemeris + sunrise tithi + Amavasya lunar-month resolver"}
def festivals_for_date(target,state_code,lat,lon,timezone):
    key=f"festivals:v6:{target}:{state_code.upper()}:{lat:.5f}:{lon:.5f}:{timezone}";return get_or_create(key,"festivals",lambda:resolve_festivals(target,state_code,lat,lon,timezone))
def festivals_for_month(year,month,state_code,lat,lon,timezone):
    start=date(year,month,1);next_month=date(year+(month==12),1 if month==12 else month+1,1);events=[];cursor=start
    while cursor<next_month:events.extend(festivals_for_date(cursor,state_code,lat,lon,timezone)["events"]);cursor+=timedelta(days=1)
    return {"year":year,"month":month,"state_code":state_code.upper(),"timezone":timezone,"events":events}