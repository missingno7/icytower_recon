"""Translation-unit compile-context model for GCC 4.4.1 (diagnostic; never a proof).

Two cross-function mechanisms were identified and reproduced exactly:

1. Emission order.  `cgraph_expand_all_functions` expands `cgraph_postorder` in reverse.  The
   postorder walks *caller* edges from every node in `cgraph_nodes` order (newest node first);
   nodes are created at definition (finalize, in source order) and, for callees without a body,
   during analysis (analysis order is the LIFO queue of needed functions, i.e. reverse definition
   order; static callees are analysed when first reached); caller lists are prepended as edges are
   created.  `emission_order` implements this and reproduces the `nm -n` order of the compiled
   object for every checked layout.

2. Peephole2 scratch cursor.  `peep2_find_free_register` keeps a file-static `search_ofs` that
   advances past every scratch register it hands out, across all functions of the unit.  The
   register chosen for `cmp mem,0` -> `mov mem,reg; test reg,reg` (and similar peepholes) in a
   function therefore depends on how many scratch registers every earlier-emitted function used.

Consequences: a body change or a definition move changes the emission order and the cursor for
every later function; exactness of a cursor-dependent function is honest only when its whole
historical emission prefix is exact and in order.  These facts drive the TU_CONTEXT transaction
model.  The strict verifier remains the only function-equality oracle.
"""
import re, json
from pathlib import Path
from common import ROOT, read_json


def emission_order(defs, callees):
    """GCC 4.4.1 expansion order for definitions `defs` = [(name, is_static)] in source order with
    per-function callee lists (call-site order, duplicates allowed, external names included)."""
    names = [n for n, _ in defs]; static = {n for n, s in defs if s}
    uid = {}
    def node(n):
        if n not in uid: uid[n] = len(uid)
    for n in names: node(n)
    queue = [n for n in names if n not in static][::-1]
    analyzed = set(); reachable = set(queue); edges = []
    while queue:
        n = queue.pop(0)
        if n in analyzed: continue
        analyzed.add(n)
        for c in callees.get(n, []): node(c); edges.append((n, c))
        for c in reversed(callees.get(n, [])):
            if c in static and c not in reachable: reachable.add(c); queue.insert(0, c)
    callers = {n: [] for n in uid}
    for caller, callee in edges: callers[callee].insert(0, caller)
    nodes = sorted(uid, key=lambda n: -uid[n])
    aux = {}; order = []; LAST = object()
    for n in nodes:
        if n in aux: continue
        node2 = n; aux[node2] = list(callers[node2]) or LAST; stack = []
        while node2 is not None:
            while aux[node2] is not LAST:
                lst = aux[node2]; e = lst[0]; aux[node2] = lst[1:] or LAST
                if e not in aux:
                    aux[e] = list(callers[e]) or LAST; stack.append(node2); node2 = e; break
            if aux[node2] is LAST:
                order.append(node2); node2 = stack.pop() if stack else None
    defined = set(names)
    return [n for n in reversed(order) if n in defined]


def callees_from_dump(dump_text, section='Optimized callgraph:'):
    """Per node: callee list in call-site order and (body, flags) from a -fdump-ipa-cgraph dump."""
    i = dump_text.index(section); body = dump_text[i + len(section):]
    m = re.search(r'\n(?=[A-Za-z][^\n/]*:\s*\n)', body); body = body[:m.start()] if m else body
    out = {}; meta = {}; cur = None
    for line in body.splitlines():
        m = re.match(r'^([A-Za-z_]\w*)/(\d+)\((-?\d+)\):(.*)$', line)
        if m: cur = m.group(1); meta[cur] = (int(m.group(3)), m.group(4)); out[cur] = []; continue
        if cur and line.strip().startswith('calls:'):
            # `name/uid` optionally followed by annotations; edges with zero frequency (after a noreturn
            # call such as exit) carry no `(N per call)` annotation, so the annotation must be optional.
            out[cur] = list(reversed(re.findall(r'(?<![\w/])([A-Za-z_]\w*)/\d+(?=\s|$)', line.split('calls:', 1)[1])))
    return out, meta


