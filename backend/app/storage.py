import json
from .config import settings
from .cache import cache
from .database import audit

def ensure_dirs():
    (settings.absolute_data_dir/"panchang").mkdir(parents=True,exist_ok=True)
    (settings.absolute_data_dir/"rashifal").mkdir(parents=True,exist_ok=True)

def safe_key(x):
    return x.replace("/","_").replace("\\","_").replace(":","_").replace(" ","_")

def get_or_create(key,kind,generator):
    v=cache.get(key)
    if v is not None: return v
    path=settings.absolute_data_dir/kind/f"{safe_key(key)}.json"
    if path.exists():
        try:
            v=json.loads(path.read_text(encoding="utf-8"))
            cache.set(key,v)
            return v
        except Exception:
            pass
    v=generator()
    tmp=path.with_suffix(".tmp")
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding="utf-8")
    tmp.replace(path)
    cache.set(key,v)
    audit(kind,key,json.dumps(v,ensure_ascii=False))
    return v

ensure_dirs()
