from backend.app.festivals import _load_definitions, _applies

def test_festival_dataset_is_non_empty():
    definitions=_load_definitions()
    assert len(definitions)>=20
    assert {x["rule"]["type"] for x in definitions}>={"solar_ingress","tithi"}
    assert all(x.get("names",{}).get("en") for x in definitions)

def test_regional_filtering():
    diwali=next(x for x in _load_definitions() if x["id"]=="diwali")
    pongal=next(x for x in _load_definitions() if x["id"]=="pongal")
    assert _applies(diwali,"KA")
    assert _applies(pongal,"TN")
    assert not _applies(pongal,"KA")

def test_lunar_rules_are_not_fixed_gregorian_dates():
    diwali=next(x for x in _load_definitions() if x["id"]=="diwali")
    assert diwali["rule"]["type"]=="tithi"
    assert diwali["rule"]["lunar_month"]==8
    assert diwali["rule"]["paksha"]=="Krishna"
