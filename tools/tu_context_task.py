"""TU_CONTEXT: one atomic translation-unit context transaction.

A transaction is a complete generated edit set for one source file: definition order (historical
DWARF order or an explicit list), complete retained body replacements (explicit evidence files,
one definition each), historically evidenced storage classes, and forward prototypes derived from
the definitions themselves.  Component edits are never judged separately; the unit is compiled
once and the FINAL state is accepted or rejected as a whole.

Strict final-state gate (in addition to every existing verifier rule):
  * every function that was FUNCTION_MATCH before is FUNCTION_MATCH after (no_regressions);
  * every definition not named in `bodies` is byte-identical to its production island;
  * every replaced body equals its retained evidence file (identity recorded in the plan);
  * no new implicit declarations; no forbidden code-generation directives introduced;
  * no proven data owner regressed; ordinary link still succeeds; fresh locked identities.
Nothing here changes the meaning of FUNCTION_MATCH.

Commands: plan NAME SPEC.json | begin NAME | apply NAME | check NAME | promote NAME | abort NAME
"""
import argparse, json, os, re, subprocess, sys
from pathlib import Path
from common import ROOT, read_json, write_json, identity
from grinder_task import SESSION, snapshot_files
from promote_function import promotion_lock, no_regressions, commit_reports, JOURNAL
from refresh_recovery import validate_ledger
from recovery_pipeline import fresh_verify, validate_report, CURRENT

PLANS = ROOT / 'docs/current/tu-context-tasks'
TRANSACTIONS = ROOT / 'docs/attempts/tu-context/transactions'
CRLF = chr(13) + chr(10); LF = chr(10)
FORBIDDEN = r'\b(?:asm|__asm__|__asm|__attribute__|volatile)\b|^\s*#\s*pragma'


def plan(name, spec_path):
    from tu_context_probe import build_text, islands, retained_body
    spec = read_json(Path(spec_path)); target = spec['target']; source = spec['source']
    ledger = read_json(ROOT / 'src/recovery.json'); validate_ledger(ledger)
    if ledger[source]['verified_report'] and read_json(ROOT / ledger[source]['verified_report'])['build']['target'] != target: raise ValueError('target/source mismatch')
    new, edits, headers = build_text(target, source, spec)
    text = (ROOT / source).read_bytes().decode('cp1252')
    old_isl = {i['name']: i for i in islands(text)}; new_isl = {i['name']: i for i in islands(new)}
    if set(old_isl) != set(new_isl): raise ValueError('Definition set changed: ' + str(set(old_isl) ^ set(new_isl)))
    statics = set(edits['statics'])
    preserved = [n for n in old_isl if n not in edits['bodies'] and island_key(old_isl[n], n in statics) == island_key(new_isl[n], n in statics)]
    if len(preserved) != len(old_isl) - len(edits['bodies']): raise ValueError('A definition island changed without a retained body: ' + str([n for n in old_isl if n not in edits['bodies'] and n not in preserved]))
    for n in edits['bodies']:
        if island_key(new_isl[n], n in statics, definition_only=True) != island_key({'text': retained_body(ROOT / edits['bodies'][n]['path'])['text']}, n in statics): raise ValueError('Planned island differs from retained body: ' + n)
    from source_scope import sanitized
    if len(re.findall(FORBIDDEN, sanitized(new), re.M)) > len(re.findall(FORBIDDEN, sanitized(text), re.M)): raise ValueError('Transaction introduces forbidden code-generation directives')
    files = [source] + sorted(headers)
    card = {'schema': 1, 'task_kind': 'TU_CONTEXT', 'function': name, 'source': source, 'sources': files, 'target': target, 'affected_targets': [target],
            'difficulty': 'CHEAP', 'priority': 200, 'spec': spec, 'edits': edits, 'source_identities': {f: identity(ROOT / f) for f in files},
            'new_text_identity': identity_text(new), 'new_header_identities': {h: identity_text(t) for h, t in headers.items()}, 'preserved_definitions': sorted(preserved), 'replaced_definitions': sorted(edits['bodies']),
            'body_edit_allowed': False, 'state': 'TU_CONTEXT_TRANSACTION',
            'begin_command': 'python tools/tu_context_task.py begin ' + name, 'apply_command': 'python tools/tu_context_task.py apply ' + name,
            'verification_command': 'python tools/tu_context_task.py check ' + name, 'promotion_command': 'python tools/tu_context_task.py promote ' + name,
            'reason': 'Atomic translation-unit context transaction: definition order, retained bodies and evidenced declarations are compiled together and accepted only on the final unit state (no exact-function or data-owner regression).'}
    PLANS.mkdir(parents=True, exist_ok=True); write_json(PLANS / (name + '.json'), card)
    print('planned TU_CONTEXT', name, ':', len(edits['order']), 'ordered definitions,', len(edits['bodies']), 'retained bodies,', len(preserved), 'byte-preserved islands')
    return card


