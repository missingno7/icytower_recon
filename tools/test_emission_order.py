"""Emission-order context and probe-driven single-move admission controls."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import ROOT, read_json, identity
from emission_order import emission_context, priority_adjustment, move_edit, candidate_moves, move_plans, _definition_spans


def report(order_hist, order_cand, exact):
    rows = []
    for i, name in enumerate(order_hist):
        rows.append({'name': name, 'va': 1000 + 100 * i, 'candidate_offset': 100 * order_cand.index(name), 'status': 'FUNCTION_MATCH' if name in exact else 'DIFFER', 'original_size': 50})
    return {'functions': rows}


class EmissionContextTests(unittest.TestCase):
    def test_frontier_requires_exact_in_order_prefix(self):
        r = report(['a', 'b', 'c', 'd'], ['a', 'b', 'c', 'd'], {'a', 'b'})
        c = emission_context(r, 'c')
        self.assertTrue(c['frontier']); self.assertTrue(c['predecessor_same']); self.assertTrue(c['predecessor_exact'])
        self.assertEqual(priority_adjustment(c)[0], 15)
        d = emission_context(r, 'd')
        self.assertFalse(d['frontier']); self.assertFalse(d['predecessor_exact']); self.assertEqual(priority_adjustment(d)[0], -5)
        # An exact prefix in the wrong candidate order is not the frontier.
        r2 = report(['a', 'b', 'c', 'd'], ['b', 'a', 'c', 'd'], {'a', 'b'})
        self.assertFalse(emission_context(r2, 'c')['frontier'])
        self.assertEqual(priority_adjustment(emission_context(r2, 'c'))[0], -10)
        self.assertEqual(emission_context(r2, 'c')['cu_same_predecessor_count'], 1)  # only d keeps its predecessor
        self.assertIsNone(emission_context(r2, 'zzz'))
        self.assertEqual(priority_adjustment(None), (0, None))

    def test_real_main_context_matches_recorded_orders(self):
        r = read_json(ROOT / 'docs/current/reports/game-main.json')
        c = emission_context(r, 'get_version_str')
        self.assertEqual(c['historical_position'], 0); self.assertIsNone(c['historical_predecessor'])
        self.assertTrue(c['predecessor_exact'])
        for f in r['functions']:
            ctx = emission_context(r, f['name'])
            self.assertEqual(ctx['cu_function_count'], len(r['functions']))


class MoveTests(unittest.TestCase):
    text = '/* head */\nint a(void) { return 1; }\n\nextern int z;\n\n/* about b */\nint b(void) { return 2; }\n\nint c(void) { return 3; }\n'

    def test_move_edit_keeps_bodies_and_leading_comment(self):
        from interface_tasks import patch_text
        from source_scope import function_span
        spans = _definition_spans(self.text)
        edits = move_edit(self.text, spans, 'b', 'c')
        new = patch_text(self.text, edits)
        self.assertLess(new.index('int c('), new.index('int b('))
        self.assertIn('/* about b */\nint b(void)', new)
        self.assertIn('extern int z;', new)
        for name in ('a', 'b', 'c'):
            x, y = function_span(self.text, name); p, q = function_span(new, name)
            self.assertEqual(self.text[x:y], new[p:q])

    def test_candidate_moves_list_only_out_of_order_functions(self):
        spans = _definition_spans(self.text)
        self.assertEqual(candidate_moves(self.text, spans, {'a': 10, 'b': 30, 'c': 20}), [('b', 'c'), ('c', 'a')])
        self.assertEqual(candidate_moves(self.text, spans, {'a': 10, 'b': 20, 'c': 30}), [])

    def fixture(self, results, stale=False, source_stale=False):
        import emission_order
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'src').mkdir(); (root / 'docs/attempts/order-moves').mkdir(parents=True); (root / 'docs/current/reports').mkdir(parents=True)
            src = root / 'src/x.c'; src.write_text(self.text)
            rep = root / 'docs/current/reports/game-x.json'; rep.write_text('{"build": {"target": "game-x", "object": {"size": 1, "sha256": "obj"}}}')
            ledger = {'src/x.c': {'verified_report': 'docs/current/reports/game-x.json', 'verified_report_identity': identity(rep)}}
            record = {'target': 'game-x', 'source': 'src/x.c', 'source_identity': identity(src), 'object_identity': {'size': 1, 'sha256': 'obj'} if not stale else {'size': 0, 'sha256': 'x'}, 'results': results}
            (root / 'docs/attempts/order-moves/game-x.json').write_text(__import__('json').dumps(record))
            if source_stale: src.write_text(self.text + '\n')
            with patch.object(emission_order, 'ROOT', root), patch.object(emission_order, 'EVIDENCE', root / 'docs/attempts/order-moves'):
                return move_plans({'source': 'src/x.c'}, ledger)

    def test_move_plans_admit_only_gains_without_regression_on_current_inputs(self):
        good = {'move': 'b', 'after': 'c', 'compile': 'OK', 'gains': ['b'], 'losses': []}
        plans = self.fixture([good])
        self.assertEqual([p['function'] for p in plans], ['move_x_b']); self.assertEqual(plans[0]['difficulty'], 'CHEAP')
        self.assertEqual(len(plans[0]['changes']), 2); self.assertEqual(plans[0]['moved_function'], 'b')
        self.assertTrue(all(e['file'] == 'src/x.c' for e in plans[0]['changes']))
        for bad in (dict(good, losses=['a']), dict(good, gains=[]), dict(good, compile='FAILED', gains=['b']), dict(good, move='nope'), dict(good, new_implicit_declarations=['b'])):
            self.assertEqual(self.fixture([bad]), [], bad)
        self.assertEqual(self.fixture([good], stale=True), [])
        self.assertEqual(self.fixture([good], source_stale=True), [])


if __name__ == '__main__': unittest.main()
