"""Focused regressions for diagnostic blind spots; no recovery verdicts are changed."""
import unittest

from binary import Binary
from common import ROOT
from function_data_refs import data_section, literal_at, reference, refs
from unused_locals import unmentioned
from recovered_game_link import provenance_status
from classify_diff import classify


class DataReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exe = Binary(str(ROOT / 'assets/icytower15.exe'))

    def test_pe_section_instead_of_hex_prefix(self):
        self.assertEqual(data_section(self.exe, 0x4bc020)['name'], '.data')
        self.assertEqual(data_section(self.exe, 0x4dd160)['name'], '.bss')
        self.assertIsNone(data_section(self.exe, 0x4bbfff))
        self.assertEqual(reference(self.exe, 0x4bbfff, '', {}, [], None, {})['kind'], 'unknown')
        self.assertIn(0x4bc020, [int(r['va'], 16) for r in refs('game-main', 'play')])

    def test_empty_string_and_unknown_are_explicit(self):
        self.assertEqual(literal_at(self.exe, 0x4d4bb3, 'push $0x4d4bb3')['kind'], 'empty_string')
        self.assertEqual(reference(self.exe, 0, '', {}, [], None, {})['kind'], 'null_pointer')
        row = reference(self.exe, 0x514000, 'mov 0x514000,%eax', {}, [], None, {})
        self.assertEqual(row['kind'], 'literal')
        self.assertEqual(row['literal']['kind'], 'unknown')


class DwarfLocalTests(unittest.TestCase):
    def test_comments_and_strings_do_not_count_as_usage(self):
        locals_ = [{'die': 1, 'name': 'missing', 'scope': 2},
                   {'die': 2, 'name': 'used', 'scope': 2}]
        total, missing = unmentioned(locals_, '/* missing */ char *s = "missing"; int used = 1;')
        self.assertEqual(total, 2)
        self.assertEqual([x['name'] for x in missing], ['missing'])


class LinkProvenanceTests(unittest.TestCase):
    def test_active_replacements_block_recovered_game_claim(self):
        state = provenance_status()
        self.assertIn('src/main.c::draw_frame', state['known_synthetic_bodies'])
        self.assertIn('src/main.c::play', state['known_synthetic_bodies'])
        self.assertIn('src/main.c::main_menu_callback', state['known_placeholder_bodies'])
        self.assertIn('src/main.c::play', state['nonmatching_functions'])


class ClassificationTests(unittest.TestCase):
    def test_missing_body_outweighs_first_frame_byte(self):
        row = {'status': 'DIFFER', 'original_size': 17420, 'candidate_size': 623,
               'frame_layout': {'first_mismatch_is_frame_allocation': True}}
        self.assertEqual(classify(row), 'SOURCE_INCOMPLETE')


if __name__ == '__main__':
    unittest.main()
