"""
run_all.py
End-to-end pipeline driver. Executes:
    01_preprocess.py  -> 02_mw_imputation.py
                      -> 03_descriptive_analysis.py
                      -> 04_host_vs_nonhost.py
                      -> 05_nb_regression.py
                      -> 06_tariff_scoring.py
                      -> 07_figures.py
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = [
    "01_preprocess.py",
    "02_mw_imputation.py",
    "03_descriptive_analysis.py",
    "04_host_vs_nonhost.py",
    "05_nb_regression.py",
    "06_tariff_scoring.py",
    "07_figures.py",
]

if __name__ == "__main__":
    for step in STEPS:
        print(f"\n{'='*70}\n  Running {step}\n{'='*70}")
        rc = subprocess.call([sys.executable, str(HERE / step)])
        if rc != 0:
            sys.exit(f"Step {step} failed (exit {rc}).")
    print("\nPipeline complete.")
