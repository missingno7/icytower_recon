"""Plan-level tests for the TU_CONTEXT transaction (no compiler run): the generated edit set preserves every
unlisted definition byte-for-byte, replaces only explicitly retained bodies, refuses unevidenced declaration
changes and forbidden directives, and the island comparison key normalizes nothing inside a body."""
import json, re, tempfile, unittest
from pathlib import Path
from common import ROOT, read_json
from tu_context_probe import build_text, islands, historical_static, header_edits, retained_body
from tu_context_task import island_key, FORBIDDEN

SOURCE = 'src/main.c'; TARGET = 'game-main'
RETAINED = 'docs/attempts/game-main/handle_player_input-reconstruction.c'


class PlanConstraints(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / SOURCE).read_bytes().decode('cp1252')
        self.unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == SOURCE)

    def test_historical_order_preserves_every_island(self):
        new, edits, headers = build_text(TARGET, SOURCE, {'order': 'historical'})
        old = {i['name']: i for i in islands(self.text)}; cur = {i['name']: i for i in islands(new)}
        self.assertEqual(set(old), set(cur))
        for n in old: self.assertEqual(island_key(old[n]), island_key(cur[n]), n)
        self.assertNotEqual([i['name'] for i in islands(self.text)], [i['name'] for i in islands(new)])
        self.assertEqual(headers, {}); self.assertEqual(edits['bodies'], {})

    def test_retained_body_replaces_only_its_definition(self):
        new, edits, _ = build_text(TARGET, SOURCE, {'order': 'current', 'bodies': {'handle_player_input': RETAINED}})
        old = {i['name']: i for i in islands(self.text)}; cur = {i['name']: i for i in islands(new)}
        self.assertEqual([i['name'] for i in islands(self.text)], [i['name'] for i in islands(new)])
        for n in old:
            if n != 'handle_player_input': self.assertEqual(island_key(old[n]), island_key(cur[n]), n)
        self.assertEqual(island_key(cur['handle_player_input'], definition_only=True), island_key({'text': retained_body(ROOT / RETAINED)['text']}))
        self.assertEqual(edits['bodies']['handle_player_input']['path'], RETAINED)

    def test_retained_body_must_define_the_named_function(self):
        with self.assertRaises(ValueError): build_text(TARGET, SOURCE, {'order': 'current', 'bodies': {'checkMenuFocus': RETAINED}})

    def test_retained_body_file_must_hold_exactly_one_definition(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'two.c'; p.write_text('void a(void)\n{\n}\n\nvoid b(void)\n{\n}\n')
            with self.assertRaises(ValueError): retained_body(p)

    def test_main_has_no_historically_static_function(self):
        self.assertEqual(historical_static(self.unit), set())
        loadpng = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == 'src/loadpng.c')
        self.assertIn('really_load_png', historical_static(loadpng))

    def test_header_removal_requires_evidence(self):
        with self.assertRaises(ValueError): header_edits(self.unit, SOURCE, {'new_srand'}, {'include/game_services.h': ['new_srand']})
        with self.assertRaises(ValueError): header_edits(self.unit, SOURCE, set(), {'include/game_services.h': ['new_srand']})

    def test_forbidden_directives_are_counted(self):
        self.assertEqual(len(re.findall(FORBIDDEN, 'int x;\n', re.M)), 0)
        self.assertEqual(len(re.findall(FORBIDDEN, 'int x __attribute__((aligned(16)));\nasm("nop");\n#pragma GCC optimize("O0")\n', re.M)), 3)


class GeneratedCards(unittest.TestCase):
    def test_interleaved_unit_becomes_tu_context_card_gated_by_retained_probe(self):
        from source_order import plan_order
        ledger = read_json(ROOT / 'src/recovery.json')
        unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == SOURCE)
        card = plan_order(unit, ledger)
        self.assertEqual(card['task_kind'], 'TU_CONTEXT'); self.assertFalse(card['body_edit_allowed'])
        self.assertIn('tu_context_task.py promote order_main', card['promotion_command'])
        if card.get('probe_summary'):
            losses = card['probe_summary']['losses']
            self.assertEqual(card['difficulty'] == 'CHEAP', not losses and not card['probe_summary']['new_implicit_declarations'])
            if losses: self.assertIn(losses[0], card['reason'])

    def test_agreeing_unit_is_not_queued(self):
        from source_order import plan_order
        ledger = read_json(ROOT / 'src/recovery.json')
        unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == 'src/profile.c')
        self.assertEqual(plan_order(unit, ledger)['status'], 'DEFINITION_ORDER_AGREES')


class IslandKey(unittest.TestCase):
    def test_body_bytes_are_not_normalized(self):
        a = {'text': '/* c */\nint f(void)\n{\n    return 1;\n}\n'}
        self.assertEqual(island_key(a), island_key({'text': a['text'].replace('\n', '\r\n')}))
        self.assertNotEqual(island_key(a), island_key({'text': a['text'].replace('    return', '  return')}))
        self.assertEqual(island_key(a, definition_only=True), 'int f(void)\n{\n    return 1;\n}')
        self.assertEqual(island_key({'text': 'static int f(void)\n{\n}'}, static_evidenced=True), 'int f(void)\n{\n}')
        self.assertNotEqual(island_key({'text': 'static int f(void)\n{\n}'}), 'int f(void)\n{\n}')


if __name__ == '__main__':
    unittest.main()
