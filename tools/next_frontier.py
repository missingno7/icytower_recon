"""Rank unresolved functions using ledger facts and optional staged evidence."""
import argparse
import json

from common import ROOT, read_json, write_json
from recovery_state import frontier_rows

PRIORITY = {'MISSING': 0, 'DIFFER': 2, 'CODEGEN_SIMILAR': 4}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--evidence', help='Optional staged candidate-evidence JSON')
    ap.add_argument('--output')
    a = ap.parse_args()
    evidence = read_json(a.evidence) if a.evidence else {'functions': []}
    boosted = {(x.get('source'), x.get('function')) for x in evidence.get('functions', [])
               if x.get('confidence') in ('strong', 'proven')}
    rows = frontier_rows()
    for row in rows:
        rank = PRIORITY[row['status']]
        if (row['source'], row['function']) in boosted:
            rank -= 2
        if row['classification'] != 'GAME':
            rank += 1
        row['priority'] = 'P%d' % max(0, min(5, rank))
        row['reason'] = ('strong external candidate evidence' if (row['source'], row['function']) in boosted
                         else row['dimensions']['difference'].lower())
    rows.sort(key=lambda x: (int(x['priority'][1:]), -x['size'], x['source'], x['function']))
    result = {'authority': 'src/recovery.json', 'rows': rows}
    if a.output:
        write_json(a.output, result)
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
