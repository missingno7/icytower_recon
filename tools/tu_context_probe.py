"""Atomic translation-unit context experiments (supervisor diagnostic; never a proof).

GCC 4.4.1 compiles one translation unit as a whole: the emission order follows the call graph
(cgraph postorder over caller edges, node creation order, reversed expansion) and the peephole2
scratch-register cursor (`peep2_find_free_register`'s static `search_ofs`) carries over from one
function to the next in that emission order.  A single local edit therefore changes the compile
context of every later function, so monotonic single-edit acceptance can deadlock.

This tool applies a bounded SET of context edits to an isolated overlay, compiles the unit once
with the locked command, and reports the final TU state:

  * definition order (historical DWARF decl_line order, the current order, or an explicit list),
  * complete retained body replacements (explicit files only; no free-form mutation),
  * historically evidenced storage class changes (DWARF DW_AT_external),
  * generated forward prototypes derived from the moved definitions' own signatures.

Every metric here is a search heuristic.  Function equality is decided only by the strict
verifier (`experiment.compare`), and nothing in this module writes to production sources.
"""
import argparse, json, os, re, subprocess, hashlib
from pathlib import Path
from common import ROOT, read_json, write_json, identity

EVIDENCE = ROOT / 'docs/attempts/tu-context'
OUT = ROOT / 'build/tu-context'


def _spans(text):
    from emission_order import _definition_spans
    return _definition_spans(text)


def islands(text):
    """Top-level function definition islands: leading comment + definition, plus END_OF_MAIN() as WinMain."""
    from source_scope import sanitized
    spans = _spans(text); clean = sanitized(text)
    out = []
    for s in spans:
        sig = re.sub(r'\s+', ' ', text[s['start']:s['body_start']]).strip()
        out.append({'name': s['name'], 'start': s['cstart'], 'def_start': s['start'], 'end': s['end'], 'signature': sig, 'text': text[s['cstart']:s['end']]})
    m = re.search(r'(?m)^[ \t]*END_OF_MAIN\(\)[ \t]*;?[ \t]*$', clean)
    if m:
        out.append({'name': 'WinMain', 'start': m.start(), 'def_start': m.start(), 'end': m.end(), 'signature': None, 'text': text[m.start():m.end()], 'macro': True})
    out.sort(key=lambda i: i['start'])
    for a, b in zip(out, out[1:]):
        if a['end'] > b['start']: raise ValueError('Overlapping islands: ' + a['name'] + ' / ' + b['name'])
    return out


def historical_order(unit, source):
    from emission_order import _historical_lines
    lines = _historical_lines(unit, source)
    return [n for n, _ in sorted(lines.items(), key=lambda kv: kv[1])], lines


def historical_static(unit):
    """Functions the DWARF records without DW_AT_external (historically static).  Out-of-line instances of
    inline functions carry only DW_AT_abstract_origin; linkage is read from the resolved (origin-merged)
    attributes, so the four `inline` helpers of main.c are correctly seen as extern inline, not static."""
    from type_graph import graph
    g = graph(); out = set()
    for d in g.dies.values():
        if d['tag'] != 'DW_TAG_subprogram' or d.get('cu') != unit['cu_die'] or d.get('low_pc') is None or not d.get('name'): continue
        attrs = d.get('resolved') or d['attrs']
        if 'DW_AT_external' not in attrs and 'DW_AT_declaration' not in attrs: out.add(d['name'])
    return out


def prototype(signature):
    """A forward declaration derived from a definition's own signature text."""
    sig = signature.strip()
    return sig + ';'


