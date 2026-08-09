from __future__ import annotations
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
from .ephemeris import sidereal_longitudes, rise_set
from .storage import get_or_create
from .regional_v2 import STATE_CONFIGS
DATA_FILE=Path(__file__).resolve().parents[1]/"data"/"festivals.json"
AMANTA_MONTHS=["Chaitra","Vaishakha","Jyeshtha","Ashadha","Shravana","Bhadrapada","Ashwin","Kartika","Margashirsha","Pausha","Magha","Phalguna"]
SOLAR_MONTHS={"tamil":["Chithirai","Vaikasi","Aani","Aadi","Avani","Purattasi","Aippasi","Karthigai","Margazhi","Thai","Maasi","Panguni"],"malayalam":["Medam","Edavam","Mithunam","Karkidakam","Chingam","Kanni","Thulam","Vrischikam","Dhanu","Makaram","Kumbham","Meenam"]}
FULL_MOON_SIGN_TO_MONTH={11:1,0:2,1:3,2:4,3:5,4:6,5:7,6:8,7:9,8:10,9:11,10:12}
def _load_definitions():
    with DATA_FILE.open("r",encoding="utf-8") as fh:return json.load(fh)["festivals"]
def _applies(defn,state_code):
    states={s.upper() for s in defn.get("states",["ALL"])};return "ALL" in states or state_code.upper() in states
def _phase(dt):
    sun,moon=sidereal_longitudes(dt);return (moon-sun)%360,sun
def _full_moon(dt,forward=False):
    step=timedelta(hours=6);cur=dt;prev,_=_phase(cur)
    for _ in range(70):
        nxt=cur+(step if forward else -step);angle,_=_phase(nxt);crossed=(prev<180<=angle) if forward else (angle<180<=prev)
        if crossed:
            a,b=(cur,nxt) if forward else (nxt,cur)
            for _ in range(28):
                mid=a+(b-a)/2;ma,_=_phase(mid)
                if ma>=180:b=mid
                else:a=mid
            return a+(b-a)/2
        cur,prev=nxt,angle
    return None
def _lunar_month(dt,system="Amanta"):
    angle,_=_phase(dt);full=_full_moon(dt,forward=angle<180)
    if not full:return None
    _,sun=_phase(full);amanta=FULL_MOON_SIGN_TO_MONTH[int(sun//30)];tithi=int(angle//12)+1;month=amanta
    if system=="Purnimanta" and tithi>15:month=(amanta%12)+1
    return {"index":month,"name":AMANTA_MONTHS[month-1],"system":system,"tithi_index":tithi,"paksha":"Shukla" if tithi<=15 else "Krishna"}
def lunar_month_for_date(target,state_code,lat,lon,timezone):
    cfg=STATE_CONFIGS.get(state_code.upper(),STATE_CONFIGS["KA"]);system=cfg.get("system","Amanta");sunrise,_=rise_set(target,lat,lon,timezone);dt=sunrise or datetime(target.year,target.month,target.day,6,tzinfo=ZoneInfo(timezone));sun,_moon=sidereal_longitudes(dt);sign=int(sun//30)
    if system=="Solar":
        names=SOLAR_MONTHS.get(cfg.get("style","hindu"))
        if names:return {"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone,"system":"Solar","index":sign+1,"name":names[sign]}
    result=_lunar_month(dt,system) or {"index":None,"name":None,"system":system};result.update({"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone});return result
def _sunrise_tithi(target,lat,lon,timezone):
    sunrise,_=rise_set(target,lat,lon,timezone);dt=sunrise or datetime(target.year,target.month,target.day,6,tzinfo=ZoneInfo(timezone));angle,_=_phase(dt);idx=int(angle//12)+1;return idx,"Shukla" if idx<=15 else "Krishna",dt
def _solar_ingress_date(target,longitude,timezone):
    tz=ZoneInfo(timezone)
    for delta in range(-3,4):
        d=target+timedelta(days=delta);noon=datetime(d.year,d.month,d.day,12,tzinfo=tz);sun_b=sidereal_longitudes(noon-timedelta(hours=12))[0];sun_a=sidereal_longitudes(noon+timedelta(hours=12))[0]
        if longitude==0:
            if sun_b>330 and sun_a<30:return d
        elif sun_b<=longitude<=sun_a:return d
    return None
def _matches(defn,target,lat,lon,timezone,state):
    rule=defn["rule"];kind=rule.get("type")
    if kind=="solar_ingress":return target==_solar_ingress_date(target,rule["longitude"],timezone)
    if kind=="fixed":return target.month==rule["month"] and target.day==rule["day"]
    if kind!="tithi":return False
    idx,paksha,sunrise=_sunrise_tithi(target,lat,lon,timezone)
    if idx!=rule["tithi"] or (rule.get("paksha") and paksha!=rule["paksha"]):return False
    if rule.get("lunar_month"):
        lm=_lunar_month(sunrise,defn.get("calendar_system","Amanta"))
        if not lm or lm["index"]!=rule["lunar_month"]:return False
    return True
def _event(defn,target):return {"id":defn["id"],"date":target.isoformat(),"category":defn.get("category","major"),"names":defn.get("names",{}),"accuracy":defn.get("accuracy","astronomical-rule"),"source_rule":defn["rule"]["type"]}
def resolve_festivals(target,state_code,lat,lon,timezone):
    events=[_event(d,target) for d in _load_definitions() if _applies(d,state_code) and _matches(d,target,lat,lon,timezone,state_code)];events.sort(key=lambda x:(x["category"]!="major",x["id"]));return {"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone,"events":events,"engine":"Swiss Ephemeris + sunrise tithi + astronomical lunar-month resolver"}
def festivals_for_date(target,state_code,lat,lon,timezone):
    key=f"festivals:v2:{target}:{state_code.upper()}:{lat:.5f}:{lon:.5f}:{timezone}";return get_or_create(key,"festivals",lambda:resolve_festivals(target,state_code,lat,lon,timezone))
def festivals_for_month(year,month,state_code,lat,lon,timezone):
    start=date(year,month,1);next_month=date(year+(month==12),1 if month==12 else month+1,1);events=[];cursor=start
    while cursor<next_month:events.extend(festivals_for_date(cursor,state_code,lat,lon,timezone)["events"]);cursor+=timedelta(days=1)
    return {"year":year,"month":month,"state_code":state_code.upper(),"timezone":timezone,"events":events}