"""Aligned original-versus-candidate disassembly for one function (diagnostic only; never a proof).

    python tools/aligned_view.py diff <target> <function> [context]      # masked shape diff (relocated targets/addresses masked)
    python tools/aligned_view.py sbs  <target> <function> [lo] [hi]      # side by side by function offset
    python tools/aligned_view.py orig <target> <function> [lo] [hi]      # original instructions only

Reads the latest owning-CU check (build/fast/<target>/comparison.json, written by check_function.py) or,
when absent, the ledger's verified report.  Masking hides relocation fields so only real register, operand
and control-flow shape differences remain; a masked-equal line can still differ in bytes.
"""
import sys, re, difflib, itertools
from common import ROOT, read_json
from recovery_pipeline import original_slice


def load(target, fn):
    fast = ROOT / 'build/fast' / target / 'comparison.json'
    rep = read_json(fast) if fast.exists() else None
    if rep is None or not any(x['name'] == fn for x in rep['functions']):
        ledger = read_json(ROOT / 'src/recovery.json')
        source = next(s for s, e in ledger.items() if e.get('verified_report') and read_json(ROOT / e['verified_report'])['build']['target'] == target)
        rep = read_json(ROOT / ledger[source]['verified_report'])
    f = next(x for x in rep['functions'] if x['name'] == fn)
    O = [(i['address'] - f['va'], i['assembly']) for i in original_slice(f['va'], f['original_size'])]
    C = [(i['address'] - f['candidate_offset'], i['assembly']) for i in f.get('instructions', [])] if f.get('candidate_offset') is not None else []
    return f, O, C


def norm(a):
    a = re.sub(r'<[^>]*>', '', a)
    a = re.sub(r'(call|j[a-z]+|jmp)\s+\*?0x[0-9a-f]+|(call|j[a-z]+)\s+[0-9a-f]+', lambda m: m.group(0).split()[0] + ' T', a)
    a = re.sub(r'\$0x[0-9a-f]{5,}', '$IMM', a)
    a = re.sub(r'(?<![\w(])0x[0-9a-f]{5,}(?!\()', 'MEM', a)
    return re.sub(r'\s+', ' ', a).strip()


def diff(target, fn, ctx=3):
    f, O, C = load(target, fn)
    on = [norm(a) for _, a in O]; cn = [norm(a) for _, a in C]
    sm = difflib.SequenceMatcher(None, on, cn, autojunk=False)
    print(fn, 'orig', f['original_size'], 'cand', f.get('candidate_size'), 'instr', len(O), len(C), 'status', f['status'])
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal': continue
        print('--- %s orig[%d:%d]@%d cand[%d:%d]@%d' % (tag, i1, i2, O[i1][0] if i1 < len(O) else -1, j1, j2, C[j1][0] if j1 < len(C) else -1))
        for k in range(max(0, i1 - ctx), i1): print('    %5d %s' % O[k])
        for k in range(i1, i2): print('  O %5d %s' % O[k])
        for k in range(j1, j2): print('  C %5d %s' % C[k])
        for k in range(i2, min(len(O), i2 + ctx)): print('    %5d %s' % O[k])


def sbs(target, fn, lo=0, hi=10 ** 9, original_only=False):
    f, O, C = load(target, fn)
    oi = [x for x in O if lo <= x[0] <= hi]; ci = [x for x in C if lo <= x[0] <= hi]
    if original_only:
        for a in oi: print('%6d  %s' % a)
        return
    for a, b in itertools.zip_longest(oi, ci, fillvalue=('', '')): print('%6s %-48s | %6s %s' % (a[0], a[1][:47], b[0], b[1][:47]))


if __name__ == '__main__':
    mode, target, fn = sys.argv[1:4]; rest = [int(x, 0) for x in sys.argv[4:]]
    if mode == 'diff': diff(target, fn, *(rest[:1] or [3]))
    elif mode == 'sbs': sbs(target, fn, *rest[:2])
    elif mode == 'orig': sbs(target, fn, *rest[:2], original_only=True)
    else: raise SystemExit(__doc__)
