"""Plan-level tests for the TU_CONTEXT transaction (no compiler run): the generated edit set preserves every
unlisted definition byte-for-byte, replaces only explicitly retained bodies, refuses unevidenced declaration
changes and forbidden directives, and the island comparison key normalizes nothing inside a body."""
import json, re, tempfile, unittest
from pathlib import Path
from common import ROOT, read_json, identity
from tu_context_probe import build_text, islands, historical_static, header_edits, retained_body, layout
from tu_context_task import island_key, provenance_update, generated_include_identities, FORBIDDEN

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
        self.assertEqual([i['name'] for i in islands(self.text)], [i['name'] for i in islands(new)])
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
        unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == 'src/fld_adspot.c')
        card = plan_order(unit, ledger)
        self.assertEqual(card['task_kind'], 'TU_CONTEXT'); self.assertFalse(card['body_edit_allowed'])
        self.assertIn('tu_context_task.py promote order_fld_adspot', card['promotion_command'])
        if card.get('probe_summary'):
            losses = card['probe_summary']['losses']
            self.assertEqual(card['difficulty'] == 'CHEAP', not losses and not card['probe_summary']['new_implicit_declarations'])
            if losses: self.assertIn(losses[0], card['reason'])

    def test_promoted_main_order_is_not_queued(self):
        from source_order import plan_order
        ledger = read_json(ROOT / 'src/recovery.json')
        unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == SOURCE)
        self.assertEqual(plan_order(unit, ledger)['status'], 'DEFINITION_ORDER_AGREES')

    def test_agreeing_unit_is_not_queued(self):
        from source_order import plan_order
        ledger = read_json(ROOT / 'src/recovery.json')
        unit = next(u for u in read_json(ROOT / 'src/units.json') if u['source'] == 'src/profile.c')
        self.assertEqual(plan_order(unit, ledger)['status'], 'DEFINITION_ORDER_AGREES')


class DeclarationEdits(unittest.TestCase):
    def test_generated_early_include_is_identity_bound(self):
        spec = {'declarations': {'includes_after': {'allegro.h': ['recovered/Treplay_post.h']}}}
        identities = generated_include_identities(spec)
        self.assertEqual(list(identities), ['include/recovered/Treplay_post.h'])
        self.assertEqual(identities['include/recovered/Treplay_post.h'],
                         identity(ROOT / 'include/recovered/Treplay_post.h'))
        with self.assertRaisesRegex(ValueError, 'one recovered type header'):
            generated_include_identities({'declarations': {'includes_after': {
                'allegro.h': ['recovered/../Treplay_post.h']}}})

    def test_production_plan_rejects_diagnostic_research_base(self):
        from tu_context_task import plan
        with tempfile.TemporaryDirectory() as tmp:
            spec = Path(tmp) / 'research.json'
            spec.write_text(json.dumps({'target': 'game-profile', 'source': 'src/profile.c',
                                        'research_base': 'docs/attempts/example.c'}))
            with self.assertRaisesRegex(ValueError, 'diagnostic only'):
                plan('forbidden_research_base_test', spec)

    def test_removes_only_named_top_level_declarations_and_inserts_includes(self):
        from tu_context_probe import declaration_edits
        text = ('#include <allegro.h>\n#include "x.h"\nextern void *__attribute__((stdcall)) ShellExecuteA(void *hwnd,\n    const char *op);\n'
                'typedef struct {\n    unsigned short a;\n    char *b;\n} WSADATA;\nextern int keep(int);\n'
                '#define MAKEWORD(a,b) ((unsigned short)(((unsigned char)(a)) | \\\n    ((unsigned short)((unsigned char)(b)) << 8)))\n#define LOBYTE(v) ((v) & 0xff)\nint itrcheck;\n')
        new, removed = declaration_edits(text, {'remove_top_level': ['ShellExecuteA', 'WSADATA', 'MAKEWORD'], 'includes_after': {'allegro.h': ['winalleg.h']}}, '\n')
        self.assertEqual([r['name'] for r in removed], ['ShellExecuteA', 'WSADATA', 'MAKEWORD'])
        self.assertEqual(new, '#include <allegro.h>\n#include <winalleg.h>\n#include "x.h"\nextern int keep(int);\n#define LOBYTE(v) ((v) & 0xff)\nint itrcheck;\n')
        with self.assertRaises(ValueError): declaration_edits(text, {'remove_top_level': ['itrcheck']}, '\n')
        with self.assertRaises(ValueError): declaration_edits(text, {'includes_after': {'nothere.h': ['a.h']}}, '\n')

    def test_duplicate_bare_prototypes_can_be_removed_before_late_type_visibility(self):
        from tu_context_probe import declaration_edits
        text = ('void draw_profile_selector(char *p);\n'
                'void draw_profile_selector(char *p);\n'
                'int keep(void);\n')
        new, removed = declaration_edits(text, {'remove_top_level': ['draw_profile_selector', 'draw_profile_selector']}, '\n')
        self.assertEqual(new, 'int keep(void);\n')
        self.assertEqual(len(removed), 2)

    def test_generated_header_visibility_can_follow_an_unchanged_definition(self):
        text = 'int before(void) { return 1; }\nint after(void) { return before(); }\n'
        late = [{'after': 'before', 'header': 'recovered/Tavailable_profile.h',
                 'declarations': ['extern int rebuild_profile_list(Tavailable_profile **profs);']}]
        new = layout(text, ['before', 'after'], prototypes='none', late_declarations=late)
        self.assertLess(new.index('return 1;'), new.index('#include "recovered/Tavailable_profile.h"'))
        self.assertLess(new.index('#include "recovered/Tavailable_profile.h"'), new.index('int after(void)'))
        old = {i['name']: i for i in islands(text)}; cur = {i['name']: i for i in islands(new)}
        for name in old: self.assertEqual(island_key(old[name]), island_key(cur[name]))
        with self.assertRaises(ValueError):
            layout(text, ['before', 'after'], prototypes='none',
                   late_declarations=[{'after': 'before', 'header': 'private.h', 'declarations': []}])


