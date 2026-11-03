#!/usr/bin/env python3
"""Offline ABIZ schema + optional DNS/document consistency validator.

This does not perform DNS lookups, registry checks, or HTTPS fetches.

ABIZ 1.1: the DNS p tag is REQUIRED and must be an Ed25519 public key in
standard base64 (44 characters, one "="). A missing p, or any other p value,
including an ABIZ 1.0 hex token or base64url, makes the assertion invalid.
The same tags may instead come from https://<domain>/.well-known/abiz.json
(SPEC section 3.4); a DNS assertion takes precedence over that file.
The key format check uses the standard library.

ABIZ 1.1: every business record carries public_key and signature (SPEC
section 4.6). signature is a PureEd25519 signature over the RFC 8785 (JCS)
canonical form of the record without its signature member; the validator
always verifies it, and checks public_key against the DNS or well-known p
(or a p supplied with --p). Verification needs the cryptography package,
which is in requirements-dev.txt:

    python -m pip install -r requirements-dev.txt
"""
from __future__ import annotations
import argparse
import base64
import binascii
import ipaddress
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from decimal import Decimal
from urllib.parse import urlsplit

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "abiz-business-record-v1.schema.json"
WELL_KNOWN_SCHEMA = ROOT / "schemas" / "abiz-well-known-v1.schema.json"
# SPEC.md section 3.4: the well-known file and its limits.
WELL_KNOWN_PATH = "/.well-known/abiz.json"
WELL_KNOWN_MAX_BYTES = 65_536
WELL_KNOWN_MEMBERS = ("v", "k", "h", "p")
# SPEC.md section 4.5: the format query parameter and its media types.
FORMAT_MEDIA_TYPES = {
    "html": "text/html; charset=utf-8",
    "markdown": "text/markdown; charset=utf-8",
    "json": "application/json",
}
FORMAT_ALIASES = {"md": "markdown"}
ISO3166 = json.loads((ROOT / "data" / "iso3166.json").read_text(encoding="utf-8"))
COUNTRIES = frozenset(ISO3166["countries"])
SUBDIVISIONS = {c: frozenset(v) for c, v in ISO3166["subdivisions"].items()}
# SPEC.md section 4.2.2: countries whose key includes a subdivision.
# "required": always; "provincial": required except for a federal (Corporations Canada) key.
SUBDIVISION_RULE = {"us": "required", "ae": "required", "ca": "provincial"}
# SPEC.md section 4.2.7: assigned codes that ABIZ does not support.
UNSUPPORTED_COUNTRIES = frozenset({"kp"})
REG_NUMBER_RE = re.compile(r"^[A-Za-z0-9]+$")
BUSINESS_KEY_MAX = 128
# Removed by producer normalisation after NFKC (section 4.2.3).
_REG_SEPARATORS = dict.fromkeys(map(ord, "-./\u2010\u2011\u2012\u2013\u2014\u2015\u2212"))
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


def check_country(code: str) -> str:
    """Return the canonical (lowercase) country code, or raise if it is not assigned."""
    if not re.fullmatch(r"[A-Za-z]{2}", code or "") or code.lower() not in COUNTRIES:
        raise ValueError(f"country {code!r} is not an assigned ISO 3166-1 alpha-2 code")
    if code.lower() in UNSUPPORTED_COUNTRIES:
        raise ValueError(f"country {code!r} is not supported by ABIZ (SPEC section 4.2.7)")
    return code.lower()


def parse_business_key(value: str) -> tuple[str, str | None, str]:
    """Split a business key (SPEC section 4.2.1) into canonical (country, subdivision, number).

    Raises ValueError for bad grammar, unassigned codes, or a subdivision that
    section 4.2.2 requires but is missing, or forbids but is present.
    """
    if not isinstance(value, str) or len(value) > BUSINESS_KEY_MAX:
        raise ValueError(f"business key must be at most {BUSINESS_KEY_MAX} characters")
    parts = value.split("-")
    if len(parts) == 2:
        country, subdivision, number = parts[0], None, parts[1]
    elif len(parts) == 3:
        country, subdivision, number = parts
    else:
        raise ValueError("business key must be country-number or country-subdivision-number")
    country = check_country(country)
    if not REG_NUMBER_RE.fullmatch(number):
        raise ValueError("business key registration number must be ASCII letters and digits only")
    rule = SUBDIVISION_RULE.get(country)
    if subdivision is None:
        if rule == "required":
            raise ValueError(f"business key for {country} requires a subdivision code")
    else:
        if not re.fullmatch(r"[A-Za-z0-9]{1,3}", subdivision):
            raise ValueError("business key subdivision must be 1 to 3 ASCII letters or digits")
        if rule is None:
            raise ValueError(f"business key for {country} must not include a subdivision")
        subdivision = subdivision.lower()
        if subdivision not in SUBDIVISIONS[country]:
            raise ValueError(f"{country}-{subdivision} is not a permitted ISO 3166-2 subdivision for a business key")
    return country, subdivision, number.upper()


