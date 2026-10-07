"""Read either an original gzip cache or Kaggle's expanded copy explicitly."""
import gzip
from pathlib import Path


def open_cache(path, mode="rt", **kwargs):
    path = Path(path)
    return gzip.open(path, mode, **kwargs) if path.suffix == ".gz" else path.open(mode, **kwargs)


def logical_name(name):
    return name[:-3] if name.endswith(".gz") else name


def discover_cache_files(directory, pattern):
    files = sorted(Path(directory).glob(pattern))
    names = [logical_name(path.name) for path in files]
    if len(names) != len(set(names)):
        raise ValueError("duplicate logical cache partition: compressed and expanded copies coexist")
    return sorted(files, key=lambda path: logical_name(path.name))