class IslandKey(unittest.TestCase):
    def test_body_bytes_are_not_normalized(self):
        a = {'text': '/* c */\nint f(void)\n{\n    return 1;\n}\n'}
        self.assertEqual(island_key(a), island_key({'text': a['text'].replace('\n', '\r\n')}))
        self.assertNotEqual(island_key(a), island_key({'text': a['text'].replace('    return', '  return')}))
        self.assertEqual(island_key(a, definition_only=True), 'int f(void)\n{\n    return 1;\n}')
        self.assertEqual(island_key({'text': 'static int f(void)\n{\n}'}, static_evidenced=True), 'int f(void)\n{\n}')
        self.assertNotEqual(island_key({'text': 'static int f(void)\n{\n}'}), 'int f(void)\n{\n}')


class ProvenanceTransaction(unittest.TestCase):
    def test_reclassification_is_coupled_to_one_replaced_body(self):
        from source_scope import body_hash
        old = 'int f(void) { return 1; }\n'
        new = 'int f(void) { return 2; }\n'
        manifest = json.dumps({'bodies': [{'source': 'src/x.c', 'function': 'f',
                                           'kind': 'synthetic_replacement',
                                           'body_sha256': body_hash(old, 'f'),
                                           'evidence': 'old'}]})
        spec = {'bodies': {'f': 'candidate.c'},
                'provenance': {'f': {'kind': 'incomplete_evidence_candidate',
                                     'evidence': 'Observed source paths remain incomplete.'}}}
        result = json.loads(provenance_update(manifest, old, new, 'src/x.c', spec))
        row = result['bodies'][0]
        self.assertEqual(row['body_sha256'], body_hash(new, 'f'))
        self.assertEqual(row['kind'], 'incomplete_evidence_candidate')
        with self.assertRaises(ValueError):
            provenance_update(manifest, old, new, 'src/x.c', {'provenance': spec['provenance']})
        with self.assertRaises(ValueError):
            provenance_update(manifest, new, old, 'src/x.c', spec)


if __name__ == '__main__':
    unittest.main()
