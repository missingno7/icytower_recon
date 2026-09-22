"""Every access to one local's stack slot in an original function (diagnostic only; never a proof).

A reconstruction often writes a value the original writes and then stops, because the statements that
READ that value are missing; GCC then deletes the write as dead and the body compiles short with no
obvious cause.  This lists, for a DWARF local or a raw slot, every instruction in the original that
touches it, with the historical source line, so the missing readers can be found.

    python tools/local_slot_trace.py game-main play rank_y
    python tools/local_slot_trace.py game-main play --slot -0x940

Slots are reused across scopes, so a slot's accesses can belong to several locals: the source line
tells them apart.  Read or write is inferred from the operand position and is a hint, not evidence.
"""
import argparse, bisect, re
from common import ROOT, read_json
from recovery_pipeline import original_slice


def function(target, fn):
    ledger = read_json(ROOT / 'src/recovery.json')
    for source, entry in ledger.items():
        if not entry.get('verified_report'): continue
        rep = read_json(ROOT / entry['verified_report'])
        if rep['build']['target'] == target: break
    return source, next(x for x in rep['functions'] if x['name'] == fn)


def slots_of(source, fn, name):
    """Every stack slot the DWARF gives that local, as signed offsets from ebp."""
    stem = source.split('/')[-1].rsplit('.', 1)[0]
    ev = read_json(ROOT / 'docs/current/function-evidence' / stem / (fn + '.json'))
    out = []
    for l in ev.get('locals', []):
        if l['name'] != name: continue
        loc = l.get('location') or ''
        m = re.search(r'DW_OP_breg5 \(ebp\): (-?\d+)', loc)
        if m: out.append(int(m.group(1)))
        m = re.search(r'DW_OP_fbreg: (-?\d+)', loc)
        if m: out.append(int(m.group(1)) + 8)      # frame base is ebp+8
    return out


def trace(target, fn, slot):
    source, f = function(target, fn)
    rows = [(i['address'] - f['va'], i['assembly']) for i in original_slice(f['va'], f['original_size'])]
    lines = {}
    for x in read_json(ROOT / 'evidence/census/line-mappings.json'):
        if f['va'] <= x['address'] < f['va'] + f['original_size']: lines[x['address'] - f['va']] = (x['file'], x['line'])
    keys = sorted(lines)
    text = '%s(%%ebp)' % ('-0x%x' % -slot if slot < 0 else '0x%x' % slot)
    out = []
    for off, asm in rows:
        if text not in asm: continue
        i = bisect.bisect_right(keys, off) - 1
        where = lines[keys[i]] if i >= 0 else ('?', 0)
        write = bool(re.search(r',\s*' + re.escape(text) + r'\s*$', asm)) and not asm.startswith(('cmp', 'test'))
        write = write or asm.startswith(('movl ', 'movb ', 'movw ', 'fistp'))
        kind = 'read+write' if asm.startswith(('inc', 'dec', 'add', 'sub', 'and', 'or ', 'xor', 'shl', 'sar')) and write else ('write' if write else 'read')
        out.append((off, where, kind, asm))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('function'); ap.add_argument('local', nargs='?')
    ap.add_argument('--slot', help='raw slot instead of a DWARF name, e.g. -0x940')
    a = ap.parse_args()
    source, _ = function(a.target, a.function)
    slots = [int(a.slot, 0)] if a.slot else slots_of(source, a.function, a.local)
    if not slots: raise SystemExit('no stack slot for that local (it may live in a register; check --blocks)')
    for slot in slots:
        rows = trace(a.target, a.function, slot)
        print('%s at %s(%%ebp): %d accesses' % (a.local or a.slot, '-0x%x' % -slot if slot < 0 else hex(slot), len(rows)))
        for off, (file, line), kind, asm in rows:
            print('  %6d  %s:%-5d %-5s %s' % (off, file, line, kind, asm))


if __name__ == '__main__':
    main()