def declaration_edits(skeleton, decl, nl):
    """Evidenced top-level declaration edits on the skeleton (never inside a definition island):
    `remove_top_level`: names whose hand-written top-level declaration is deleted (an `extern ...;`
    prototype, a `typedef struct {...} NAME;`, or a `#define NAME` line); `add_top_level`: [{name,
    declaration, after}] inserts a declaration directly after the declaration of an existing name
    (its historical DWARF neighbour); `includes_after`: {header: [names]} inserts `#include <name>`
    lines directly after `#include <header>`.  Evidence is recorded by the caller."""
    from source_scope import sanitized
    removed = []
    for name in decl.get('remove_top_level', []):
        clean = sanitized(skeleton); found = None
        m = re.search(r'(?m)^[ \t]*#[ \t]*define[ \t]+' + re.escape(name) + r'\b', clean)
        if m:   # a #define with its backslash-continued lines
            end = m.start()
            while True:
                nl_at = clean.find('\n', end); end = len(clean) if nl_at < 0 else nl_at + 1
                if nl_at < 0 or not clean[:nl_at].rstrip('\r').endswith('\\'): break
            found = (m.start(), end)
        patterns = [r'(?ms)^[ \t]*typedef[ \t]+struct[^{;]*\{.*?\}[ \t]*' + re.escape(name) + r'[ \t]*;[ \t]*\n?',
                    r'(?ms)^[ \t]*extern\b[^;{]*?\b' + re.escape(name) + r'[ \t]*\([^;{]*\)[ \t]*;[ \t]*\n?']
        for pat in patterns:
            if found: break
            m = re.search(pat, clean)
            if m: found = (m.start(), m.end())
        if not found: raise ValueError('No removable top-level declaration for ' + name)
        removed.append({'name': name, 'text': skeleton[found[0]:found[1]]})
        skeleton = skeleton[:found[0]] + skeleton[found[1]:]
    for item in decl.get('add_top_level', []):
        anchor = item['after']; name = item['name']
        m = re.search(r'(?m)^[A-Za-z_][^;()\n]*\b' + re.escape(anchor) + r'\b', skeleton)
        if m:   # end of that declaration: the first semicolon outside braces, plus its line break
            depth = 0; k = m.end()
            while k < len(skeleton):
                c = skeleton[k]
                if c == '{': depth += 1
                elif c == '}': depth -= 1
                elif c == ';' and depth == 0: break
                k += 1
            nl_at = skeleton.find(chr(10), k)
            m = type('M', (), {'end': staticmethod(lambda e=(len(skeleton) if nl_at < 0 else nl_at + 1): e)})
        if not m: raise ValueError('Declaration anchor not found: ' + anchor)
        if re.search(r'(?m)^[A-Za-z_][^;()\n]*\b' + re.escape(name) + r'\b[^;()\n]*;', skeleton): raise ValueError('Already declared: ' + name)
        skeleton = skeleton[:m.end()] + item['declaration'] + nl + skeleton[m.end():]
        removed.append({'name': name, 'added': item['declaration'], 'after': anchor})
    for header, names in (decl.get('includes_after') or {}).items():
        anchor = re.search(r'(?m)^[ \t]*#[ \t]*include[ \t]*<' + re.escape(header) + r'>[^\n]*\n', skeleton)
        if not anchor: raise ValueError('Include anchor not found: ' + header)
        skeleton = skeleton[:anchor.end()] + ''.join('#include <%s>%s' % (n, nl) for n in names) + skeleton[anchor.end():]
    return skeleton, removed


