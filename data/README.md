# Bundled ISO 3166 codes

`iso3166.json` lists every assigned ISO 3166-1 alpha-2 country code, and the ISO 3166-2 subdivision codes of the countries that SPEC.md section 4.2.2 says use a subdivision in the business key (`us`, `ca`, `ae`). Codes are lowercase, the canonical ABIZ form.

- Source: pycountry 26.2.16 (https://pypi.org/project/pycountry/26.2.16/), which redistributes the Debian iso-codes data (https://salsa.debian.org/iso-codes-team/iso-codes). The SHA-256 of the two source files is recorded in `iso3166.json`.
- Licence: iso-codes and pycountry are distributed under the GNU Lesser General Public License, version 2.1. This file contains only the codes, extracted unmodified apart from lowercasing. The codes themselves are maintained by the ISO 3166 Maintenance Agency.
- Regenerate with `scripts/build_iso3166.py` (instructions in the script). A change to the list is a change to what the validator accepts, so record it in CHANGELOG.md.
