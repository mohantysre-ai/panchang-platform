STATE_CONFIGS = {
"UP":{"system":"Purnimanta","muhurat":"Choghadiya"},
"RJ":{"system":"Purnimanta","muhurat":"Choghadiya"},
"GJ":{"system":"Amanta","muhurat":"Choghadiya"},
"MH":{"system":"Amanta","muhurat":"Choghadiya"},
"TN":{"system":"Solar","muhurat":"Gowri"},
"KA":{"system":"Amanta","muhurat":"Gowri"},
"AP":{"system":"Amanta","muhurat":"Gowri"},
"TS":{"system":"Amanta","muhurat":"Gowri"},
"KL":{"system":"Solar","muhurat":"Gowri"},
"WB":{"system":"Amanta","muhurat":"Choghadiya"},
"OD":{"system":"Amanta","muhurat":"Choghadiya"}
}
CHOGHADIYA = {
0:["Udveg","Amrut","Kala","Shubh","Roga","Udveg","Chala","Labha"],
1:["Amrut","Kala","Shubh","Roga","Udveg","Chala","Labha","Amrut"],
2:["Roga","Udveg","Chala","Labha","Amrut","Kala","Shubh","Roga"],
3:["Labha","Amrut","Kala","Shubh","Roga","Udveg","Chala","Labha"],
4:["Shubh","Roga","Udveg","Chala","Labha","Amrut","Kala","Shubh"],
5:["Chala","Labha","Amrut","Kala","Shubh","Roga","Udveg","Chala"],
6:["Kala","Shubh","Roga","Udveg","Chala","Labha","Amrut","Kala"]
}
GOWRI = {
0:["Udyoga","Shunya","Labha","Chal","Roga","Kaal","Amrita","Shubha"],
1:["Chal","Labha","Shunya","Roga","Shubha","Kaal","Amrita","Udyoga"],
2:["Roga","Kaal","Labha","Udyoga","Chal","Amrita","Shunya","Shubha"],
3:["Labha","Shubha","Amrita","Chal","Udyoga","Shunya","Roga","Kaal"],
4:["Shubha","Roga","Shunya","Labha","Kaal","Chal","Udyoga","Amrita"],
5:["Amrita","Udyoga","Chal","Kaal","Roga","Shubha","Shunya","Labha"],
6:["Kaal","Amrita","Shunya","Udyoga","Shubha","Labha","Chal","Roga"]
}
GOOD_C = {"Amrut","Shubh","Labha","Chala"}
GOOD_G = {"Amrita","Shubha","Labha","Udyoga"}

def slots(start,end,names,good):
    if not start or not end: return []
    d=(end-start)/8
    return [{
        "slot":i+1,"name":name,
        "nature":"Good" if name in good else "Bad",
        "time":f"{(a:=start+d*i).strftime('%I:%M %p')} - {(a+d).strftime('%I:%M %p')}"
    } for i,name in enumerate(names)]

def regional_timings(sunrise,sunset,weekday,state):
    c=STATE_CONFIGS.get(state.upper(),{"system":"Amanta","muhurat":"Standard"})
    r={"system":c["system"],"muhurat_system":c["muhurat"]}
    if c["muhurat"]=="Choghadiya":
        r["choghadiya_day"]=slots(sunrise,sunset,CHOGHADIYA[weekday],GOOD_C)
    elif c["muhurat"]=="Gowri":
        r["gowri_panchangam"]=slots(sunrise,sunset,GOWRI[weekday],GOOD_G)
    return r

def available_states():
    return STATE_CONFIGS
