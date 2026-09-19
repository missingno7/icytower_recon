"""Meaningful negative controls for proof claims, using the complete timer CU."""
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
from unittest.mock import patch
from common import ROOT, identity, read_json
from binary import Binary
from build import compile_target, verify_inputs
from dwarf import parse
from experiment import compare

OBJDUMP=Path('C:/msys64/mingw64/bin/objdump.exe')
CU='F:\\projects\\icytower\\trunk\\source\\timer.c'

class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.obj=ROOT/'build/experiments/tdm-2/game-timer/O2/unit.o'
        if not cls.obj.exists(): raise RuntimeError('Run the experiment matrix first')

    def check_object(self,path):
        return compare(path,CU,ROOT/'assets/icytower15.exe',OBJDUMP)

    def mutate(self,editor):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            path=Path(folder)/'unit.o'
            contents=bytearray(self.obj.read_bytes())
            editor(contents,Binary(self.obj))
            path.write_bytes(contents)
            return self.check_object(path)

    def test_complete_timer_text(self):
        r=self.check_object(self.obj)
        self.assertEqual(r['functions_total'],3)
        self.assertEqual(r['function_matches'],3)
        self.assertTrue(r['whole_text_contribution_equal'])
        self.assertEqual(r['candidate_text_logical_size'],152)
        self.assertEqual(len(r['common_allocations']),5)
        self.assertFalse(r['object_match'])

    def test_complete_control_text(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-control/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\control.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],15)
        self.assertEqual(r['function_matches'],15)
        self.assertTrue(r['whole_text_contribution_equal'])
        self.assertEqual(r['candidate_text_logical_size'],750)
        self.assertFalse(r['object_match'])

    def test_complete_modified_logg_text_and_data(self):
        r=compare(ROOT/'build/experiments/tdm-2/allegro-logg/O2/unit.o',
                  'C:\\Lib\\allegro4\\addons\\logg\\logg.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],18)
        self.assertEqual(r['function_matches'],18)
        self.assertTrue(r['whole_text_contribution_equal'])
        self.assertEqual(r['candidate_text_logical_size'],2061)
        self.assertEqual(sum(s['logical_size'] for s in r['initialized_data_comparison'] if s['content_equal']),80)
        self.assertFalse(r['object_match'])

    def test_main_datafile_helper_is_exact(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-main-partial/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\main.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        helper=next(f for f in r['functions'] if f['name']=='getSampleFromOggDatafile')
        self.assertEqual(helper['status'],'FUNCTION_MATCH')
        self.assertEqual(helper['candidate_size'],32)
        log=next(f for f in r['functions'] if f['name']=='log2file')
        self.assertEqual(log['candidate_size'],189)
        self.assertEqual(log['original_size'],189)
        self.assertNotEqual(log['status'],'FUNCTION_MATCH')

    def test_main_random_helpers_are_exact(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-main-partial/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\main.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        rng=next(f for f in r['functions'] if f['name']=='new_rand')
        self.assertEqual(rng['status'],'FUNCTION_MATCH')
        self.assertEqual(rng['candidate_size'],128)
        seed=next(f for f in r['functions'] if f['name']=='new_srand')
        self.assertEqual(seed['status'],'FUNCTION_MATCH')
        self.assertEqual(seed['candidate_size'],14)

    def test_main_accessors_are_exact(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-main-partial/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\main.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        for name in ('get_version_str','get_demo','get_controls','ok_to_play',
                     'switchedFromProgram','switchedToProgram','clickedCloseButton',
                     'is_custom_replay','show_name','datafile_callback_slow',
                     'datafile_callback','color_map_callback','syncProfileFromOptions',
                     'startMenuMusic','play_menu_select','play_menu_move','stopMenuMusic',
                     'replaceBadCharacters','pwd_garble_string','line_intersect','WinMain',
                     'set_current_avatar','for_each_directory'):
            accessor=next(f for f in r['functions'] if f['name']==name)
            self.assertEqual(accessor['status'],'FUNCTION_MATCH')
            self.assertEqual(accessor['candidate_size'],
                             10 if name in ('get_version_str','get_demo','get_controls','ok_to_play')
                             else 66 if name=='is_custom_replay' else 36 if name=='show_name'
                             else 58 if name=='syncProfileFromOptions'
                             else 59 if name=='startMenuMusic'
                             else 37 if name in ('play_menu_select','play_menu_move')
                             else 25 if name=='stopMenuMusic'
                             else 125 if name=='replaceBadCharacters'
                             else 52 if name=='pwd_garble_string'
                             else 302 if name=='line_intersect'
                             else 50 if name=='WinMain'
                             else 96 if name=='set_current_avatar'
                             else 109 if name=='for_each_directory'
                             else 33 if name=='datafile_callback_slow'
                             else 12 if name=='datafile_callback' else 22 if name=='color_map_callback' else 15)

    def test_repeated_literal_neighbourhood_rejects_wrong_target(self):
        obj=ROOT/'build/experiments/tdm-2/game-main-partial/O2/unit.o'
        cu='F:\\projects\\icytower\\trunk\\source\\main.c'
        exact=compare(obj,cu,ROOT/'assets/icytower15.exe',OBJDUMP)
        line=next(f for f in exact['functions'] if f['name']=='line_intersect')
        relocation=line['relocations'][0]
        b=Binary(obj)
        section=next(s for s in b.sections if s['index']==relocation['section'])
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            altered=Path(folder)/'unit.o'
            contents=bytearray(obj.read_bytes())
            # Select the preceding table field while leaving the instruction
            # body masked-equal.  A table neighbourhood must not hide this.
            struct.pack_into('<I',contents,section['raw_pointer']+relocation['offset'],
                             relocation['addend']-4)
            altered.write_bytes(contents)
            wrong=compare(altered,cu,ROOT/'assets/icytower15.exe',OBJDUMP)
        line=next(f for f in wrong['functions'] if f['name']=='line_intersect')
        self.assertTrue(line['masked_equal'])
        self.assertFalse(line['relocation_resolved_equal'])
        self.assertNotEqual(line['status'],'FUNCTION_MATCH')

    def test_complete_directories_text_and_data(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-directories/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\directories.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],7)
        self.assertEqual(r['function_matches'],7)
        self.assertTrue(r['whole_text_contribution_equal'])
        self.assertTrue(all(s['content_equal'] for s in r['initialized_data_comparison']))
        self.assertFalse(r['object_match'])

    def test_complete_stars_text(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-stars/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\stars.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],3)
        self.assertEqual(r['function_matches'],3)
        self.assertTrue(r['whole_text_contribution_equal'])
        self.assertEqual(r['candidate_text_logical_size'],643)
        self.assertFalse(r['object_match'])

    def test_complete_particle_text(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-particle/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\particle.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],3)
        self.assertEqual(r['function_matches'],3)
        self.assertTrue(r['whole_text_contribution_equal'])
        self.assertEqual(r['candidate_text_logical_size'],304)
        self.assertFalse(r['object_match'])

    def test_partial_scroller_text(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-scroller/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\scroller.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],4)
        self.assertEqual(r['function_matches'],3)
        self.assertEqual({f['name'] for f in r['functions'] if f['status']=='FUNCTION_MATCH'},
                         {'scroll_scroller','restart_scroller','init_scroller'})
        self.assertEqual(next(f for f in r['functions'] if f['name']=='draw_scroller')['candidate_size'],396)
        self.assertFalse(r['whole_text_contribution_equal'])

    def test_partial_map_text(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-map/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\map.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],5)
        self.assertEqual(r['function_matches'],3)
        self.assertEqual({f['name'] for f in r['functions'] if f['status']=='FUNCTION_MATCH'},
                         {'reset_map','is_solid','get_level'})
        floor=next(f for f in r['functions'] if f['name']=='getFloorData')
        self.assertEqual(floor['candidate_size'],107)
        self.assertEqual(next(f for f in r['functions'] if f['name']=='add_floor')['status'],'MISSING')

    def test_complete_beta_text(self):
        r=compare(ROOT/'build/experiments/tdm-2/game-beta/O2/unit.o',
                  'F:\\projects\\icytower\\trunk\\source\\beta.c',ROOT/'assets/icytower15.exe',OBJDUMP)
        self.assertEqual(r['functions_total'],7)
        self.assertEqual(r['function_matches'],7)
        self.assertTrue(r['whole_text_contribution_equal'])
        loader=next(f for f in r['functions'] if f['name']=='load_plain_data')
        self.assertEqual(loader['candidate_size'],loader['original_size'])

    def test_csv_duplicate_string_uses_coff_owner_not_tested_operand(self):
        obj=ROOT/'build/experiments/tdm-2/game-csv/O2/unit.o'
        original=ROOT/'assets/icytower15.exe'
        cu='F:\\projects\\icytower\\trunk\\source\\csv.c'
        r=compare(obj,cu,original,OBJDUMP)
        self.assertTrue(r['whole_text_contribution_equal'])
        data=r['initialized_data_comparison'][0]
        self.assertGreater(data['matching_location_count'],1)
        self.assertIsNotNone(data['coff_contribution'])
        # Move only CSV's COFF data anchor to another identical rb string.
        # Original instruction bytes stay unchanged: masked equality is not proof.
        b=Binary(original)
        index=data['coff_contribution']['symbol_index']
        contents=bytearray(original.read_bytes())
        symbol=b.by_index[index]
        struct.pack_into('<I',contents,b.header['symbol_table_pointer']+index*18+8,symbol['value']-5)
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            altered=Path(folder)/'altered.exe'
            altered.write_bytes(contents)
            wrong=compare(obj,cu,altered,OBJDUMP)
        self.assertEqual(wrong['masked_matches'],6)
        self.assertEqual(wrong['function_matches'],5)
        self.assertFalse(wrong['whole_text_contribution_equal'])

    def test_integration_layout_preserves_first_mismatch(self):
        r=read_json(ROOT/'docs/experiments/integration-layout.json')
        self.assertEqual(r['build_report'],identity(ROOT/'build/integration/tdm-2/build.json'))
        first=r['first_layout_mismatch']
        self.assertEqual(r['natural_game_address_extent_prefix_bytes'],2576)
        self.assertFalse(first['address_equal'])

    def test_wrong_relocation_target_is_rejected_despite_masked_equality(self):
        def mutate(data,b):
            sec=b.sections[0]
            wrong=next(s['index'] for s in b.symbols if s['name']=='_fps')
            struct.pack_into('<I',data,sec['relocation_pointer']+4,wrong)
        r=self.mutate(mutate)
        fps=next(f for f in r['functions'] if f['name']=='fps_counter')
        self.assertTrue(fps['masked_equal'])
        self.assertFalse(fps['relocation_resolved_equal'])
        self.assertFalse(r['whole_text_contribution_equal'])

    def test_code_corruption_is_rejected(self):
        r=self.mutate(lambda data,b:data.__setitem__(b.sections[0]['raw_pointer'],0x90))
        self.assertFalse(r['functions'][0]['masked_equal'])
        self.assertFalse(r['whole_text_contribution_equal'])

    def test_padding_corruption_is_rejected(self):
        # 0x2d..0x2f is inter-function padding outside every DWARF extent.
        r=self.mutate(lambda data,b:data.__setitem__(b.sections[0]['raw_pointer']+0x2d,0x90))
        self.assertEqual(r['function_matches'],3)
        self.assertFalse(r['whole_text_contribution_equal'])

    def test_same_functions_wrong_spacing_is_not_cu_text_match(self):
        r=self.check_object(ROOT/'build/experiments/tdm-2/game-timer/O1/unit.o')
        self.assertEqual(r['function_matches'],3)
        self.assertFalse(r['whole_text_contribution_equal'])

    def test_unknown_relocation_type_is_rejected(self):
        def mutate(data,b): struct.pack_into('<H',data,b.sections[0]['relocation_pointer']+8,0x1234)
        r=self.mutate(mutate)
        self.assertFalse(r['whole_text_contribution_equal'])
        self.assertFalse(r['functions'][0]['relocation_resolved_equal'])

    def test_origin_chain_is_followed(self):
        text=''' <0><b>: Abbrev Number: 1 (DW_TAG_compile_unit)
    <c> DW_AT_name : test.c
 <1><20>: Abbrev Number: 2 (DW_TAG_subprogram)
    <21> DW_AT_name : original_name
    <22> DW_AT_type : <0x50>
 <1><30>: Abbrev Number: 3 (DW_TAG_subprogram)
    <31> DW_AT_specification : <0x20>
 <1><40>: Abbrev Number: 4 (DW_TAG_subprogram)
    <41> DW_AT_abstract_origin : <0x30>
    <42> DW_AT_low_pc : 0x1234
    <43> DW_AT_high_pc : 0x1240
 <1><50>: Abbrev Number: 5 (DW_TAG_base_type)
    <51> DW_AT_name : int
'''
        dies,stats=parse(text)
        self.assertEqual(dies[0x40]['name'],'original_name')
        self.assertEqual(dies[0x40]['type_ref'],0x50)
        self.assertEqual(stats['unresolved_origin_specification'],[])

    def test_audio_build_never_reads_assets_or_evidence(self):
        from build_xiph import build_library
        from audio_link import main as link_audio
        original_open=Path.open
        def guarded(path,*args,**kwargs):
            absolute=path.resolve()
            if absolute.is_relative_to(ROOT/'assets') or absolute.is_relative_to(ROOT/'evidence'):
                raise AssertionError('Audio build accessed verification inputs')
            return original_open(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):
            report=build_library()
            self.assertEqual(len(report['units']),22)
            link_audio()
            link_audio(True)
        linked=read_json(ROOT/'build/audio/tdm-2/build.json')
        self.assertFalse(linked['executed'])
        self.assertEqual(linked['executable'],identity(ROOT/'build/audio/tdm-2/audio-probe.exe'))
        custom=read_json(ROOT/'build/custom-audio/tdm-2/build.json')
        self.assertEqual(len(custom['game_objects']),4)
        self.assertFalse(custom['executed'])

    def test_normal_object_build_never_reads_assets_or_evidence(self):
        original_open=Path.open
        def guarded(path,*args,**kwargs):
            absolute=path.resolve()
            if absolute.is_relative_to(ROOT/'assets') or absolute.is_relative_to(ROOT/'evidence'):
                raise AssertionError('Normal object build tried to access verification inputs')
            return original_open(path,*args,**kwargs)
        with patch.object(Path,'open',guarded):
            verify_inputs()
            obj,_=compile_target('game-timer',dest=ROOT/'build/independence-test')
        self.assertTrue(obj.exists())

if __name__=='__main__': unittest.main(verbosity=2)
