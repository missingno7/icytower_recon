"""Historical compile order as evidence, and probe-driven single-definition moves.

GCC 4.4.1 emits functions in call-graph order derived from definition order, and the
code it chooses for a function depends on what it compiled just before (recorded
scratch-register and clear-order effects). The original function addresses give the
historical emission order exactly. This module exposes that context on function cards
and turns isolated single-move trials into bounded SOURCE_ORDER tasks only when a trial
shows a gain with no exact-function regression. Nothing here is a function proof.
"""
import json
import os
import re
import subprocess
from pathlib import Path
from common import ROOT, identity, read_json, write_json

EVIDENCE = ROOT / 'docs/attempts/order-moves'


def emission_context(report, name):
    """Predecessor facts for one function: historical versus candidate emission order."""
    rows = report['functions']
    hist = [f['name'] for f in sorted(rows, key=lambda f: f['va'])]
    cand = [f['name'] for f in sorted(rows, key=lambda f: f.get('candidate_offset') if f.get('candidate_offset') is not None else 1 << 40)]
    status = {f['name']: f['status'] for f in rows}
    if name not in hist or name not in cand: return None
    hi, ci = hist.index(name), cand.index(name)
    hpred = hist[hi - 1] if hi else None
    cpred = cand[ci - 1] if ci else None
    prefix = hist[:hi]
    prefix_exact = all(status[n] == 'FUNCTION_MATCH' for n in prefix) and cand[:hi] == prefix
    frontier = prefix_exact and status[name] != 'FUNCTION_MATCH'
    same = [n for i, n in enumerate(hist) if (hist[i - 1] if i else None) == (cand[cand.index(n) - 1] if cand.index(n) else None)]
    return {'historical_position': hi, 'candidate_position': ci, 'historical_predecessor': hpred, 'candidate_predecessor': cpred,
            'predecessor_same': hpred == cpred, 'predecessor_exact': status.get(cpred) == 'FUNCTION_MATCH' if cpred else True,
            'historical_prefix_exact': prefix_exact, 'frontier': frontier,
            'cu_same_predecessor_count': len(same), 'cu_function_count': len(hist),
            'limit': 'Compile-order context only. It explains why a body mismatch may be a neighbor artifact; it never proves or masks any byte.'}


def priority_adjustment(context):
    if not context: return 0, None
    if context['frontier']: return 15, 'Historical emission-order frontier: every earlier function already matches in order, so this body is compiled in its historical context.'
    if not context['predecessor_same']: return -10, 'Emission-order context differs from history (candidate predecessor ' + str(context['candidate_predecessor']) + ' versus historical ' + str(context['historical_predecessor']) + '); part of the mismatch may be a neighbor artifact.'
    if not context['predecessor_exact']: return -5, 'Historical predecessor is emitted in order but does not match yet; its bytes may perturb this body.'
    return 5, 'Historical predecessor is emitted in order and exact.'


def leading_comment_start(text, clean, start):
    """Start of a block comment directly preceding `start`, verified on sanitized text.

    A raw-text regex could match a `/*` inside a string literal in another function and
    turn the moved span into a malformed island; the sanitized text blanks comment and
    string interiors, so the candidate region must be entirely blank there.
    """
    p = start
    while p > 0 and text[p - 1] in ' \t\r\n': p -= 1
    if text[p - 2:p] != '*/': return start
    q = text.rfind('/*', 0, p - 2)
    if q < 0 or clean[q:p].strip(): return start
    return q


def _definition_spans(text):
    from source_order import definition_spans
    from source_scope import sanitized
    spans = definition_spans(text); clean = sanitized(text)
    for s in spans: s['cstart'] = leading_comment_start(text, clean, s['start'])
    return spans


def _historical_lines(unit, source):
    from type_graph import graph, number
    g = graph(); lines = {}
    for d in g.dies.values():
        if d['tag'] == 'DW_TAG_subprogram' and d.get('cu') == unit['cu_die'] and (d.get('decl_file_path') or '').replace('\\', '/').endswith('/' + Path(source).name):
            line = number(d['resolved'].get('DW_AT_decl_line'))
            if line: lines.setdefault(d.get('name'), set()).add(line)
    return {n: next(iter(p)) for n, p in lines.items() if len(p) == 1}


def move_edit(text, spans, name, anchor):
    """Two exact span edits that move `name` (with its leading comment) directly after `anchor`."""
    byname = {s['name']: s for s in spans}
    s, a = byname[name], byname[anchor]
    nl = '\r\n' if '\r\n' in text else '\n'
    block = text[s['cstart']:s['end']]
    return [{'start': s['cstart'], 'end': s['end'], 'before': block, 'after': '', 'reason': 'Remove the unchanged definition from its current slot'},
            {'start': a['end'], 'end': a['end'], 'before': '', 'after': nl + nl + block.strip('\r\n'), 'reason': 'Re-insert the unchanged definition after its historical predecessor'}]