def layout(text, order, bodies=None, statics=(), prototypes='auto', keep_unlisted='end', declarations=None):
    """Build the overlay text: skeleton (all non-island text in its original order, with evidenced
    declaration edits), a generated prototype block, then the islands in `order`.  Islands not in `order`
    are appended in current order (keep_unlisted='end')."""
    bodies = bodies or {}
    isl = islands(text); byname = {i['name']: i for i in isl}
    # A retained body whose name has no island in the production source is an ADDED definition: a
    # historical function this file deliberately omits (an unresolved-ownership CU emits only what
    # the oracle has independently proved).  It takes its place from `order` like any other.
    added = [n for n in order if n not in byname and n in bodies]
    for n in added:
        byname[n] = {'name': n, 'start': 0, 'def_start': 0, 'end': 0, 'signature': bodies[n]['signature'], 'text': '', 'added': True}
    unknown = [n for n in order if n not in byname]
    if unknown: raise ValueError('Unknown definitions in order: ' + ', '.join(unknown))
    nl = '\r\n' if '\r\n' in text else '\n'
    pieces = []; pos = 0
    for i in isl:
        pieces.append(text[pos:i['start']]); pos = i['end']
    pieces.append(text[pos:])
    skeleton = ''.join(pieces)
    if declarations: skeleton, layout.removed = declaration_edits(skeleton, declarations, nl)
    else: layout.removed = []
    skeleton = re.sub(r'(?:\r?\n){3,}', nl + nl, skeleton)
    seq = list(order) + ([i['name'] for i in isl if i['name'] not in set(order)] if keep_unlisted == 'end' else [])
    protos = []
    for n in seq:
        i = byname[n]
        if i.get('macro'): continue
        sig = i['signature']
        if n in bodies: sig = re.sub(r'\s+', ' ', bodies[n]['signature']).strip()
        if n in statics and not sig.startswith('static '): sig = 'static ' + sig
        protos.append(prototype(sig))
    defs = []
    for n in seq:
        i = byname[n]; t = i['text']
        if n in bodies:
            lead = '' if i.get('added') else text[i['start']:i['def_start']]
            t = lead + bodies[n]['text']
        if n in statics and not i.get('macro'):
            lead = '' if i.get('added') else text[i['start']:i['def_start']]; body_text = bodies[n]['text'] if n in bodies else text[i['def_start']:i['end']]
            if not body_text.lstrip().startswith('static'): t = lead + 'static ' + body_text.lstrip()
        defs.append(t.strip('\r\n'))
    block = ''
    if prototypes == 'auto' and protos:
        block = nl + '/* Forward declarations; definitions follow in their original source order. */' + nl + nl.join(protos) + nl
    return skeleton.rstrip() + nl + block + nl + (nl + nl).join(defs) + nl


def retained_body(path):
    """A retained complete definition (exactly one function) from an evidence file."""
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    isl = islands(text)
    if len(isl) != 1: raise ValueError('Retained body file must contain exactly one definition: ' + str(path))
    i = isl[0]
    return {'name': i['name'], 'signature': i['signature'], 'text': text[i['def_start']:i['end']], 'identity': identity(Path(path))}


def masked_code(row):
    """Instruction bytes with relocation fields zeroed: detects code changes independent of placement."""
    data = bytearray(bytes.fromhex(''.join(i['bytes'] for i in row.get('instructions', []))))
    for r in row.get('relocations', []):
        o = r.get('function_offset')
        if o is not None and 0 <= o < len(data):
            for k in range(o, min(o + 4, len(data))): data[k] = 0
    return hashlib.sha256(bytes(data)).hexdigest()


def peephole_finds(dump_dir):
    """Scratch registers chosen by peephole2 per function, in emission order, from the csa/peephole2 dumps."""
    files = os.listdir(dump_dir)
    csa = [f for f in files if f.endswith('r.csa')]; p2 = [f for f in files if f.endswith('r.peephole2')]
    if not csa or not p2: return None
    def sections(path):
        t = Path(path).read_text(encoding='utf-8', errors='replace')
        return [(m.group(1), m.group(0)) for m in re.finditer(r'^;; Function (\w+) .*?(?=^;; Function |\Z)', t, re.S | re.M)]
    before = dict(sections(os.path.join(dump_dir, csa[0]))); out = []
    for name, s in sections(os.path.join(dump_dir, p2[0])):
        ids = set(re.findall(r'^\((?:insn|jump_insn|call_insn) (\d+) ', before.get(name, ''), re.M))
        regs = []
        for m in re.finditer(r'^\(insn (\d+) \d+ \d+ \d+ (.*?)(?=^\(|\Z)', s, re.M | re.S):
            if m.group(1) in ids: continue
            mm = re.match(r'\s*(?:\S+:\d+ )?\(set \(reg:\w+ \d+ (\w+)\)\s*\((?:mem|const_int)', m.group(2))
            if mm: regs.append((int(m.group(1)), mm.group(1)))
        out.append({'function': name, 'scratch': [r for _, r in sorted(regs)]})
    return out


