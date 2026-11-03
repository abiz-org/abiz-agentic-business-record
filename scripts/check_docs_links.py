#!/usr/bin/env python3
"""Check the navigation of the ABIZ country guides.

Standard library only. Run from anywhere:

    python scripts/check_docs_links.py

It fails (exit status 1) when:

- a regional directory under docs/countries/ has no index.md;
- a country guide (.md) in a region is not linked from that region's index,
  or is linked more than once;
- a country link in an index points to a file that does not exist;
- the country table in an index is not in alphabetical order;
- a region is missing from docs/countries/README.md or the root README.md;
- a regional index does not link back to ../README.md;
- a page has more or fewer than one H1 heading;
- a relative Markdown link in README.md, docs/countries/README.md or a
  regional index does not resolve (including #anchors into Markdown files).

Links to http(s) and mailto URLs are not checked.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]

REGIONS = {
    "africa": "Africa",
    "asia": "Asia",
    "europe": "Europe",
    "north-america": "North America",
    "oceania": "Oceania",
    "south-america": "South America",
}

LINK_RE = re.compile(r"(?<!!)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN_RE = re.compile(r"`[^`]*`")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def prose_lines(text: str):
    """Yield (line_number, line) outside fenced code blocks, with code spans removed."""
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield number, CODE_SPAN_RE.sub("", line)


def links(text: str):
    for number, line in prose_lines(text):
        for match in LINK_RE.finditer(line):
            yield number, match.group(1), match.group(2)


def headings(text: str):
    for _, line in prose_lines(text):
        match = HEADING_RE.match(line)
        if match:
            yield len(match.group(1)), match.group(2)


def github_slug(heading: str) -> str:
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", heading)  # keep link text only
    text = text.replace("`", "").strip().lower()
    text = "".join(ch for ch in text if ch.isalnum() or ch in " -_")
    return text.replace(" ", "-")


def anchors(path: Path) -> set[str]:
    seen: dict[str, int] = {}
    result = set()
    for _, title in headings(path.read_text(encoding="utf-8")):
        slug = github_slug(title)
        if slug in seen:
            seen[slug] += 1
            slug = f"{slug}-{seen[slug]}"
        else:
            seen[slug] = 0
        result.add(slug)
    return result


def sort_key(name: str) -> str:
    decomposed = unicodedata.normalize("NFKD", name)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).casefold()


def is_external(target: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I))


def check_relative_links(path: Path, root: Path, errors: list[str]) -> None:
    rel = path.relative_to(root)
    for number, _, target in links(path.read_text(encoding="utf-8")):
        if is_external(target):
            continue
        file_part, _, fragment = target.partition("#")
        dest = path if not file_part else (path.parent / unquote(file_part)).resolve()
        if not dest.exists():
            errors.append(f"{rel}:{number}: link target does not exist: {target}")
            continue
        if fragment and dest.is_file() and dest.suffix == ".md":
            if unquote(fragment).lower() not in anchors(dest):
                errors.append(f"{rel}:{number}: anchor not found: {target}")


def check_single_h1(path: Path, root: Path, errors: list[str]) -> None:
    count = sum(1 for level, _ in headings(path.read_text(encoding="utf-8")) if level == 1)
    if count != 1:
        errors.append(f"{path.relative_to(root)}: expected exactly one H1 heading, found {count}")


def check_region_list(path: Path, root: Path, prefix: str, errors: list[str]) -> None:
    targets = {target for _, _, target in links(path.read_text(encoding="utf-8"))}
    for slug, name in REGIONS.items():
        if f"{prefix}{slug}/index.md" not in targets:
            errors.append(f"{path.relative_to(root)}: missing link to {name} ({prefix}{slug}/index.md)")


def check_region(region_dir: Path, root: Path, errors: list[str]) -> None:
    index = region_dir / "index.md"
    rel_dir = region_dir.relative_to(root)
    if not index.is_file():
        errors.append(f"{rel_dir}: missing index.md")
        return
    text = index.read_text(encoding="utf-8")
    guides = {p.name for p in region_dir.glob("*.md") if p.name != "index.md"}

    linked: dict[str, int] = {}
    table_names: list[str] = []
    back_link = False
    for number, label, target in links(text):
        if target == "../README.md":
            back_link = True
        if is_external(target) or "/" in target or not target.endswith(".md") or target == "index.md":
            continue
        linked[target] = linked.get(target, 0) + 1
        if not (region_dir / target).is_file():
            errors.append(f"{rel_dir}/index.md:{number}: country link points to a missing file: {target}")

    for _, line in prose_lines(text):
        if line.startswith("|") and re.search(r"\]\([^)/]+\.md\)", line):
            table_names.append(line.strip("|").split("|")[0].strip())

    for name in sorted(guides - set(linked)):
        errors.append(f"{rel_dir}/index.md: country guide not linked: {name}")
    for name, count in sorted(linked.items()):
        if count > 1:
            errors.append(f"{rel_dir}/index.md: country guide linked {count} times: {name}")
    keys = [sort_key(n) for n in table_names]
    if keys != sorted(keys):
        errors.append(f"{rel_dir}/index.md: country table is not in alphabetical order")
    if not back_link:
        errors.append(f"{rel_dir}/index.md: no link back to ../README.md")
    check_single_h1(index, root, errors)
    check_relative_links(index, root, errors)


def run(root: Path) -> list[str]:
    errors: list[str] = []
    countries = root / "docs" / "countries"
    for slug in REGIONS:
        if not (countries / slug).is_dir():
            errors.append(f"docs/countries/{slug}: regional directory is missing")
    region_dirs = sorted(p for p in countries.iterdir() if p.is_dir()) if countries.is_dir() else []
    for region_dir in region_dirs:
        check_region(region_dir, root, errors)

    central = countries / "README.md"
    if not central.is_file():
        errors.append("docs/countries/README.md: missing")
    else:
        check_region_list(central, root, "", errors)
        check_single_h1(central, root, errors)
        check_relative_links(central, root, errors)

    readme = root / "README.md"
    check_region_list(readme, root, "docs/countries/", errors)
    if "docs/countries/README.md" not in {t for _, _, t in links(readme.read_text(encoding="utf-8"))}:
        errors.append("README.md: missing link to docs/countries/README.md")
    check_single_h1(readme, root, errors)
    check_relative_links(readme, root, errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT, help="repository root (default: this checkout)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    errors = run(root)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(f"{len(errors)} documentation navigation problem(s) found.", file=sys.stderr)
        return 1
    total = sum(len([p for p in (root / "docs/countries" / s).glob("*.md") if p.name != "index.md"]) for s in REGIONS)
    print(f"OK: {len(REGIONS)} regions, {total} country guides, all navigation links resolve.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
