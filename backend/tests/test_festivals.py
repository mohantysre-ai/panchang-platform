from datetime import date
from backend.app.festivals import _load_definitions, _applies


def test_festival_dataset_is_non_empty():
    definitions = _load_definitions()
    assert len(definitions) >= 20
    assert {x["rule"]["type"] for x in definitions} >= {"fixed", "tithi"}


def test_regional_filtering():
    diwali = next(x for x in _load_definitions() if x["id"] == "diwali")
    onam = next(x for x in _load_definitions() if x["id"] == "onam")
    assert _applies(diwali, "KA")
    assert _applies(onam, "KL")
    assert not _applies(onam, "KA")
