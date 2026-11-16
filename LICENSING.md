# Licensing

Copyright 2026 To.Co Technologies Limited and the ABIZ contributors.

Different parts of this repository are under different licences. The table says which applies where. A licence notice inside a file or directory takes precedence over this table.

| Path | Licence | Full text |
| --- | --- | --- |
| `SPEC.md`, `README.md`, `CHANGELOG.md`, `docs/` | Creative Commons Attribution 4.0 International (CC BY 4.0) | [`LICENSE-docs`](LICENSE-docs) |
| `schemas/` | Apache License 2.0 | [`LICENSE`](LICENSE) |
| `scripts/`, `tests/`, and any other source code or configuration | Apache License 2.0 | [`LICENSE`](LICENSE) |
| `examples/` | CC0 1.0 Universal (public domain dedication) | [`examples/LICENSE`](examples/LICENSE) |
| `data/iso3166.json` | Third-party data, not relicensed. See below | [`data/README.md`](data/README.md) |

SPDX identifiers: `CC-BY-4.0`, `Apache-2.0`, `CC0-1.0`.

## What this means in practice

- **Implementing ABIZ.** You may implement the specification in any software, open or closed, without a fee and without joining anything.
- **Quoting or republishing the specification.** Give credit as "ABIZ — Agentic Business Record Specification, To.Co Technologies Limited and the ABIZ contributors", link to this repository, and say if you changed the text. A modified specification must not be presented as the official ABIZ specification.
- **Schemas and the reference validator.** You may copy, change and ship them under the Apache License 2.0, which includes a patent licence from each contributor for their contribution.
- **Examples.** Copy them into your tests and documentation freely. No attribution is needed.

## Third-party material

`data/iso3166.json` holds country and subdivision codes extracted from the Debian iso-codes data as redistributed by pycountry. That data is distributed under the GNU Lesser General Public License, version 2.1. The licences in the table above do not apply to it and do not change its terms. Its source, version and source hashes are recorded in [`data/README.md`](data/README.md) and in the file itself; see also [`NOTICE`](NOTICE).

## Name

"ABIZ" and the ABIZ logo identify this specification. The licences above do not grant trademark rights. You may say truthfully that your software implements, produces or consumes ABIZ records. You may not use the name or logo in a way that suggests your product is the official specification, or that To.Co Technologies Limited or the ABIZ project endorses it.

## Contributions

Contributions are accepted under the same licences that apply to the files they change. See [`CONTRIBUTING.md`](CONTRIBUTING.md).
