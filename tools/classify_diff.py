"""Classify a comparison report without changing its match verdict."""
import argparse
from pathlib import Path

from common import ROOT, read_json, write_json


def classify(row):
    if row['status'] == 'FUNCTION_MATCH':
        return 'EXACT'
    if row['status'] == 'MISSING':
        return 'SOURCE_INCOMPLETE'
    relocs = row.get('relocations', [])
    transfers = row.get('direct_transfers', [])
    if row['status'] == 'CODEGEN_SIMILAR':
        return 'RELOCATION_OR_LITERAL_LAYOUT'
    if relocs and all(x.get('symbol') == '.bss' and x.get('target_va') is None for x in relocs):
        return 'BSS_STATIC_PLACEMENT'
    if transfers and any(not x['equal'] for x in transfers):
        return 'SAME_CU_CALL_LAYOUT'
    if row.get('candidate_size') == row.get('original_size') and relocs and all(x.get('equal') for x in relocs):
        return 'REGISTER_OR_INSTRUCTION_SELECTION'
    if abs(row.get('candidate_size', 0) - row.get('original_size', 0)) <= 4:
        return 'ALIGNMENT_OR_PADDING'
    if row.get('candidate_size', 0) < row.get('original_size', 0):
        return 'SOURCE_OR_CONTROL_FLOW_INCOMPLETE'
    return 'UNCLASSIFIED'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report', type=Path)
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    report = read_json(a.report)
    rows = [{**row, 'difference_class': classify(row)} for row in report['functions']]
    result = {'report': str(a.report), 'functions': rows,
              'classes': {key: sum(x['difference_class'] == key for x in rows)
                          for key in sorted({x['difference_class'] for x in rows})}}
    if a.output:
        write_json(a.output, result)
    else:
        import json
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