def candidate_moves(text, spans, lines):
    named = [s for s in spans if s['name'] in lines]
    hist = sorted(named, key=lambda s: lines[s['name']]); cur = sorted(named, key=lambda s: s['start'])
    hpred = {s['name']: (hist[i - 1]['name'] if i else None) for i, s in enumerate(hist)}
    cpred = {s['name']: (cur[i - 1]['name'] if i else None) for i, s in enumerate(cur)}
    return [(s['name'], hpred[s['name']]) for s in cur if hpred[s['name']] and hpred[s['name']] != cpred[s['name']]]


def probe(target, source, only=()):
    """Compile one isolated single-move variant per out-of-order function and retain the outcomes."""
    from build import COMPILERS
    from experiment import compare
    from interface_tasks import patch_text
    from recovery_pipeline import OBJDUMP
    ledger = read_json(ROOT / 'src/recovery.json'); ref = read_json(ROOT / ledger[source]['verified_report']); build = ref['build']
    unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == source)
    text = (ROOT / source).read_bytes().decode('cp1252'); spans = _definition_spans(text); lines = _historical_lines(unit, source)
    before = {f['name']: f['status'] for f in ref['functions']}; sizes = {f['name']: f.get('candidate_size') for f in ref['functions']}; hsz = {f['name']: f['original_size'] for f in ref['functions']}
    env = os.environ.copy(); env['PATH'] = str(COMPILERS[build['compiler']] / 'bin') + os.pathsep + env['PATH']
    results = []
    for name, anchor in candidate_moves(text, spans, lines):
        if only and name not in only: continue
        edits = move_edit(text, spans, name, anchor); new = patch_text(text, edits)
        out = ROOT / 'build/order-moves' / target / name; overlay = out / 'overlay'; (overlay / Path(source).parent).mkdir(parents=True, exist_ok=True)
        (overlay / source).write_bytes(new.encode('cp1252'))
        args = list(build['command'])
        for flag, value in [('-MF', out / 'unit.d'), ('-aux-info', out / 'interfaces.aux'), ('-c', overlay / source), ('-o', out / 'unit.o')]: args[args.index(flag) + 1] = str(value)
        args[1:1] = ['-I' + str((ROOT / source).parent)]
        r = subprocess.run([str(x) for x in args], cwd=ROOT, env=env, capture_output=True, text=True)
        row = {'move': name, 'after': anchor}
        if r.returncode:
            errors = [l for l in r.stderr.splitlines() if 'error' in l][:3]
            kind = 'MISSING_DECLARATION' if any('undeclared' in l for l in errors) else 'PROBER_BUG_OR_MALFORMED_OVERLAY' if any('terminating' in l or 'expected' in l for l in errors) else 'COMPILE_FAILED'
            row.update(compile='FAILED', failure_kind=kind, error=errors); results.append(row); continue
        report = compare(out / 'unit.o', ref['historical_cu'], ROOT / 'assets/icytower15.exe', OBJDUMP)
        after = {f['name']: f['status'] for f in report['functions']}; asz = {f['name']: f.get('candidate_size') for f in report['functions']}
        from interfaces import declarations
        implicit_before = {d['name'] for d in declarations(ref.get('interfaces_aux', '')) if d['kind'] == 'IC'}
        implicit_after = {d['name'] for d in declarations((out / 'interfaces.aux').read_text(errors='replace')) if d['kind'] == 'IC'}
        row.update(compile='OK', matches=report['function_matches'], new_implicit_declarations=sorted(implicit_after - implicit_before),
                   gains=sorted(n for n in before if before[n] != 'FUNCTION_MATCH' and after.get(n) == 'FUNCTION_MATCH'),
                   losses=sorted(n for n in before if before[n] == 'FUNCTION_MATCH' and after.get(n) != 'FUNCTION_MATCH'),
                   now_historical_size=sorted(n for n in before if after.get(n) != 'FUNCTION_MATCH' and asz.get(n) != sizes.get(n) and asz.get(n) == hsz.get(n)),
                   other_size_changes=sorted(n for n in before if after.get(n) != 'FUNCTION_MATCH' and asz.get(n) != sizes.get(n) and asz.get(n) != hsz.get(n)))
        results.append(row)
        print(json.dumps(row), flush=True)
    record = {'scope': 'Isolated single-definition move trials; diagnostic evidence only, never a function proof or placement.',
              'target': target, 'source': source, 'source_identity': identity(ROOT / source), 'object_identity': build['object'],
              'compiler': build['compiler'], 'flags': build['flags'], 'results': results}
    write_json(EVIDENCE / (target + '.json'), record)
    return record