def island_key(island, static_evidenced=False, definition_only=False):
    """Comparison key for a definition island: line endings and outer whitespace ignored, and, when the
    storage class is historically evidenced, a leading `static` ignored.  Nothing inside the body is normalized."""
    t = island['text'].replace(CRLF, LF).strip()
    if definition_only:
        m = re.match(r'(?s)(?:/\*.*?\*/\s*|//[^\n]*\n\s*)*', t); t = t[m.end():] if m else t
    if static_evidenced: t = re.sub(r'^static\s+', '', t, count=1)
    return t


def identity_text(text):
    import hashlib
    return {'size': len(text.encode('cp1252')), 'sha256': hashlib.sha256(text.encode('cp1252')).hexdigest()}


def _card(name):
    path = PLANS / (name + '.json')
    if not path.exists(): raise ValueError('No TU_CONTEXT plan: ' + name)
    return read_json(path)


def begin(name):
    if SESSION.exists(): raise ValueError('Finish the active task first')
    card = _card(name); source = card['source']
    ledger = read_json(ROOT / 'src/recovery.json'); validate_ledger(ledger)
    for path, ident in card['source_identities'].items():
        if identity(ROOT / path) != ident: raise ValueError('Plan is stale for ' + path + '; re-plan against the current source')
    for n, b in card['edits']['bodies'].items():
        if identity(ROOT / b['path']) != b['identity']: raise ValueError('Retained body changed since planning: ' + n)
    with promotion_lock():
        link = ROOT / 'build/recovered-game/tdm-2/link.json'
        session = {'kind': 'TU_CONTEXT', 'function': name, 'plan': card, 'files': snapshot_files(), 'ledger': identity(ROOT / 'src/recovery.json'),
                   'source': source, 'source_text': (ROOT / source).read_bytes().decode('cp1252'), 'verify_only': False,
                   'header_texts': {h: (ROOT / h).read_bytes().decode('cp1252') for h in card['sources'][1:]},
                   'baseline_link': read_json(link) if link.exists() else None}
        write_json(SESSION, session)
    print('TU_CONTEXT', name, 'session started;', len(card['edits']['order']), 'ordered definitions')


def _session(name):
    if not SESSION.exists(): raise ValueError('No active task')
    s = read_json(SESSION)
    if s.get('kind') != 'TU_CONTEXT' or s['function'] != name: raise ValueError('Different task is active')
    return s


def validate_scope(session):
    current = snapshot_files(); before = session['files']; source = session['source']; allowed = set(session['plan']['sources'])
    for path in set(current) | set(before):
        if path not in allowed and current.get(path) != before.get(path): raise ValueError('Out-of-scope edit: ' + path)
    text = (ROOT / source).read_bytes().decode('cp1252')
    if text != session['source_text'] and identity_text(text) != session['plan']['new_text_identity']:
        raise ValueError('Source differs from both the production text and the planned transaction text')
    for h, old in session['header_texts'].items():
        t = (ROOT / h).read_bytes().decode('cp1252')
        if t != old and identity_text(t) != session['plan']['new_header_identities'][h]: raise ValueError('Header differs from both production and planned text: ' + h)
        if (t != old) != (text != session['source_text']): raise ValueError('Transaction files must be applied together: ' + h)
    return text


