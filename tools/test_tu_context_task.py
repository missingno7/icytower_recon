"""Plan-level tests for the TU_CONTEXT transaction (no compiler run): the generated edit set preserves every
unlisted definition byte-for-byte, replaces only explicitly retained bodies, refuses unevidenced declaration
changes and forbidden directives, and the island comparison key normalizes nothing inside a body."""
import json, re, tempfile, unittest
from pathlib import Path
from common import ROOT, read_json, identity
from tu_context_probe import (build_text, islands, historical_static, header_edits, retained_body,
                              layout, apply_draw_results_owner_route, DRAW_RESULTS_OWNER_ROUTE,
                              _CATEGORY_DECL_OLD, _RESULT_CATEGORIES_OLD, _DRAW_RESULTS_REF_OLD)
from tu_context_task import (island_key, provenance_update, generated_include_identities, FORBIDDEN,
                             _require_category_names_owner, _require_exact_neighbors_preserved,
                             _CATEGORY_NAMES_ORIGINAL_BYTES)

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

    def test_uninitialized_owner_removal_requires_one_exact_simple_declaration(self):
        from tu_context_probe import declaration_edits
        text = 'int blit_mode;\nint initialized = 1;\nint keep;\n'
        item = {'name': 'blit_mode', 'declaration': 'int blit_mode;',
                'storage_card': 'docs/current/storage/game-main/124685.json',
                'to_function': 'blit_to_screen'}
        new, removed = declaration_edits(text, {'remove_uninitialized_top_level': [item]}, '\n')
        self.assertEqual(new, 'int initialized = 1;\nint keep;\n')
        self.assertEqual(removed[0]['text'], 'int blit_mode;\n')
        with self.assertRaisesRegex(ValueError, 'one exact'):
            declaration_edits(text + 'int blit_mode;\n', {'remove_uninitialized_top_level': [item]}, '\n')
        with self.assertRaisesRegex(ValueError, 'simple uninitialized'):
            declaration_edits(text, {'remove_uninitialized_top_level':
                                     [{**item, 'declaration': 'int initialized = 1;'}]}, '\n')

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


class DrawResultsOwnerRoute(unittest.TestCase):
    def setUp(self):
        self.text = (ROOT / SOURCE).read_bytes().decode('cp1252')
        self.spec = {'order': 'current', 'prototypes': 'none',
                     'data_owner_correction': DRAW_RESULTS_OWNER_ROUTE}

    def test_fixed_route_changes_only_two_data_spans_and_draw_results_reference(self):
        new, edits, headers = build_text(TARGET, SOURCE, self.spec)
        old = {i['name']: i for i in islands(self.text)}
        current = {i['name']: i for i in islands(new)}
        self.assertEqual(set(old), set(current))
        self.assertEqual(headers, {})
        self.assertEqual(edits['data_owner_correction']['changed_functions'], ['draw_results'])
        for name in old:
            if name == 'draw_results':
                self.assertEqual(island_key(current[name]),
                                 island_key(old[name]).replace(_DRAW_RESULTS_REF_OLD,
                                                              'category_names[categories[i]]', 1))
            else:
                self.assertEqual(island_key(old[name]), island_key(current[name]), name)
        self.assertIn('char *category_names[15] = {', new)
        self.assertNotIn('result_categories', new)

    def test_route_is_limited_to_main_and_rejects_combined_edit_kinds(self):
        with self.assertRaisesRegex(ValueError, 'mis-scoped'):
            build_text('game-profile', 'src/profile.c', self.spec)
        for extra in ({'order': ['draw_results']}, {'prototypes': 'auto'}, {'bodies': {'x': RETAINED}},
                      {'declarations': {'add_top_level': []}}, {'statics': ['draw_results']}):
            with self.assertRaises(ValueError):
                build_text(TARGET, SOURCE, {**self.spec, **extra})

    def test_historical_order_is_allowed_without_other_source_mutations(self):
        new, edits, _ = build_text(TARGET, SOURCE, {**self.spec, 'order': 'historical'})
        self.assertEqual(edits['prototypes'], 'none')
        current = {i['name']: i for i in islands(new)}
        self.assertEqual(current['draw_results']['signature'],
                         next(i['signature'] for i in islands(self.text) if i['name'] == 'draw_results'))

    def test_route_rejects_missing_ambiguous_nested_or_mistyped_spans(self):
        source = self.text
        with self.assertRaisesRegex(ValueError, 'exactly one source span'):
            apply_draw_results_owner_route(source + '\n' + _CATEGORY_DECL_OLD, TARGET, SOURCE,
                                           DRAW_RESULTS_OWNER_ROUTE)
        local_only = source.replace(_CATEGORY_DECL_OLD, 'void local_owner(void) { char *category_names[15]; }', 1)
        with self.assertRaisesRegex(ValueError, 'file-scope'):
            apply_draw_results_owner_route(local_only, TARGET, SOURCE, DRAW_RESULTS_OWNER_ROUTE)
        wrong_extent = source.replace(_CATEGORY_DECL_OLD, 'char *category_names[14];', 1)
        with self.assertRaisesRegex(ValueError, 'exactly one source span'):
            apply_draw_results_owner_route(wrong_extent, TARGET, SOURCE, DRAW_RESULTS_OWNER_ROUTE)
        with self.assertRaisesRegex(ValueError, 'exactly one source span'):
            apply_draw_results_owner_route(source.replace(_RESULT_CATEGORIES_OLD, _RESULT_CATEGORIES_OLD.replace('[5]', '[6]'), 1),
                                           TARGET, SOURCE, DRAW_RESULTS_OWNER_ROUTE)
        with self.assertRaisesRegex(ValueError, 'one draw_results'):
            duplicated = source.replace(_DRAW_RESULTS_REF_OLD,
                                        _DRAW_RESULTS_REF_OLD + ' + ' + _DRAW_RESULTS_REF_OLD, 1)
            apply_draw_results_owner_route(duplicated, TARGET, SOURCE, DRAW_RESULTS_OWNER_ROUTE)


