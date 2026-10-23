#!/usr/bin/env python3
"""Offline ABIZ schema + optional DNS/document consistency validator.

This does not perform DNS lookups, registry checks, or HTTPS fetches.
"""
from __future__ import annotations
import argparse
import ipaddress
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "abiz-business-record-v1.schema.json"
HOST = re.compile(r"^[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")


def safe_host(value: str) -> bool:
    value = value.lower().rstrip(".")
    if not HOST.fullmatch(value) or ".." in value or len(value) > 253:
        return False
    if any(len(label) > 63 or label.startswith("-") or label.endswith("-") for label in value.split(".")):
        return False
    if "." not in value or value in ("localhost",):
        return False
    try:
        ipaddress.ip_address(value)
        return False  # host must be DNS name, not an IP literal
    except ValueError:
        return True


def check_https(value: str) -> bool:
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and bool(parsed.hostname) and
                safe_host(parsed.hostname or "") and
                parsed.username is None and parsed.password is None and
                parsed.fragment == "" and parsed.port in (None, 443))
    except ValueError:
        return False


def identity_parts(value: str):
    if "://" in value or "?" in value or "#" in value or "@" in value:
        return None
    p = urlsplit("https://" + value)
    if not p.hostname or not safe_host(p.hostname) or p.port not in (None, 443):
        return None
    if p.path and any(seg in (".", "..") for seg in p.path.split("/")):
        return None
    return p.hostname.lower().rstrip(".") + (p.path or "")


def dns_tags(value: str) -> dict[str, str]:
    if any(c.isspace() for c in value) or not value.startswith("v=abiz1;"):
        raise ValueError("DNS assertion must start with v=abiz1; and contain no whitespace")
    tags = {}
    for pair in value.split(";"):
        if "=" not in pair:
            raise ValueError("Every DNS tag must contain '='")
        k, v = pair.split("=", 1)
        if not k or not v or k in tags:
            raise ValueError("Empty or duplicate DNS tag")
        tags[k] = v
    if not tags.get("h"):
        raise ValueError("Missing h= DNS tag")
    if identity_parts(tags["h"]) is None:
        raise ValueError("Invalid DNS h= host/path")
    return tags


def validate_record(record: dict, schema: dict, domain=None, dns_value=None) -> list[str]:
    errors = [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in
              Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)]
    if errors:
        return sorted(errors)

    if identity_parts(record["identity-host"]) is None:
        errors.append("identity-host is not a valid DNS host / optional path")
    for d in record["domains"]:
        if not safe_host(d):
            errors.append(f"invalid declared domain: {d}")
    for k in ("website", "logo-url", "mcp-server-url"):
        if k in record and not check_https(record[k]):
            errors.append(f"{k} must be an HTTPS URL with a public DNS hostname")
    for collection in ("services", "links"):
        for item in record.get(collection, []):
            if "url" in item and not check_https(item["url"]):
                errors.append(f"{collection}.url must be a safe HTTPS URL")
    if "business-key" in record:
        prefix = record["country"].lower() + "-"
        if not record["business-key"].startswith(prefix):
            errors.append("business-key country does not match country")
        if record["business-key"] != prefix + record["registration-number"]:
            errors.append("business-key does not match registration-number")
    if domain:
        d = domain.lower().rstrip(".")
        if not safe_host(d):
            errors.append("invalid queried domain")
        elif d not in {x.lower().rstrip(".") for x in record["domains"]}:
            errors.append("DNS owner domain is missing from record.domains")
    if dns_value:
        try:
            tags = dns_tags(dns_value)
            if identity_parts(tags["h"]) != identity_parts(record["identity-host"]):
                errors.append("DNS h and identity-host do not match")
            if "business-key" in record and tags.get("k") != record["business-key"]:
                errors.append("registered business requires matching DNS k")
            if "business-key" not in record and "k" in tags:
                errors.append("DNS k is present for record without a business-key")
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json_file", type=Path)
    ap.add_argument("--domain", help="Domain under which _abiz TXT record is published")
    ap.add_argument("--dns-value", help="Value inside ABIZ TXT record, not the full DNS zone line")
    args = ap.parse_args()
    if bool(args.domain) != bool(args.dns_value):
        ap.error("--domain and --dns-value must be supplied together for DNS assertion checks")
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        record = json.loads(args.json_file.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = validate_record(record, schema, args.domain, args.dns_value)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 1
    if args.dns_value:
        print("PASS: schema + offline DNS/document consistency (not a live DNS or registry check)")
    else:
        print("PASS: ABIZ record schema and local semantics (DNS not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
