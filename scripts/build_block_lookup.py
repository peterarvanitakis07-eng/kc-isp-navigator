#!/usr/bin/env python3
"""
build_block_lookup.py — KC ISP Navigator
=========================================
Converts raw FCC Broadband Availability bulk data into the compact
block_isp_lookup.json used by the navigator tool.

USAGE
-----
1. Download the FCC fixed broadband availability data:
   https://broadbandmap.fcc.gov/data-download
   → "Fixed Broadband Availability" → select latest filing period
   → Download the national or MO/KS state-level CSV

2. Place the downloaded file(s) in this scripts/ directory (or pass --input).

3. Run:
   python3 scripts/build_block_lookup.py

4. Output: data/block_isp_lookup.json (auto-created / overwritten)

5. Update the date in index.html:
   Search for 'March 2026' and update to the new filing period date.

REQUIREMENTS
------------
- Python 3.8+
- No external libraries required (uses stdlib csv, json, os, argparse)

INPUT FORMAT (FCC bulk CSV columns used)
-----------------------------------------
  block_geoid       — 15-digit FIPS census block ID
  brand_name        — ISP brand name (maps to our ISP_DATA names)
  technology        — integer tech code (50=fiber, 40=cable, 300=LTE, etc.)
  max_down_mbps     — advertised download speed
  max_up_mbps       — advertised upload speed

OUTPUT FORMAT
-------------
  {
    "generated": "2026-06-01T14:00:00Z",
    "filing_period": "June 2026",
    "block_count": 308762,
    "blocks": {
      "290950001001000": ["AT&T", "Spectrum"],
      "200270001001000": ["Google Fiber", "AT&T"],
      ...
    }
  }

COUNTY FILTER
-------------
Filters to the 9-county KC metro (Jackson, Clay, Platte, Cass, Ray — MO;
Johnson, Wyandotte, Leavenworth, Miami — KS) plus a configurable buffer.
Edit FIPS_COUNTIES below to add/remove counties.
"""

import csv
import json
import os
import argparse
import sys
from datetime import datetime, timezone

# ─── 9-county KC Metro FIPS codes ────────────────────────────────────────────
# Missouri counties
MO_JACKSON      = "29095"
MO_CLAY         = "29047"
MO_PLATTE       = "29165"
MO_CASS         = "29037"
MO_RAY          = "29177"
# Kansas counties
KS_JOHNSON      = "20091"
KS_WYANDOTTE    = "20209"
KS_LEAVENWORTH  = "20103"
KS_MIAMI        = "20121"

KC_FIPS_COUNTIES = {
    MO_JACKSON, MO_CLAY, MO_PLATTE, MO_CASS, MO_RAY,
    KS_JOHNSON, KS_WYANDOTTE, KS_LEAVENWORTH, KS_MIAMI,
}

# ─── ISP name normalization ───────────────────────────────────────────────────
# Maps FCC brand_name variants → canonical name used in ISP_DATA.
# Add entries here whenever the FCC uses a different brand name.
ISP_NAME_MAP = {
    # AT&T
    "at&t internet":                "AT&T",
    "at&t internet services":       "AT&T",
    "at&t fiber":                   "AT&T",
    "att internet":                 "AT&T",
    # Spectrum / Charter
    "spectrum":                     "Spectrum",
    "charter spectrum":             "Spectrum",
    "charter communications":       "Spectrum",
    # T-Mobile
    "t-mobile home internet":       "T-Mobile Home Internet",
    "t-mobile":                     "T-Mobile Home Internet",
    # Verizon
    "verizon home internet":        "Verizon Home Internet",
    "verizon lte home internet":    "Verizon Home Internet",
    # Google Fiber
    "google fiber":                 "Google Fiber",
    # Brightspeed
    "brightspeed":                  "Brightspeed",
    "centurylink":                  "Brightspeed",
    # Midco
    "midco":                        "Midco",
    "midcontinent communications":  "Midco",
    # Everfast
    "everfast fiber":               "Everfast Fiber",
    "everfast":                     "Everfast Fiber",
    # ClearWave
    "clearwave fiber":              "ClearWave Fiber",
    # Mercury Broadband
    "mercury broadband":            "Mercury Broadband",
    "mercury fiber":                "Mercury Broadband",
    "mercury communications":       "Mercury Broadband",
    # Optimum
    "optimum":                      "Optimum",
    "altice usa":                   "Optimum",
    # Wisper ISP
    "wisper isp":                   "Wisper ISP",
    "wisper":                       "Wisper ISP",
    # Giant Communications
    "giant communications":         "Giant Communications",
    # Starlink
    "starlink":                     "Starlink",
    "spacex services":              "Starlink",
    # Viasat / HughesNet — excluded per project rules (high latency)
    "viasat":                       None,
    "hughesnet":                    None,
    "hughes network systems":       None,
    # EarthLink — excluded per project rules (AT&T reseller)
    "earthlink":                    None,
    # Mint Mobile — fixed home internet product only
    "mint mobile":                  "Mint Mobile Home Internet",
    # KC Coyote
    "kc coyote":                    "KC Coyote",
    # KS Broadband
    "ks broadband":                 "KS Broadband",
    "kansas broadband":             "KS Broadband",
}