def apply(name):
    s = _session(name); card = s['plan']
    validate_scope(s)
    from tu_context_probe import build_text
    new, edits, headers = build_text(card['target'], card['source'], card['spec'])
    if identity_text(new) != card['new_text_identity'] or json.loads(json.dumps(edits)) != card['edits']: raise ValueError('Regenerated transaction differs from the plan; re-plan')
    for h, t in headers.items():
        if identity_text(t) != card['new_header_identities'][h]: raise ValueError('Regenerated header differs from the plan: ' + h)
    (ROOT / card['source']).write_bytes(new.encode('cp1252'))
    for h, t in headers.items(): (ROOT / h).write_bytes(t.encode('cp1252'))
    print('applied TU_CONTEXT', name, 'to', ', '.join(card['sources']))


def _acceptance(s, report, old):
    """Strict final-state predicate beyond no_regressions."""
    from interfaces import declarations
    from tu_context_probe import islands, retained_body
    card = s['plan']
    no_regressions(old, report)
    before_implicit = {d['name'] for d in declarations(old.get('interfaces_aux', '')) if d['kind'] == 'IC'}
    after_implicit = {d['name'] for d in declarations(report.get('interfaces_aux', '')) if d['kind'] == 'IC'}
    if after_implicit - before_implicit: raise ValueError('New implicit declarations: ' + ', '.join(sorted(after_implicit - before_implicit)))
    owners = lambda r: {(tuple(o['scope']), o['name'], o['original_va'], o['size']) for o in r.get('object_ownership', {}).get('accepted', [])}
    if owners(old) - owners(report): raise ValueError('Proven data owner regressed: ' + str(sorted(owners(old) - owners(report))[:3]))
    if report.get('unresolved_text_relocations') and not old.get('unresolved_text_relocations'): raise ValueError('Unresolved text relocations appeared')
    text = (ROOT / card['source']).read_bytes().decode('cp1252'); isl = {i['name']: i for i in islands(text)}
    old_isl = {i['name']: i for i in islands(s['source_text'])}; statics = set(card['edits']['statics'])
    if set(isl) != set(old_isl): raise ValueError('Definition set changed')
    for n in card['preserved_definitions']:
        if island_key(isl[n], n in statics) != island_key(old_isl[n], n in statics): raise ValueError('Preserved definition changed: ' + n)
    for n, b in card['edits']['bodies'].items():
        if identity(ROOT / b['path']) != b['identity']: raise ValueError('Retained body changed: ' + n)
        if island_key(isl[n], n in statics, definition_only=True) != island_key({'text': retained_body(ROOT / b['path'])['text']}, n in statics):
            raise ValueError('Replaced body does not equal its retained evidence: ' + n)
    before_exact = sum(1 for f in old['functions'] if f['status'] == 'FUNCTION_MATCH'); after_exact = report['function_matches']
    return {'exact_before': before_exact, 'exact_after': after_exact,
            'gains': sorted(f['name'] for f in report['functions'] if f['status'] == 'FUNCTION_MATCH' and next(o for o in old['functions'] if o['name'] == f['name'])['status'] != 'FUNCTION_MATCH')}


