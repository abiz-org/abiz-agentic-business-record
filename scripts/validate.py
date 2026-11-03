#!/usr/bin/env python3
"""Offline ABIZ schema + optional DNS/document consistency validator.

This does not perform DNS lookups, registry checks, or HTTPS fetches.

ABIZ 1.1 (proposed): a DNS p tag, when present, must be an Ed25519 public
key in standard base64 (44 characters, one "="). Any other p value,
including an ABIZ 1.0 hex token or base64url, makes the assertion invalid.
The key format check uses the standard library. Verifying an optional
detached signature (--p-message / --p-signature) imports the optional
cryptography package on demand:

    python -m pip install -r requirements-p-key.txt
"""
from __future__ import annotations
import argparse
import base64
import binascii
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
# 32 raw bytes, standard base64 (RFC 4648 section 4): 43 alphabet chars + one "=".
P_KEY_RE = re.compile(r"^[A-Za-z0-9+/]{43}=$")
# 64-byte Ed25519 signature: 86 alphabet chars + "==".
P_SIG_RE = re.compile(r"^[A-Za-z0-9+/]{86}==$")


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


# ABIZ 1.1 (proposed) tag-list grammar, SPEC.md section 3.1.1. Optional SP or HTAB may
# surround ";" and "=", and may lead or trail the value; one trailing ";" is allowed.
# Tag names and values contain no whitespace. Every valid ABIZ 1.0 value still parses.
WSP = " \t"
RECOGNISED_TAGS = frozenset({"v", "h", "k", "p"})
ASSERTION_START = re.compile(r"^[ \t]*v[ \t]*=[ \t]*abiz1[ \t]*(?:;|$)")


def is_abiz_assertion(value: str) -> bool:
    """True when a TXT value's first tag is v=abiz1 (section 3.1). Used to select the RRset."""
    return bool(ASSERTION_START.match(value))


def dns_tags(value: str) -> dict[str, str]:
    if any(c.isspace() and c not in WSP for c in value):
        raise ValueError("DNS assertion may contain only SP or HTAB as whitespace")
    body = value.strip(WSP)
    if body.endswith(";"):
        body = body[:-1]  # one optional trailing ";"
    tags: dict[str, str] = {}
    for index, raw in enumerate(body.split(";")):
        pair = raw.strip(WSP)
        if "=" not in pair:
            raise ValueError("Every DNS tag must contain '=' (an empty tag or ';;' is invalid)")
        # Split on the first "=" only. A 1.1 p value ends with base64 padding.
        k, v = pair.split("=", 1)
        k, v = k.rstrip(WSP), v.lstrip(WSP)
        if not k or not v:
            raise ValueError("Empty DNS tag name or value")
        if any(c.isspace() for c in k) or any(c.isspace() for c in v):
            raise ValueError("DNS tag names and values must not contain whitespace")
        if index == 0 and (k, v) != ("v", "abiz1"):
            raise ValueError("DNS assertion must start with v=abiz1")
        if k in tags:
            if k in RECOGNISED_TAGS:
                raise ValueError(f"Duplicate DNS tag {k}=")
            continue  # unknown tags are ignored, including repeats
        tags[k] = v
    if not tags.get("h"):
        raise ValueError("Missing h= DNS tag")
    if identity_parts(tags["h"]) is None:
        raise ValueError("Invalid DNS h= host/path")
    if "p" in tags:
        # ABIZ 1.1: p is optional, but when present it MUST be a key (SPEC 3.3.2, 3.3.7).
        decode_ed25519_public_key(tags["p"])
    return tags


def _decode_standard_base64(value: str, pattern: re.Pattern[str], purpose: str, size: int) -> bytes:
    if not pattern.fullmatch(value):
        raise ValueError(
            f"{purpose} must be canonical standard base64 (RFC 4648 section 4) "
            f"of exactly {size} bytes"
        )
    try:
        raw = base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"{purpose} is not canonical standard base64") from exc
    if len(raw) != size or base64.b64encode(raw).decode("ascii") != value:
        raise ValueError(f"{purpose} must decode to exactly {size} bytes")
    return raw