# Tech codes we care about (FCC technology integer codes)
# 50=GPON Fiber, 51=EPON Fiber, 52=active fiber, 40=cable, 300=LTE, 400=5G NR,
# 10=DSL, 11=ADSL2, 12=VDSL, 20=cable modem (other), 60=satellite
TECH_CODES_INCLUDE = {10, 11, 12, 20, 40, 50, 51, 52, 60, 300, 400, 500, 600}

# Minimum speed threshold (Mbps) — skip entries below this (satellite noise, etc.)
MIN_DOWN_MBPS = 5


def normalize_name(raw: str) -> str | None:
    """Return canonical ISP name, or None to exclude."""
    key = raw.strip().lower()
    # Direct match
    if key in ISP_NAME_MAP:
        return ISP_NAME_MAP[key]
    # Partial match fallback
    for pattern, canonical in ISP_NAME_MAP.items():
        if pattern in key or key in pattern:
            return canonical
    # Unknown ISP — include as-is (capitalized) so we can spot new entrants
    return raw.strip().title()


def is_kc_block(block_geoid: str) -> bool:
    """Check if a 15-digit block FIPS is in a KC metro county."""
    if len(block_geoid) < 10:
        return False
    # State (2) + County (3) = first 5 digits
    county_fips = block_geoid[:5]
    return county_fips in KC_FIPS_COUNTIES


def build_lookup(input_files: list[str], filing_period: str) -> dict:
    """Parse FCC CSV(s) and build block→ISP lookup dict."""
    blocks: dict[str, set] = {}
    rows_read = 0
    rows_kept = 0

    for fpath in input_files:
        print(f"Reading {fpath} …", file=sys.stderr)
        with open(fpath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # FCC column names vary slightly — detect them
            fieldnames = [n.lower().strip() for n in reader.fieldnames or []]
            col_block = next((n for n in reader.fieldnames if "block_geoid" in n.lower() or "geoid" in n.lower()), None)
            col_brand = next((n for n in reader.fieldnames if "brand_name" in n.lower()), None)
            col_tech  = next((n for n in reader.fieldnames if "technology" in n.lower()), None)
            col_down  = next((n for n in reader.fieldnames if "max_down" in n.lower() or "down_mbps" in n.lower()), None)

            if not col_block or not col_brand:
                print(f"  ⚠ Could not find required columns in {fpath}. "
                      f"Found: {reader.fieldnames}", file=sys.stderr)
                continue

            for row in reader:
                rows_read += 1
                block_id = row[col_block].strip().zfill(15)

                if not is_kc_block(block_id):
                    continue

                # Speed filter
                if col_down:
                    try:
                        down = float(row[col_down] or 0)
                        if down < MIN_DOWN_MBPS:
                            continue
                    except ValueError:
                        pass

                # Tech filter
                if col_tech:
                    try:
                        tech = int(row[col_tech] or 0)
                        if tech not in TECH_CODES_INCLUDE:
                            continue
                    except ValueError:
                        pass

                canonical = normalize_name(row[col_brand])
                if canonical is None:
                    continue  # excluded ISP

                if block_id not in blocks:
                    blocks[block_id] = set()
                blocks[block_id].add(canonical)
                rows_kept += 1

        print(f"  → {rows_kept:,} rows kept so far", file=sys.stderr)

    print(f"\nTotal rows read: {rows_read:,}", file=sys.stderr)
    print(f"Blocks with KC ISPs: {len(blocks):,}", file=sys.stderr)

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "filing_period": filing_period,
        "block_count": len(blocks),
        "blocks": {k: sorted(v) for k, v in blocks.items()},
    }


def main():
    parser = argparse.ArgumentParser(
        description="Build block_isp_lookup.json from FCC broadband data CSV(s)"
    )
    parser.add_argument(
        "--input", "-i",
        nargs="+",
        help="Path(s) to FCC CSV file(s). Defaults to any .csv in scripts/",
    )
    parser.add_argument(
        "--output", "-o",
        default=os.path.join(os.path.dirname(__file__), "..", "data", "block_isp_lookup.json"),
        help="Output JSON path (default: data/block_isp_lookup.json)",
    )
    parser.add_argument(
        "--period",
        default="June 2026",
        help="FCC filing period label, e.g. 'June 2026' (used in output + index.html reminder)",
    )
    args = parser.parse_args()

    # Auto-detect input CSVs if not specified
    if not args.input:
        scripts_dir = os.path.dirname(os.path.abspath(__file__))
        csvs = [os.path.join(scripts_dir, f) for f in os.listdir(scripts_dir) if f.endswith(".csv")]
        if not csvs:
            print("No CSV files found. Download FCC data and place in scripts/ or use --input.", file=sys.stderr)
            print("https://broadbandmap.fcc.gov/data-download", file=sys.stderr)
            sys.exit(1)
        args.input = csvs
        print(f"Auto-detected input files: {csvs}", file=sys.stderr)

    result = build_lookup(args.input, args.period)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, separators=(",", ":"))

    size_kb = os.path.getsize(args.output) / 1024
    print(f"\n✅ Written to {args.output}", file=sys.stderr)
    print(f"   {result['block_count']:,} blocks · {size_kb:.0f} KB", file=sys.stderr)
    print(f"\nNext step: update 'March 2026' → '{args.period}' in index.html", file=sys.stderr)


if __name__ == "__main__":
    main()
