"""Restore www/iros DNS and add calendar.sigq.in for the iros-desk tunnel."""
from __future__ import annotations

import base64
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

CERT = Path.home() / ".cloudflared" / "cert.pem"
TUNNEL_ID = "c953e8f3-2809-4986-9153-edc30190f53a"
TUNNEL_TARGET = f"{TUNNEL_ID}.cfargotunnel.com"
DESIRED = ("calendar.sigq.in", "sigq.in", "www.sigq.in", "iros.sigq.in")


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


def api(token: str, method: str, path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4" + path,
        data=data,
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

    existing = {r["name"]: r for r in listing.get("result", [])}
    print("before", sorted(existing))

    for name in DESIRED:
        if name in existing:
            rec = existing[name]
            if rec.get("type") == "CNAME" and rec.get("content") == TUNNEL_TARGET:
                print(f"ok {name}")
                continue
            print(f"update {name}")
            result = api(
                token,
                "PUT",
                f"/zones/{zone_id}/dns_records/{rec['id']}",
                {
                    "type": "CNAME",
                    "name": name,
                    "content": TUNNEL_TARGET,
                    "proxied": True,
                    "ttl": 1,
                },
            )
            print(f"  success={result.get('success')}")
        else:
            print(f"create {name}")
            result = api(
                token,
                "POST",
                f"/zones/{zone_id}/dns_records",
                {
                    "type": "CNAME",
                    "name": name,
                    "content": TUNNEL_TARGET,
                    "proxied": True,
                    "ttl": 1,
                },
            )
            print(f"  success={result.get('success')} errors={result.get('errors')}")

    listing2 = api(token, "GET", f"/zones/{zone_id}/dns_records?{params}")
    names = sorted({r["name"] for r in listing2.get("result", [])})
    print("after", names)
    missing = [n for n in DESIRED if n not in names]
    if missing:
        raise SystemExit(f"missing after upsert: {missing}")


if __name__ == "__main__":
    main()
