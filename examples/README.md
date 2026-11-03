# Examples

Each example identifies the business-record revision it demonstrates. `record_version` is `abiz1` in both revisions. The revision is the schema, not the DNS wire tag.

| Path | Revision | Schema |
| --- | --- | --- |
| `examples/abiz-1.0/` | Published ABIZ 1.0 | `schemas/abiz-business-record-v1.schema.json` |
| Every other JSON example under `examples/` | Proposed ABIZ 1.1 | `schemas/abiz-business-record-v1.1.schema.json` |

`examples/REVISION` contains `1.1`. `examples/abiz-1.0/REVISION` contains `1.0`. The reference validator reads the nearest `REVISION` file. `--revision` overrides it. An unsupported revision is reported as such, and is not an invalid signature.

ABIZ 1.1 is proposed. It is not a formal publication. The 1.0 examples are the records from the published 1.0 specification.
