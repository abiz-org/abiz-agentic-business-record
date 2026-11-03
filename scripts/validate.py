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

ABIZ 1.1, 2026-11-03 location, contact, hours and listing amendment (SPEC
section 4.7): after the schema passes, the validator also checks what JSON
Schema cannot express: every URL is a safe HTTPS URL on a public DNS name;
country, service-area and tax jurisdiction codes are assigned, and region codes
match their country (ISO 3166-2 coverage is partial: assigned subdivision codes
are confirmed only for US, CA and AE, see data/README.md); time
zones are IANA identifiers; opening periods do not overlap (overnight periods
included); location_id, media id and position, tax registrations and review
platforms are unique; a rating is within its scale; and no recent_posts member
appears anywhere, extensions included.

Schema revisions are selected with --revision. 1.0 is the published contract
(schemas/abiz-business-record-v1.schema.json). 1.1 is the latest published specification
(schemas/abiz-business-record-v1.1.schema.json) and is the default. record_version
and the DNS tag v stay abiz1 in both revisions and do not select the schema.
An unsupported revision is reported as unsupported. It is not an invalid signature.
A schema mismatch is not an invalid signature. The nearest REVISION file is used
when --revision is omitted.
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

try:
    from zoneinfo import available_timezones
except ImportError:  # pragma: no cover - Python < 3.9
    available_timezones = None

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_REVISION_1_0 = ROOT / "schemas" / "abiz-business-record-v1.schema.json"
SCHEMA_REVISION_1_1 = ROOT / "schemas" / "abiz-business-record-v1.1.schema.json"
WELL_KNOWN_SCHEMA = ROOT / "schemas" / "abiz-well-known-v1.1.schema.json"
# Default path used by the published 1.1 checks. The earlier 1.0 contract is separate.
SCHEMA = SCHEMA_REVISION_1_1
SUPPORTED_REVISIONS = ("1.0", "1.1")
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
# SPEC.md section 4.7: limits that JSON Schema states but the validator also relies on.
URL_MAX = 2048
DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
PROHIBITED_MEMBERS = frozenset({"recent_posts"})
_TIME_ZONES: frozenset[str] | None = None


def known_time_zones() -> frozenset[str]:
    """IANA time zone names known to this Python (empty when no tz database is installed)."""
    global _TIME_ZONES
    if _TIME_ZONES is None:
        try:
            _TIME_ZONES = frozenset(available_timezones()) if available_timezones else frozenset()
        except Exception:  # pragma: no cover - broken tz installation
            _TIME_ZONES = frozenset()
    return _TIME_ZONES


# Special-use and private-use names (RFC 6761, RFC 6762, RFC 7686, RFC 8375, RFC 9476,
# and the ICANN-reserved .internal). They are never public DNS host names, so a
# published ABIZ 1.1 URL or record host on them fails SPEC sections 3.2 and 4.7.1.
# .example, .test and the other documentation names stay accepted for examples.
NON_PUBLIC_SUFFIXES = ("localhost", "local", "internal", "home.arpa", "onion", "invalid", "alt")


def public_dns_host(value: str) -> bool:
    """True for a safe_host() name that is not a special-use or private-use name."""
    if not safe_host(value):
        return False
    name = value.lower().rstrip(".")
    return not any(name == suffix or name.endswith("." + suffix) for suffix in NON_PUBLIC_SUFFIXES)


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


def check_url(value: str) -> bool:
    """SPEC section 4.7.1: HTTPS, public DNS host, no credentials, at most 2048 characters.

    This is an offline check of the URL text. It cannot tell whether a public name
    resolves to a private address; a consumer that fetches the URL still needs the
    SSRF safeguards of SPEC section 9.
    """
    if not (isinstance(value, str) and len(value) <= URL_MAX and check_https(value)):
        return False
    return public_dns_host(urlsplit(value).hostname or "")


def identity_parts(value: str, revision: str = "1.1"):
    """Normalise a record host (DNS h, identity_host): host lower-cased, path kept as is.

    Published ABIZ 1.1 (SPEC section 3.2): no scheme, query, fragment, port or user
    information, and a public DNS host name. The published 1.0 reference validator
    accepted an explicit :443, so revision "1.0" keeps that behaviour.
    """
    if "://" in value or "?" in value or "#" in value or "@" in value:
        return None
    p = urlsplit("https://" + value)
    if revision != "1.0" and ":" in p.netloc:
        return None  # SPEC 3.2: h carries no port, not even :443
    try:
        port = p.port
    except ValueError:
        return None
    if not p.hostname or not safe_host(p.hostname) or port not in (None, 443):
        return None
    if revision != "1.0" and not public_dns_host(p.hostname):
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


