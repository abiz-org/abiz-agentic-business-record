#!/usr/bin/env python3
"""Rebuild data/iso3166.json from a pinned pycountry wheel.

    python -m pip download --no-deps pycountry==26.2.16
    python scripts/build_iso3166.py pycountry-26.2.16-py3-none-any.whl

pycountry redistributes the Debian iso-codes data (LGPL-2.1). Only the codes are
extracted: every assigned ISO 3166-1 alpha-2 code, and the ISO 3166-2 codes of the
countries in SPEC.md section 4.2.2 that use a subdivision.
"""
from __future__ import annotations
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYCOUNTRY_VERSION = "26.2.16"
# SPEC.md section 4.2.2. US territories with their own alpha-2 code (PR, GU, VI,
# AS, MP) and US-UM are excluded; they use their own country code.
SUBDIVISION_COUNTRIES = {
    "us": {"types": {"State", "District"}},
    "ca": {"types": {"Province", "Territory"}},
    "ae": {"types": {"Emirate"}},
}


def main(wheel: str) -> None:
    with zipfile.ZipFile(wheel) as z:
        raw1 = z.read("pycountry/databases/iso3166-1.json")
        raw2 = z.read("pycountry/databases/iso3166-2.json")
    countries = sorted(e["alpha_2"].lower() for e in json.loads(raw1)["3166-1"])
    subdivisions = {}
    for country, rule in SUBDIVISION_COUNTRIES.items():
        subdivisions[country] = sorted(
            e["code"].split("-", 1)[1].lower()
            for e in json.loads(raw2)["3166-2"]
            if e["code"].lower().startswith(country + "-") and e["type"] in rule["types"]
        )
    out = {
        "source": f"pycountry {PYCOUNTRY_VERSION} (Debian iso-codes data), https://pypi.org/project/pycountry/{PYCOUNTRY_VERSION}/",
        "licence": "Codes extracted from iso-codes, LGPL-2.1; see data/README.md",
        "iso3166-1.json-sha256": hashlib.sha256(raw1).hexdigest(),
        "iso3166-2.json-sha256": hashlib.sha256(raw2).hexdigest(),
        "countries": countries,
        "subdivisions": subdivisions,
    }
    (ROOT / "data" / "iso3166.json").write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