def canonical_business_key(value: str) -> str:
    country, subdivision, number = parse_business_key(value)
    return "-".join(x for x in (country, subdivision, number) if x)


def normalise_registration_number(raw: str) -> str:
    """Producer normalisation (SPEC section 4.2.3): NFKC, strip separators, uppercase."""
    text = unicodedata.normalize("NFKC", raw)
    text = "".join(ch for ch in text if not ch.isspace()).translate(_REG_SEPARATORS).upper()
    if not REG_NUMBER_RE.fullmatch(text) or not text.isascii():
        raise ValueError("registration number cannot be expressed in ASCII letters and digits")
    return text


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
    if "k" in tags:
        parse_business_key(tags["k"])  # SPEC section 4.2.1
    if "p" not in tags:
        # ABIZ 1.1: p is REQUIRED (SPEC 3.2, 3.3.1).
        raise ValueError("Missing p= DNS tag (p is required, SPEC section 3.2)")
    # p MUST be an Ed25519 public key (SPEC 3.3.2, 3.3.7).
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


# ---------------------------------------------------------------------------
# Record signing, SPEC.md section 4.6: RFC 8785 JSON Canonicalization Scheme.
# ---------------------------------------------------------------------------
SIGNATURE_MEMBER = "signature"
PUBLIC_KEY_MEMBER = "public_key"


def _jcs_number(value: float | int) -> str:
    """Serialise a number as ECMAScript Number.prototype.toString does (RFC 8785 section 3.2.2.3)."""
    if isinstance(value, int):
        if abs(value) > 2**53:
            raise ValueError("JCS: integer outside the IEEE 754 double safe range")
        value = float(value)
    if math.isnan(value) or math.isinf(value):
        raise ValueError("JCS: NaN and Infinity are not valid JSON numbers")
    if value == 0:
        return "0"
    sign = "-" if value < 0 else ""
    # repr() gives the shortest digits that round-trip, as ECMAScript requires.
    digits_tuple = Decimal(repr(abs(value))).as_tuple()
    digits = "".join(map(str, digits_tuple.digits)).rstrip("0") or "0"
    exponent = digits_tuple.exponent + (len(digits_tuple.digits) - len(digits))
    k, n = len(digits), len(digits) + exponent
    if k <= n <= 21:
        text = digits + "0" * (n - k)
    elif 0 < n <= 21:
        text = digits[:n] + "." + digits[n:]
    elif -6 < n <= 0:
        text = "0." + "0" * (-n) + digits
    else:
        e = n - 1
        text = digits[0] + ("." + digits[1:] if k > 1 else "") + "e" + ("+" if e >= 0 else "-") + str(abs(e))
    return sign + text


def _jcs_string(value: str) -> str:
    if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise ValueError("JCS: lone surrogate in string")
    # ensure_ascii=False matches RFC 8785 section 3.2.2.2: only '"', '\' and
    # U+0000..U+001F are escaped, using \b \t \n \f \r or lowercase \u00xx.
    return json.dumps(value, ensure_ascii=False)


def jcs_canonicalize(value: object) -> str:
    """Return the RFC 8785 canonical JSON text of a parsed JSON value."""
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return _jcs_number(value)
    if isinstance(value, str):
        return _jcs_string(value)
    if isinstance(value, (list, tuple)):
        return "[" + ",".join(jcs_canonicalize(v) for v in value) + "]"
    if isinstance(value, dict):
        for key in value:
            if not isinstance(key, str):
                raise ValueError("JCS: object member names must be strings")
        # Members sorted by their UTF-16 code units (RFC 8785 section 3.2.3).
        ordered = sorted(value.items(), key=lambda kv: kv[0].encode("utf-16-be"))
        return "{" + ",".join(_jcs_string(k) + ":" + jcs_canonicalize(v) for k, v in ordered) + "}"
    raise ValueError(f"JCS: unsupported value of type {type(value).__name__}")


