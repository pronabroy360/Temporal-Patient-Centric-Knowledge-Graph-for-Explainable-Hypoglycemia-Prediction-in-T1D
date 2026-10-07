"""Reject incomplete event exports before an expensive cache rebuild."""
import hashlib
from pathlib import Path

LOOP_20230131_EVENTS = {
    "basal": [f"LOOPDeviceBasal{index}.txt" for index in (1, 2, 3)],
    "bolus": ["LOOPDeviceBolus.txt"],
    "food": ["LOOPDeviceFood.txt"],
}


def require_source_inventory(tables, actual_paths, expected=None):
    """Validate exact filenames before partitioning. Alternate exports need an explicit inventory."""
    expected = LOOP_20230131_EVENTS if expected is None else expected
    if set(expected) != set(LOOP_20230131_EVENTS) or any(not names for names in expected.values()):
        raise ValueError("source inventory must specify nonempty basal, bolus and food file lists")
    for modality, names in expected.items():
        if len(names) != len(set(names)) or any(Path(name).name != name for name in names):
            raise ValueError("source inventory filenames must be unique basenames")
        if set(names) != {path.name for path in actual_paths[modality]}:
            raise ValueError(f"incomplete or unexpected {modality} source inventory; expected {names}")
        if any(not (tables / name).is_file() for name in names):
            raise ValueError("source inventory contains missing files")


def source_fingerprints(paths):
    result = []
    for path in paths:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        result.append({"file": path.name, "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    return result
