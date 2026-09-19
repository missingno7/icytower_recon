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