def signing_input(record: dict) -> bytes:
    """The octets a record signature covers: UTF-8 JCS of the record without "signature"."""
    if not isinstance(record, dict):
        raise ValueError("business record must be a JSON object")
    unsigned = {k: v for k, v in record.items() if k != SIGNATURE_MEMBER}
    return jcs_canonicalize(unsigned).encode("utf-8")


def sign_record(record: dict, private_key) -> dict:
    """Producer helper: return a copy of record with public_key and signature set.

    private_key is a cryptography Ed25519PrivateKey. Any existing signature is replaced.
    """
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    raw = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    signed = {k: v for k, v in record.items() if k != SIGNATURE_MEMBER}
    signed[PUBLIC_KEY_MEMBER] = base64.b64encode(raw).decode("ascii")
    signed[SIGNATURE_MEMBER] = base64.b64encode(private_key.sign(signing_input(signed))).decode("ascii")
    return signed


def verify_record_signature(record: dict) -> bytes:
    """Verify record["signature"] with record["public_key"] (SPEC section 4.6.4, steps 1 to 4).

    Returns the 32-byte public key. Raises ValueError (not verified) or
    RuntimeError (cryptography is not installed).
    """
    for member in (PUBLIC_KEY_MEMBER, SIGNATURE_MEMBER):
        if not isinstance(record.get(member), str):
            raise ValueError(f"record {member} is missing: the record is not verified")
    key = _decode_standard_base64(record[PUBLIC_KEY_MEMBER], P_KEY_RE, "public_key (Ed25519 public key)", 32)
    signature = _decode_standard_base64(record[SIGNATURE_MEMBER], P_SIG_RE, "signature (Ed25519 signature)", 64)
    try:
        verify_ed25519_signature(key, signing_input(record), signature)
    except ValueError as exc:
        raise ValueError("record signature did not verify with public_key: the record is not verified") from exc
    return key


def check_public_key_matches_p(record: dict, p_value: str) -> None:
    """SPEC section 4.6.4 step 5: public_key MUST equal the pointer's p."""
    decode_ed25519_public_key(p_value)
    if record.get(PUBLIC_KEY_MEMBER) != p_value:
        raise ValueError("record public_key does not match p: the identity claim is rejected")


def _reject_duplicate_members(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError(f"duplicate JSON member {key!r} (SPEC section 4.6.2)")
        out[key] = value
    return out


def load_json_strict(text: str) -> object:
    """Parse JSON as SPEC section 4.6.2 requires: I-JSON, no duplicate member names."""
    def bad_constant(name):
        raise ValueError(f"{name} is not valid JSON")
    return json.loads(text, object_pairs_hook=_reject_duplicate_members, parse_constant=bad_constant)


def well_known_tags(document: object) -> dict[str, str]:
    """Read the tags of a /.well-known/abiz.json document (SPEC section 3.4).

    The document carries the same v, k, h and p as the DNS assertion, one JSON
    string each. Unknown members are ignored. Every value obeys the same rules
    as the DNS tag value, so the result is checked exactly as dns_tags() checks
    a TXT value.
    """
    if not isinstance(document, dict):
        raise ValueError("well-known document must be a JSON object")
    for member in WELL_KNOWN_MEMBERS:
        if member in document and not isinstance(document[member], str):
            raise ValueError(f"well-known member {member!r} must be a string")
    if document.get("v") != "abiz1":
        raise ValueError('well-known document must have "v": "abiz1"')
    for member in ("h", "p"):
        if member not in document:
            raise ValueError(f"well-known document is missing {member!r}")
    parts = ["v=abiz1"]
    for member in ("k", "h", "p"):
        if member not in document:
            continue
        value = document[member]
        if not value or any(c.isspace() or c == ";" for c in value):
            raise ValueError(f"well-known member {member!r} must be a non-empty value without whitespace or ';'")
        parts.append(f"{member}={value}")
    return dns_tags(";".join(parts))


def _same_tags(a: dict[str, str], b: dict[str, str]) -> bool:
    if identity_parts(a["h"]) != identity_parts(b["h"]) or a["p"] != b["p"]:
        return False
    return a.get("k", "").lower() == b.get("k", "").lower()


def resolve_sources(
    txt_values: list[str] | None,
    document: object | None,
    warnings: list[str] | None = None,
) -> tuple[dict[str, str], str]:
    """Apply the precedence rules of SPEC section 3.4.4. Returns (tags, source).

    txt_values is the TXT RRset at _abiz.<domain> (None when the DNS query
    failed); document is the parsed well-known file (None when it is absent).
    source is "dns" or "well-known".
    """
    if txt_values is None:
        raise ValueError("DNS lookup failed: the result is unavailable, not absent (no fallback)")
    assertions = [v for v in txt_values if is_abiz_assertion(v)]
    if len(assertions) > 1:
        raise ValueError("More than one v=abiz1 TXT record: invalid (the well-known file is not used)")
    if assertions:
        tags = dns_tags(assertions[0])  # a malformed DNS assertion is invalid: no fallback
        if document is not None and warnings is not None:
            try:
                if not _same_tags(tags, well_known_tags(document)):
                    warnings.append("well-known file disagrees with the DNS assertion; DNS used")
            except ValueError as exc:
                warnings.append(f"well-known file ignored ({exc}); DNS used")
        return tags, "dns"
    if document is None:
        raise ValueError("No ABIZ assertion: no v=abiz1 TXT record and no well-known file")
    return well_known_tags(document), "well-known"


def select_representation(format_value: str | None, accept: str | None = None) -> str:
    """Reference host behaviour for the record host (SPEC section 4.5).

    An explicit, recognised format parameter wins. Otherwise (absent or not
    recognised) the Accept header decides. The default is HTML.
    """
    if format_value is not None:
        chosen = FORMAT_ALIASES.get(format_value, format_value)
        if chosen in FORMAT_MEDIA_TYPES:
            return chosen
    ranked = []
    for index, item in enumerate((accept or "").split(",")):
        fields = [f.strip() for f in item.split(";")]
        media, q = fields[0].lower(), 1.0
        for f in fields[1:]:
            if f.lower().startswith("q="):
                try:
                    q = float(f[2:])
                except ValueError:
                    q = 0.0
        if q > 0:
            ranked.append((-q, index, media))
    for _, _, media in sorted(ranked):
        if media == "application/json":
            return "json"
        if media == "text/markdown":
            return "markdown"
        if media in ("text/html", "application/xhtml+xml", "*/*", "text/*"):
            return "html"
    return "html"


def validate_well_known(document: object, schema: dict | None = None) -> list[str]:
    """Check a /.well-known/abiz.json document on its own (SPEC section 3.4)."""
    if schema is None:
        schema = json.loads(WELL_KNOWN_SCHEMA.read_text(encoding="utf-8"))
    errors = [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in
              Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document)]
    if errors:
        return sorted(errors)
    try:
        well_known_tags(document)
    except ValueError as exc:
        errors.append(str(exc))
    return errors


