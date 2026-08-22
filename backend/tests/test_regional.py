from backend.app.regional_v2 import STATE_CONFIGS, regional_month_name

EXPECTED_CODES = {
    "UP","RJ","GJ","MH","TN","KA","AP","TS","KL","WB","OD","AS","PB","BR","MP","CG","JH","UK","HP","JK","GA","DL","HR",
    "AR","MN","ML","MZ","NL","SK","TR","AN","CH","DN","LA","LD","PY"
}

def test_all_36_state_ut_codes_are_configured():
    assert len(STATE_CONFIGS) == 36
    assert set(STATE_CONFIGS) == EXPECTED_CODES
    for code, cfg in STATE_CONFIGS.items():
        assert cfg["system"]
        assert cfg["muhurat"] in {"Choghadiya", "Gowri"}
        assert cfg["style"]
        assert cfg["accent"].startswith("#")
        assert cfg["priority_fields"]

def test_regional_month_name_exists():
    for code in EXPECTED_CODES:
        assert regional_month_name(code, 1)
        assert regional_month_name(code, 12)
from app.main import _state_code_from_address


def test_state_code_from_reverse_geocoder_address():
    assert _state_code_from_address({"ISO3166-2-lvl4": "IN-OD"}) == "OD"
    assert _state_code_from_address({"state": "Karnataka"}) == "KA"
    assert _state_code_from_address({"state": "Maharashtra"}) == "MH"
    assert _state_code_from_address({"state": "Unknown"}) is None