def object_order(obj, defined):
    """Function order of a COFF object from nm -n, restricted to `defined`."""
    import subprocess
    from build import COMPILERS
    nm = COMPILERS['tdm-2'] / 'bin' / 'nm.exe'
    out = subprocess.run([str(nm), '-n', '--defined-only', str(obj)], capture_output=True, text=True).stdout
    rows = [re.sub(r'@\d+$', '', l.split()[2])[1:] for l in out.splitlines() if len(l.split()) == 3 and l.split()[1] in ('T', 't')]
    return [r for r in rows if r in defined]


def historical_definition_order(unit, source):
    from emission_order import _historical_lines
    lines = _historical_lines(unit, source)
    return [n for n, _ in sorted(lines.items(), key=lambda kv: kv[1])], lines


def historical_callees(report, exe_functions):
    """Direct calls and tail jumps of every original function (library callees named by the census).
    Inlined builtin calls (strlen/memcpy/...) are not visible in the bytes, so this is a lower bound."""
    from recovery_pipeline import original_slice
    byva = {f['va']: f['name'] for f in report['functions']}
    out = {}
    for f in report['functions']:
        cs = []
        for r in original_slice(f['va'], f['original_size']):
            m = re.match(r'(?:call|jmp)\s+([0-9a-f]+)', r['assembly'])
            if not m: continue
            va = int(m.group(1), 16)
            if f['va'] <= va < f['va'] + f['original_size']: continue
            cs.append(byva.get(va) or exe_functions.get(va) or 'ext_%x' % va)
        out[f['name']] = cs
    return out


def exe_functions():
    out = {}
    for u in read_json(ROOT / 'src/units.json'):
        for f in u.get('functions', []): out[f['va']] = f['name']
    for r in read_json(ROOT / 'evidence/census/functions.json'):
        if r.get('va') and r.get('name'): out.setdefault(r['va'], re.sub(r'^_+|@\d+$', '', r['name']))
    return out


def context_table(report, ref_report, lines, finds=None):
    """Per-function context rows: historical/candidate predecessors, statuses, definition positions, scratch finds."""
    rows = report['functions']
    hist = [f['name'] for f in sorted(rows, key=lambda f: f['va'])]
    cand = [f['name'] for f in sorted(rows, key=lambda f: (f.get('candidate_offset') is None, f.get('candidate_offset') or 0))]
    status = {f['name']: f['status'] for f in rows}; ref = {f['name']: f for f in (ref_report or report)['functions']}
    hpos = {n: i for i, n in enumerate(hist)}; cpos = {n: i for i, n in enumerate(cand)}
    lpos = {n: i for i, n in enumerate(sorted(lines, key=lambda n: lines[n]))}
    finds = finds or {}
    table = []
    prefix_exact = True
    for i, n in enumerate(hist):
        hp = hist[i - 1] if i else None; cp = cand[cpos[n] - 1] if cpos[n] else None
        exact = status[n] == 'FUNCTION_MATCH'
        prefix_exact = prefix_exact and exact and cand[i] == n
        f = next(r for r in rows if r['name'] == n)
        table.append({'function': n, 'status': status[n], 'historical_position': i, 'candidate_position': cpos[n],
                      'historical_predecessor': hp, 'candidate_predecessor': cp, 'predecessor_same': hp == cp,
                      'historical_predecessor_exact': status.get(hp) == 'FUNCTION_MATCH' if hp else True,
                      'candidate_predecessor_exact': status.get(cp) == 'FUNCTION_MATCH' if cp else True,
                      'definition_position_historical': lpos.get(n), 'historical_line': lines.get(n),
                      'candidate_size': f.get('candidate_size'), 'historical_size': f['original_size'],
                      'body_completeness': round((f.get('candidate_size') or 0) / f['original_size'], 3) if f['original_size'] else None,
                      'peephole_scratch_finds': finds.get(n), 'cursor_dependent': bool(finds.get(n)),
                      'historical_prefix_exact_and_in_order': prefix_exact})
    return table
