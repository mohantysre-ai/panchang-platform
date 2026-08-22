"""Safely delete www.sigq.in and iros.sigq.in DNS records; keep apex sigq.in."""
from __future__ import annotations

import base64
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

CERT = Path.home() / ".cloudflared" / "cert.pem"
KEEP = {"sigq.in"}
DELETE = {"www.sigq.in", "iros.sigq.in"}


def load_creds() -> dict:
    raw = CERT.read_text(encoding="utf-8")
    match = re.search(
        r"-----BEGIN ARGO TUNNEL TOKEN-----\s*(.*?)\s*-----END ARGO TUNNEL TOKEN-----",
        raw,
        re.S,
    )
    if not match:
        raise SystemExit("No ARGO TUNNEL TOKEN found in cert.pem")
    blob = re.sub(r"\s+", "", match.group(1))
    pad = "=" * (-len(blob) % 4)
    return json.loads(base64.b64decode(blob + pad))


def api(token: str, method: str, path: str) -> dict:
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4" + path,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main() -> None:
    creds = load_creds()
    zone_id = creds["zoneID"]
    token = creds["apiToken"]

    params = urllib.parse.urlencode({"per_page": 100})
    listing = api(token, "GET", f"/zones/{zone_id}/dns_records?{params}")
    if not listing.get("success"):
        raise SystemExit(f"list failed: {listing.get('errors')}")

    records = listing.get("result", [])
    print(
        "found_records",
        [
            (
                r["name"],
                r["type"],
                (r.get("content") or "")[:48],
            )
            for r in records
        ],
    )

    to_delete = [r for r in records if r.get("name") in DELETE]
    print("will_delete", [r["name"] for r in to_delete])
    print("keeping", sorted(KEEP & {r["name"] for r in records}))

    for rec in to_delete:
        result = api(token, "DELETE", f"/zones/{zone_id}/dns_records/{rec['id']}")
        print(f"deleted {rec['name']} success={result.get('success')}")

    listing2 = api(token, "GET", f"/zones/{zone_id}/dns_records?{params}")
    names = sorted({r["name"] for r in listing2.get("result", [])})
    print("remaining_names", names)

    leftover = DELETE & set(names)
    if leftover:
        raise SystemExit(f"still present after delete: {sorted(leftover)}")
    if "sigq.in" not in names and not any(n == "sigq.in" for n in names):
        # Apex might appear as sigq.in; warn only if missing entirely
        print("WARNING: apex sigq.in not found in remaining DNS names")


if __name__ == "__main__":
    main()