def move_plans(unit, ledger):
    """Bounded SOURCE_ORDER tasks for moves whose retained trial gained exact functions without regression."""
    source = unit['source']; path = EVIDENCE / (read_json(ROOT / ledger[source]['verified_report'])['build']['target'] + '.json')
    if not path.exists(): return []
    record = read_json(path)
    if record.get('source') != source or record.get('source_identity') != identity(ROOT / source): return []
    if record.get('object_identity') != read_json(ROOT / ledger[source]['verified_report'])['build'].get('object'): return []
    text = (ROOT / source).read_bytes().decode('cp1252'); spans = _definition_spans(text); byname = {s['name']: s for s in spans}
    blocked = ROOT / 'docs/current/interface-blocks.json'; blocks = read_json(blocked) if blocked.exists() else {}
    cards = []
    for row in record['results']:
        if row.get('compile') != 'OK' or not row.get('gains') or row.get('losses') or row.get('new_implicit_declarations'): continue
        name, anchor = row['move'], row['after']
        if name not in byname or anchor not in byname: continue
        task = 'move_' + Path(source).stem.replace('-', '_') + '_' + name
        if task in blocks: continue
        cards.append({'schema': 1, 'task_kind': 'SOURCE_ORDER', 'function': task, 'source': source, 'sources': [source],
                      'target': record['target'], 'affected_targets': [record['target']], 'difficulty': 'CHEAP', 'priority': 290,
                      'changes': [dict(e, file=source) for e in move_edit(text, spans, name, anchor)], 'source_identities': {source: identity(ROOT / source)},
                      'body_edit_allowed': False, 'state': 'SOURCE_ORDER_REPAIR', 'status': 'DEFINITION_ORDER_DIFFERS',
                      'difference_class': 'HISTORICAL_DEFINITION_ORDER', 'definition_order': [{'function': anchor}, {'function': name}],
                      'current_order': [s['name'] for s in spans], 'moved_function': name, 'historical_predecessor': anchor,
                      'trial': row, 'trial_evidence': path.relative_to(ROOT).as_posix(),
                      'begin_command': 'python tools/interface_task.py begin ' + task, 'apply_command': 'python tools/interface_task.py apply ' + task,
                      'verification_command': 'python tools/interface_task.py check ' + task, 'promotion_command': 'python tools/interface_task.py promote ' + task,
                      'reason': 'Retained isolated trial: moving this unchanged definition after its historical predecessor gained ' + ', '.join(row['gains']) + ' with no exact-function regression. Fresh strict acceptance remains mandatory.',
                      'edit_scope': 'Move one complete unchanged definition after its historical predecessor. No body, declaration or flag edits.'})
    return cards


def block_edits(text, spans, functions, lines):
    """Edits that place `functions` consecutively in historical line order at the slot of the earliest one.

    Definitions move with their leading comments; declarations between them stay where
    they are. Nothing else changes.
    """
    byname = {s['name']: s for s in spans}
    chosen = [byname[n] for n in functions]
    ordered = sorted(chosen, key=lambda s: lines[s['name']])
    slot = min(s['cstart'] for s in chosen)
    nl = '\r\n' if '\r\n' in text else '\n'
    blocks = [text[s['cstart']:s['end']].strip('\r\n') for s in ordered]
    edits = [{'start': s['cstart'], 'end': s['end'], 'before': text[s['cstart']:s['end']], 'after': '', 'reason': 'Remove the unchanged definition from its current slot'} for s in chosen]
    edits.append({'start': slot, 'end': slot, 'before': '', 'after': (nl + nl).join(blocks) + nl + nl, 'reason': 'Re-insert the historical block in historical order'})
    return edits


