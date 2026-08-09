"""Download Noto Sans woff2 fonts for all regional scripts (self-host)."""
from __future__ import annotations

import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "frontend" / "assets" / "fonts"
OUT.mkdir(parents=True, exist_ok=True)

# fontsource CDN — reliable woff2 per script
# https://cdn.jsdelivr.net/fontsource/fonts/<family>@5.0.0/<script>-<weight>-normal.woff2
FAMILIES = {
    "devanagari": "noto-sans-devanagari",
    "bengali": "noto-sans-bengali",
    "kannada": "noto-sans-kannada",
    "tamil": "noto-sans-tamil",
    "telugu": "noto-sans-telugu",
    "oriya": "noto-sans-oriya",
    "gurmukhi": "noto-sans-gurmukhi",
    "gujarati": "noto-sans-gujarati",
    "malayalam": "noto-sans-malayalam",
}

WEIGHTS = (400, 500, 600, 700)
UA = "Mozilla/5.0 (compatible; PanchangPlatform/1.0)"


def url_for(family: str, script: str, weight: int) -> str:
    return (
        f"https://cdn.jsdelivr.net/fontsource/fonts/{family}@5.2.5/"
        f"{script}-{weight}-normal.woff2"
    )


def download(url: str, dest: Path) -> bool:
    if dest.exists() and dest.stat().st_size > 1000:
        print("skip", dest.name)
        return True
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
        if len(data) < 1000:
            print("too small", url, len(data))
            return False
        dest.write_bytes(data)
        print("ok", dest.name, len(data))
        return True
    except Exception as e:
        print("fail", url, e)
        return False


def write_css(ok_files: list[tuple[str, str, int]]) -> None:
    # Map script -> CSS family name used in app
    family_name = {
        "devanagari": "NotoSansDevanagari",
        "bengali": "NotoSansBengali",
        "kannada": "NotoSansKannada",
        "tamil": "NotoSansTamil",
        "telugu": "NotoSansTelugu",
        "oriya": "NotoSansOriya",
        "gurmukhi": "NotoSansGurmukhi",
        "gujarati": "NotoSansGujarati",
        "malayalam": "NotoSansMalayalam",
    }
    lines = ["/* Self-hosted regional fonts — no CDN at runtime */", ""]
    for script, _fam, weight in ok_files:
        fname = f"noto-{script}-{weight}.woff2"
        css_fam = family_name[script]
        lines.append("@font-face {")
        lines.append(f"  font-family: '{css_fam}';")
        lines.append(f"  src: url('/assets/fonts/{fname}') format('woff2');")
        lines.append(f"  font-weight: {weight};")
        lines.append("  font-style: normal;")
        lines.append("  font-display: swap;")
        lines.append("}")
        lines.append("")
    css_path = ROOT / "frontend" / "fonts.css"
    css_path.write_text("\n".join(lines), encoding="utf-8")
    print("wrote", css_path)


def main() -> None:
    ok: list[tuple[str, str, int]] = []
    for script, family in FAMILIES.items():
        for weight in WEIGHTS:
            dest = OUT / f"noto-{script}-{weight}.woff2"
            if download(url_for(family, script, weight), dest):
                ok.append((script, family, weight))
    write_css(ok)
    print("done", len(ok), "files")


if __name__ == "__main__":
    main()
