import copy
import unittest
from unittest.mock import patch
from global_type_tasks import source_edits,fingerprint,verify
from promote_function import no_regressions


INT={'kind':'base_type','size':4,'type':'int'}


def fixture():
    text='int item;\nvoid *p = &item;\nvoid f(void) { item = 1; }\n'
    old={'name':'item','type':'Historic','layout':{'kind':'structure_type','size':8,'type':'Historic','members':[
        {'name':'value','offset':0,'bitfield':False,'layout':INT},{'name':'extra','offset':4,'bitfield':False,'layout':INT}]}}
    new={'type':'int','layout':INT,'declaration_line':1}
    report={'functions':[{'name':'f','workflow':{'state':'FUNCTION_MATCH'}}],
            'candidate_debug':{'functions':{'f':{'variables':[]}}}}
    return text,'src/a.c',old,new,report,'include/recovered/Historic.h'


class GlobalTypeTests(unittest.TestCase):
    def test_plan_cannot_redirect_layout_object_header_or_compilation_unit(self):
        old={'die':1,'name':'item','type':'Historic','layout':{'kind':'structure_type','size':8}}
        current={'name':'item','type':'int'}
        report={'build':{'target':'game-example','config':{'source':'src/example.c'}}}
        plan={'original_die':1,'original':old,'candidate':current,'object':'item',
              'expected_layout':old['layout'],'header':'include/recovered/Historic.h',
              'source':'src/example.c','target':'game-example'}
        for key,value in [('object','other'),('expected_layout',{'kind':'structure_type','size':4}),
                          ('header','include/recovered/Other.h'),('source','src/other.c'),('target','game-other')]:
            modified=copy.deepcopy(plan);modified[key]=value
            with patch('global_type_tasks.diagnose',return_value={'objects':[{'original':old,'candidate':current}]}),patch('global_type_tasks.source_edits') as edits:
                with self.assertRaisesRegex(ValueError,'redirected'):verify(report,report,modified,'','')
                edits.assert_not_called()

    def test_only_definition_and_scalar_use_change(self):
        args=fixture(); edits,functions=source_edits(*args)
        self.assertEqual(functions,['f']); self.assertEqual(len(edits),3)
        self.assertEqual([e['after'] for e in edits if e['role']=='offset_zero_scalar_access'],['item.value'])
        self.assertFalse(any(e['before']=='&item' for e in edits))

    def test_layout_proven_body_or_shadow_requires_supervisor(self):
        for kind in ('layout','shadow'):
            args=fixture()
            if kind=='layout': args[4]['functions'][0]['workflow']['state']='BODY_MATCH_LAYOUT_BLOCKED'
            else: args[4]['candidate_debug']['functions']['f']['variables']=[{'name':'item'}]
            with self.assertRaises(ValueError): source_edits(*args)

    def test_nonzero_bitfield_qualified_or_incompatible_member_is_refused(self):
        for kind in ('offset','bitfield','qualified','type'):
            args=list(fixture()); args[2]=copy.deepcopy(args[2]); m=args[2]['layout']['members'][0]
            if kind=='offset': m['offset']=4
            elif kind=='bitfield': m['bitfield']=True
            elif kind=='qualified': args[2]['layout']['qualifiers']=['volatile']
            else: m['layout']={**INT,'type':'unsigned int'}
            with self.assertRaises(ValueError): source_edits(*args)

    def test_size_query_and_other_global_declaration_are_not_rewritten(self):
        for text in ('int item;\nvoid f(){ return sizeof(item); }','int item;\nextern int item;\nvoid f(){ item=1; }'):
            args=list(fixture()); args[0]=text
            with self.assertRaises(ValueError): source_edits(*args)

    def test_exact_body_exception_requires_all_proofs_and_authorized_hash_pair(self):
        before={'name':'f','status':'FUNCTION_MATCH','workflow':{'state':'FUNCTION_MATCH'},'source_body_sha256':'old',
                'instructions':[{'bytes':'c3'}],'relocations':[]}
        after={**before,'source_body_sha256':'new'}
        no_regressions({'functions':[before]},{'functions':[after]},{'f':('old','new')})
        for kind in ('no-authority','wrong-hash','code','relocation','layout','missing-code'):
            a=copy.deepcopy(before); b=copy.deepcopy(after); authority={'f':('old','new')}
            if kind=='no-authority': authority=None
            elif kind=='wrong-hash': authority={'f':('old','different')}
            elif kind=='code': b['instructions'][0]['bytes']='90'
            elif kind=='relocation': b['relocations']=[{'symbol':'wrong'}]
            elif kind=='layout': a['workflow']['state']='BODY_MATCH_LAYOUT_BLOCKED'
            else: a['instructions']=b['instructions']=[]
            with self.assertRaises(ValueError): no_regressions({'functions':[a]},{'functions':[b]},authority)

    def test_fingerprint_normalizes_only_authorized_common_size(self):
        plan={'object':'item','original':{'size':8},'candidate':{'size':4}}
        def data(size): return {'common':[('_item',size,2),('_other',4,2)],'relocations':[('.text',1,6,'_item',0,size),('.text',8,6,'_other',0,4)]}
        with patch('global_type_tasks.contribution_fingerprint',side_effect=lambda r:r):
            self.assertEqual(fingerprint(data(4),plan,4),fingerprint(data(8),plan,8))
            changed=data(8); changed['common'][1]=('_other',8,2)
            self.assertNotEqual(fingerprint(data(4),plan,4),fingerprint(changed,plan,8))
            with self.assertRaises(ValueError): fingerprint(data(16),plan,8)
            bad=data(8); bad['relocations'][0]=('.text',1,6,'_item',0,16)
            with self.assertRaises(ValueError): fingerprint(bad,plan,8)


if __name__=='__main__': unittest.main()
