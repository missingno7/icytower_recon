"""Publish generated recovery progress from the canonical ledger."""
import argparse

from common import ROOT, read_json, write_json
from recovery_state import frontier_rows, load_ledger, progress_document


def blocker_summary(ledger):
    rows = frontier_rows(ledger)
    counts = {}
    for row in rows:
        key = row['dimensions']['difference']
        counts[key] = counts.get(key, 0) + 1
    return {'schema': 1, 'authority': 'src/recovery.json',
            'unresolved_functions': len(rows),
            'difference_classes': dict(sorted(counts.items())),
            'note': 'This is generated status only. docs/blockers.json retains curated hypotheses and experiments.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true', help='Fail when generated documents are stale.')
    a = ap.parse_args()
    ledger = load_ledger()
    generated = {ROOT / 'docs/progress.json': progress_document(ledger),
                 ROOT / 'docs/current/progress.json': progress_document(ledger),
                 ROOT / 'docs/blocker-summary.json': blocker_summary(ledger)}
    stale = [path for path, value in generated.items() if not path.exists() or read_json(path) != value]
    if a.check:
        if stale:
            raise ValueError('Stale generated recovery document: ' + ', '.join(str(x.relative_to(ROOT)) for x in stale))
        print('PASS: recovery progress and blocker summary derive from src/recovery.json.')
        return
    for path, value in generated.items():
        write_json(path, value)
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
