#!/usr/bin/env python3
"""Recompute corrected metrics from protected predictions without training."""
import argparse
from collections import defaultdict
import gzip
import json
from pathlib import Path

from t1d_tkg.metrics import METRIC_VERSION, average_precision


def rescore(directory):
    metadata = json.loads((directory / 'run.json').read_text())
    if not metadata.get('complete'):
        raise ValueError('cannot rescore an incomplete run')
    totals = defaultdict(lambda: defaultdict(float))
    report = metadata['report']
    for group in report['groups']:
        for path in sorted(directory.glob(f'{group}-*.jsonl.gz')):
            with gzip.open(path, 'rt') as handle:
                records = [json.loads(line) for line in handle]
            labels = [r['label'] for r in records]
            totals[group]['participants'] += 1
            totals[group]['windows'] += len(labels)
            totals[group]['positive_labels'] += sum(labels)
            for name in ('score', 'rule_score'):
                scores = [r[name] for r in records]
                ap = average_precision(labels, scores)
                if ap is not None:
                    totals[group][name+'_ap_sum'] += ap
                    totals[group][name+'_ap_count'] += 1
                totals[group][name+'_se'] += sum((s-y)**2 for s,y in zip(scores,labels,strict=True))
        counts = totals[group]
        expected = report['groups'][group]
        for key in ('participants', 'windows', 'positive_labels'):
            if counts[key] != expected[key]:
                raise ValueError('prediction archive does not match report coverage')
        model_key = 'event_summary_logistic' if 'event_summary_logistic' in expected else 'streaming_logistic'
        for name, key in (('score',model_key),('rule_score','persistence_slope_rule')):
            denominator = counts[name+'_ap_count']
            expected[key] = {'ap_defined_participants':int(denominator),
                             'participant_macro_ap':counts[name+'_ap_sum']/denominator if denominator else None,
                             'brier_score':counts[name+'_se']/counts['windows'] if counts['windows'] else None}
    report['metric_version'] = METRIC_VERSION
    report['rescored_from'] = str(directory)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_directory', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    report = rescore(args.run_directory)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as handle:
        json.dump(report, handle, indent=2)
        handle.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