def compile_overlay(target, source, new_text, label, dumps=True, headers=None, cgraph=False, extra_flags=()):
    from build import COMPILERS
    ledger = read_json(ROOT / 'src/recovery.json'); ref = read_json(ROOT / ledger[source]['verified_report']); build = ref['build']
    out = OUT / target / label; overlay = out / 'overlay'; (overlay / Path(source).parent).mkdir(parents=True, exist_ok=True)
    for f in out.glob('*.c.*'): f.unlink()
    (overlay / source).write_bytes(new_text.encode('cp1252'))
    for h, t in (headers or {}).items():
        (overlay / h).parent.mkdir(parents=True, exist_ok=True); (overlay / h).write_bytes(t.encode('cp1252'))
    args = list(build['command'])
    for flag, value in [('-MF', out / 'unit.d'), ('-aux-info', out / 'interfaces.aux'), ('-c', overlay / source), ('-o', out / 'unit.o')]: args[args.index(flag) + 1] = str(value)
    args[1:1] = ['-I' + str((ROOT / source).parent)]
    args[1:1] = ['-I' + str(overlay / Path(h).parent) for h in (headers or {})]
    args = [a if not (isinstance(a, str) and a.startswith('-I') and not os.path.isabs(a[2:])) else '-I' + str(ROOT / a[2:]) for a in args]
    args[1:1] = list(extra_flags)   # diagnostic-only flags; never used by evaluate() or by any promotion path
    if dumps: args[1:1] = ['-fdump-ipa-cgraph', '-fdump-rtl-csa', '-fdump-rtl-peephole2']
    elif cgraph: args[1:1] = ['-fdump-ipa-cgraph']
    env = os.environ.copy(); env['PATH'] = str(COMPILERS[build['compiler']] / 'bin') + os.pathsep + env['PATH']
    r = subprocess.run([str(x) for x in args], cwd=out, env=env, capture_output=True, text=True)
    return out, ref, build, r


