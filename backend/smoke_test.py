import json
from datetime import date
from app.panchang import calculate_panchang

result=calculate_panchang(date.today(),12.9716,77.5946,"Asia/Kolkata","KA")
print(json.dumps(result,indent=2,ensure_ascii=False))
print("SMOKE TEST OK")
