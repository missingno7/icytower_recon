"""Read-only section-base consistency check for a strict comparison report.

For a candidate DIR32 relocation into a section, a single linked section
contribution would require ``historical_operand = section_base + addend``.
Different implied bases expose an ownership/layout conflict even when each
reference separately resolves by unique content. This is diagnostic only.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from binary import Binary
from common import ROOT


def analyze(report, symbol, names=None, historical_ranges=()):
    groups = defaultdict(list)
    non_address_operands = []
    for function in report.get('functions', []):
        if names and function.get('name') not in names:
            continue
        for relocation in function.get('relocations', []):
            if relocation.get('symbol') != symbol or relocation.get('type') != 6:
                continue
            addend = relocation.get('addend')
            operand = relocation.get('original_value')
            if not isinstance(addend, int) or not isinstance(operand, int):
                continue
            if historical_ranges and not any(start <= operand < end for start, end in historical_ranges):
                non_address_operands.append({'function': function['name'], 'offset': relocation.get('function_offset'),
                                             'historical_operand': operand})
                continue
            base = operand - addend
            groups[base].append({
                'function': function['name'],
                'function_status': function.get('status'),
                'offset': relocation.get('function_offset'),
                'addend': addend,
                'historical_operand': operand,
                'resolution': relocation.get('resolution'),
                'strict_equal': relocation.get('equal'),
            })
    return {
        'symbol': symbol,
        'relocation_type': 'IMAGE_REL_I386_DIR32 (6)',
        'scope': 'Arithmetic constraints for one hypothetical contiguous candidate section placement. Linker pooling and distinct original owners can break this mapping; no owner binding, function match, or link/layout proof.',
        'single_base_compatible': len(groups) <= 1,
        'non_address_operands': non_address_operands,
        'groups': [
            {'implied_base': base, 'count': len(rows), 'references': rows}
            for base, rows in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', help='existing strict comparison JSON')
    parser.add_argument('--symbol', default='.rdata')
    parser.add_argument('--function', action='append', dest='names', help='limit to one or more functions')
    parser.add_argument('--json', action='store_true', help='print complete diagnostic JSON')
    args = parser.parse_args()
    exe = Binary(ROOT / 'assets/icytower15.exe')
    historical_ranges = [
        (exe.image_base + section['rva'], exe.image_base + section['rva'] + section['virtual_size'])
        for section in exe.sections if section['name'] == args.symbol
    ]
    result = analyze(json.loads(Path(args.report).read_text(encoding='utf-8')),
                     args.symbol, set(args.names or []), historical_ranges)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(args.report, args.symbol, 'single_base_compatible=' + str(result['single_base_compatible']),
          'non_address_operands=' + str(len(result['non_address_operands'])))
    for group in result['groups']:
        refs = group['references']
        examples = ', '.join(f"{r['function']}+{r['offset']} ({r['function_status']}): {r['resolution']}" for r in refs[:4])
        if len(refs) > 4:
            examples += f', ... ({len(refs) - 4} more)'
        print(f"  base={group['implied_base']:#x} references={group['count']}  {examples}")


if __name__ == '__main__':
    main()