def evaluate(target, source, new_text, label, edits, dumps=True, headers=None):
    from experiment import compare
    from recovery_pipeline import OBJDUMP
    from interfaces import declarations
    out, ref, build, r = compile_overlay(target, source, new_text, label, dumps, headers, cgraph=bool(edits.get('focus')))
    record = {'scope': 'Atomic translation-unit context experiment on an isolated overlay; diagnostic only, never a function proof or a production edit.',
              'target': target, 'source': source, 'label': label, 'edits': edits,
              'source_identity': identity(ROOT / source),
              'object_identity': build['object'],  # verified production object used as comparison baseline
              'compiler': build['compiler'], 'flags': build['flags'],
              'overlay_identity': hashlib.sha256(new_text.encode('cp1252')).hexdigest()}
    if r.returncode:
        errors = [l for l in r.stderr.splitlines() if 'error' in l][:8]
        record.update(compile='FAILED', errors=errors); write_json(EVIDENCE / target / (label + '.json'), record); return record
    record['compiled_object_identity'] = identity(out / 'unit.o')
    report = compare(out / 'unit.o', ref['historical_cu'], ROOT / 'assets/icytower15.exe', OBJDUMP)
    before = {f['name']: f for f in ref['functions']}; after = {f['name']: f for f in report['functions']}
    hist = [f['name'] for f in sorted(report['functions'], key=lambda f: f['va'])]
    cand = [f['name'] for f in sorted(report['functions'], key=lambda f: (f.get('candidate_offset') is None, f.get('candidate_offset') or 0))]
    cand_before = [f['name'] for f in sorted(ref['functions'], key=lambda f: (f.get('candidate_offset') is None, f.get('candidate_offset') or 0))]
    def pred(order): return {n: (order[i - 1] if i else None) for i, n in enumerate(order)}
    hp, cp, cbp = pred(hist), pred(cand), pred(cand_before)
    same = sum(1 for n in hist if hp[n] == cp.get(n)); same_before = sum(1 for n in hist if hp[n] == cbp.get(n))
    status_after = {n: after[n]['status'] for n in after}
    prefix = 0
    for n in hist:
        if status_after.get(n) == 'FUNCTION_MATCH' and cand[prefix] == n: prefix += 1
        else: break
    gains = sorted(n for n in before if before[n]['status'] != 'FUNCTION_MATCH' and status_after.get(n) == 'FUNCTION_MATCH')
    losses = sorted(n for n in before if before[n]['status'] == 'FUNCTION_MATCH' and status_after.get(n) != 'FUNCTION_MATCH')
    changed_bodies = set(edits.get('bodies', {}))
    code_changed = sorted(n for n in before if n in after and n not in changed_bodies and masked_code(before[n]) != masked_code(after[n]))
    sizes = {n: [before[n].get('candidate_size'), after[n].get('candidate_size'), before[n]['original_size']] for n in before if n in after and before[n].get('candidate_size') != after[n].get('candidate_size')}
    implicit_before = {d['name'] for d in declarations(ref.get('interfaces_aux', '')) if d['kind'] == 'IC'}
    implicit_after = {d['name'] for d in declarations((out / 'interfaces.aux').read_text(errors='replace')) if d['kind'] == 'IC'}
    finds = peephole_finds(out) if dumps else None
    finds_map = {x['function']: x['scratch'] for x in (finds or [])}
    unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == source)
    from tu_context_model import context_table, callees_from_dump, emission_order, object_order
    _, lines = historical_order(unit, source)
    table = context_table(report, ref, lines, finds_map)
    model_check = None
    dump_file = next((f for f in os.listdir(out) if f.endswith('i.cgraph')), None)
    if dump_file:
        callees, meta = callees_from_dump((out / dump_file).read_text(encoding='utf-8', errors='replace'))
        defs = edits.get('definition_order_with_static') or [(n, False) for n in edits.get('order', [])]
        if defs:
            defined = {n for n, (b, flags) in meta.items() if b >= 0 and 'needed' in flags}
            predicted = [n for n in emission_order(defs, callees) if n in defined]
            model_check = {'predicted_equals_object': predicted == object_order(out / 'unit.o', defined), 'predicted': predicted}
        if edits.get('focus'):
            # Source-level edges come from the pre-inlining section: a call GCC inlined into its caller
            # disappears from the optimized call graph without disappearing from the source.
            initial, _ = callees_from_dump((out / dump_file).read_text(encoding='utf-8', errors='replace'), 'Initial callgraph:')
            record['focus'] = focus_report(report, initial, callees, edits['focus'])
    record.update(compile='OK', context_table=table, emission_model=model_check, matches_before=ref['function_matches'], matches_after=report['function_matches'],
                  emission_order=cand, historical_order=hist, same_historical_predecessor={'before': same_before, 'after': same, 'total': len(hist)},
                  longest_exact_historical_prefix=prefix, at_historical_offset=sum(1 for n in hist if after[n].get('candidate_offset') == before[n].get('candidate_offset')),
                  gains=gains, losses=losses, code_changed_with_unchanged_body=code_changed, size_changes=sizes,
                  new_implicit_declarations=sorted(implicit_after - implicit_before),
                  statuses=status_after, whole_text_contribution_equal=report.get('whole_text_contribution_equal'),
                  peephole_scratch=finds, report_path=str((out / 'comparison.json').relative_to(ROOT)).replace('\\', '/'))
    write_json(out / 'comparison.json', report)
    write_json(EVIDENCE / target / (label + '.json'), record)
    return record


