"""Typed initializer paths, exact edit scope and independent ownership negative controls."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import sha
from type_graph import graph
from dwarf_layout import layout,locate,reference
from initializer_scope import field_span
from data_tasks import plan,fingerprint,verify_owner
from data_diagnostics import candidate_reference,original_reference
from types import SimpleNamespace


class DataTaskTests(unittest.TestCase):
    def test_symbolic_target_ambiguity_is_not_guessed(self):
        node={'kind':'base_type','size':4,'type':'int'}
        variables=[{'name':'a','address':100,'layout':node,'die':1},{'name':'b','address':100,'layout':node,'die':2}]
        exe=SimpleNamespace(symbols=[{'name':'_a','va':100},{'name':'_b','va':100}])
        with patch('data_diagnostics.original_globals',return_value=variables): self.assertIsNone(original_reference(100,exe))
        with patch('data_diagnostics.original_globals',return_value=variables[:1]):
            self.assertEqual(original_reference(100,exe)['expression'],'a')

    def test_candidate_symbol_and_owner_offsets_are_distinct(self):
        declarations=[{'name':'a','layout':{'kind':'base_type','size':4,'type':'int'}}]
        owner={'name':'a','scope':['GLOBAL'],'section_index':2,'candidate_offset':8,'size':4}
        self.assertEqual(candidate_reference({'name':'.data','section':2,'value':0},8,[owner],declarations)['expression'],'a')
        self.assertIsNone(candidate_reference({'name':'.data','section':2,'value':0},9,[owner],declarations))
        self.assertIsNone(candidate_reference({'name':'.data','section':2,'value':0},8,[owner,owner],declarations))
        self.assertEqual(candidate_reference({'name':'_a','section':0,'value':4},0,[],declarations)['expression'],'a')
        self.assertIsNone(candidate_reference({'name':'_a','section':0,'value':4},0,[],declarations*2))
    def test_original_nested_path_and_target_member(self):
        g=graph()
        ctrl=next(d for d in g.dies.values() if d['tag']=='DW_TAG_variable' and d.get('name')=='ctrl_menu' and d.get('address'))
        item=locate(layout(g,ctrl['type_ref']),736,'ctrl_menu')
        self.assertEqual((item['expression'],item['size'],item['kind']),('ctrl_menu[4].data',4,'pointer_type'))
        options=layout(g,g.game_types['Toptions'][0]['type_ref'])
        self.assertEqual(reference(options,8,'options')['expression'],'options.jump_hold')
        self.assertIsNone(reference(options,9,'options'))

    def test_padding_overlap_union_and_unknown_bounds_are_not_fields(self):
        leaf={'kind':'base_type','size':4,'type':'int'}
        node={'kind':'structure_type','size':12,'type':'struct x','members':[{'name':'a','offset':0,'bitfield':False,'layout':leaf},{'name':'b','offset':8,'bitfield':False,'layout':leaf}]}
        self.assertIsNone(locate(node,5,'x'))
        node['members'][1]['offset']=0
        self.assertIsNone(locate(node,0,'x'))
        self.assertIsNone(locate({'kind':'union_type','size':4,'type':'union x'},0,'x'))
        self.assertIsNone(locate({'kind':'array_type','size':4,'dimensions':[None],'element':leaf},0,'x'))

    def test_multidimensional_array_path(self):
        node={'kind':'array_type','size':24,'type':'int [2][3]','dimensions':[2,3],'element':{'kind':'base_type','size':4,'type':'int'}}
        self.assertEqual(locate(node,20,'x')['expression'],'x[1][2]')

    def test_initializer_positional_scope_ignores_string_and_character_commas(self):
        text='X data[2] = { { "a,{", \',\', &one }, { "b}", 2, &other.field } };'
        a,b=field_span(text,'data',[{'index':1},{'member':'p','index':2}])
        self.assertEqual(text[a:b],'&other.field')
        for bad in ('X data[2] = { [1]={0,1,&one} };','X data[2] = { {0} };',
                    'void f(void) { X data[2] = { {0,1,&one},{0,1,&other} }; }',
                    'X data[2] = {{0,1,&one},{0,1,&other}}; X data[2] = {{0}};'):
            with self.assertRaises(ValueError): field_span(bad,'data',[{'index':1},{'index':2}])

    def fixture(self,folder):
        root=Path(folder); (root/'src').mkdir(); source='src/a.c'
        (root/source).write_text('X data[1] = { { "hello", &one } };\n')
        field={'expression':'data[0].p','offset':16,'size':4,'kind':'pointer_type','steps':[{'index':0},{'member':'p','index':1}],
               'classification':'SYMBOLIC_POINTER_DIFFERENCE','candidate_target_path_agrees':True,
               'expected_reference':{'root':'settings','expression':'settings.member'},'candidate_reference':{'root':'one','expression':'one'}}
        item={'name':'data','scope':['GLOBAL'],'fields':[field],'mismatch_byte_count':2,'unresolved_byte_count':0,
              'original_die':123,'section_index':2,'candidate_offset':0,'size':20}
        return root,source,field,item

    def test_plan_is_symbolic_single_field_only(self):
        import data_tasks
        with tempfile.TemporaryDirectory() as folder:
            root,source,field,item=self.fixture(folder)
            with patch.object(data_tasks,'ROOT',root),patch.object(data_tasks,'affected_targets',return_value=['game-a']):
                card=plan(source,{'build':{'target':'game-a'}},item,{})
                self.assertEqual(card['difficulty'],'CHEAP',card['reason'])
                self.assertEqual(card['changes'][0]['after'],'&settings.member')
                self.assertEqual(card['changes'][0]['before'],'&one')
                field['candidate_target_path_agrees']=False
                self.assertEqual(plan(source,{'build':{'target':'game-a'}},item,{})['difficulty'],'SUPERVISOR')

    def test_matching_symbolic_dependency_is_never_rewritten(self):
        import data_tasks
        with tempfile.TemporaryDirectory() as folder:
            root,source,field,item=self.fixture(folder)
            field['classification']='OWNER_CONTENT_DEPENDENCY'; item.update(mismatch_byte_count=0,unresolved_byte_count=4)
            with patch.object(data_tasks,'ROOT',root),patch.object(data_tasks,'affected_targets',return_value=['game-a']):
                card=plan(source,{'build':{'target':'game-a'}},item,{})
                self.assertEqual(card['state'],'WAITING_FOR_OWNER')
                self.assertEqual(card['changes'],[])

    def report(self,data=bytes(16),symbol=10):
        sections=[{'index':i,'name':name,'virtual_size':0,'raw_size':len(raw),'characteristics':0,'sha256':sha(raw)}
                  for i,name,raw in ((1,'.text',b'code'),(2,'.data',data))]
        return {'build':{'object':{'sha256':'object'}},'data_snapshot':{'object':{'sha256':'object'},'sections':{'2':data.hex()}},
                'object_sections':sections,'object_symbols':[{'index':i,'name':name,'section':0,'value':4,'storage_class':2} for i,name in ((10,'_one'),(11,'_other'))],
                'object_relocations':[{'section':2,'offset':4,'type':6,'symbol_index':symbol}],
                'common_allocations':[],'candidate_zero_clear_projection':{'sha256':'projection'}}

    def test_only_authorized_word_and_its_relocation_may_change(self):
        allowed={'section_index':2,'section_offset':4,'field_size':4}
        old=self.report(); data=bytearray(16); data[4]=8; new=self.report(bytes(data),11)
        self.assertEqual(fingerprint(old,allowed),fingerprint(new,allowed))
        data[12]=1
        self.assertNotEqual(fingerprint(old,allowed),fingerprint(self.report(bytes(data),11),allowed))
        new['object_sections'][0]['sha256']='changed code'
        self.assertNotEqual(fingerprint(old,allowed),fingerprint(new,allowed))

    def test_bad_snapshot_or_crossing_relocation_rejected(self):
        allowed={'section_index':2,'section_offset':4,'field_size':4}
        for change in ('snapshot','object','crossing','type'):
            report=self.report()
            if change=='snapshot': report['data_snapshot']['sections']['2']='ff'*16
            elif change=='object': report['data_snapshot']['object']={'sha256':'wrong'}
            elif change=='crossing': report['object_relocations'][0]['offset']=5
            else: report['object_relocations'][0]['type']=20
            with self.assertRaises(ValueError): fingerprint(report,allowed)

    def test_preservation_fingerprint_never_substitutes_for_owner_proof(self):
        allowed={'object':'data','original_die':123,'field_offset':4,'section_index':2,'section_offset':4}
        with self.assertRaises(ValueError): verify_owner({'object_ownership':{'accepted':[]}},allowed)
        owner={'name':'data','original_die':123,'candidate_offset':0,'section_index':2}
        verify_owner({'object_ownership':{'accepted':[owner]}},allowed)
        owner['candidate_offset']=4
        with self.assertRaises(ValueError): verify_owner({'object_ownership':{'accepted':[owner]}},allowed)


if __name__=='__main__': unittest.main()
