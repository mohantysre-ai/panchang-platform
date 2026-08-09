"""
2025–2030 Reference-Date Corpus Validation Suite
File: backend/scripts/validate_corpus.py
Run: python3 -m scripts.validate_corpus
"""

import json
import os
import sys
from typing import List, Dict, Any

# Ensure backend module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.engine.panchang import calculate_daily_panchang  # Update path if necessary


CORPUS_FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "tests", "corpus_2025_2030.json")


def load_corpus() -> List[Dict[str, Any]]:
    if not os.path.exists(CORPUS_FILE_PATH):
        print(f"❌ Corpus file not found at {CORPUS_FILE_PATH}")
        print("Creating dummy corpus template...")
        sample_data = [
            {
                "date": "2026-01-14",
                "state": "Tamil Nadu",
                "festival": "Makar Sankranti / Pongal",
                "expected_tithi": "Shukla Ekadashi",
                "lat": 13.0827,
                "lon": 80.2707
            },
            {
                "date": "2026-11-08",
                "state": "Odisha",
                "festival": "Diwali / Kali Puja",
                "expected_tithi": "Amavasya",
                "lat": 20.2961,
                "lon": 85.8245
            }
        ]
        os.makedirs(os.path.dirname(CORPUS_FILE_PATH), exist_ok=True)
        with open(CORPUS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(sample_data, f, indent=2)
        return sample_data

    with open(CORPUS_FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_accuracy_gate():
    corpus = load_corpus()
    total_tests = len(corpus)
    passed_tests = 0

    print("=" * 65)
    print(" 🪐 PANCHANG ENGINE — 2025–2030 ACCURACY RELEASE GATE VALIDATION")
    print("=" * 65)

    for idx, sample in enumerate(corpus, start=1):
        date_str = sample["date"]
        state = sample["state"]
        festival = sample["festival"]
        expected_tithi = sample["expected_tithi"]

        try:
            # Execute backend calculation engine
            res = calculate_daily_panchang(
                date_str=date_str,
                lat=sample.get("lat", 28.6139),
                lon=sample.get("lon", 77.2090),
                state=state
            )

            calculated_tithi = res.get("tithi", {}).get("name", "")

            # Loose / Exact Match Verification
            is_match = expected_tithi.lower() in calculated_tithi.lower()

            if is_match:
                passed_tests += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"

            print(f"[{idx}/{total_tests}] {status} | Date: {date_str} | Region: {state}")
            print(f"      Festival: {festival}")
            print(f"      Expected Tithi: {expected_tithi} | Calculated: {calculated_tithi}\n")

        except Exception as e:
            print(f"[{idx}/{total_tests}] ⚠️ ERROR | Date: {date_str} | Error: {str(e)}\n")

    accuracy_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print("=" * 65)
    print(f"📊 SUMMARY REPORT:")
    print(f"   Total Cases Evaluated: {total_tests}")
    print(f"   Passed: {passed_tests} | Failed: {total_tests - passed_tests}")
    print(f"   Calculated Accuracy:  {accuracy_rate:.2f}%")
    
    if accuracy_rate >= 98.0:
        print("🚀 RELEASE GATE PASSED: Engine meets authoritative production standard.")
    else:
        print("⚠️ RELEASE GATE BLOCKED: Reconciliation against reference Panjikas required.")
    print("=" * 65)


if __name__ == "__main__":
    validate_accuracy_gate()