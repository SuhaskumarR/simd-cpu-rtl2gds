#!/usr/bin/env python3
"""
pick_best.py — picks the highest-frequency, clean-timing run under an
optional area cap.

Run from ~/simd_cpu/sweep/
    python3 pick_best.py                  # no area cap
    python3 pick_best.py --max-area 150000 # area cap in um^2
"""
import argparse
import csv
from pathlib import Path

SWEEP_DIR = Path(__file__).resolve().parent
RESULTS_CSV = SWEEP_DIR / "results.csv"


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-area", type=float, default=None,
                     help="reject runs with area_um2 above this")
    args = ap.parse_args()

    with open(RESULTS_CSV) as f:
        rows = list(csv.DictReader(f))

    candidates = []
    for r in rows:
        wns = to_float(r["wns_setup_ns"])
        antenna = to_float(r["antenna_violations"])
        area = to_float(r["area_um2"])
        freq = to_float(r["freq_mhz"])
        if wns is None or wns < 0:
            continue
        if antenna and antenna > 0:
            continue
        if args.max_area and (area is None or area > args.max_area):
            continue
        candidates.append((freq, area, r))

    if not candidates:
        print("No run satisfies the constraints.")
        return

    candidates.sort(key=lambda t: (-t[0], t[1]))  # highest freq, then smallest area
    best_freq, best_area, best_row = candidates[0]

    print("Best configuration:")
    print(f"  run_id           : {best_row['run_id']}")
    print(f"  frequency (MHz)  : {best_freq}")
    print(f"  area (um^2)      : {best_area}")
    print(f"  power_total (W)  : {best_row['power_total_w']}")
    print(f"  wns_setup (ns)   : {best_row['wns_setup_ns']}")
    print(f"  antenna_viol     : {best_row['antenna_violations']}")


if __name__ == "__main__":
    main()
