#!/usr/bin/env python3
"""
visualize.py — plots area-vs-frequency and power-vs-frequency tradeoff
curves from results.csv.

Run from ~/simd_cpu/sweep/
    python3 visualize.py
"""
import csv
from pathlib import Path
import matplotlib.pyplot as plt

SWEEP_DIR = Path(__file__).resolve().parent
RESULTS_CSV = SWEEP_DIR / "results.csv"
PLOTS_DIR = SWEEP_DIR / "plots"


def load_rows():
    with open(RESULTS_CSV) as f:
        return list(csv.DictReader(f))


def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def main():
    rows = load_rows()
    PLOTS_DIR.mkdir(exist_ok=True)

    freq = [to_float(r["freq_mhz"]) for r in rows]
    area = [to_float(r["area_um2"]) for r in rows]
    power = [to_float(r["power_total_w"]) for r in rows]
    # mark runs with any violation in red, clean runs in green
    clean = [
        (to_float(r["wns_setup_ns"]) or 0) >= 0
        and int(to_float(r["antenna_violations"]) or 0) == 0
        for r in rows
    ]
    colors = ["tab:green" if c else "tab:red" for c in clean]

    # --- Area vs Frequency ---
    plt.figure(figsize=(7, 5))
    plt.scatter(freq, area, c=colors)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Std-cell area (µm²)")
    plt.title("CPUtop — Area vs Frequency\n(green = clean timing/antenna, red = violation)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "area_vs_freq.png", dpi=150)
    plt.close()

    # --- Power vs Frequency ---
    plt.figure(figsize=(7, 5))
    plt.scatter(freq, power, c=colors)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Total power (W)")
    plt.title("CPUtop — Power vs Frequency\n(green = clean timing/antenna, red = violation)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "power_vs_freq.png", dpi=150)
    plt.close()

    print(f"Saved plots to {PLOTS_DIR}/")


if __name__ == "__main__":
    main()