def focus_report(report, callees, optimized, focus):
    """Per focus function: historical direct callees (from the original bytes) versus the compiled call graph,
    size and emission positions.  Call-graph convergence is the structural goal for large bodies."""
    from tu_context_model import historical_callees, exe_functions
    hist_calls = historical_callees(report, exe_functions()) if focus else {}
    hist = [f['name'] for f in sorted(report['functions'], key=lambda f: f['va'])]
    cand = [f['name'] for f in sorted(report['functions'], key=lambda f: (f.get('candidate_offset') is None, f.get('candidate_offset') or 0))]
    out = {}
    for n in focus:
        f = next((x for x in report['functions'] if x['name'] == n), None)
        if not f: continue
        h = sorted(set(hist_calls.get(n, []))); c = sorted(set(callees.get(n, [])))
        inlined = sorted(set(c) - set(optimized.get(n, [])))
        key = lambda x: re.sub(r'^__builtin_', '', x).lstrip('_') if x != '_mangled_main' else x   # census `_errno` == cgraph `errno`
        hk = {key(x) for x in h}; ck = {key(x) for x in c}
        out[n] = {'status': f['status'], 'candidate_size': f.get('candidate_size'), 'historical_size': f['original_size'],
                  'historical_callees': h, 'current_callees': c, 'missing_edges': sorted(x for x in h if key(x) not in ck), 'extra_edges': sorted(x for x in c if key(x) not in hk),
                  'historical_position': hist.index(n), 'candidate_position': cand.index(n), 'inlined_into_this_caller': inlined,
                  'limit': 'Historical callees are the direct calls visible in the original bytes (inlined builtins invisible); current callees are the source-level edges before inlining. A callee listed in inlined_into_this_caller is called in the source but inlined here, so it is absent from the emitted call graph; history did not inline it.'}
    return out


def build_text(target, source, spec):
    """Overlay text from an edit spec: order ('historical'|'current'|list), bodies {name: path}, statics ('historical'|list), prototypes."""
    text = (ROOT / source).read_bytes().decode('cp1252')
    unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == source)
    isl = islands(text); current = [i['name'] for i in isl]
    order = spec.get('order', 'current')
    bodies = {n: retained_body(ROOT / p) for n, p in (spec.get('bodies') or {}).items()}
    # A retained body with no island in the production source is an added definition and takes its
    # historical place; it is not filtered out with the names this file does not define.
    emitted = set(current) | set(bodies)
    if order == 'historical':
        order, lines = historical_order(unit, source)
        order = [n for n in order if n in emitted]
    elif order == 'current': order = current + [n for n in bodies if n not in set(current)]
    for n, b in bodies.items():
        if b['name'] != n: raise ValueError('Retained body defines ' + b['name'] + ' not ' + n)
    statics = spec.get('statics') or []
    if statics == 'historical': statics = sorted(historical_static(unit) & set(current))
    new = layout(text, order, bodies, set(statics), spec.get('prototypes', 'auto'), declarations=spec.get('declarations'))
    headers = header_edits(unit, source, statics, spec.get('headers') or {})
    full = list(order) + [n for n in current if n not in set(order)]
    cur_static = {i['name'] for i in isl if i.get('signature') and 'static' in i['signature'].split()}
    edits = {'focus': spec.get('focus') or [], 'declarations': ({**spec['declarations'], 'removed_text': layout.removed} if spec.get('declarations') else {}), 'order': order, 'definition_order_with_static': [(n, (n in cur_static) or (n in set(statics))) for n in full], 'bodies': {n: {'path': spec['bodies'][n], 'identity': bodies[n]['identity']} for n in bodies}, 'statics': list(statics), 'prototypes': spec.get('prototypes', 'auto'),
             'headers': {h: {'removed_declarations': v['removed'], 'evidence': v['evidence']} for h, v in headers.items()}}
    return new, edits, {h: v['text'] for h, v in headers.items()}


