# -*- coding: utf-8 -*-
"""Add Odia (or) language pack and map OD -> or. ASCII-only source."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TERMS = Path(__file__).with_name("terms.json")
EMIT = Path(__file__).with_name("emit_regional.py")
RASHIFAL = ROOT / "backend" / "app" / "rashifal.py"
INDEX = ROOT / "frontend" / "index.html"

OR_UI = {
    "title": "\u0b2a\u0b4d\u0b30\u0b3e\u0b26\u0b47\u0b36\u0b3f\u0b15 \u0b2a\u0b1e\u0b4d\u0b1a\u0b3e\u0b19\u0b4d\u0b17",
    "subtitle": "\u0b30\u0b3e\u0b1c\u0b4d\u0b5f \u0b06\u0b27\u0b3e\u0b30\u0b3f\u0b24 \u0b2a\u0b1e\u0b4d\u0b1a\u0b3e\u0b19\u0b4d\u0b17 \u00b7 \u0b30\u0b3e\u0b36\u0b3f\u0b2b\u0b33 \u00b7 \u0b2e\u0b41\u0b39\u0b42\u0b30\u0b4d\u0b24\u0b4d\u0b24",
    "calculate": "\u0b17\u0b23\u0b28\u0b3e \u0b15\u0b30\u0b28\u0b4d\u0b24\u0b41",
    "calculating": "\u0b17\u0b23\u0b28\u0b3e \u0b1a\u0b3e\u0b32\u0b3f\u0b1b\u0b3f\u2026",
    "complete": "\u0b38\u0b2e\u0b4d\u0b2a\u0b42\u0b30\u0b4d\u0b23",
    "error": "\u0b24\u0b4d\u0b30\u0b41\u0b1f\u0b3f",
    "state": "\u0b30\u0b3e\u0b1c\u0b4d\u0b5f",
    "latitude": "\u0b05\u0b15\u0b4d\u0b37\u0b3e\u0b02\u0b36",
    "longitude": "\u0b26\u0b4d\u0b30\u0b3e\u0b18\u0b3f\u0b2e\u0b3e",
    "date": "\u0b24\u0b3e\u0b30\u0b3f\u0b16",
    "language": "\u0b2d\u0b3e\u0b37\u0b3e",
    "tithi": "\u0b24\u0b3f\u0b25\u0b3f",
    "nakshatra": "\u0b28\u0b15\u0b4d\u0b37\u0b24\u0b4d\u0b30",
    "yoga": "\u0b5f\u0b4b\u0b17",
    "karana": "\u0b15\u0b30\u0b23",
    "vaar": "\u0b2c\u0b3e\u0b30",
    "pada": "\u0b2a\u0b3e\u0b26",
    "sunrise": "\u0b38\u0b42\u0b30\u0b4d\u0b5f\u0b4b\u0b26\u0b5f",
    "sunset": "\u0b38\u0b42\u0b30\u0b4d\u0b5f\u0b3e\u0b38\u0b4d\u0b24",
    "abhijit": "\u0b05\u0b2d\u0b3f\u0b1c\u0b3f\u0b24 \u0b2e\u0b41\u0b39\u0b42\u0b30\u0b4d\u0b24\u0b4d\u0b24",
    "rahu_kalam": "\u0b30\u0b3e\u0b39\u0b41 \u0b15\u0b3e\u0b33",
    "system": "\u0b2a\u0b26\u0b4d\u0b27\u0b24\u0b3f",
    "choghadiya": "\u0b1a\u0b4c\u0b18\u0b21\u0b3c\u0b3f\u0b5f\u0b3e",
    "gowri": "\u0b17\u0b4c\u0b30\u0b40 \u0b2a\u0b1e\u0b4d\u0b1a\u0b3e\u0b19\u0b4d\u0b17",
    "rashifal": "\u0b26\u0b48\u0b28\u0b3f\u0b15 \u0b30\u0b3e\u0b36\u0b3f\u0b2b\u0b33",
    "lucky": "\u0b36\u0b41\u0b2d",
    "good": "\u0b36\u0b41\u0b2d",
    "bad": "\u0b05\u0b36\u0b41\u0b2d",
}

OR_STATES = {
    "KA": "\u0b15\u0b30\u0b4d\u0b23\u0b3e\u0b1f\u0b15",
    "TN": "\u0b24\u0b2e\u0b3f\u0b33\u0b28\u0b3e\u0b21\u0b41",
    "AP": "\u0b06\u0b28\u0b4d\u0b27\u0b4d\u0b30 \u0b2a\u0b4d\u0b30\u0b26\u0b47\u0b36",
    "TS": "\u0b24\u0b47\u0b32\u0b47\u0b19\u0b4d\u0b17\u0b3e\u0b23\u0b3e",
    "MH": "\u0b2e\u0b39\u0b3e\u0b30\u0b3e\u0b37\u0b4d\u0b1f\u0b4d\u0b30",
    "GJ": "\u0b17\u0b41\u0b1c\u0b30\u0b3e\u0b1f",
    "UP": "\u0b09\u0b24\u0b4d\u0b24\u0b30 \u0b2a\u0b4d\u0b30\u0b26\u0b47\u0b36",
    "RJ": "\u0b30\u0b3e\u0b1c\u0b38\u0b4d\u0b25\u0b3e\u0b28",
    "KL": "\u0b15\u0b47\u0b30\u0b33",
    "WB": "\u0b2a\u0b36\u0b4d\u0b1a\u0b3f\u0b2e\u0b2c\u0b19\u0b4d\u0b17",
    "OD": "\u0b13\u0b21\u0b3c\u0b3f\u0b36\u0b3e",
}

OR_TERMS = {
    "systems": {
        "Purnimanta": "\u0b2a\u0b42\u0b30\u0b4d\u0b23\u0b3f\u0b2e\u0b3e\u0b28\u0b4d\u0b24",
        "Amanta": "\u0b05\u0b2e\u0b3e\u0b28\u0b4d\u0b24",
        "Solar": "\u0b38\u0b4c\u0b30",
        "Standard": "\u0b38\u0b3e\u0b27\u0b3e\u0b30\u0b23",
        "Choghadiya": "\u0b1a\u0b4c\u0b18\u0b21\u0b3c\u0b3f\u0b5f\u0b3e",
        "Gowri": "\u0b17\u0b4c\u0b30\u0b40",
    },
    "tithi": [
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b2a\u0b4d\u0b30\u0b24\u0b3f\u0b2a\u0b26", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b26\u0b4d\u0b71\u0b3f\u0b24\u0b40\u0b5f\u0b3e",
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b24\u0b43\u0b24\u0b40\u0b5f\u0b3e", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b1a\u0b24\u0b41\u0b30\u0b4d\u0b25\u0b40",
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b2a\u0b1e\u0b4d\u0b1a\u0b2e\u0b40", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b37\u0b37\u0b4d\u0b20\u0b40",
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b38\u0b2a\u0b4d\u0b24\u0b2e\u0b40", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b05\u0b37\u0b4d\u0b1f\u0b2e\u0b40",
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b28\u0b2c\u0b2e\u0b40", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b26\u0b36\u0b2e\u0b40",
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b0f\u0b15\u0b3e\u0b26\u0b36\u0b40", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b26\u0b4d\u0b71\u0b3e\u0b26\u0b36\u0b40",
        "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b24\u0b4d\u0b30\u0b5f\u0b4b\u0b26\u0b36\u0b40", "\u0b36\u0b41\u0b15\u0b4d\u0b32 \u0b1a\u0b24\u0b41\u0b30\u0b4d\u0b26\u0b36\u0b40",
        "\u0b2a\u0b42\u0b30\u0b4d\u0b23\u0b3f\u0b2e\u0b3e",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b2a\u0b4d\u0b30\u0b24\u0b3f\u0b2a\u0b26", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b26\u0b4d\u0b71\u0b3f\u0b24\u0b40\u0b5f\u0b3e",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b24\u0b43\u0b24\u0b40\u0b5f\u0b3e", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b1a\u0b24\u0b41\u0b30\u0b4d\u0b25\u0b40",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b2a\u0b1e\u0b4d\u0b1a\u0b2e\u0b40", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b37\u0b37\u0b4d\u0b20\u0b40",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b38\u0b2a\u0b4d\u0b24\u0b2e\u0b40", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b05\u0b37\u0b4d\u0b1f\u0b2e\u0b40",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b28\u0b2c\u0b2e\u0b40", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b26\u0b36\u0b2e\u0b40",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b0f\u0b15\u0b3e\u0b26\u0b36\u0b40", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b26\u0b4d\u0b71\u0b3e\u0b26\u0b36\u0b40",
        "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b24\u0b4d\u0b30\u0b5f\u0b4b\u0b26\u0b36\u0b40", "\u0b15\u0b43\u0b37\u0b4d\u0b23 \u0b1a\u0b24\u0b41\u0b30\u0b4d\u0b26\u0b36\u0b40",
        "\u0b05\u0b2e\u0b3e\u0b2c\u0b3e\u0b38\u0b4d\u0b5f\u0b3e",
    ],
    "nakshatra": [
        "\u0b05\u0b36\u0b4d\u0b71\u0b3f\u0b28\u0b40", "\u0b2d\u0b30\u0b23\u0b40", "\u0b15\u0b43\u0b24\u0b4d\u0b24\u0b3f\u0b15\u0b3e", "\u0b30\u0b4b\u0b39\u0b3f\u0b23\u0b40",
        "\u0b2e\u0b43\u0b17\u0b36\u0b3f\u0b30\u0b3e", "\u0b06\u0b30\u0b4d\u0b26\u0b4d\u0b30\u0b3e", "\u0b2a\u0b41\u0b28\u0b30\u0b4d\u0b2c\u0b38\u0b41", "\u0b2a\u0b41\u0b37\u0b4d\u0b5f",
        "\u0b06\u0b36\u0b4d\u0b32\u0b47\u0b37\u0b3e", "\u0b2e\u0b18\u0b3e", "\u0b2a\u0b42\u0b30\u0b4d\u0b2c\u0b3e \u0b2b\u0b3e\u0b32\u0b4d\u0b17\u0b41\u0b28\u0b40",
        "\u0b09\u0b24\u0b4d\u0b24\u0b30\u0b3e \u0b2b\u0b3e\u0b32\u0b4d\u0b17\u0b41\u0b28\u0b40", "\u0b39\u0b38\u0b4d\u0b24", "\u0b1a\u0b3f\u0b24\u0b4d\u0b30\u0b3e", "\u0b38\u0b4d\u0b71\u0b3e\u0b24\u0b40",
        "\u0b2c\u0b3f\u0b36\u0b3e\u0b16\u0b3e", "\u0b05\u0b28\u0b41\u0b30\u0b3e\u0b27\u0b3e", "\u0b1c\u0b4d\u0b5f\u0b47\u0b37\u0b4d\u0b20\u0b3e", "\u0b2e\u0b42\u0b33",
        "\u0b2a\u0b42\u0b30\u0b4d\u0b2c\u0b3e\u0b37\u0b3e\u0b22\u0b3c\u0b3e", "\u0b09\u0b24\u0b4d\u0b24\u0b30\u0b3e\u0b37\u0b3e\u0b22\u0b3c\u0b3e", "\u0b36\u0b4d\u0b30\u0b2c\u0b23",
        "\u0b27\u0b28\u0b3f\u0b37\u0b4d\u0b20\u0b3e", "\u0b36\u0b24\u0b2d\u0b3f\u0b37\u0b3e", "\u0b2a\u0b42\u0b30\u0b4d\u0b2c\u0b3e \u0b2d\u0b3e\u0b26\u0b4d\u0b30\u0b2a\u0b26",
        "\u0b09\u0b24\u0b4d\u0b24\u0b30\u0b3e \u0b2d\u0b3e\u0b26\u0b4d\u0b30\u0b2a\u0b26", "\u0b30\u0b47\u0b2c\u0b24\u0b40",
    ],
    "yoga": [
        "\u0b2c\u0b3f\u0b37\u0b4d\u0b15\u0b2e\u0b4d\u0b2d", "\u0b2a\u0b4d\u0b30\u0b40\u0b24\u0b3f", "\u0b06\u0b5f\u0b41\u0b37\u0b4d\u0b2e\u0b3e\u0b28", "\u0b38\u0b4c\u0b2d\u0b3e\u0b17\u0b4d\u0b5f",
        "\u0b36\u0b4b\u0b2d\u0b28", "\u0b05\u0b24\u0b3f\u0b17\u0b23\u0b4d\u0b21", "\u0b38\u0b41\u0b15\u0b30\u0b4d\u0b2e", "\u0b27\u0b43\u0b24\u0b3f", "\u0b36\u0b42\u0b33",
        "\u0b17\u0b23\u0b4d\u0b21", "\u0b2c\u0b43\u0b26\u0b4d\u0b27\u0b3f", "\u0b27\u0b4d\u0b30\u0b41\u0b2c", "\u0b2c\u0b4d\u0b5f\u0b3e\u0b18\u0b3e\u0b24", "\u0b39\u0b30\u0b4d\u0b37\u0b23",
        "\u0b2c\u0b1c\u0b4d\u0b30", "\u0b38\u0b3f\u0b26\u0b4d\u0b27\u0b3f", "\u0b2c\u0b4d\u0b5f\u0b24\u0b40\u0b2a\u0b3e\u0b24", "\u0b2c\u0b30\u0b40\u0b5f\u0b3e\u0b28", "\u0b2a\u0b30\u0b3f\u0b18",
        "\u0b36\u0b3f\u0b2c", "\u0b38\u0b3f\u0b26\u0b4d\u0b27", "\u0b38\u0b3e\u0b27\u0b4d\u0b5f", "\u0b36\u0b41\u0b2d", "\u0b36\u0b41\u0b15\u0b4d\u0b32", "\u0b2c\u0b4d\u0b30\u0b39\u0b4d\u0b2e",
        "\u0b07\u0b28\u0b4d\u0b26\u0b4d\u0b30", "\u0b2c\u0b48\u0b27\u0b43\u0b24\u0b3f",
    ],
    "karana": {
        "Kimstughna": "\u0b15\u0b3f\u0b02\u0b38\u0b4d\u0b24\u0b41\u0b18\u0b4d\u0b28", "Bava": "\u0b2c\u0b2c", "Balava": "\u0b2c\u0b3e\u0b32\u0b2c",
        "Kaulava": "\u0b15\u0b4c\u0b32\u0b2c", "Taitila": "\u0b24\u0b48\u0b24\u0b3f\u0b32", "Garaja": "\u0b17\u0b30\u0b1c",
        "Vanija": "\u0b2c\u0b23\u0b3f\u0b1c", "Vishti": "\u0b2c\u0b3f\u0b37\u0b4d\u0b1f\u0b3f", "Shakuni": "\u0b36\u0b15\u0b41\u0b28\u0b3f",
        "Chatushpada": "\u0b1a\u0b24\u0b41\u0b37\u0b4d\u0b2a\u0b3e\u0b26", "Naga": "\u0b28\u0b3e\u0b17",
    },
    "vaar": [
        "\u0b30\u0b2c\u0b3f\u0b2c\u0b3e\u0b30", "\u0b38\u0b4b\u0b2e\u0b2c\u0b3e\u0b30", "\u0b2e\u0b19\u0b4d\u0b17\u0b33\u0b2c\u0b3e\u0b30",
        "\u0b2c\u0b41\u0b27\u0b2c\u0b3e\u0b30", "\u0b17\u0b41\u0b30\u0b41\u0b2c\u0b3e\u0b30", "\u0b36\u0b41\u0b15\u0b4d\u0b30\u0b2c\u0b3e\u0b30", "\u0b36\u0b28\u0b3f\u0b2c\u0b3e\u0b30",
    ],
    "choghadiya": {
        "Udveg": "\u0b09\u0b26\u0b4d\u0b2c\u0b47\u0b17", "Amrut": "\u0b05\u0b2e\u0b43\u0b24", "Kala": "\u0b15\u0b3e\u0b33",
        "Shubh": "\u0b36\u0b41\u0b2d", "Roga": "\u0b30\u0b4b\u0b17", "Chala": "\u0b1a\u0b33", "Labha": "\u0b32\u0b3e\u0b2d",
    },
    "gowri": {
        "Udyoga": "\u0b09\u0b26\u0b4d\u0b5f\u0b4b\u0b17", "Shunya": "\u0b36\u0b42\u0b28\u0b4d\u0b5f", "Labha": "\u0b32\u0b3e\u0b2d",
        "Chal": "\u0b1a\u0b33", "Roga": "\u0b30\u0b4b\u0b17", "Kaal": "\u0b15\u0b3e\u0b33", "Amrita": "\u0b05\u0b2e\u0b43\u0b24", "Shubha": "\u0b36\u0b41\u0b2d",
    },
    "rashi": [
        "\u0b2e\u0b47\u0b37", "\u0b2c\u0b43\u0b37\u0b2d", "\u0b2e\u0b3f\u0b25\u0b41\u0b28", "\u0b15\u0b30\u0b4d\u0b15", "\u0b38\u0b3f\u0b02\u0b39", "\u0b15\u0b28\u0b4d\u0b5f\u0b3e",
        "\u0b24\u0b41\u0b33\u0b3e", "\u0b2c\u0b43\u0b36\u0b4d\u0b1a\u0b3f\u0b15", "\u0b27\u0b28\u0b41", "\u0b2e\u0b15\u0b30", "\u0b15\u0b41\u0b2e\u0b4d\u0b2d", "\u0b2e\u0b40\u0b28",
    ],
    "colors": [
        "\u0b32\u0b3e\u0b32", "\u0b27\u0b33\u0b3e", "\u0b38\u0b2c\u0b41\u0b1c", "\u0b39\u0b33\u0b26\u0b3f\u0b06",
        "\u0b15\u0b2e\u0b33\u0b3e", "\u0b28\u0b40\u0b33", "\u0b17\u0b4b\u0b32\u0b3e\u0b2a\u0b40", "\u0b2c\u0b47\u0b17\u0b41\u0b23\u0b40",
    ],
    "predictions": [
        "\u0b06\u0b1c\u0b3f \u0b2a\u0b4d\u0b30\u0b3e\u0b25\u0b2e\u0b3f\u0b15\u0b24\u0b3e \u0b09\u0b2a\u0b30\u0b47 \u0b27\u0b4d\u0b5f\u0b3e\u0b28 \u0b26\u0b3f\u0b05\u0b28\u0b4d\u0b24\u0b41 \u0b0f\u0b2c\u0b02 \u0b05\u0b28\u0b3e\u0b2c\u0b36\u0b4d\u0b5f\u0b15 \u0b2c\u0b3f\u0b1a\u0b33\u0b28\u0b30\u0b41 \u0b8f\u0b21\u0b3c\u0b3e\u0b28\u0b4d\u0b24\u0b41\u0964",
        "\u0b2c\u0b4d\u0b5f\u0b2c\u0b39\u0b3e\u0b30\u0b3f\u0b15 \u0b26\u0b43\u0b37\u0b4d\u0b1f\u0b3f\u0b15\u0b4b\u0b23\u0b30\u0b47 \u0b06\u0b1c\u0b3f \u0b38\u0b4d\u0b25\u0b3f\u0b30 \u0b09\u0b28\u0b4d\u0b28\u0b24\u0b3f \u0b38\u0b2e\u0b4d\u0b2d\u0b2c\u0964",
        "\u0b5f\u0b4b\u0b17\u0b3e\u0b5f\u0b4b\u0b17 \u0b38\u0b4d\u0b2a\u0b37\u0b4d\u0b1f \u0b30\u0b16\u0b28\u0b4d\u0b24\u0b41 \u0b0f\u0b2c\u0b02 \u0b17\u0b41\u0b30\u0b41\u0b24\u0b4d\u0b71\u0b2a\u0b42\u0b30\u0b4d\u0b23 \u0b28\u0b3f\u0b30\u0b4d\u0b23\u0b5f\u0b15\u0b41 \u0b2a\u0b30\u0b4d\u0b5f\u0b3e\u0b2a\u0b4d\u0b24 \u0b38\u0b2e\u0b5f \u0b26\u0b3f\u0b05\u0b28\u0b4d\u0b24\u0b41\u0964",
        "\u0b38\u0b28\u0b4d\u0b24\u0b41\u0b33\u0b3f\u0b24 \u0b26\u0b3f\u0b28\u0b1a\u0b30\u0b4d\u0b5f\u0b3e \u0b06\u0b1c\u0b3f\u0b30 \u0b26\u0b3e\u0b5f\u0b3f\u0b24\u0b4d\u0b71\u0b15\u0b41 \u0b38\u0b39\u0b1c \u0b15\u0b30\u0b3f\u0b2a\u0b3e\u0b30\u0b47\u0964",
    ],
}


def patch_emit() -> None:
    text = EMIT.read_text(encoding="utf-8")
    if '"or"' not in text.split("LANGUAGES", 1)[1][:200]:
        text = text.replace(
            '"mr": "\\u092e\\u0930\\u093e\\u0920\\u0940",\n}',
            '"mr": "\\u092e\\u0930\\u093e\\u0920\\u0940",\n'
            '    "or": "\\u0b13\\u0b21\\u0b3c\\u0b3f\\u0b06",\n}',
            1,
        )
    text = text.replace('"OD": "hi"', '"OD": "or"')
    if "Noto Sans Oriya" not in text:
        text = text.replace(
            '"te": \'"Noto Sans Telugu", "Noto Serif Telugu", sans-serif\',\n}',
            '"te": \'"Noto Sans Telugu", "Noto Serif Telugu", sans-serif\',\n'
            '    "or": \'"Noto Sans Oriya", "Noto Serif Oriya", sans-serif\',\n}',
            1,
        )
        text = text.replace(
            "family=Noto+Sans+Telugu:wght@400;600;700&display=swap\"",
            "family=Noto+Sans+Telugu:wght@400;600;700&"
            "family=Noto+Sans+Oriya:wght@400;600;700&display=swap\"",
            1,
        )

    # Inject Odia UI + states into JSON blobs if missing
    if '"or":' not in text.split('"ui"', 1)[-1][:5000]:
        ui_blob = json.dumps(OR_UI, ensure_ascii=True)
        states_blob = json.dumps(OR_STATES, ensure_ascii=True)
        text = text.replace(
            '  "mr": {\n    "title": "\\u092a\\u094d\\u0930\\u093e\\u0926\\u0947\\u0936\\u093f\\u0915 \\u092a\\u0902\\u091a\\u093e\\u0902\\u0917",',
            f'  "or": {ui_blob},\n  "mr": {{\n    "title": "\\u092a\\u094d\\u0930\\u093e\\u0926\\u0947\\u0936\\u093f\\u0915 \\u092a\\u0902\\u091a\\u093e\\u0902\\u0917",',
            1,
        )
        # STATES json: add or before closing
        text = text.replace(
            '  "mr": {"KA":"\\u0915\\u0930\\u094d\\u0928\\u093e\\u091f\\u0915"',
            f'  "or": {states_blob},\n  "mr": {{"KA":"\\u0915\\u0930\\u094d\\u0928\\u093e\\u091f\\u0915"',
            1,
        )
    EMIT.write_text(text, encoding="utf-8")
    print("Patched", EMIT)


def patch_rashifal() -> None:
    text = RASHIFAL.read_text(encoding="utf-8")
    text = text.replace(
        'LANGUAGES = {\n    "hi": "हिन्दी",\n    "kn": "ಕನ್ನಡ",\n    "ta": "தமிழ்",\n    "te": "తెలుగు",\n    "mr": "मराठी",\n}',
        'LANGUAGES = {\n'
        '    "hi": "\\u0939\\u093f\\u0928\\u094d\\u0926\\u0940",\n'
        '    "kn": "\\u0c95\\u0ca8\\u0ccd\\u0ca8\\u0ca1",\n'
        '    "ta": "\\u0ba4\\u0bae\\u0bbf\\u0bb4\\u0bcd",\n'
        '    "te": "\\u0c24\\u0c46\\u0c32\\u0c41\\u0c17\\u0c41",\n'
        '    "mr": "\\u092e\\u0930\\u093e\\u0920\\u0940",\n'
        '    "or": "\\u0b13\\u0b21\\u0b3c\\u0b3f\\u0b06",\n'
        '}',
    )
    # If replace failed because of already-unicode text, inject or key
    if '"or"' not in text:
        text = text.replace(
            '"mr": "मराठी",\n}',
            '"mr": "मराठी",\n    "or": "ଓଡ଼ିଆ",\n}',
        )
    text = text.replace('language or "hi"', 'language or "kn"')
    text = text.replace('return "hi"', 'return "kn"')  # avoid Hindi global default
    text = text.replace(
        'if code == "en" or code not in LANGUAGES:\n        return "hi"',
        'if code == "en" or code not in LANGUAGES:\n        return "kn"',
    )
    RASHIFAL.write_text(text, encoding="utf-8")
    print("Patched", RASHIFAL)


def patch_index() -> None:
    text = INDEX.read_text(encoding="utf-8")
    text = text.replace(
        'family=Noto+Sans+Telugu:wght@400;600;700&display=swap',
        'family=Noto+Sans+Telugu:wght@400;600;700&family=Noto+Sans+Oriya:wght@400;600;700&display=swap',
    )
    # Prefer state language; never hard-fallback to Hindi
    text = text.replace(
        'return I.languages[v] ? v : "hi";',
        'return I.languages[v] ? v : (I.stateLang[$("state").value] || "kn");',
    )
    text = text.replace(
        'sel.value = I.languages[cur] ? cur : "hi";',
        'sel.value = I.languages[cur] ? cur : (I.stateLang[$("state").value] || "kn");',
    )
    INDEX.write_text(text, encoding="utf-8")
    print("Patched", INDEX)


def main() -> None:
    data = json.loads(TERMS.read_text(encoding="utf-8"))
    for key, value in OR_TERMS.items():
        data[key]["or"] = value
    assert len(data["tithi"]["or"]) == 30
    assert len(data["nakshatra"]["or"]) == 27
    assert len(data["yoga"]["or"]) == 27
    assert len(data["vaar"]["or"]) == 7
    assert len(data["rashi"]["or"]) == 12
    TERMS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Updated", TERMS)

    patch_emit()
    patch_rashifal()
    patch_index()

    # Rebuild i18n.js via emit script after ensuring emit has or UI
    # Re-run emit by importing after reloading file content carefully
    import importlib.util
    # Manually merge or into emit's runtime by executing patched emit
    spec = importlib.util.spec_from_file_location("emit_regional", EMIT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    try:
        spec.loader.exec_module(mod)
        mod.main()
    except Exception as exc:
        # If emit UI JSON parse fails due to injection, write i18n.js directly
        print("emit failed, writing i18n.js directly:", exc)
        write_i18n_direct(data)


def write_i18n_direct(terms: dict) -> None:
    emit_text = EMIT.read_text(encoding="utf-8")
    # Minimal pack builder
    languages = {
        "hi": "\u0939\u093f\u0928\u094d\u0926\u0940",
        "kn": "\u0c95\u0ca8\u0ccd\u0ca8\u0ca1",
        "ta": "\u0ba4\u0bae\u0bbf\u0bb4\u0bcd",
        "te": "\u0c24\u0c46\u0c32\u0c41\u0c17\u0c41",
        "mr": "\u092e\u0930\u093e\u0920\u0940",
        "or": "\u0b13\u0b21\u0b3c\u0b3f\u0b06",
    }
    state_lang = {
        "KA": "kn", "TN": "ta", "AP": "te", "TS": "te", "MH": "mr",
        "GJ": "hi", "UP": "hi", "RJ": "hi", "KL": "ta", "WB": "hi", "OD": "or",
    }
    fonts = {
        "hi": '"Noto Sans Devanagari", "Tiro Devanagari Hindi", sans-serif',
        "mr": '"Noto Sans Devanagari", "Tiro Devanagari Marathi", sans-serif',
        "kn": '"Noto Sans Kannada", "Noto Serif Kannada", sans-serif',
        "ta": '"Noto Sans Tamil", "Noto Serif Tamil", sans-serif',
        "te": '"Noto Sans Telugu", "Noto Serif Telugu", sans-serif',
        "or": '"Noto Sans Oriya", "Noto Serif Oriya", sans-serif',
    }
    # Pull existing UI/states from current i18n.js if present
    i18n_path = ROOT / "frontend" / "i18n.js"
    existing = {}
    if i18n_path.exists():
        raw = i18n_path.read_text(encoding="utf-8")
        existing = json.loads(raw.replace("window.I18N = ", "").rstrip().rstrip(";"))
    ui = existing.get("ui", {})
    ui["or"] = OR_UI
    states = existing.get("states", {})
    states["or"] = OR_STATES
    pack = {
        "languages": languages,
        "stateLang": state_lang,
        "fonts": fonts,
        "googleFonts": (
            "https://fonts.googleapis.com/css2?"
            "family=Noto+Sans+Devanagari:wght@400;600;700&"
            "family=Noto+Sans+Kannada:wght@400;600;700&"
            "family=Noto+Sans+Tamil:wght@400;600;700&"
            "family=Noto+Sans+Telugu:wght@400;600;700&"
            "family=Noto+Sans+Oriya:wght@400;600;700&display=swap"
        ),
        "ui": ui,
        "states": states,
        **terms,
    }
    i18n_path.write_text("window.I18N = " + json.dumps(pack, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")
    print("Wrote", i18n_path)


if __name__ == "__main__":
    main()
