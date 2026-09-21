"""Pool-aligned read-only literal content diagnosis.

A CU's anonymous read-only literals are emitted in one pool. When several candidate
literals locate uniquely in the original read-only data and agree on a base, the pool
order matches history over that run, and every candidate literal in the run has a
historical address base+addend without consulting any instruction operand. A candidate
string whose historical counterpart at that address differs is a literal content
difference; it is proposed as a repair only when the following literals re-synchronize
under the implied length delta (or the next unique anchor confirms the shifted base).
Proposals are source evidence for the verifier-guarded edit path, never a proof.
"""
import json
import re
from difflib import SequenceMatcher
from pathlib import Path
from common import ROOT, identity, read_json, write_json
from binary import Binary

EVIDENCE = ROOT / 'docs/attempts/pool-literals'


def c_escape(text):
    out = ''
    for ch in text:
        if ch == '\\': out += '\\\\'
        elif ch == '"': out += '\\"'
        elif ch == '\n': out += '\\n'
        elif ch == '\t': out += '\\t'
        elif ch == '\r': out += '\\r'
        elif 32 <= ord(ch) < 127: out += ch
        else: out += '\\x%02x' % ord(ch)
    return out


def cstring(data, offset, limit=300):
    end = data.find(b'\0', offset, offset + limit)
    return data[offset:end + 1] if end >= 0 else None


def printable(literal):
    return literal is not None and len(literal) >= 2 and all(32 <= c < 127 or c in (9, 10, 13) for c in literal[:-1])


def pool_references(report):
    refs = {}
    for f in report['functions']:
        for r in f.get('relocations', []):
            if r['symbol'] == '.rdata': refs.setdefault(r['addend'], set()).add(f['name'])
    return refs


def locate_all(haystacks, needle):
    out = []
    for data, base in haystacks:
        start = 0
        while True:
            i = data.find(needle, start)
            if i < 0: break
            out.append(base + i); start = i + 1
    return out


def diagnose(report, pool, exe):
    """Return anchors and proposed string repairs for one CU pool."""
    haystacks = [(exe.section_bytes(s), exe.image_base + s['rva']) for s in exe.sections if s['name'] == '.rdata']
    refs = pool_references(report)
    anchors = {}
    for addend in refs:
        literal = cstring(pool, addend)
        if printable(literal) and len(literal) > 2:
            locations = locate_all(haystacks, literal)
            if len(locations) == 1: anchors[addend] = locations[0] - addend
    ordered = sorted(refs)
    proposals = []; base = None; delta = 0; pending = []
    def confirm():
        proposals.extend(pending); pending.clear()
    for addend in ordered:
        if addend in anchors:
            # A unique anchor re-synchronizes the run; it confirms a pending chain only when its
            # own base equals the base implied by the accumulated length delta.
            if pending and anchors[addend] == base + delta: confirm()
            pending.clear(); base = anchors[addend]; delta = 0; continue
        literal = cstring(pool, addend)
        if base is None or not printable(literal): continue
        original = cstring(exe.at_va(base + delta + addend, 300), 0)
        if original is None or not printable(original):
            pending.clear(); base = None; continue
        if original == literal:
            if pending: confirm()
            continue
        if len(pending) >= 6: pending.clear(); base = None; continue
        # The historical text must start at a literal boundary, and a repair must be a
        # recognizable variant of the candidate (spacing, version digits), not a neighbour.
        boundary = exe.at_va(base + delta + addend - 1, 1) == bytes([0])
        similar = SequenceMatcher(None, literal, original).ratio() >= 0.5
        if not boundary or not similar: pending.clear(); base = None; continue
        pending.append({'addend': addend, 'historical_va': base + delta + addend, 'functions': sorted(refs[addend]),
                        'candidate': literal[:-1].decode('latin1'), 'historical': original[:-1].decode('latin1'),
                        'length_delta': len(original) - len(literal)})
        delta += len(original) - len(literal)
    return anchors, proposals


def source_repairs(source_text, proposals):
    """Turn proposals into unique-token string edits; ambiguous or absent tokens are reported, not edited."""
    edits = []; skipped = []
    for p in proposals:
        token = '"' + c_escape(p['candidate']) + '"'
        count = source_text.count(token)
        if count != 1:
            skipped.append({**p, 'token': token, 'token_count': count, 'reason': 'source token absent or ambiguous'}); continue
        start = source_text.index(token)
        edits.append({'start': start, 'end': start + len(token), 'before': token, 'after': '"' + c_escape(p['historical']) + '"', 'proposal': p})
    return edits, skipped


def run(target):
    ledger = read_json(ROOT / 'src/recovery.json')
    source, entry = next((s, e) for s, e in ledger.items() if read_json(ROOT / e['verified_report'])['build']['target'] == target)
    report = read_json(ROOT / entry['verified_report'])
    objp = Path(report['build']['command'][-1])
    if not (objp.exists() and identity(objp) == report['build']['object']):
        objp = ROOT / 'build/recovered-game/tdm-2' / target / 'unit.o'
    if not (objp.exists() and identity(objp) == report['build']['object']): raise ValueError('Verified object is unavailable for ' + target)
    obj = Binary(objp); sections = [s for s in obj.sections if s['name'] == '.rdata']
    if not sections: return None
    exe = Binary(ROOT / 'assets/icytower15.exe')
    anchors, proposals = diagnose(report, obj.section_bytes(sections[0]), exe)
    text = (ROOT / source).read_bytes().decode('cp1252')
    edits, skipped = source_repairs(text, proposals)
    record = {'scope': 'Pool-aligned literal content diagnosis from candidate pool bytes and original read-only data; operands are never consulted. Proposals are source evidence for a verifier-guarded edit, never a proof.',
              'target': target, 'source': source, 'object_identity': report['build']['object'], 'source_identity': identity(ROOT / source),
              'anchor_count': len(anchors), 'proposals': proposals, 'edits': edits, 'skipped': skipped}
    EVIDENCE.mkdir(parents=True, exist_ok=True); write_json(EVIDENCE / (target + '.json'), record)
    return record


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('targets', nargs='+'); a = p.parse_args()
    for t in a.targets:
        r = run(t)
        if r is None: print(t, 'no read-only pool'); continue
        print(t, 'anchors', r['anchor_count'], 'proposals', len(r['proposals']), 'unique-token edits', len(r['edits']), 'skipped', len(r['skipped']))
        for e in r['edits']: print('   ', e['proposal']['functions'][:2], e['before'][:60], '->', e['after'][:60])