def probe_block(target, source, functions):
    """Diagnostic compound move of a small historical block; scratch overlay only, never promotion."""
    from build import COMPILERS
    from experiment import compare
    from interface_tasks import patch_text
    from interfaces import declarations
    from recovery_pipeline import OBJDUMP
    if not 2 <= len(functions) <= 8: raise ValueError('A block probe moves two to eight complete definitions')
    ledger = read_json(ROOT / 'src/recovery.json'); ref = read_json(ROOT / ledger[source]['verified_report']); build = ref['build']
    unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == source)
    text = (ROOT / source).read_bytes().decode('cp1252'); spans = _definition_spans(text); lines = _historical_lines(unit, source)
    missing = [f for f in functions if f not in {s['name'] for s in spans} or f not in lines]
    if missing: raise ValueError('Unknown or unlined definitions: ' + ', '.join(missing))
    edits = block_edits(text, spans, functions, lines); new = patch_text(text, edits)
    label = '+'.join(functions); out = ROOT / 'build/order-blocks' / target / label; overlay = out / 'overlay'; (overlay / Path(source).parent).mkdir(parents=True, exist_ok=True)
    (overlay / source).write_bytes(new.encode('cp1252'))
    env = os.environ.copy(); env['PATH'] = str(COMPILERS[build['compiler']] / 'bin') + os.pathsep + env['PATH']
    args = list(build['command'])
    for flag, value in [('-MF', out / 'unit.d'), ('-aux-info', out / 'interfaces.aux'), ('-c', overlay / source), ('-o', out / 'unit.o')]: args[args.index(flag) + 1] = str(value)
    args[1:1] = ['-I' + str((ROOT / source).parent)]
    record = {'scope': 'Diagnostic compound definition move in a scratch overlay; complete definitions only, no body or declaration edits, never a promotion input.',
              'target': target, 'source': source, 'functions': functions, 'source_identity': identity(ROOT / source), 'object_identity': build['object']}
    r = subprocess.run([str(x) for x in args], cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode:
        errors = [l for l in r.stderr.splitlines() if 'error' in l][:5]
        record.update(compile='FAILED', failure_kind='MISSING_DECLARATION' if any('undeclared' in l for l in errors) else 'COMPILE_FAILED', error=errors)
    else:
        report = compare(out / 'unit.o', ref['historical_cu'], ROOT / 'assets/icytower15.exe', OBJDUMP)
        before = {f['name']: f['status'] for f in ref['functions']}; after = {f['name']: f['status'] for f in report['functions']}
        sizes = {f['name']: f.get('candidate_size') for f in ref['functions']}; asz = {f['name']: f.get('candidate_size') for f in report['functions']}; hsz = {f['name']: f['original_size'] for f in ref['functions']}
        hist = [f['name'] for f in sorted(report['functions'], key=lambda f: f['va'])]
        cand = [f['name'] for f in sorted(report['functions'], key=lambda f: f.get('candidate_offset') if f.get('candidate_offset') is not None else 1 << 40)]
        same = sum(1 for i, n in enumerate(hist) if (hist[i - 1] if i else None) == (cand[cand.index(n) - 1] if cand.index(n) else None))
        old_same = emission_context(ref, hist[0])['cu_same_predecessor_count']
        implicit_before = {d['name'] for d in declarations(ref.get('interfaces_aux', '')) if d['kind'] == 'IC'}
        implicit_after = {d['name'] for d in declarations((out / 'interfaces.aux').read_text(errors='replace')) if d['kind'] == 'IC'}
        record.update(compile='OK', matches_before=ref['function_matches'], matches_after=report['function_matches'],
                      gains=sorted(n for n in before if before[n] != 'FUNCTION_MATCH' and after.get(n) == 'FUNCTION_MATCH'),
                      losses=sorted(n for n in before if before[n] == 'FUNCTION_MATCH' and after.get(n) != 'FUNCTION_MATCH'),
                      now_historical_size=sorted(n for n in before if after.get(n) != 'FUNCTION_MATCH' and asz.get(n) != sizes.get(n) and asz.get(n) == hsz.get(n)),
                      size_changes={n: [sizes.get(n), asz.get(n), hsz.get(n)] for n in before if asz.get(n) != sizes.get(n)},
                      same_predecessor_before=old_same, same_predecessor_after=same, function_count=len(hist),
                      new_implicit_declarations=sorted(implicit_after - implicit_before))
    folder = EVIDENCE.parent / 'order-blocks' / target; folder.mkdir(parents=True, exist_ok=True)
    write_json(folder / (label + '.json'), record)
    return record


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('target'); p.add_argument('source'); p.add_argument('functions', nargs='*')
    p.add_argument('--block', action='store_true', help='Diagnostic compound move of the named definitions as one historical block (no promotion).')
    a = p.parse_args()
    if a.block:
        record = probe_block(a.target, a.source, list(a.functions))
        print(json.dumps({k: v for k, v in record.items() if k not in ('scope', 'size_changes')}, indent=1))
    else:
        record = probe(a.target, a.source, tuple(a.functions))
        print('safe moves:', [r['move'] for r in record['results'] if r.get('compile') == 'OK' and r.get('gains') and not r.get('losses') and not r.get('new_implicit_declarations')])
