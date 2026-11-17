#!/usr/bin/env python3
"""Build Bahmni's six-level Uganda address hierarchy from the pinned UBOS gazetteer."""
import argparse
import csv
import hashlib
import io
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://pub-91f97fd178b74b919b3e8f204d254970.r2.dev/downloads/administrative-units/2026-11-13/gazetteer.csv"
EXPECTED_SHA256 = "effbc52af0a37985acb205f3217f10014c32a8c9d6fca920ee942d38bea14b5c"
EXPECTED_ROWS = 71679
FIELDS = (
    "district_name",
    "county_name",
    "sub_county_name",
    "parish_name",
    "village_name",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Destination CSV (without a header)")
    args = parser.parse_args()

    request = urllib.request.Request(
        SOURCE_URL,
        headers={"User-Agent": "Bwongo-Digital-Solutions-ClinicConfig/1.0"},
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        payload = response.read()

    actual_sha = hashlib.sha256(payload).hexdigest()
    if actual_sha != EXPECTED_SHA256:
        raise SystemExit(
            f"UBOS gazetteer checksum mismatch: expected {EXPECTED_SHA256}, got {actual_sha}"
        )

    text = payload.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text, newline=""))
    required = {"village_id", *FIELDS}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit(f"UBOS gazetteer is missing required columns: {sorted(missing)}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    rows = 0
    with output_path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
        for line_number, record in enumerate(reader, start=2):
            values = [record.get(field, "").strip() for field in FIELDS]
            if any(not value for value in values):
                raise SystemExit(
                    f"Missing administrative ancestor at gazetteer row {line_number}: {values}"
                )
            path = ("Uganda", *values)
            if path in seen:
                raise SystemExit(f"Duplicate address path at gazetteer row {line_number}: {path}")
            seen.add(path)
            writer.writerow(path)
            rows += 1

    if rows != EXPECTED_ROWS:
        raise SystemExit(f"Unexpected UBOS village count: expected {EXPECTED_ROWS}, got {rows}")

    generated = output_path.read_text(encoding="utf-8")
    for forbidden in ("Himachal Pradesh", "Kangra", "India"):
        if forbidden.casefold() in generated.casefold():
            raise SystemExit(f"Non-Ugandan address value detected: {forbidden}")

    print(
        f"Generated {rows:,} Uganda address paths from UBOS gazetteer "
        f"(SHA-256 {actual_sha}) -> {output_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
