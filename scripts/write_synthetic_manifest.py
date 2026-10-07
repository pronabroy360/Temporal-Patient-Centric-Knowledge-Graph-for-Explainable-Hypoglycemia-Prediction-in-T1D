#!/usr/bin/env python3
"""Write the deterministic fixture's patient-disjoint LOSO manifest."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from t1d_tkg.manifest import build_loso_manifest, save_manifest
from t1d_tkg.synthetic import synthetic_events


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    patients = {event.patient_id for event in synthetic_events()}
    manifest = build_loso_manifest(patients)
    checksum = save_manifest(args.output, manifest)
    print(checksum)


if __name__ == "__main__":
    main()

