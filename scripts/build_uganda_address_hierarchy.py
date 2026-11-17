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
EXPECTED_SOURCE_ROWS = 71679
FIELDS = (
    "district_name",
    "county_name",
    "sub_county_name",
    "parish_name",
    "village_name",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="Destination hierarchy file (without a header)")
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

    reader = csv.DictReader(io.StringIO(payload.decode("utf-8-sig"), newline=""))
    required = {"village_id", *FIELDS}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit(f"UBOS gazetteer is missing required columns: {sorted(missing)}")

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    seen = set()
    source_rows = 0
    written_rows = 0
    duplicate_paths = 0
    normalized_quotes = 0
    with output_path.open("w", encoding="utf-8", newline="") as output:
        # Address Hierarchy splits on a regex delimiter, not a quote-aware CSV parser.
        # Use a pipe delimiter and reject characters that would break its path parser.
        writer = csv.writer(
            output,
            delimiter="|",
            quoting=csv.QUOTE_NONE,
            escapechar="\\",
            lineterminator="\n",
        )
        for line_number, record in enumerate(reader, start=2):
            source_rows += 1
            raw_values = [record.get(field, "").strip() for field in FIELDS]
            normalized_quotes += sum(value.count(chr(34)) for value in raw_values)
            values = [value.replace(chr(34), "") for value in raw_values]
            if any(not value for value in values):
                raise SystemExit(
                    f"Missing administrative ancestor at gazetteer row {line_number}: {values}"
                )
            if any("|" in value for value in values):
                raise SystemExit(
                    f"Unsupported pipe delimiter in UBOS location name at row {line_number}: {values}"
                )
            path = ("Uganda", *values)
            # Some UBOS records have different source IDs but the same visible path.
            # Keep one entry per distinct parent/name path for the hierarchy tree.
            if path in seen:
                duplicate_paths += 1
                continue
            seen.add(path)
            writer.writerow(path)
            written_rows += 1

    if source_rows != EXPECTED_SOURCE_ROWS:
        raise SystemExit(
            f"Unexpected UBOS source row count: expected {EXPECTED_SOURCE_ROWS}, got {source_rows}"
        )
    if written_rows < 70000 or written_rows > EXPECTED_SOURCE_ROWS:
        raise SystemExit(f"Unexpected number of unique address paths: {written_rows}")
    if duplicate_paths > EXPECTED_SOURCE_ROWS * 0.01:
        raise SystemExit(f"Too many duplicate address paths to safely deduplicate: {duplicate_paths}")

    # Validate complete hierarchy fields, not substrings. A substring check
    # falsely rejects legitimate Ugandan place names containing words such as
    # "India" as part of a longer name.
    forbidden_values = {"himachal pradesh", "kangra", "india"}
    with output_path.open(encoding="utf-8", newline="") as generated_file:
        for row_number, row in enumerate(csv.reader(generated_file, delimiter="|"), start=1):
            matches = [value for value in row if value.strip().casefold() in forbidden_values]
            if matches:
                raise SystemExit(
                    f"Non-Ugandan address value detected at generated row {row_number}: {matches}"
                )

    print(
        f"Generated {written_rows:,} unique Uganda address paths "
        f"from {source_rows:,} UBOS village rows ({duplicate_paths:,} duplicate paths collapsed, "
        f"{normalized_quotes:,} quote marks normalized); "
        f"SHA-256 {actual_sha} -> {output_path}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
