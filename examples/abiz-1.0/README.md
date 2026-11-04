# ABIZ 1.0 examples

These records follow the ABIZ 1.0 schema. They use hyphenated member names and have no `public_key` or `signature`. `record-version` is `abiz1`.

Validate them with the 1.0 schema:

```sh
python scripts/validate.py examples/abiz-1.0/registered-us.json --revision 1.0
```

The nearest `REVISION` file is `1.0`, so `--revision` can be omitted for files in this directory. They fail the ABIZ 1.1 schema. That failure is a schema mismatch, not an invalid signature.

ABIZ 1.1, the latest published specification, requires `p`.
