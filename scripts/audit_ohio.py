#!/usr/bin/env python3
"""Audit authorized OhioT1DM XML files without training a model."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from t1d_tkg.audit import audit_dataset
from t1d_tkg.manifest import build_loso_manifest, save_manifest
from t1d_tkg.ohio import parse_ohio_xml


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--split", default=None, help="source split label, e.g. training or testing")
    parser.add_argument("--timezone", required=True, help="IANA timezone name documented for the deidentified release")
    parser.add_argument("--output", type=Path, default=None, help="optional JSON audit report path")
    parser.add_argument("--manifest-output", type=Path, default=None, help="optional patient-disjoint fold manifest path")
    args = parser.parse_args()
    try:
        from zoneinfo import ZoneInfo
        zone = ZoneInfo(args.timezone)
    except Exception as exc:
        parser.error(f"invalid timezone {args.timezone!r}: {exc}")
    paths = sorted(args.directory.glob("*.xml"))
    if not paths:
        parser.error(f"no .xml files found in {args.directory}")
    results = []
    parse_errors = []
    for path in paths:
        try:
            results.append(parse_ohio_xml(path, timezone=zone, source_split=args.split))
        except Exception as exc:
            # Continue the audit so one malformed file does not hide the
            # release-wide participant and coverage summary.
            parse_errors.append({"source_file": path.name, "error": str(exc)})
    events = [event for result in results for event in result.events]
    report = audit_dataset(events)
    report["source_files"] = [result.source_file for result in results]
    report["metadata"] = [result.metadata for result in results]
    report["parse_errors"] = parse_errors
    if args.manifest_output is not None:
        if not results:
            parser.error("cannot write a fold manifest because no XML files parsed successfully")
        manifest = build_loso_manifest(result.patient_id for result in results)
        args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
        checksum = save_manifest(args.manifest_output, manifest)
        report["fold_manifest"] = {"path": str(args.manifest_output), "checksum": checksum, "version": manifest["version"]}
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")


if __name__ == "__main__":
    main()
