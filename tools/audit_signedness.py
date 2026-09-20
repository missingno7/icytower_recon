"""List unresolved functions whose sources use signedness-sensitive operations."""
import argparse
import re

from common import ROOT, write_json
from recovery_state import frontier_rows

PATTERN = re.compile(r'(?:\bunsigned\b|\bchar\b|>>|<<|\(int\)|\(unsigned)')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output')
    a = ap.parse_args()
    rows = []
    for row in frontier_rows():
        source = ROOT / row['source'].replace('-partial', '')
        text = source.read_text(encoding='cp1252')
        hits = [i + 1 for i, line in enumerate(text.splitlines()) if PATTERN.search(line)]
        if hits:
            rows.append({**row, 'source_file': str(source.relative_to(ROOT)).replace('\\', '/'),
                         'candidate_lines': hits[:32],
                         'note': 'Review signed shifts, char promotion, and explicit casts against DWARF/disassembly before source changes.'})
    result = {'authority': 'src/recovery.json', 'rows': rows}
    if a.output:
        write_json(a.output, result)
    else:
        import json
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