def is_well_known_document(document: object) -> bool:
    """A JSON file with "v" and no "record_version" is a well-known document, not a business record."""
    return isinstance(document, dict) and "v" in document and "record_version" not in document


def validate_record(
    record: dict,
    schema: dict,
    domain=None,
    dns_value=None,
    *,
    p_message: bytes | None = None,
    p_signature: str | None = None,
    well_known: object | None = None,
    warnings: list[str] | None = None,
    p_value: str | None = None,
) -> list[str]:
    """Validate a business record. Returns a list of errors (empty when it passes).

    The record signature is always verified (SPEC section 4.6). public_key is
    compared with p from dns_value or well_known, or with p_value when given.
    """
    errors = [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in
              Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)]
    if errors:
        return sorted(errors)

    if identity_parts(record["identity_host"]) is None:
        errors.append("identity_host is not a valid DNS host / optional path")
    for d in record["domains"]:
        if not safe_host(d):
            errors.append(f"invalid declared domain: {d}")
    for k in ("website", "logo_url", "mcp_server_url"):
        if k in record and not check_https(record[k]):
            errors.append(f"{k} must be an HTTPS URL with a public DNS hostname")
    for collection in ("services", "links"):
        for item in record.get(collection, []):
            if "url" in item and not check_https(item["url"]):
                errors.append(f"{collection}.url must be a safe HTTPS URL")
    try:
        check_country(record["country"])
    except ValueError as exc:
        errors.append(str(exc))
    for location in record.get("locations", []):
        try:
            check_country(location["country"])
        except ValueError as exc:
            errors.append(f"locations: {exc}")
    if "business_key" in record:
        try:
            country, _, number = parse_business_key(record["business_key"])
            if country != record["country"].lower():
                errors.append("business_key country does not match country")
            if number != record["registration_number"].upper():
                errors.append("business_key does not match registration_number")
        except ValueError as exc:
            errors.append(str(exc))
    if domain:
        d = domain.lower().rstrip(".")
        if not safe_host(d):
            errors.append("invalid queried domain")
        elif d not in {x.lower().rstrip(".") for x in record["domains"]}:
            errors.append("DNS owner domain is missing from record.domains")
    try:
        verify_record_signature(record)
    except (ValueError, RuntimeError) as exc:
        errors.append(str(exc))
    if p_value is not None:
        try:
            check_public_key_matches_p(record, p_value)
        except ValueError as exc:
            errors.append(str(exc))
    if (p_message is None) != (p_signature is None):
        errors.append("p signature verification needs both a message and a signature")
    if dns_value or well_known is not None:
        try:
            tags, _source = resolve_sources([dns_value] if dns_value else [], well_known, warnings)
            if identity_parts(tags["h"]) != identity_parts(record["identity_host"]):
                errors.append("DNS h and identity_host do not match")
            # k is optional (SPEC section 3.2). When present it must equal business_key,
            # compared case-insensitively (section 4.2.4).
            if "k" in tags:
                if "business_key" not in record:
                    errors.append("DNS k is present for record without a business_key")
                elif tags["k"].lower() != record["business_key"].lower():
                    errors.append("DNS k does not match business_key")
            if record.get(PUBLIC_KEY_MEMBER) != tags["p"]:
                errors.append("record public_key does not match p: the identity claim is rejected")
            if p_message is not None and p_signature is not None:
                check_p_signature(tags, p_message, p_signature)
        except (ValueError, RuntimeError) as exc:
            errors.append(str(exc))
    elif p_signature is not None:
        errors.append("p signature verification requires a DNS assertion or well-known file")
    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("json_file", type=Path)
    ap.add_argument("--domain", help="Domain under which _abiz TXT record is published")
    ap.add_argument("--dns-value", help="Value inside ABIZ TXT record, not the full DNS zone line")
    ap.add_argument(
        "--well-known",
        type=Path,
        help="Local copy of https://<domain>/.well-known/abiz.json (SPEC section 3.4); DNS wins if both are given",
    )
    ap.add_argument(
        "--p",
        dest="p_value",
        help="An Ed25519 p value (44-character standard base64) to compare with the record's public_key, "
        "for example one read from DNS by other means",
    )
    ap.add_argument(
        "--p-message",
        help="UTF-8 message for an optional PureEd25519 check (requires --dns-value and --p-signature)",
    )
    ap.add_argument(
        "--p-signature",
        help="Standard base64 of the 64-byte Ed25519 signature (requires --dns-value and --p-message)",
    )
    args = ap.parse_args()
    has_source = bool(args.dns_value) or args.well_known is not None
    if bool(args.domain) != has_source:
        ap.error("--domain needs --dns-value or --well-known, and they need --domain")
    if (args.p_message is None) != (args.p_signature is None):
        ap.error("--p-message and --p-signature must be supplied together")
    if args.p_signature is not None and not has_source:
        ap.error("--p-message and --p-signature require --domain and --dns-value or --well-known")
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        record = load_json_strict(args.json_file.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        well_known = None
        if args.well_known is not None:
            raw = args.well_known.read_bytes()
            if len(raw) > WELL_KNOWN_MAX_BYTES:
                raise ValueError(f"well-known file is larger than {WELL_KNOWN_MAX_BYTES} bytes")
            well_known = load_json_strict(raw.decode("utf-8"))
        warnings: list[str] = []
        if is_well_known_document(record):
            if has_source or args.p_value is not None:
                ap.error("a well-known document is checked on its own; omit --domain, --dns-value, --well-known and --p")
            errors = validate_well_known(record)
            for error in errors:
                print("ERROR:", error, file=sys.stderr)
            if not errors:
                print("PASS: ABIZ well-known document (/.well-known/abiz.json) schema and tag rules")
            return 1 if errors else 0
        errors = validate_record(
            record,
            schema,
            args.domain,
            args.dns_value,
            p_message=None if args.p_message is None else args.p_message.encode("utf-8"),
            p_signature=args.p_signature,
            well_known=well_known,
            warnings=warnings,
            p_value=args.p_value,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid: {exc}", file=sys.stderr)
        return 1
    for warning in warnings:
        print("WARNING:", warning, file=sys.stderr)
    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 1
    if args.p_signature is not None:
        print("PASS: schema + record signature + offline DNS/document consistency; detached Ed25519 signature matches p")
    elif has_source:
        print("PASS: schema + record signature + offline DNS/document consistency; public_key matches p "
              "(not a live DNS or registry check)")
    elif args.p_value is not None:
        print("PASS: schema + record signature; public_key matches the supplied p (DNS not checked)")
    else:
        print("PASS: ABIZ record schema, local semantics and record signature; "
              "public_key not checked against DNS p, so the identity claim is unconfirmed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
