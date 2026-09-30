#!/usr/bin/env python3
"""
run_sweep.py — launches OpenLane2 sequentially for every config variant
in configs/. Must be run FROM INSIDE the OpenLane2 nix shell.

Run from ~/simd_cpu/sweep/
    python3 run_sweep.py
"""
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent   # ~/simd_cpu
SWEEP_DIR = Path(__file__).resolve().parent
CONFIGS_DIR = SWEEP_DIR / "configs"
LOGS_DIR = SWEEP_DIR / "logs"
PDK = "sky130A"


def main():
    manifest = json.loads((SWEEP_DIR / "manifest.json").read_text())
    LOGS_DIR.mkdir(exist_ok=True)

    results = {}
    for i, run_id in enumerate(manifest, 1):
        config_path = CONFIGS_DIR / f"{run_id}.json"
        log_path = LOGS_DIR / f"{run_id}.log"
        print(f"[{i}/{len(manifest)}] Running {run_id} ...")

        cmd = [
            "openlane", "--pdk", PDK,
            "--run-tag", run_id,
            str(config_path),
        ]
        with open(log_path, "w") as logf:
            proc = subprocess.run(
                cmd, cwd=PROJECT_ROOT, stdout=logf, stderr=subprocess.STDOUT
            )

        ok = proc.returncode == 0
        results[run_id] = "OK" if ok else f"FAILED (see {log_path.name})"
        print(f"    -> {results[run_id]}")

    (SWEEP_DIR / "sweep_status.json").write_text(json.dumps(results, indent=2))
    print("\nSweep complete. See sweep_status.json for pass/fail per run.")


if __name__ == "__main__":
    main()
