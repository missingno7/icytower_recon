import unittest,copy
from types import SimpleNamespace
from storage_diagnostics import correlate,storage_rows
from type_graph import TypeGraph


def variable(name='buffer',scope=None,die=1):
    return {'name':name,'die':die,'scope':scope or ['GLOBAL'],'layout':{'kind':'base_type','size':4,'type':'int'},'type':'int','size':4,
            'coff':[{'name':'_'+name,'section':2,'value':0,'storage_class':3,'index':2}],'section':'.data'}


class StorageTests(unittest.TestCase):
    def test_scope_gap_retained_without_ownership(self):
        old=variable(scope=['FUNCTION_STATIC','f']); new=variable(die=2)
        result=correlate([old],[new],{})
        self.assertEqual(result['objects'][0]['state'],'SOURCE_SCOPE_DIFFERS')
        self.assertEqual(result['objects'][0]['candidate']['scope'],['GLOBAL'])

    def test_missing_and_unpaired_are_both_visible_not_guessed_by_shape(self):
        result=correlate([variable('HEADER')],[variable('header',die=2)],{})
        self.assertEqual(result['objects'][0]['state'],'CANDIDATE_DECLARATION_MISSING')
        self.assertEqual(len(result['unpaired_candidates']),1)

    def test_duplicate_candidate_scope_is_ambiguous(self):
        result=correlate([variable()],[variable(die=2),variable(die=3)],{})
        self.assertEqual(result['objects'][0]['state'],'AMBIGUOUS_CANDIDATE_DECLARATION')

    def test_exact_owner_comes_only_from_verifier(self):
        old=variable(); new=variable(die=2)
        self.assertEqual(correlate([old],[new],{})['objects'][0]['state'],'INITIALIZER_OR_OWNER_UNPROVEN')
        proof={'accepted':[{'original_die':1}]}
        self.assertEqual(correlate([old],[new],proof)['objects'][0]['state'],'EXACT_OWNER')

    def test_type_section_and_common_are_distinct(self):
        old=variable(); new=variable(die=2)
        new['layout']['type']='unsigned int'
        self.assertEqual(correlate([old],[new],{})['objects'][0]['state'],'STORAGE_TYPE_DIFFERS')
        new=variable(die=2); new['section']='.rdata'
        self.assertEqual(correlate([old],[new],{})['objects'][0]['state'],'STORAGE_SECTION_DIFFERS')
        new['section']='COMMON'
        self.assertEqual(correlate([old],[new],{})['objects'][0]['state'],'COMMON_DECLARATION_AGREES')

    def test_common_dwarf_addend_is_never_a_virtual_address(self):
        rows=[{'offset':1,'cu':1,'parent':None,'name':'a.c','tag':'DW_TAG_compile_unit','resolved':{}},
              {'offset':2,'cu':1,'parent':1,'name':'int','tag':'DW_TAG_base_type','type_ref':None,'resolved':{'DW_AT_byte_size':'4','DW_AT_encoding':'5 (signed)'}},
              {'offset':3,'cu':1,'parent':1,'name':'n','tag':'DW_TAG_variable','type_ref':2,'address':4294967292,'resolved':{}}]
        binary=SimpleNamespace(pe=False,sections=[],symbols=[{'name':'_n','index':1,'section':0,'value':4,'storage_class':2}])
        result=storage_rows(TypeGraph(rows),binary)[0]
        self.assertEqual(result['section'],'COMMON')
        self.assertNotIn('historical_va',result)
        self.assertNotIn('candidate_offset',result)


if __name__=='__main__': unittest.main()