# published ABIZ 1.1 tag-list grammar, SPEC.md section 3.1.1. Optional SP or HTAB may
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
    """Decode a published ABIZ 1.1 p value to 32 raw public-key bytes; reject anything else."""
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


def _reject_lone_surrogates(value: object) -> None:
    if isinstance(value, str):
        if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
            raise ValueError("not I-JSON: lone surrogate in a string (SPEC section 4.6.2)")
    elif isinstance(value, dict):
        for key, item in value.items():
            _reject_lone_surrogates(key)
            _reject_lone_surrogates(item)
    elif isinstance(value, list):
        for item in value:
            _reject_lone_surrogates(item)


def _i_json_float(text: str) -> float:
    number = float(text)
    if math.isinf(number):
        raise ValueError(f"not I-JSON: number {text[:40]} does not fit an IEEE 754 double (SPEC section 4.6.2)")
    return number


def _i_json_int(text: str) -> int:
    number = int(text)
    if abs(number) > 2**53:
        raise ValueError(f"not I-JSON: integer {text[:40]} is outside the exact IEEE 754 double range (SPEC section 4.6.2)")
    return number


def load_json_strict(text: str) -> object:
    """Parse JSON as SPEC section 4.6.2 requires: I-JSON, no duplicate member names.

    Rejects duplicate members, NaN and Infinity, numbers that overflow a double,
    integers beyond 2**53 and lone surrogates, so a malformed record is reported
    as malformed before any signature check, never as a bad signature.
    """
    def bad_constant(name):
        raise ValueError(f"{name} is not valid JSON")
    document = json.loads(text, object_pairs_hook=_reject_duplicate_members, parse_constant=bad_constant,
                          parse_float=_i_json_float, parse_int=_i_json_int)
    _reject_lone_surrogates(document)
    return document


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


