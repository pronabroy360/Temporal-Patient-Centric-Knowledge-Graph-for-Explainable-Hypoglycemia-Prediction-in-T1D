#!/usr/bin/env python3
"""Select epochs using corrected, matched outer-0 validation artifacts."""
import argparse
import json
from pathlib import Path
from t1d_tkg.metrics import METRIC_VERSION


def select(paths):
    reports = [json.loads(path.read_text()) for path in paths]
    signatures = set()
    for report in reports:
        if report.get('metric_version') != METRIC_VERSION or report.get('fold') != 'outer-0':
            raise ValueError('requires corrected outer-0 metrics')
        if set(report['groups']) != {'validation'}:
            raise ValueError('configuration selection requires validation-only artifacts')
        group = report['groups']['validation']
        signatures.add(json.dumps([report['manifest_sha256'], report['features'], report['learning_rate'],
                                    report['window_verification'], group['windows'], group['positive_labels'],
                                    group['streaming_logistic']['ap_defined_participants']], sort_keys=True))
        if group['streaming_logistic']['participant_macro_ap'] is None:
            raise ValueError('undefined validation AP')
    if len(signatures) != 1 or sorted(report['epochs'] for report in reports) != [1,2]:
        raise ValueError('requires matched one-epoch and two-epoch candidates')
    winner = max(reports, key=lambda report: (report['groups']['validation']['streaming_logistic']['participant_macro_ap'],
                                              -report['groups']['validation']['streaming_logistic']['brier_score'],
                                              -report['epochs']))
    return {'metric_version': METRIC_VERSION, 'epochs':winner['epochs'], 'learning_rate':winner['learning_rate'],
            'manifest_sha256':winner['manifest_sha256'], 'features':winner['features'],
            'candidate_paths':[str(path) for path in paths],
            'policy':'Development-only AP selection; lower Brier breaks ties, then fewer epochs.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('candidates', type=Path, nargs=2)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    selected = select(args.candidates)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as handle:
        json.dump(selected,handle,indent=2)
        handle.write('\n')
    print(json.dumps(selected,indent=2))
