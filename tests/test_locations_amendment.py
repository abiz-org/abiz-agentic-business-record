"""ABIZ 1.1 (proposed), 2026-11-03 amendment: location, contact, hours and listing fields (SPEC section 4.7)."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from validate import (
    check_opening_hours,
    jcs_canonicalize,
    sign_record,
    validate_record,
    verify_record_signature,
)

SCHEMA = json.loads((ROOT / "schemas" / "abiz-business-record-v1.1.schema.json").read_text())
EXAMPLES = ROOT / "examples" / "locations-and-listings"
INVALID = EXAMPLES / "invalid"
TEST_KEY = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
MULTI = json.loads((EXAMPLES / "multi-location-gb.json").read_text())


def resign(record):
    return sign_record(record, TEST_KEY)


def assertions():
    out = {}
    for line in (EXAMPLES / "dns-assertions.txt").read_text().splitlines():
        if line and not line.startswith("#"):
            name, value = line.split(" ", 1)
            out[name] = value
    return out


def errors_for(record):
    return validate_record(resign(record), SCHEMA)


def hours(weekly=None, exceptions=None, tz="Europe/London"):
    h = {"time_zone": tz}
    if weekly is not None:
        h["weekly"] = [{"day": d, "periods": [{"opens": o, "closes": c} for o, c in p]} for d, p in weekly]
    if exceptions is not None:
        h["exceptions"] = [{"date": d, "periods": [{"opens": o, "closes": c} for o, c in p]} for d, p in exceptions]
    return h


def with_hours(h):
    r = copy.deepcopy(MULTI)
    r["locations"][1]["opening_hours"] = h
    return r


class ExampleSetTests(unittest.TestCase):
    """Section 9.3 example set: every record is valid, signed, and bound to its DNS p."""

    EXPECTED = {
        "minimal-registered-gb.json", "online-only-de.json", "multi-location-gb.json",
        "private-trading-address-au.json", "service-area-us.json", "24-hour-location-ca.json",
        "temporary-closure-ie.json", "verified-vat-fr.json", "vat-withdrawn-fr.json",
        "public-listings-gb.json", "blog-rss-only-nz.json",
    }

    def test_every_case_has_an_example(self):
        self.assertEqual({p.name for p in EXAMPLES.glob("*.json")}, self.EXPECTED)
        self.assertEqual(set(assertions()), self.EXPECTED)

    def test_examples_validate_against_their_dns_assertion(self):
        for name, dns in assertions().items():
            record = json.loads((EXAMPLES / name).read_text())
            with self.subTest(example=name):
                self.assertEqual(validate_record(record, SCHEMA), [])
                self.assertEqual(validate_record(record, SCHEMA, record["domains"][0], dns), [])
                self.assertNotEqual(record["public_key"], resign(record)["public_key"])

    def test_examples_are_signed_with_distinct_keys_except_one_business(self):
        keys = {}
        for name, dns in assertions().items():
            keys.setdefault(dns.rsplit("p=", 1)[1], set()).add(name)
        shared = [names for names in keys.values() if len(names) > 1]
        self.assertEqual(shared, [{"verified-vat-fr.json", "vat-withdrawn-fr.json"}])

    def test_vat_withdrawal_removes_the_claim_and_re_signs(self):
        verified = json.loads((EXAMPLES / "verified-vat-fr.json").read_text())
        withdrawn = json.loads((EXAMPLES / "vat-withdrawn-fr.json").read_text())
        self.assertIn("tax_registrations", verified)
        self.assertNotIn("tax_registrations", withdrawn)
        self.assertGreater(withdrawn["last_updated"], verified["last_updated"])
        self.assertNotEqual(verified["signature"], withdrawn["signature"])

    def test_examples_name_no_provider_except_as_platform_values(self):
        for path in EXAMPLES.glob("*.json"):
            text = path.read_text().lower()
            with self.subTest(example=path.name):
                for host in ("google.com", "apple.com", "goo.gl"):
                    self.assertNotIn(host, text)


class NegativeExampleTests(unittest.TestCase):
    def test_each_invalid_example_fails_for_its_rule(self):
        expected = json.loads((INVALID / "expected-errors.json").read_text())
        self.assertEqual({p.name for p in INVALID.glob("*.json")} - {"expected-errors.json"}, set(expected))
        for name, fragment in expected.items():
            record = json.loads((INVALID / name).read_text())
            with self.subTest(example=name):
                errors = validate_record(record, SCHEMA)
                self.assertTrue(errors)
                self.assertTrue(any(fragment in e for e in errors), errors)

    def test_invalid_examples_other_than_bad_signature_are_validly_signed(self):
        for path in INVALID.glob("*.json"):
            if path.name in ("expected-errors.json", "bad-signature.json"):
                continue
            with self.subTest(example=path.name):
                verify_record_signature(json.loads(path.read_text()))


class RenameAndRemovalTests(unittest.TestCase):
    def test_email_and_phone_replace_contact_members(self):
        self.assertEqual(errors_for(MULTI), [])
        for old, new in (("contact_email", "email"), ("contact_phone", "phone")):
            r = copy.deepcopy(MULTI)
            r[old] = r.pop(new)
            with self.subTest(member=old):
                self.assertTrue(any(f"'{old}' was unexpected" in e for e in errors_for(r)))

    def test_root_opening_hours_is_removed(self):
        r = copy.deepcopy(MULTI)
        r["opening_hours"] = ["Mo-Fr 09:00-17:00"]
        self.assertTrue(errors_for(r))
        r["opening_hours"] = MULTI["locations"][1]["opening_hours"]
        self.assertTrue(errors_for(r))

    def test_flat_location_members_are_removed(self):
        for member, value in (("city", "Bristol"), ("country", "gb"), ("street", "1 Example Street"),
                              ("postal_code", "BS1 4XX"), ("region", "England")):
            r = copy.deepcopy(MULTI)
            r["locations"][1][member] = value
            with self.subTest(member=member):
                self.assertTrue(errors_for(r))

    def test_location_needs_no_address(self):
        r = copy.deepcopy(MULTI)
        r["locations"] = [{"location_id": "online", "kind": "other", "website": "https://cliftoncycles.example/shop"}]
        self.assertEqual(errors_for(r), [])
        r["locations"] = [{}]
        self.assertTrue(errors_for(r))

    def test_address_rules(self):
        cases = {
            "street without locality": {"street_lines": ["1 Example Street"], "country": {"code": "GB"}},
            "no country": {"locality": "Bristol"},
            "lowercase country": {"locality": "Bristol", "country": {"code": "gb"}},
            "unassigned country": {"locality": "Bristol", "country": {"code": "ZZ"}},
            "kp": {"locality": "Pyongyang", "country": {"code": "KP"}},
            "four street lines": {"street_lines": ["a", "b", "c", "d"], "locality": "Bristol", "country": {"code": "GB"}},
            "empty region": {"locality": "Bristol", "region": {}, "country": {"code": "GB"}},
            "region of another country": {"locality": "Bristol", "region": {"code": "US-OR"}, "country": {"code": "GB"}},
            "unassigned US state": {"locality": "Springfield", "region": {"code": "US-ZZ"}, "country": {"code": "US"}},
        }
        for label, address in cases.items():
            r = copy.deepcopy(MULTI)
            r["locations"][2]["address"] = address
            with self.subTest(case=label):
                self.assertTrue(errors_for(r))
        r = copy.deepcopy(MULTI)
        r["locations"][2]["address"] = {"region": {"name": "Wales"}, "country": {"code": "GB", "name": "Y Deyrnas Unedig"}}
        self.assertEqual(errors_for(r), [])

    def test_duplicate_location_id_rejected(self):
        r = copy.deepcopy(MULTI)
        r["locations"][2]["location_id"] = r["locations"][1]["location_id"]
        self.assertTrue(any("not unique" in e for e in errors_for(r)))
        r["locations"][2]["location_id"] = "Cardiff Bay"
        self.assertTrue(errors_for(r))


class GeoTests(unittest.TestCase):
    def test_geo_needs_both_coordinates(self):
        for missing in ("latitude", "longitude"):
            r = copy.deepcopy(MULTI)
            del r["locations"][1]["geo"][missing]
            with self.subTest(missing=missing):
                self.assertTrue(any(f"'{missing}' is a required property" in e for e in errors_for(r)))

    def test_geo_ranges(self):
        for geo in ({"latitude": 91, "longitude": 0}, {"latitude": 0, "longitude": -180.5},
                    {"latitude": "51.4", "longitude": -2.6}, {"latitude": 51.4, "longitude": -2.6, "altitude": 10}):
            r = copy.deepcopy(MULTI)
            r["locations"][1]["geo"] = geo
            with self.subTest(geo=geo):
                self.assertTrue(errors_for(r))

    def test_geo_needs_a_published_street(self):
        r = copy.deepcopy(MULTI)
        del r["locations"][1]["address"]["street_lines"]
        self.assertTrue(errors_for(r))
        r = copy.deepcopy(MULTI)
        del r["locations"][1]["address"]
        self.assertTrue(errors_for(r))

    def test_numbers_canonicalise_per_rfc_8785(self):
        self.assertEqual(jcs_canonicalize({"latitude": 51.4550, "rating": 5.0, "count": 83}),
                         '{"count":83,"latitude":51.455,"rating":5}')
        self.assertEqual(jcs_canonicalize([-2.6175, 0.000001, 1e21]), "[-2.6175,0.000001,1e+21]")


class OpeningHoursTests(unittest.TestCase):
    def test_valid_shapes(self):
        cases = {
            "split": hours([("monday", [("08:00", "12:30"), ("13:30", "18:00")])]),
            "adjacent periods": hours([("monday", [("08:00", "12:30"), ("12:30", "18:00")])]),
            "four periods": hours([("monday", [("06:00", "07:00"), ("08:00", "09:00"), ("10:00", "11:00"), ("12:00", "13:00")])]),
            "overnight": hours([("friday", [("19:00", "02:00")]), ("saturday", [("10:00", "18:00")])]),
            "24 hours every day": hours([(d, [("00:00", "24:00")]) for d in
                                         ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")]),
            "closed day": hours([("sunday", [])]),
            "exceptions only": hours(exceptions=[("2026-12-25", []), ("2026-12-24", [("09:00", "13:00")])]),
            "sunday overnight before a late monday": hours([("sunday", [("20:00", "02:00")]), ("monday", [("09:00", "17:00")])]),
        }
        for label, h in cases.items():
            with self.subTest(case=label):
                self.assertEqual(errors_for(with_hours(h)), [])
        appointment = {"time_zone": "Australia/Melbourne", "appointment_only": True}
        self.assertEqual(errors_for(with_hours(appointment)), [])

    def test_overlapping_hours_rejected(self):
        cases = {
            "same day": hours([("monday", [("08:00", "13:00"), ("12:30", "18:00")])]),
            "same period twice": hours([("monday", [("08:00", "13:00"), ("08:00", "13:00")])]),
            "contained": hours([("monday", [("08:00", "18:00"), ("09:00", "10:00")])]),
            "overnight into next day": hours([("friday", [("19:00", "11:00")]), ("saturday", [("10:00", "18:00")])]),
            "sunday overnight into monday": hours([("sunday", [("20:00", "09:30")]), ("monday", [("09:00", "17:00")])]),
            "24 hours plus a period": hours([("monday", [("00:00", "24:00"), ("09:00", "10:00")])]),
            "exception": hours(exceptions=[("2026-12-24", [("09:00", "13:00"), ("12:00", "15:00")])]),
        }
        for label, h in cases.items():
            with self.subTest(case=label):
                errors = errors_for(with_hours(h))
                self.assertTrue(any("overlap" in e or "order" in e for e in errors), errors)

    def test_other_hours_rules(self):
        cases = {
            "no time zone": {"weekly": [{"day": "monday", "periods": []}]},
            "unknown time zone": hours([("monday", [])], tz="Europe/Bristol"),
            "nothing but a time zone": {"time_zone": "Europe/London"},
            "day twice": hours([("monday", []), ("monday", [("09:00", "17:00")])]),
            "date twice": hours(exceptions=[("2026-12-25", []), ("2026-12-25", [])]),
            "five periods": hours([("monday", [("01:00", "02:00"), ("03:00", "04:00"), ("05:00", "06:00"),
                                               ("07:00", "08:00"), ("09:00", "10:00")])]),
            "out of order": hours([("monday", [("13:30", "18:00"), ("08:00", "12:30")])]),
            "opens equals closes": hours([("monday", [("09:00", "09:00")])]),
            "opens 24:00": hours([("monday", [("24:00", "02:00")])]),
            "bad time": hours([("monday", [("9:00", "17:00")])]),
            "capitalised day": {"time_zone": "Europe/London", "weekly": [{"day": "Monday", "periods": []}]},
            "bad date": hours(exceptions=[("2026-02-30", [])]),
        }
        for label, h in cases.items():
            with self.subTest(case=label):
                self.assertTrue(errors_for(with_hours(h)))

    def test_exception_limit(self):
        import datetime
        start = datetime.date(2027, 1, 1)
        dates = [((start + datetime.timedelta(days=i)).isoformat(), []) for i in range(101)]
        self.assertTrue(errors_for(with_hours(hours(exceptions=dates))))
        self.assertEqual(errors_for(with_hours(hours(exceptions=dates[:100]))), [])

    def test_check_opening_hours_directly(self):
        self.assertEqual(check_opening_hours(hours([("monday", [("22:00", "02:00")])]), "h"), [])
        self.assertTrue(check_opening_hours(hours([("monday", [("22:00", "02:00")]),
                                                   ("tuesday", [("01:00", "05:00")])]), "h"))


class MemberTests(unittest.TestCase):
    def test_recent_posts_rejected_everywhere(self):
        posts = [{"title": "Winter hours", "url": "https://cliftoncycles.example/news/winter"}]
        r = copy.deepcopy(MULTI)
        r["recent_posts"] = posts
        self.assertTrue(any("recent_posts" in e for e in errors_for(r)))
        r = copy.deepcopy(MULTI)
        r["locations"][1]["recent_posts"] = posts
        self.assertTrue(any("recent_posts" in e for e in errors_for(r)))
        r = copy.deepcopy(MULTI)
        r["extensions"] = {"example.cliftoncycles": {"feed": {"recent_posts": posts}}}
        self.assertEqual(errors_for(r), ["$/extensions/example.cliftoncycles/feed/recent_posts: recent_posts is prohibited (SPEC section 4.7.12)"])
        r["extensions"] = {"example.cliftoncycles": {"feed_url": "https://cliftoncycles.example/rss.xml"}}
        self.assertEqual(errors_for(r), [])

    def test_blog_and_rss_urls(self):
        r = copy.deepcopy(MULTI)
        r["blog_url"], r["rss_url"] = "https://cliftoncycles.example/news", "https://cliftoncycles.example/news/rss.xml"
        self.assertEqual(errors_for(r), [])
        for bad in ("http://cliftoncycles.example/news", "https://user:secret@cliftoncycles.example/news",
                    "https://cliftoncycles.example:8443/news", "https://192.0.2.1/news", "https://cliftoncycles.example/news#top",
                    "https://cliftoncycles.example/" + "a" * 2030, "ftp://cliftoncycles.example/news", ""):
            with self.subTest(url=bad[:60]):
                self.assertTrue(errors_for({**r, "rss_url": bad}))

    def test_url_length_limit_applies_to_services_and_links(self):
        long = "https://cliftoncycles.example/" + "a" * 2019
        self.assertEqual(len(long), 2049)
        r = copy.deepcopy(MULTI)
        r["services"] = [{"name": "Servicing", "url": long}]
        self.assertTrue(errors_for(r))
        r["services"] = [{"name": "Servicing", "url": long[:-1]}]
        self.assertEqual(errors_for(r), [])

    def test_media_cap(self):
        def item(i):
            return {"id": f"photo-{i}", "kind": "image", "url": f"https://cliftoncycles.example/{i}.jpg",
                    "content_type": "image/jpeg", "alt_text": f"Photo {i}", "position": i}
        r = copy.deepcopy(MULTI)
        r["media"] = [item(i) for i in range(1, 11)]
        self.assertEqual(errors_for(r), [])
        r["media"].append({**item(11), "position": 10})
        r["media"][-1].pop("position")
        self.assertTrue(any("too long" in e for e in errors_for(r)))

    def test_media_items(self):
        base = {"id": "shop", "kind": "image", "url": "https://cliftoncycles.example/shop.jpg", "content_type": "image/jpeg"}
        good = [{**base, "alt_text": "The shop front"}, {**base, "decorative": True},
                {"id": "tour", "kind": "video", "url": "https://cliftoncycles.example/tour.mp4", "content_type": "video/mp4"}]
        for media in good:
            with self.subTest(good=media):
                self.assertEqual(errors_for({**MULTI, "media": [media]}), [])
        bad = [base, {**base, "decorative": True, "alt_text": "x"}, {**base, "decorative": False},
               {**base, "alt_text": "x", "content_type": "video/mp4"}, {**base, "alt_text": "x", "content_type": "text/html"},
               {**base, "alt_text": "x", "kind": "banner"}, {**base, "alt_text": "x", "exif": {}},
               {**good[2], "width": 1920}, {**good[2], "content_type": "image/png"}, {**good[2], "alt_text": "A tour"},
               {**base, "alt_text": "x", "position": 11}]
        for media in bad:
            with self.subTest(bad=media):
                self.assertTrue(errors_for({**MULTI, "media": [media]}))
        dup = [{**base, "alt_text": "a"}, {**base, "alt_text": "b"}]
        self.assertTrue(any("not unique" in e for e in errors_for({**MULTI, "media": dup})))
        same_position = [{**base, "alt_text": "a", "position": 1}, {**base, "id": "two", "alt_text": "b", "position": 1}]
        self.assertTrue(errors_for({**MULTI, "media": same_position}))
        r = copy.deepcopy(MULTI)
        r["locations"][1]["media"] = [good[0]]
        self.assertTrue(errors_for(r))

    def test_tax_registration_required_members(self):
        item = {"jurisdiction": "GB", "scheme": "vat", "number": "GB123456789",
                "verified_at": "2026-11-02T10:00:00Z", "verification_source": "hmrc_vat"}
        self.assertEqual(errors_for({**MULTI, "tax_registrations": [item]}), [])
        for member in ("jurisdiction", "scheme", "number", "verified_at", "verification_source"):
            partial = {k: v for k, v in item.items() if k != member}
            with self.subTest(missing=member):
                errors = errors_for({**MULTI, "tax_registrations": [partial]})
                self.assertTrue(any(f"'{member}' is a required property" in e for e in errors), errors)

    def test_tax_registration_values(self):
        item = {"jurisdiction": "GB", "scheme": "vat", "number": "GB123456789",
                "verified_at": "2026-11-02T10:00:00Z", "verification_source": "hmrc_vat"}
        good = [{**item, "jurisdiction": "US-WA", "scheme": "sales_tax"},
                {**item, "verification_source": "https://ec.europa.eu/taxation_customs/vies/"},
                {**item, "verification_expires_at": "2027-02-02T10:00:00Z"}]
        for tax in good:
            with self.subTest(good=tax):
                self.assertEqual(errors_for({**MULTI, "tax_registrations": [tax]}), [])
        bad = [{**item, "scheme": "income_tax"}, {**item, "jurisdiction": "gb"}, {**item, "jurisdiction": "EU"},
               {**item, "jurisdiction": "KP"}, {**item, "jurisdiction": "US-ZZ"}, {**item, "number": ""},
               {**item, "number": "x" * 101}, {**item, "verified_at": "yesterday"},
               {**item, "verification_source": "http://example.com/check"}, {**item, "verification_source": "HMRC VAT"},
               {**item, "verification_expires_at": "2026-11-01T10:00:00Z"}, {**item, "status": "verified"}]
        for tax in bad:
            with self.subTest(bad=tax):
                self.assertTrue(errors_for({**MULTI, "tax_registrations": [tax]}))
        self.assertTrue(errors_for({**MULTI, "tax_registrations": [item, item]}))
        many = [{**item, "number": f"GB{n:09d}"} for n in range(21)]
        self.assertTrue(errors_for({**MULTI, "tax_registrations": many}))
        self.assertEqual(errors_for({**MULTI, "tax_registrations": many[:20]}), [])
        self.assertTrue(errors_for({**MULTI, "tax_registrations": []}))

    def test_social_profiles(self):
        r = copy.deepcopy(MULTI)
        r["social_profiles"] = {"x": "https://x.example/cliftoncycles", "linkedin": "https://linkedin.example/company/cliftoncycles"}
        self.assertEqual(errors_for(r), [])
        for bad in ({"mastodon": "https://social.example/@clifton"}, {"x": "http://x.example/cliftoncycles"}, {},
                    {"X": "https://x.example/cliftoncycles"}):
            with self.subTest(bad=bad):
                self.assertTrue(errors_for({**r, "social_profiles": bad}))

    def test_categories(self):
        cat = {"taxonomy": "uk_sic_2007", "id": "47640", "name": "Retail sale of sports goods"}
        good = [{"primary": cat}, {"additional": [cat]},
                {"primary": {"taxonomy": "https://categories.example/v1", "id": "bicycle_shop"}}]
        for c in good:
            with self.subTest(good=c):
                self.assertEqual(errors_for({**MULTI, "categories": c}), [])
        bad = [{}, {"primary": {"taxonomy": "uk_sic_2007"}}, {"primary": {"taxonomy": "my_own", "id": "1"}},
               {"primary": {"taxonomy": "http://categories.example/v1", "id": "1"}}, {"primary": {"id": "1", "name": "Shop"}},
               {"additional": [cat] * 10}]
        for c in bad:
            with self.subTest(bad=c):
                self.assertTrue(errors_for({**MULTI, "categories": c}))

    def test_service_areas(self):
        good = [{"code": "GB"}, {"code": "GB-WLS"}, {"postal_code": "CF10", "country": "GB"},
                {"center": {"latitude": 51.48, "longitude": -3.18}, "radius_m": 25000}]
        r = copy.deepcopy(MULTI)
        r["locations"][2]["service_areas"] = good
        self.assertEqual(errors_for(r), [])
        bad = [{"code": "gb"}, {"code": "ZZ"}, {"code": "KP"}, {"code": "US-ZZ"}, {"postal_code": "CF10"},
               {"center": {"latitude": 51.48, "longitude": -3.18}}, {"center": {"latitude": 51.48, "longitude": -3.18}, "radius_m": 0},
               {"center": {"latitude": 51.48, "longitude": -3.18}, "radius_m": 500001},
               {"type": "Polygon", "coordinates": []}, {"code": "GB", "postal_code": "CF10", "country": "GB"}, {"place_id": "abc"}]
        for area in bad:
            r["locations"][2]["service_areas"] = [area]
            with self.subTest(bad=area):
                self.assertTrue(errors_for(r))

    def test_review_summaries(self):
        summary = {"platform": "google_business_profile", "rating": 4.6, "rating_scale": 5, "review_count": 83,
                   "source_url": "https://listings.example.com/clifton", "observed_at": "2026-11-03T10:00:00Z"}
        self.assertEqual(errors_for({**MULTI, "review_summaries": [summary, {**summary, "platform": "com.example.maps"}]}), [])
        bad = [{**summary, "rating": 5.1}, {**summary, "rating": -1}, {**summary, "review_count": 1.5},
               {**summary, "platform": "Google"}, {k: v for k, v in summary.items() if k != "observed_at"},
               {**summary, "reviews": [{"author": "A. Person", "text": "Great"}]}, {**summary, "source_url": "http://x.example"}]
        for item in bad:
            with self.subTest(bad=item):
                self.assertTrue(errors_for({**MULTI, "review_summaries": [item]}))
        self.assertTrue(any("more than one summary" in e for e in errors_for({**MULTI, "review_summaries": [summary, summary]})))

    def test_external_listings(self):
        listing = {"platform": "apple_maps", "public_url": "https://listings.example.com/apple/clifton"}
        r = copy.deepcopy(MULTI)
        r["locations"][1]["external_listings"] = [listing, {**listing, "platform": "google_business_profile",
                                                            "external_id": "abc", "claimed_by_business": True,
                                                            "observed_at": "2026-11-03T10:00:00Z"}]
        self.assertEqual(errors_for(r), [])
        for bad in ({"platform": "apple_maps"}, {**listing, "access_token": "x"}, {**listing, "public_url": "http://x.example"},
                    {**listing, "claimed_by_business": "yes"}):
            r["locations"][1]["external_listings"] = [bad]
            with self.subTest(bad=bad):
                self.assertTrue(errors_for(r))
        self.assertTrue(errors_for({**MULTI, "external_listings": [listing]}))

    def test_operational_status(self):
        for status in ("open", "temporarily_closed", "permanently_closed", "unknown"):
            r = copy.deepcopy(MULTI)
            r["operational_status"] = status
            r["locations"][1]["operational_status"] = status
            self.assertEqual(errors_for(r), [])
        self.assertTrue(errors_for({**MULTI, "operational_status": "closed"}))

    def test_location_values_are_not_inherited(self):
        # A location with no phone has none, whatever the business-level phone is.
        cardiff = MULTI["locations"][2]
        self.assertNotIn("email", cardiff)
        self.assertIn("email", MULTI)
        clifton = MULTI["locations"][1]
        self.assertNotEqual(clifton["phone"], MULTI["phone"])


class SignatureTests(unittest.TestCase):
    def test_new_members_are_covered_by_the_signature(self):
        for path in list(EXAMPLES.glob("*.json")):
            record = json.loads(path.read_text())
            verify_record_signature(record)
            for key in record:
                if key in ("signature", "public_key"):
                    continue
                tampered = copy.deepcopy(record)
                tampered[key] = "changed" if isinstance(record[key], str) else None
                with self.subTest(example=path.name, member=key), self.assertRaises(ValueError):
                    verify_record_signature(tampered)

    def test_changing_hours_needs_a_new_signature(self):
        tampered = copy.deepcopy(MULTI)
        tampered["locations"][1]["opening_hours"]["weekly"][0]["periods"][0]["opens"] = "08:30"
        self.assertTrue(any("did not verify" in e for e in validate_record(tampered, SCHEMA)))
        self.assertEqual(errors_for(tampered), [])


if __name__ == "__main__":
    unittest.main()


class CountryGuideTests(unittest.TestCase):
    """Every ABIZ record in the country guides, SPEC.md and README.md is valid under the amendment."""

    def test_guide_records_validate_and_match_their_p(self):
        import re
        paths = sorted((ROOT / "docs").rglob("*.md")) + [ROOT / "SPEC.md", ROOT / "README.md"]
        count = 0
        for path in paths:
            text = path.read_text(encoding="utf-8")
            keys = set()
            for block in re.findall(r"```json\n(.*?)```", text, re.S):
                try:
                    record = json.loads(block)
                except ValueError:
                    continue
                if not (isinstance(record, dict) and record.get("record_version") == "abiz1"):
                    continue
                count += 1
                keys.add(record["public_key"])
                with self.subTest(path=str(path.relative_to(ROOT)), record=record.get("identity_host")):
                    self.assertEqual(validate_record(record, SCHEMA), [])
            if keys and path.parent.parent.name == "countries":
                for p in re.findall(r"\bp=([A-Za-z0-9+/]{43}=)", text):
                    with self.subTest(path=path.name, p=p):
                        self.assertIn(p, keys)
        self.assertGreater(count, 190)
