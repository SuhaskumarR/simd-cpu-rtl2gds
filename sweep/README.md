# CPUtop PPA Sweep Framework

Automates config generation, OpenLane2 runs, metrics extraction, and
PPA tradeoff visualization for the SIMD CPU design.

## Layout
```
sweep/
├── generate_configs.py   # builds config.json per parameter combo
├── run_sweep.py           # launches OpenLane2 for each variant
├── parse_results.py       # extracts metrics into results.csv
├── visualize.py            # area-vs-freq, power-vs-freq plots
├── pick_best.py            # picks best config under a target
├── configs/                # generated (config_<id>.json)
├── logs/                   # per-run OpenLane logs
├── plots/                  # generated PNGs
├── manifest.json           # list of run IDs (generated)
├── sweep_status.json       # pass/fail per run (generated)
└── results.csv             # extracted PPA data (generated)
```

## Usage
Edit `PARAM_GRID` in `generate_configs.py` to set the sweep space
(clock period, floorplan utilization, placement density — add more
keys as needed, e.g. `CTS_CLK_MAX_SKEW`).

```bash
cd ~/simd_cpu/sweep
python3 generate_configs.py

# inside the OpenLane2 nix shell:
nix-shell --pure ~/openlane2/shell.nix
python3 run_sweep.py            # sequential; can take a while for many combos

python3 parse_results.py
python3 visualize.py            # needs matplotlib: pip install matplotlib --break-system-packages
python3 pick_best.py --max-area 150000
```

## Notes
- Each variant runs under its own `--run-tag`, landing in
  `~/simd_cpu/runs/<run_id>/` alongside your manual runs — nothing is
  overwritten.
- `parse_results.py` reads the highest-numbered step's `state_out.json`
  per run, since OpenLane2 metrics accumulate through the flow.
- A run is failed intentionally at extreme settings (e.g. very low
  utilization with a very tight clock) — `run_sweep.py` logs and
  continues rather than aborting the whole sweep.
- 36 combos (4 clock × 3 util × 3 density) at ~5–7 min/run on this
  design ≈ 3–4 hours sequential. Shrink `PARAM_GRID` for a faster
  first pass, or parallelize `run_sweep.py` with a process pool if
  your machine has the cores/memory to spare.