def _minutes(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 60 + int(minutes)


def _period_spans(periods: list[dict], day_index: int | None) -> list[tuple[int, int]]:
    """Turn periods into [start, end) minute spans. day_index places them on a weekly timeline."""
    base = 0 if day_index is None else day_index * 1440
    spans = []
    for period in periods:
        opens, closes = _minutes(period["opens"]), _minutes(period["closes"])
        if closes == opens:
            raise ValueError(f"period {period['opens']}-{period['closes']} opens and closes at the same time")
        if closes < opens:
            closes += 1440  # closes the next day (overnight)
        spans.append((base + opens, base + closes))
    return spans


def _overlaps(spans: list[tuple[int, int]], wrap: int | None = None) -> bool:
    spans = sorted(spans)
    if wrap is not None:
        # A Sunday overnight period continues into Monday: compare it with Monday too.
        spans = spans + [(s + wrap, e + wrap) for s, e in spans if s < 1440]
        spans.sort()
    return any(spans[i + 1][0] < spans[i][1] for i in range(len(spans) - 1))


def check_opening_hours(hours: dict, where: str) -> list[str]:
    """SPEC section 4.7.6.4: time zone, ordered and non-overlapping periods, unique days and dates."""
    errors = []
    zones = known_time_zones()
    if zones and hours["time_zone"] not in zones:
        errors.append(f"{where}.time_zone {hours['time_zone']!r} is not an IANA time zone")
    weekly_spans = []
    seen_days = set()
    for entry in hours.get("weekly", []):
        day = entry["day"]
        if day in seen_days:
            errors.append(f"{where}.weekly lists {day} more than once")
            continue
        seen_days.add(day)
        periods = entry["periods"]
        if [p["opens"] for p in periods] != sorted(p["opens"] for p in periods):
            errors.append(f"{where}.weekly {day}: periods are not in order of opens")
        try:
            spans = _period_spans(periods, DAYS.index(day))
        except ValueError as exc:
            errors.append(f"{where}.weekly {day}: {exc}")
            continue
        if _overlaps(spans):
            errors.append(f"{where}.weekly {day}: periods overlap")
        weekly_spans.extend(spans)
    if not any("periods overlap" in e for e in errors) and _overlaps(weekly_spans, wrap=7 * 1440):
        errors.append(f"{where}.weekly: an overnight period overlaps the next day's hours")
    seen_dates = set()
    for entry in hours.get("exceptions", []):
        date = entry["date"]
        if date in seen_dates:
            errors.append(f"{where}.exceptions lists {date} more than once")
            continue
        seen_dates.add(date)
        periods = entry["periods"]
        if [p["opens"] for p in periods] != sorted(p["opens"] for p in periods):
            errors.append(f"{where}.exceptions {date}: periods are not in order of opens")
        try:
            if _overlaps(_period_spans(periods, None)):
                errors.append(f"{where}.exceptions {date}: periods overlap")
        except ValueError as exc:
            errors.append(f"{where}.exceptions {date}: {exc}")
    return errors


def check_region_code(code: str, country: str) -> str | None:
    """Return an error for an ISO 3166-2 code that does not belong to country, else None.

    data/iso3166.json lists subdivisions only for the countries whose business
    key uses them (us, ca, ae); for those the code must be assigned. Elsewhere
    the validator checks the form and the country part only.
    """
    prefix, _, sub = code.partition("-")
    if prefix.lower() != country.lower():
        return f"region code {code!r} does not belong to country {country!r}"
    known = SUBDIVISIONS.get(country.lower())
    if known is not None and sub.lower() not in known:
        return f"region code {code!r} is not an assigned ISO 3166-2 code"
    return None


def _check_code(code: str, where: str) -> list[str]:
    """A country (XX) or subdivision (XX-YYY) code, uppercase in the schema."""
    country = code.split("-", 1)[0]
    try:
        check_country(country)
    except ValueError as exc:
        return [f"{where}: {exc}"]
    if "-" in code:
        problem = check_region_code(code, country)
        if problem:
            return [f"{where}: {problem}"]
    return []


def _find_prohibited(value: object, path: str) -> list[str]:
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PROHIBITED_MEMBERS:
                found.append(f"{path}/{key}: recent_posts is prohibited (SPEC section 4.7.12)")
            found.extend(_find_prohibited(item, f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            found.extend(_find_prohibited(item, f"{path}/{index}"))
    return found


def _check_listing_members(holder: dict, where: str) -> list[str]:
    errors = []
    for name, url in holder.get("social_profiles", {}).items():
        if not check_url(url):
            errors.append(f"{where}social_profiles.{name} must be a safe HTTPS URL")
    for listing in holder.get("external_listings", []):
        if not check_url(listing["public_url"]):
            errors.append(f"{where}external_listings.public_url must be a safe HTTPS URL")
    platforms = set()
    for summary in holder.get("review_summaries", []):
        if summary["rating"] > summary["rating_scale"]:
            errors.append(f"{where}review_summaries: rating {summary['rating']} exceeds rating_scale {summary['rating_scale']}")
        if summary["platform"] in platforms:
            errors.append(f"{where}review_summaries: more than one summary for {summary['platform']}")
        platforms.add(summary["platform"])
        if not check_url(summary["source_url"]):
            errors.append(f"{where}review_summaries.source_url must be a safe HTTPS URL")
    categories = holder.get("categories", {})
    for category in ([categories["primary"]] if "primary" in categories else []) + categories.get("additional", []):
        if category["taxonomy"].startswith("https:") and not check_url(category["taxonomy"]):
            errors.append(f"{where}categories.taxonomy must be a registered token or a safe HTTPS URI")
    return errors


def check_amended_members(record: dict) -> list[str]:
    """SPEC section 4.7 checks that JSON Schema cannot express. Call only after the schema passes."""
    errors = _find_prohibited(record, "$")
    for k in ("website", "logo_url", "mcp_server_url", "blog_url", "rss_url"):
        if k in record and not check_url(record[k]):
            errors.append(f"{k} must be an HTTPS URL with a public DNS hostname")
    for collection in ("services", "links"):
        for item in record.get(collection, []):
            if "url" in item and not check_url(item["url"]):
                errors.append(f"{collection}.url must be a safe HTTPS URL")
    errors.extend(_check_listing_members(record, ""))

    seen_ids = set()
    for index, location in enumerate(record.get("locations", [])):
        where = f"locations/{index}"
        location_id = location.get("location_id")
        if location_id is not None:
            if location_id in seen_ids:
                errors.append(f"{where}: location_id {location_id!r} is not unique")
            seen_ids.add(location_id)
        address = location.get("address")
        if address:
            country = address["country"]["code"]
            try:
                check_country(country)
            except ValueError as exc:
                errors.append(f"{where}.address: {exc}")
            else:
                region = address.get("region", {})
                if "code" in region:
                    problem = check_region_code(region["code"], country)
                    if problem:
                        errors.append(f"{where}.address: {problem}")
        for k in ("website", "logo_url"):
            if k in location and not check_url(location[k]):
                errors.append(f"{where}.{k} must be a safe HTTPS URL")
        errors.extend(_check_listing_members(location, f"{where}."))
        if "opening_hours" in location:
            errors.extend(check_opening_hours(location["opening_hours"], f"{where}.opening_hours"))
        for area in location.get("service_areas", []):
            if "code" in area:
                errors.extend(_check_code(area["code"], f"{where}.service_areas"))
            elif "country" in area:
                errors.extend(_check_code(area["country"], f"{where}.service_areas"))

    seen_tax = set()
    for item in record.get("tax_registrations", []):
        errors.extend(_check_code(item["jurisdiction"], "tax_registrations.jurisdiction"))
        key = (item["jurisdiction"], item["scheme"], item["number"])
        if key in seen_tax:
            errors.append(f"tax_registrations: {item['scheme']} {item['number']} is listed more than once")
        seen_tax.add(key)
        source = item["verification_source"]
        if source.startswith("https:") and not check_url(source):
            errors.append("tax_registrations.verification_source must be a token or a safe HTTPS URL")
        if "verification_expires_at" in item and _instant(item["verification_expires_at"]) <= _instant(item["verified_at"]):
            errors.append("tax_registrations: verification_expires_at must be later than verified_at")

    media_ids, positions = set(), set()
    for item in record.get("media", []):
        if item["id"] in media_ids:
            errors.append(f"media: id {item['id']!r} is not unique")
        media_ids.add(item["id"])
        if "position" in item:
            if item["position"] in positions:
                errors.append(f"media: position {item['position']} is used more than once")
            positions.add(item["position"])
        if not check_url(item["url"]):
            errors.append("media.url must be a safe HTTPS URL")
    return errors


def _instant(value: str):
    from datetime import datetime
    return datetime.fromisoformat(value.replace("Z", "+00:00").replace("z", "+00:00"))


class UnsupportedRevision(Exception):
    """The caller named a schema revision this validator does not implement.

    This is not an invalid signature and not a schema failure.
    """


def infer_revision(path: Path) -> str:
    """Read the nearest REVISION file, walking from the file's directory toward the repository root."""
    current = path.resolve().parent
    root = ROOT.resolve()
    while True:
        marker = current / "REVISION"
        if marker.is_file():
            return marker.read_text(encoding="utf-8").strip()
        if current == root or current.parent == current:
            return "1.1"
        current = current.parent


def dns_tags_v1_0(value: str) -> dict[str, str]:
    """Published ABIZ 1.0 DNS tag parser: compact form, h required, p not a signing key."""
    if any(c.isspace() for c in value) or not value.startswith("v=abiz1;"):
        raise ValueError("DNS assertion must start with v=abiz1; and contain no whitespace")
    tags = {}
    for pair in value.split(";"):
        if "=" not in pair:
            raise ValueError("Every DNS tag must contain '='")
        key, item = pair.split("=", 1)
        if not key or not item or key in tags:
            raise ValueError("Empty or duplicate DNS tag")
        tags[key] = item
    if not tags.get("h"):
        raise ValueError("Missing h= DNS tag")
    if identity_parts(tags["h"], "1.0") is None:
        raise ValueError("Invalid DNS h= host/path")
    return tags


def validate_record_v1_0(record: dict, schema: dict, domain=None, dns_value=None) -> list[str]:
    """Validate a published ABIZ 1.0 business record. There is no record signature."""
    errors = [f"{'/'.join(map(str, e.path)) or '$'}: {e.message}" for e in
              Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(record)]
    if errors:
        return sorted(errors)

    if identity_parts(record["identity-host"], "1.0") is None:
        errors.append("identity-host is not a valid DNS host / optional path")
    for item in record["domains"]:
        if not safe_host(item):
            errors.append(f"invalid declared domain: {item}")
    for key in ("website", "logo-url", "mcp-server-url"):
        if key in record and not check_https(record[key]):
            errors.append(f"{key} must be an HTTPS URL with a public DNS hostname")
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
        owner = domain.lower().rstrip(".")
        if not safe_host(owner):
            errors.append("invalid queried domain")
        elif owner not in {item.lower().rstrip(".") for item in record["domains"]}:
            errors.append("DNS owner domain is missing from record.domains")
    if dns_value:
        try:
            tags = dns_tags_v1_0(dns_value)
            if identity_parts(tags["h"], "1.0") != identity_parts(record["identity-host"], "1.0"):
                errors.append("DNS h and identity-host do not match")
            if "business-key" in record and tags.get("k") != record["business-key"]:
                errors.append("registered business requires matching DNS k")
            if "business-key" not in record and "k" in tags:
                errors.append("DNS k is present for record without a business-key")
        except ValueError as exc:
            errors.append(str(exc))
    return errors


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
    errors.extend(check_amended_members(record))
    try:
        check_country(record["country"])
    except ValueError as exc:
        errors.append(str(exc))
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
    ap.add_argument(
        "--revision",
        help="Business-record schema revision: 1.0 (published) or 1.1 (published). "
        "Default: the nearest REVISION file, otherwise 1.1. record_version and v=abiz1 do not select it. "
        "An unsupported value is not an invalid signature.",
    )
    args = ap.parse_args()
    revision = (args.revision if args.revision is not None else infer_revision(args.json_file)).strip()
    if revision not in SUPPORTED_REVISIONS:
        print(
            f"unsupported schema revision {revision!r}. Supported revisions are 1.0 and 1.1. "
            "This is not an invalid signature.",
            file=sys.stderr,
        )
        return 2
    has_source = bool(args.dns_value) or args.well_known is not None
    if bool(args.domain) != has_source:
        ap.error("--domain needs --dns-value or --well-known, and they need --domain")
    if (args.p_message is None) != (args.p_signature is None):
        ap.error("--p-message and --p-signature must be supplied together")
    if args.p_signature is not None and not has_source:
        ap.error("--p-message and --p-signature require --domain and --dns-value or --well-known")
    if revision == "1.0" and (args.well_known is not None or args.p_value is not None or args.p_signature is not None):
        print(
            "Invalid: --well-known, --p and detached p signatures belong to published ABIZ 1.1, "
            "not the published 1.0 contract. This is not an invalid signature.",
            file=sys.stderr,
        )
        return 1
    try:
        schema_path = SCHEMA_REVISION_1_0 if revision == "1.0" else SCHEMA_REVISION_1_1
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        record_text = args.json_file.read_text(encoding="utf-8")
        record = json.loads(record_text) if revision == "1.0" else load_json_strict(record_text)
        Draft202012Validator.check_schema(schema)
        well_known = None
        if args.well_known is not None:
            raw = args.well_known.read_bytes()
            if len(raw) > WELL_KNOWN_MAX_BYTES:
                raise ValueError(f"well-known file is larger than {WELL_KNOWN_MAX_BYTES} bytes")
            well_known = load_json_strict(raw.decode("utf-8"))
        warnings: list[str] = []
        if revision == "1.0":
            if is_well_known_document(record):
                print(
                    "Invalid: the well-known file is part of published ABIZ 1.1 and is not part of the "
                    "published 1.0 contract. This is not an invalid signature.",
                    file=sys.stderr,
                )
                return 1
            errors = validate_record_v1_0(record, schema, args.domain, args.dns_value)
            if errors:
                for error in errors:
                    print("ERROR:", error, file=sys.stderr)
                return 1
            if args.dns_value:
                print("PASS: ABIZ 1.0 schema + offline DNS/document consistency "
                      "(not a live DNS or registry check; no record signature in ABIZ 1.0)")
            else:
                print("PASS: ABIZ 1.0 record schema and local semantics "
                      "(DNS not checked; no record signature in ABIZ 1.0)")
            return 0
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
