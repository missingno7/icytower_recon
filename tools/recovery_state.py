"""Canonical recovery-ledger helpers.

The ledger is intentionally small: it records observed function codegen status.
This module derives summaries from it and never writes it from experiment output.
"""
from collections import Counter
from pathlib import Path

from common import ROOT, identity, read_json

STATUSES = {'FUNCTION_MATCH', 'CODEGEN_SIMILAR', 'DIFFER', 'MISSING'}
SOURCE_ALIASES = {'src/main-partial.c': 'src/main.c'}


def unit_for(units, source):
    return units.get(SOURCE_ALIASES.get(source, source))


def load_ledger(path=ROOT / 'src/recovery.json'):
    ledger = read_json(path)
    if not isinstance(ledger, dict):
        raise ValueError('Recovery ledger must be an object')
    for source, row in ledger.items():
        if not source.startswith('src/') or not isinstance(row, dict):
            raise ValueError('Invalid recovery source: ' + source)
        functions = row.get('functions')
        if not isinstance(functions, dict):
            raise ValueError('Missing function state: ' + source)
        bad = set(functions.values()) - STATUSES
        if bad:
            raise ValueError('Unknown recovery status in %s: %s' % (source, sorted(bad)))
    return ledger


def function_dimensions(status, override=None):
    """Conservative dimensions derived only from the recorded codegen result."""
    if status == 'FUNCTION_MATCH':
        result = {'source': 'RECOVERED', 'semantic': 'VERIFIED', 'difference': 'EXACT'}
    elif status == 'MISSING':
        result = {'source': 'INCOMPLETE', 'semantic': 'UNKNOWN', 'difference': 'SOURCE_INCOMPLETE'}
    elif status == 'CODEGEN_SIMILAR':
        result = {'source': 'RECOVERED', 'semantic': 'UNVERIFIED', 'difference': 'RELOCATION_OR_LAYOUT'}
    else:
        result = {'source': 'CANDIDATE', 'semantic': 'UNVERIFIED', 'difference': 'UNCLASSIFIED'}
    if override:
        unexpected = set(override) - set(result)
        if unexpected:
            raise ValueError('Unknown function dimension: ' + ', '.join(sorted(unexpected)))
        result.update(override)
    return result


def progress_document(ledger=None):
    ledger = load_ledger() if ledger is None else ledger
    units = {u['source']: u for u in read_json(ROOT / 'src/units.json')}
    statuses = Counter()
    dimensions = Counter()
    matched_bytes = 0
    total_bytes = 0
    game_sources = 0
    for source, row in ledger.items():
        unit = unit_for(units, source)
        if unit is None:
            raise ValueError('Ledger source is not an owned CU: ' + source)
        if unit['classification'] == 'GAME':
            game_sources += 1
        by_name = {f['name']: f for f in unit['functions']}
        for name, status in row['functions'].items():
            if name not in by_name:
                raise ValueError('%s is absent from units inventory for %s' % (name, source))
            statuses[status] += 1
            dimensions[function_dimensions(status, row.get('function_dimensions', {}).get(name))['difference']] += 1
            if unit['classification'] == 'GAME':
                total_bytes += by_name[name]['size']
                if status == 'FUNCTION_MATCH':
                    matched_bytes += by_name[name]['size']
    return {
        'schema': 2,
        'authority': 'src/recovery.json',
        'ledger_identity': identity(ROOT / 'src/recovery.json'),
        'ledger_sources': len(ledger),
        'game_sources': game_sources,
        'function_statuses': dict(sorted(statuses.items())),
        'difference_dimensions': dict(sorted(dimensions.items())),
        'game_function_bytes': {'total': total_bytes, 'function_match': matched_bytes,
                                'remaining': total_bytes - matched_bytes},
        'scope': 'Function status is ledger-derived. Object, CU, layout, and runtime closure are separate evidence.'
    }


def frontier_rows(ledger=None):
    ledger = load_ledger() if ledger is None else ledger
    units = {u['source']: u for u in read_json(ROOT / 'src/units.json')}
    rows = []
    for source, row in ledger.items():
        unit = unit_for(units, source)
        by_name = {f['name']: f for f in unit['functions']}
        for name, status in row['functions'].items():
            if status == 'FUNCTION_MATCH':
                continue
            f = by_name[name]
            rows.append({'source': source, 'function': name, 'status': status,
                         'dimensions': function_dimensions(status, row.get('function_dimensions', {}).get(name)), 'va': f['va'], 'size': f['size'],
                         'classification': unit['classification']})
    return rows