def decode_ed25519_public_key(value: str) -> bytes:
    """Decode an ABIZ 1.1 (proposed) p value to 32 raw public-key bytes; reject anything else."""
    return _decode_standard_base64(value, P_KEY_RE, "p (Ed25519 public key)", 32)


def decode_ed25519_signature(value: str) -> bytes:
    """Decode a detached PureEd25519 signature from standard base64."""
    return _decode_standard_base64(value, P_SIG_RE, "Ed25519 signature", 64)


def verify_ed25519_signature(public_key: bytes, message: bytes, signature: bytes) -> None:
    """Verify a PureEd25519 signature. Imports cryptography only when called."""
    try:
        from cryptography.exceptions import InvalidSignature
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError as exc:
        raise RuntimeError(
            "Ed25519 signature verification requires the optional cryptography package "
            "(python -m pip install -r requirements-p-key.txt)"
        ) from exc
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(signature, message)
    except InvalidSignature as exc:
        raise ValueError("Ed25519 signature did not verify") from exc


def check_p_signature(tags: dict[str, str], message: bytes, signature: str) -> bytes:
    """Verify a detached PureEd25519 signature against the DNS p key."""
    if "p" not in tags:
        raise ValueError("DNS assertion has no p= tag to verify a signature against")
    key = decode_ed25519_public_key(tags["p"])
    verify_ed25519_signature(key, message, decode_ed25519_signature(signature))
    return key


def validate_record(
    record: dict,
    schema: dict,
    domain=None,
    dns_value=None,
    *,
    p_message: bytes | None = None,
    p_signature: str | None = None,
) -> list[str]:
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
    if (p_message is None) != (p_signature is None):
        errors.append("p signature verification needs both a message and a signature")
    if dns_value:
        try:
            tags = dns_tags(dns_value)
            if identity_parts(tags["h"]) != identity_parts(record["identity-host"]):
                errors.append("DNS h and identity-host do not match")
            if "business-key" in record and tags.get("k") != record["business-key"]:
                errors.append("registered business requires matching DNS k")
            if "business-key" not in record and "k" in tags:
                errors.append("DNS k is present for record without a business-key")
            if p_message is not None and p_signature is not None:
                check_p_signature(tags, p_message, p_signature)
        except (ValueError, RuntimeError) as exc:
            errors.append(str(exc))
    elif p_signature is not None:
        errors.append("p signature verification requires a DNS assertion")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json_file", type=Path)
    ap.add_argument("--domain", help="Domain under which _abiz TXT record is published")
    ap.add_argument("--dns-value", help="Value inside ABIZ TXT record, not the full DNS zone line")
    ap.add_argument(
        "--p-message",
        help="UTF-8 message for an optional PureEd25519 check (requires --dns-value and --p-signature)",
    )
    ap.add_argument(
        "--p-signature",
        help="Standard base64 of the 64-byte Ed25519 signature (requires --dns-value and --p-message)",
    )
    args = ap.parse_args()
    if bool(args.domain) != bool(args.dns_value):
        ap.error("--domain and --dns-value must be supplied together for DNS assertion checks")
    if (args.p_message is None) != (args.p_signature is None):
        ap.error("--p-message and --p-signature must be supplied together")
    if args.p_signature is not None and not args.dns_value:
        ap.error("--p-message and --p-signature require --domain and --dns-value")
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        record = json.loads(args.json_file.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = validate_record(
            record,
            schema,
            args.domain,
            args.dns_value,
            p_message=None if args.p_message is None else args.p_message.encode("utf-8"),
            p_signature=args.p_signature,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 1
    if args.p_signature is not None:
        print("PASS: schema + offline DNS/document consistency; Ed25519 signature matches p")
    elif args.dns_value:
        print("PASS: schema + offline DNS/document consistency (not a live DNS or registry check)")
    else:
        print("PASS: ABIZ record schema and local semantics (DNS not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