class StrictCategoryOwnerGate(unittest.TestCase):
    def valid_report(self):
        import struct
        targets = struct.unpack('<15I', bytes.fromhex(_CATEGORY_NAMES_ORIGINAL_BYTES))
        relocs = [{'object_offset': i * 4, 'type': 6, 'symbol': '.rdata', 'target_va': targets[i],
                   'resolution': 'unique read-only initializer literal or table content'} for i in range(15)]
        owner = {'name': 'category_names', 'scope': ['GLOBAL'], 'original_die': 136974,
                 'original_va': 4964480, 'section': '.data', 'candidate_offset': 128,
                 'size': 60, 'dwarf_type': 'char *[15]', 'candidate_type': 'char *[15]',
                 'proof': 'Unique CU/scope/name, identical DWARF type graph, COFF owner, storage and complete independently resolved initializer',
                 'initializer': 'all initialized bytes equal after independent relocation resolution',
                 'initial_value': _CATEGORY_NAMES_ORIGINAL_BYTES, 'initializer_relocations': relocs}
        return {'object_ownership': {'accepted': [owner]}}

    def test_requires_exact_owner_and_all_15_resolved_targets(self):
        _require_category_names_owner(self.valid_report())

    def test_requires_owner_in_fresh_in_memory_report(self):
        report = self.valid_report()
        report['object_ownership']['accepted'][0]['scope'] = ('GLOBAL',)
        _require_category_names_owner(report)

    def test_rejects_absent_duplicate_wrong_extent_wrong_type_or_bad_target(self):
        report = self.valid_report()
        cases = []
        cases.append({'object_ownership': {'accepted': []}})
        cases.append({'object_ownership': {'accepted': report['object_ownership']['accepted'] * 2}})
        for key, value in [('size', 20), ('candidate_type', 'char *[5]'),
                           ('section', 'COMMON'), ('original_die', 1),
                           ('initial_value', '00' * 60)]:
            bad = self.valid_report(); bad['object_ownership']['accepted'][0][key] = value; cases.append(bad)
        for mutate in (lambda x: x.pop(), lambda x: x[1].update(object_offset=8),
                       lambda x: x[0].update(target_va=x[0]['target_va'] + 1),
                       lambda x: x[0].update(resolution='ambiguous')):
            bad = self.valid_report(); mutate(bad['object_ownership']['accepted'][0]['initializer_relocations']); cases.append(bad)
        for bad in cases:
            with self.assertRaises(ValueError): _require_category_names_owner(bad)

    def test_no_exact_peer_losses_is_mandatory(self):
        before = {'functions': [{'name': 'peer', 'status': 'FUNCTION_MATCH'},
                                {'name': 'target', 'status': 'DIFFER'}]}
        _require_exact_neighbors_preserved(before, {'functions': [{'name': 'peer', 'status': 'FUNCTION_MATCH'},
                                                                  {'name': 'target', 'status': 'FUNCTION_MATCH'}]})
        with self.assertRaisesRegex(ValueError, 'Exact neighbor regressed: peer'):
            _require_exact_neighbors_preserved(before, {'functions': [{'name': 'peer', 'status': 'DIFFER'},
                                                                      {'name': 'target', 'status': 'FUNCTION_MATCH'}]})


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
