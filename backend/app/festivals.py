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
PURNIMA_NAKSHATRA_MONTH={14:1,16:2,18:3,20:4,21:4,22:5,25:6,26:6,1:7,2:7,3:8,5:9,8:10,10:11,11:12,12:12}
def _load_definitions():
    with DATA_FILE.open("r",encoding="utf-8") as fh:return json.load(fh)["festivals"]
def _applies(defn,state_code):
    states={s.upper() for s in defn.get("states",["ALL"])};return "ALL" in states or state_code.upper() in states
def _phase(dt):
    sun,moon=sidereal_longitudes(dt);return (moon-sun)%360,sun
def _cross_phase(dt,phase,forward):
    step=timedelta(hours=6);cur=dt;prev,_=_phase(cur)
    for _ in range(70):
        nxt=cur+(step if forward else -step);angle,_=_phase(nxt)
        if phase==180:crossed=(prev<180<=angle) if forward else (angle<180<=prev)
        else:crossed=(prev>300 and angle<60) if forward else (angle>300 and prev<60)
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
    angle,_=_phase(dt);full=_full_moon(dt)
    if not full:return None
    _,moon=sidereal_longitudes(full);nak=int(moon/(360/27))+1;month=PURNIMA_NAKSHATRA_MONTH.get(nak)
    if not month:return None
    prev_new=_new_moon(dt,False);next_new=_new_moon(dt,True);adhika=False
    if prev_new and next_new:
        prev_sun=sidereal_longitudes(prev_new)[0];next_sun=sidereal_longitudes(next_new)[0];adhika=int(prev_sun//30)==int(next_sun//30)
    tithi=int(angle//12)+1
    if system=="Purnimanta" and tithi>15:
        month=(month+1)%12 or 12
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
    if idx!=rule["tithi"] or (rule.get("paksha") and paksha!=rule["paksha"]):return False
    if rule.get("lunar_month"):
        lm=_lunar_month(sunrise,defn.get("calendar_system","Amanta"))
        if not lm or lm["index"]!=rule["lunar_month"] or (lm.get("adhika") and not rule.get("allow_adhika",False)):return False
    return True
def _event(defn,target):return {"id":defn["id"],"date":target.isoformat(),"category":defn.get("category","major"),"names":defn.get("names",{}),"accuracy":defn.get("accuracy","astronomical-rule"),"source_rule":defn["rule"]["type"]}
def resolve_festivals(target,state_code,lat,lon,timezone):
    events=[_event(d,target) for d in _load_definitions() if _applies(d,state_code) and _matches(d,target,lat,lon,timezone,state_code)];events.sort(key=lambda x:(x["category"]!="major",x["id"]));return {"date":target.isoformat(),"state_code":state_code.upper(),"timezone":timezone,"events":events,"engine":"Swiss Ephemeris + sunrise tithi + Purnima-nakshatra lunar-month resolver"}
def festivals_for_date(target,state_code,lat,lon,timezone):
    key=f"festivals:v3:{target}:{state_code.upper()}:{lat:.5f}:{lon:.5f}:{timezone}";return get_or_create(key,"festivals",lambda:resolve_festivals(target,state_code,lat,lon,timezone))
def festivals_for_month(year,month,state_code,lat,lon,timezone):
    start=date(year,month,1);next_month=date(year+(month==12),1 if month==12 else month+1,1);events=[];cursor=start
    while cursor<next_month:events.extend(festivals_for_date(cursor,state_code,lat,lon,timezone)["events"]);cursor+=timedelta(days=1)
    return {"year":year,"month":month,"state_code":state_code.upper(),"timezone":timezone,"events":events}