def header_edits(unit, source, statics, requested):
    """Evidenced declaration removals from shared headers: {header: [names]}.  A name may be removed only when
    the DWARF records it without DW_AT_external in this CU (historically static), it is listed in `statics`, and
    no other source file references it.  Nothing else in a header may change."""
    from source_scope import sanitized
    hist_static = historical_static(unit); out = {}
    for header, names in requested.items():
        text = (ROOT / header).read_bytes().decode('cp1252'); new = text; removed = []; evidence = {}
        for n in names:
            if n not in hist_static or n not in statics: raise ValueError('No historical static evidence for ' + n)
            users = [str(p.relative_to(ROOT).as_posix()) for p in sorted((ROOT / 'src').glob('*.c')) if p.name != Path(source).name and re.search(r'\b' + re.escape(n) + r'\s*\(', sanitized(p.read_bytes().decode('cp1252')))]
            if users: raise ValueError(n + ' is referenced outside its CU: ' + ', '.join(users))
            pat = re.compile(r'(?m)^[^\n]*\b' + re.escape(n) + r'\s*\([^;]*\)\s*;[ \t]*\r?\n')
            m = pat.search(new)
            if not m: raise ValueError('Declaration of ' + n + ' not found in ' + header)
            new = new[:m.start()] + new[m.end():]; removed.append(n)
            evidence[n] = {'dwarf': 'DW_TAG_subprogram without DW_AT_external in CU ' + str(unit['cu_die']), 'other_cu_references': []}
        out[header] = {'text': new, 'removed': removed, 'evidence': evidence}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('target'); ap.add_argument('source'); ap.add_argument('label')
    ap.add_argument('--order', default='current', help="'historical', 'current', or a JSON list file")
    ap.add_argument('--body', action='append', default=[], help='name=path of a retained complete definition')
    ap.add_argument('--statics', default=None, help="'historical' or comma-separated names")
    ap.add_argument('--no-prototypes', action='store_true')
    ap.add_argument('--no-dumps', action='store_true')
    ap.add_argument('--header', action='append', default=[], help='header=name[,name] declarations to remove with historical static evidence')
    ap.add_argument('--focus', action='append', default=[], help='function whose historical-versus-compiled callee sets and positions are reported')
    ap.add_argument('--declarations', help='JSON file: {"remove_top_level": [names], "includes_after": {"allegro.h": ["winalleg.h"]}, "evidence": "..."}')
    a = ap.parse_args()
    order = a.order
    if order not in ('historical', 'current'): order = read_json(Path(order))
    spec = {'order': order, 'bodies': dict(b.split('=', 1) for b in a.body), 'prototypes': 'none' if a.no_prototypes else 'auto'}
    if a.statics: spec['statics'] = 'historical' if a.statics == 'historical' else a.statics.split(',')
    if a.header: spec['headers'] = {h: names.split(',') for h, names in (x.split('=', 1) for x in a.header)}
    spec['focus'] = a.focus
    if a.declarations: spec['declarations'] = read_json(Path(a.declarations))
    new, edits, headers = build_text(a.target, a.source, spec)
    rec = evaluate(a.target, a.source, new, a.label, edits, dumps=not a.no_dumps, headers=headers)
    keys = ['compile', 'errors', 'matches_before', 'matches_after', 'same_historical_predecessor', 'longest_exact_historical_prefix', 'at_historical_offset', 'gains', 'losses', 'code_changed_with_unchanged_body', 'new_implicit_declarations', 'whole_text_contribution_equal']
    print(json.dumps({k: rec.get(k) for k in keys if k in rec}, indent=1))
    for n, fr in (rec.get('focus') or {}).items():
        print('focus', n, json.dumps({k: fr[k] for k in ('status', 'candidate_size', 'historical_size', 'historical_position', 'candidate_position')}))
        print('  missing edges (%d):' % len(fr['missing_edges']), ' '.join(fr['missing_edges']))
        print('  extra edges (%d):' % len(fr['extra_edges']), ' '.join(fr['extra_edges']))
        if fr.get('inlined_into_this_caller'): print('  inlined here (%d):' % len(fr['inlined_into_this_caller']), ' '.join(fr['inlined_into_this_caller']))


if __name__ == '__main__':
    main()