def check(name):
    s = _session(name); card = s['plan']; target = card['target']; source = card['source']
    validate_scope(s)
    ledger = read_json(ROOT / 'src/recovery.json'); old = read_json(ROOT / ledger[source]['verified_report'])
    report = fresh_verify(target, dest=ROOT / 'build/tu-context/check' / name)
    try:
        result = _acceptance(s, report, old); verdict = 'ACCEPTABLE'
    except ValueError as exc:
        result = {'rejection': str(exc)}; verdict = 'REJECTED'
    hist = [f['name'] for f in sorted(report['functions'], key=lambda f: f['va'])]
    cand = [f['name'] for f in sorted(report['functions'], key=lambda f: (f.get('candidate_offset') is None, f.get('candidate_offset') or 0))]
    same = sum(1 for i, n in enumerate(hist) if i and cand.index(n) and cand[cand.index(n) - 1] == hist[i - 1])
    status = {f['name']: f['status'] for f in report['functions']}
    losses = sorted(f['name'] for f in old['functions'] if f['status'] == 'FUNCTION_MATCH' and status[f['name']] != 'FUNCTION_MATCH')
    gains = sorted(f['name'] for f in old['functions'] if f['status'] != 'FUNCTION_MATCH' and status[f['name']] == 'FUNCTION_MATCH')
    summary = {'task': name, 'verdict': verdict, 'matches_before': sum(1 for f in old['functions'] if f['status'] == 'FUNCTION_MATCH'), 'matches_after': report['function_matches'],
               'same_historical_predecessor': same, 'losses': losses, 'gains': gains, **result,
               'limit': 'Whole-unit final-state check on the applied transaction; not a promotion and not a function proof.'}
    TRANSACTIONS.mkdir(parents=True, exist_ok=True); write_json(TRANSACTIONS / (name + '-check.json'), {**summary, 'plan_edits': card['edits']})
    print(json.dumps(summary, indent=1))
    return verdict == 'ACCEPTABLE'


def promote(name):
    from promote_function import run
    with promotion_lock():
        s = _session(name); card = s['plan']; target = card['target']; source = card['source']
        validate_scope(s)
        if identity(ROOT / 'src/recovery.json') != s['ledger']: raise ValueError('Ledger changed during task')
        ledger = read_json(ROOT / 'src/recovery.json'); old = read_json(ROOT / ledger[source]['verified_report'])
        report = fresh_verify(target, dest=ROOT / 'build/acceptance' / target)
        result = _acceptance(s, report, old)
        print(run([sys.executable, 'tools/acceptance_tests.py', 'function']), end='')
        print(run([sys.executable, 'tools/recovered_game_link.py']), end='')
        link = read_json(ROOT / 'build/recovered-game/tdm-2/link.json')
        if not link['linked']: raise ValueError('Ordinary source link failed: ' + str(link.get('unresolved_symbols')))
        validate_report(report); validate_scope(s)
        commit_reports(ledger, {source: report}, link)
        TRANSACTIONS.mkdir(parents=True, exist_ok=True)
        write_json(TRANSACTIONS / (name + '.json'), {'task': name, 'plan': card, 'result': result, 'matches_after': report['function_matches'],
                   'source_identity_after': identity(ROOT / source), 'report': ledger[source]['verified_report'], 'state': 'PROMOTED_TU_CONTEXT',
                   'limit': 'Whole-unit transaction accepted on its final verified state; every function status inside remains the strict verifier verdict.'})
        write_json(PLANS / (name + '.json'), {**card, 'state': 'PROMOTED_TU_CONTEXT', 'transaction': (TRANSACTIONS / (name + '.json')).relative_to(ROOT).as_posix()})
        SESSION.unlink()
        print('PROMOTED TU_CONTEXT', name, 'exact', result['exact_before'], '->', result['exact_after'], 'gains', result['gains'])


def abort(name):
    s = _session(name)
    (ROOT / s['source']).write_bytes(s['source_text'].encode('cp1252'))
    for h, t in s['header_texts'].items(): (ROOT / h).write_bytes(t.encode('cp1252'))
    SESSION.unlink()
    print('aborted; production text restored')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['plan', 'begin', 'apply', 'check', 'promote', 'abort']); ap.add_argument('name'); ap.add_argument('spec', nargs='?')
    a = ap.parse_args()
    if a.action == 'plan': plan(a.name, a.spec)
    elif a.action == 'begin': begin(a.name)
    elif a.action == 'apply': apply(a.name)
    elif a.action == 'check': sys.exit(0 if check(a.name) else 1)
    elif a.action == 'promote': promote(a.name)
    else: abort(a.name)


if __name__ == '__main__':
    main()
