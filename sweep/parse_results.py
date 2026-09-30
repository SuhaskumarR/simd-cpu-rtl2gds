#!/usr/bin/env python3
"""
parse_results.py — walks runs/<run_tag>/ for every swept variant, finds
the highest-numbered step's state_out.json (metrics accumulate through
the flow, so the last step has the full picture), and extracts the PPA
numbers that matter into results.csv.

Run from ~/simd_cpu/sweep/
    python3 parse_results.py
"""
import csv
import json
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent   # ~/simd_cpu
SWEEP_DIR = Path(__file__).resolve().parent
RUNS_DIR = PROJECT_ROOT / "runs"

# metric key -> output column name
METRIC_KEYS = {
    "timing__setup__wns": "wns_setup_ns",
    "timing__setup__tns": "tns_setup_ns",
    "timing__hold__wns": "wns_hold_ns",
    "design__instance__area": "area_um2",
    "design__die__area": "die_area_um2",
    "power__total": "power_total_w",
    "antenna__violating__nets": "antenna_violations",
    "design__max_slew_violation__count": "slew_violations",
    "design__max_cap_violation__count": "cap_violations",
    "design__lvs_error__count": "lvs_errors",
    "magic__drc_error__count": "drc_errors_magic",
}


def latest_state_out(run_dir: Path):
    """Return the state_out.json with the highest leading step number."""
    candidates = []
    for sub in run_dir.iterdir():
        if not sub.is_dir():
            continue
        m = re.match(r"^(\d+)-", sub.name)
        state_file = sub / "state_out.json"
        if m and state_file.exists():
            candidates.append((int(m.group(1)), state_file))
    if not candidates:
        return None
    candidates.sort(key=lambda t: t[0])
    return candidates[-1][1]


# must match ABBREV in generate_configs.py
ABBREV_TO_KEY = {
    "cp": "clock_period",
    "util": "fp_core_util",
    "dens": "pl_target_density_pct",
}


def parse_run_id(run_id: str):
    """cp30_util40_dens45 -> {'clock_period':30, 'fp_core_util':40, ...}"""
    parts = {}
    for token in run_id.split("_"):
        m = re.match(r"([a-z]+)(\d+)$", token)
        if m and m.group(1) in ABBREV_TO_KEY:
            parts[ABBREV_TO_KEY[m.group(1)]] = int(m.group(2))
    return parts


def main():
    manifest = json.loads((SWEEP_DIR / "manifest.json").read_text())
    rows = []

    for run_id in manifest:
        run_dir = RUNS_DIR / run_id
        if not run_dir.exists():
            print(f"skip {run_id}: no run directory")
            continue

        state_file = latest_state_out(run_dir)
        if state_file is None:
            print(f"skip {run_id}: no state_out.json found")
            continue

        metrics = json.loads(state_file.read_text()).get("metrics", {})
        row = {"run_id": run_id}
        row.update(parse_run_id(run_id))
        for key, col in METRIC_KEYS.items():
            row[col] = metrics.get(key)

        # derived: frequency in MHz from clock period in ns
        cp = row.get("clock_period")
        row["freq_mhz"] = round(1000.0 / cp, 2) if cp else None

        rows.append(row)

    if not rows:
        print("No results parsed — did the sweep run yet?")
        return

    fieldnames = list(rows[0].keys())
    out_csv = SWEEP_DIR / "results.csv"
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {out_csv}")


if __name__ == "__main__":
    main()
