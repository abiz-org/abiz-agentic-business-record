# Published ABIZ 1.0 examples

These records demonstrate the published ABIZ 1.0 contract. They use hyphenated member names and have no `public_key` or `signature`. `record-version` is `abiz1`.

Validate them with the 1.0 schema:

```sh
python scripts/validate.py examples/abiz-1.0/registered-us.json --revision 1.0
```

The nearest `REVISION` file is `1.0`, so `--revision` can be omitted for files in this directory. They fail the proposed 1.1 schema. That failure is a schema mismatch, not an invalid signature.

Historical note: in ABIZ 1.0 the DNS `p` tag was optional and was not a signing key. ABIZ 1.1, which is still a proposal, requires `p`.
