#!/usr/bin/env python3
"""Run the first audit milestone without restricted patient data."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from t1d_tkg.audit import audit_dataset
from t1d_tkg.synthetic import synthetic_events


if __name__ == "__main__":
    print(json.dumps(audit_dataset(synthetic_events()), indent=2, sort_keys=True))
