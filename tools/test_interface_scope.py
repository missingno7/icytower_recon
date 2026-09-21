import copy
import unittest
from interface_scope import assess,partition,callees


def fixture():
    d={'cu':'src/a.c','file':'include/shared.h','return_type':'int','parameter_types':['Alias*'],
       'canonical_return_type':'int','canonical_parameter_types':['Original*'],'game_type_layouts':[{'status':'AGREE'}]}
    remote={**d,'cu':'src/b.c','return_type':'void','canonical_return_type':'void','game_type_layouts':[{'status':'MISMATCH'}]}
    return {'function':'f','historical':[{'return_type':'int','parameter_types':['Original*'],'variadic':False,'calling_convention':None}],
            'candidate_declarations':[d,remote],'type_layout_issues':[{'cu':'src/b.c','status':'MISMATCH'}]}


class InterfaceScopeTests(unittest.TestCase):
    def test_remote_conflict_retained_without_blocking_proven_local_declarations(self):
        c=fixture();before=copy.deepcopy(c);blocked,assessments=partition([c],'src/a.c')
        self.assertFalse(blocked);self.assertEqual(assessments[0]['state'],'LOCAL_AGREEMENT_REMOTE_CONFLICT')
        self.assertEqual(c,before);self.assertTrue(assess(c,'src/b.c')['blocking'])

    def test_cu_not_header_path_determines_ownership(self):
        c=fixture();c['candidate_declarations'][0]['file']='src/b.c'
        self.assertFalse(assess(c,'src/a.c')['blocking'])
        c['candidate_declarations'][0]['game_type_layouts'][0]['status']='MISMATCH'
        self.assertTrue(assess(c,'src/a.c')['blocking'])

    def test_unknown_or_incomplete_evidence_stays_blocked(self):
        for change in ('owner','missing-local','layout-owner','missing-layout-check','calling-convention','ambiguous','local-issue'):
            c=fixture()
            if change=='owner': del c['candidate_declarations'][1]['cu']
            elif change=='missing-local': c['candidate_declarations']=c['candidate_declarations'][1:]
            elif change=='layout-owner': del c['type_layout_issues'][0]['cu']
            elif change=='missing-layout-check': del c['candidate_declarations'][0]['game_type_layouts']
            elif change=='calling-convention': c['historical'][0]['calling_convention']='nondefault'
            elif change=='ambiguous': c['historical'].append({**c['historical'][0],'return_type':'void'})
            else: c['type_layout_issues'].append({'cu':'src/a.c','status':'UNAVAILABLE'})
            self.assertTrue(assess(c,'src/a.c')['blocking'],change)

    def test_callee_address_proof_does_not_hide_local_interface_conflict(self):
        c=fixture();calls=[{'function':'f','function_offset':20,'verified':True},{'function':'f','function_offset':10,'verified':True}]
        result=callees(calls,{'f':[c]},'src/b.c')
        self.assertEqual(result['blocking_functions'],['f'])
        self.assertEqual(result['observations'][0]['call_offsets'],[10,20])
        self.assertEqual(result['observations'][0]['local_declarations'][0]['return_type'],'void')
        self.assertTrue(result['observations'][0]['layout_issues'])
        local=callees(calls,{'f':[c]},'src/a.c')
        self.assertFalse(local['blocking_functions'])
        self.assertEqual(local['observations'][0]['state'],'LOCAL_AGREEMENT_REMOTE_CONFLICT')

    def test_missing_callee_declaration_blocks_but_unknown_targets_are_not_guessed(self):
        c=fixture();calls=[{'function':'f','function_offset':1},{'symbol':'_f','function_offset':2},{'function':'other','function_offset':3}]
        result=callees(calls,{'f':[c]},'src/missing.c')
        self.assertEqual(result['blocking_functions'],['f'])
        self.assertEqual(result['observations'][0]['call_offsets'],[1])
        self.assertEqual(len(result['observations']),1)

    def test_variadic_signature_is_checked(self):
        c=fixture();c['historical'][0]['variadic']=True
        self.assertTrue(assess(c,'src/a.c')['blocking'])
        c['candidate_declarations'][0]['canonical_parameter_types'].append('...')
        self.assertFalse(assess(c,'src/a.c')['blocking'])


if __name__=='__main__': unittest.main()
