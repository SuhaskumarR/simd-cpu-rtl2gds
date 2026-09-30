#!/usr/bin/env python3
"""
generate_configs.py — builds one OpenLane2 config.json per parameter
combination for the CPUtop PPA sweep.

Run from ~/simd_cpu/sweep/
    python3 generate_configs.py
"""
import json
import itertools
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent   # ~/simd_cpu
BASE_CONFIG = PROJECT_ROOT / "config.json"
OUT_DIR = Path(__file__).resolve().parent / "configs"

# --- sweep grid: edit these to explore different knobs -------------------
PARAM_GRID = {
    "CLOCK_PERIOD": [40, 50],                  # ns — tighter = higher freq target
    "FP_CORE_UTIL": [35, 45],                  # % floorplan core utilization
    "PL_TARGET_DENSITY_PCT": [55],             # % placement density (must exceed util)
}

# short, underscore-free tags used in run IDs (must stay in sync with
# the keys above, and with ABBREV_TO_KEY in parse_results.py)
ABBREV = {
    "CLOCK_PERIOD": "cp",
    "FP_CORE_UTIL": "util",
    "PL_TARGET_DENSITY_PCT": "dens",
}
# ---------------------------------------------------------------------


def resolve_dir_refs(obj, root: Path):
    """Recursively replace 'dir::x/y' with an absolute path so variant
    configs work regardless of where they're launched from."""
    if isinstance(obj, dict):
        return {k: resolve_dir_refs(v, root) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_dir_refs(v, root) for v in obj]
    if isinstance(obj, str) and obj.startswith("dir::"):
        return str((root / obj[len("dir::"):]).resolve())
    return obj


def main():
    base = json.loads(BASE_CONFIG.read_text())
    base = resolve_dir_refs(base, PROJECT_ROOT)

    OUT_DIR.mkdir(exist_ok=True)
    keys = list(PARAM_GRID.keys())
    combos = list(itertools.product(*PARAM_GRID.values()))

    manifest = []
    for combo in combos:
        cfg = dict(base)
        run_id_parts = []
        for k, v in zip(keys, combo):
            cfg[k] = v
            run_id_parts.append(f"{ABBREV[k]}{v}")
        run_id = "_".join(run_id_parts)

        out_path = OUT_DIR / f"{run_id}.json"
        out_path.write_text(json.dumps(cfg, indent=2))
        manifest.append(run_id)

    (Path(__file__).resolve().parent / "manifest.json").write_text(
        json.dumps(manifest, indent=2)
    )
    print(f"Generated {len(manifest)} config variants in {OUT_DIR}")


if __name__ == "__main__":
    main()
