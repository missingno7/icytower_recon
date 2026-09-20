import copy
import unittest
from reference_diagnostics import diagnose,counterpart,memory_operand,source_pattern
from classify_diff import workflow


INT={'kind':'base_type','size':4,'type':'int'}


def fixture():
    row={'name':'f','va':0x100,'candidate_offset':0,'status':'DIFFER','masked_equal':True,'instruction_boundaries_verified':True,
         'instructions':[{'address':0,'bytes':'a300000000','mnemonic':'mov','assembly':'mov %eax,0'}],
         'relocations':[{'type':6,'symbol':'_wrong','equal':False,'resolution':'named symbol','target_va':0x401000,'resolved_value':0x401000,'original_value':0x402004,'function_offset':1,'addend':0}]}
    original=[{'address':0x100,'bytes':'a304204000','mnemonic':'mov','assembly':'mov %eax,0x402004'}]
    current={**INT,'expression':'wrong','offset':0,'root':'wrong','root_offset':0}
    expected={**INT,'expression':'menu.max','offset':4,'root':'menu','root_offset':4}
    lookup=lambda address:{0x401000:current,0x402004:expected}.get(address)
    globals_=[{'name':'wrong','layout':INT},{'name':'menu','layout':INT}]
    return row,original,globals_,lookup


class ReferenceTests(unittest.TestCase):
    def test_wrong_global_field_routes_to_owner_not_layout_or_body_edit(self):
        args=fixture(); row=args[0]; result=diagnose(*args); row['reference_diagnostics']=result
        self.assertEqual(result[0]['expected_reference']['expression'],'menu.max')
        self.assertEqual(result[0]['prerequisite'],'OWNER_DECLARATION_REPAIR')
        self.assertFalse(result[0]['expected_declaration_in_candidate']['agrees'])
        self.assertEqual(workflow(row)['difference_class'],'SYMBOLIC_REFERENCE_DIFFERENCE')
        self.assertEqual(workflow(row)['state'],'SOURCE_DIFFER'); self.assertFalse(workflow(row)['body_edit_allowed'])
        self.assertEqual(row['status'],'DIFFER')

    def test_compatible_field_still_needs_source_reference_repair(self):
        args=fixture(); args[2][1]['layout']={'kind':'structure_type','type':'Menu','size':8,'members':[
            {'name':'min','offset':0,'layout':INT,'bitfield':False},{'name':'max','offset':4,'layout':INT,'bitfield':False}]}
        result=diagnose(*args)[0]
        self.assertTrue(result['expected_declaration_in_candidate']['agrees'])
        self.assertEqual(result['prerequisite'],'SOURCE_REFERENCE_REPAIR'); self.assertFalse(result['body_edit_allowed'])

    def test_unknown_shifted_or_contradictory_evidence_is_omitted(self):
        for change in ('opcode','boundary','original-value','candidate-addend','binding','symbol','resolution','overlap','unknown-target'):
            args=fixture(); row,old,globals_,lookup=args; r=row['relocations'][0]
            if change=='opcode': old[0]['bytes']='a104204000'
            elif change=='boundary': old[0]['address']+=1
            elif change=='original-value': r['original_value']+=1
            elif change=='candidate-addend': r['addend']=4
            elif change=='binding': r['resolved_value']=0x403000
            elif change=='symbol': r['symbol']='_different'
            elif change=='resolution': r['resolution']='guessed section'
            elif change=='overlap': row['relocations'].append(copy.deepcopy(r))
            else: args=(*args[:3],lambda address:None)
            self.assertFalse(diagnose(*args),change)

    def test_partial_instruction_skeleton_does_not_establish_source_difference(self):
        args=fixture(); args[0]['masked_equal']=False
        result=diagnose(*args)
        self.assertEqual(result[0]['classification'],'ALIGNED_REFERENCE_OBSERVATION')
        self.assertEqual(result[0]['prerequisite'],'ESTABLISH_INSTRUCTION_CORRESPONDENCE')

    def test_ambiguous_declarations_and_padding_do_not_supply_a_field(self):
        expected=fixture()[3](0x402004)
        self.assertFalse(counterpart(expected,[])['agrees'])
        self.assertFalse(counterpart(expected,[{'name':'menu','layout':INT}]*2)['agrees'])
        self.assertFalse(counterpart(expected,[{'name':'menu','layout':{'kind':'structure_type','type':'Menu','size':8,'members':[]}}])['agrees'])

    def pattern_fixture(self):
        args=fixture(); args[2][1]['layout']={'kind':'structure_type','type':'Menu','size':8,'members':[
            {'name':'min','offset':0,'layout':INT,'bitfield':False},{'name':'max','offset':4,'layout':INT,'bitfield':False}]}
        row=args[0]; row['reference_diagnostics']=diagnose(*args)
        row['reference_diagnostics'][0]['candidate_source_lines']=[{'line':2,'text':'    wrong = n - 1;'}]
        return row,'void f(void) {\n    wrong = n - 1;\n}\n'

    def test_unique_mapped_assignment_recipe_does_not_grant_match(self):
        row,text=self.pattern_fixture(); pattern=source_pattern(row,text,[])
        self.assertEqual(pattern['changes'][0]['before'],'wrong')
        self.assertEqual(pattern['changes'][0]['after'],'menu.max')
        row['reference_source_pattern']=pattern
        self.assertTrue(workflow(row)['body_edit_allowed'])
        self.assertEqual(workflow(row)['state'],'SOURCE_DIFFER')
        self.assertEqual(row['status'],'DIFFER')

    def test_assignment_recipe_rejects_ambiguous_or_incomplete_evidence(self):
        for change in ('read','partial','type','mapping','lines','missing-owner','local','macro','duplicate','compound','member','boundary'):
            row,text=self.pattern_fixture(); d=row['reference_diagnostics'][0]; variables=[]
            if change=='read': d['access']='READ'
            elif change=='partial': row['masked_equal']=False
            elif change=='type': d['expected_reference']['type']='unsigned int'
            elif change=='mapping': d['candidate_source_lines'][0]['text']='wrong = n;'
            elif change=='lines': d['candidate_source_lines']*=2
            elif change=='missing-owner': d['prerequisite']='OWNER_DECLARATION_REPAIR'
            elif change=='local': variables=[{'name':'menu'}]
            elif change=='macro': text='#define menu other\n'+text
            elif change=='duplicate': text=text.replace('}\n','wrong = 2; }\n')
            elif change=='compound': text=text.replace('wrong =','wrong +='); d['candidate_source_lines'][0]['text']='    wrong += n - 1;'
            elif change=='member': d['candidate_reference']['expression']='wrong.value'
            elif change=='boundary': row['instruction_boundaries_verified']=False
            self.assertIsNone(source_pattern(row,text,variables),change)

    def test_reference_and_literal_recipe_requires_all_explicit_tokens(self):
        row,text=self.pattern_fixture()
        text=text.replace('    wrong', '    log("old");\n    wrong')
        row['reference_diagnostics'][0]['candidate_source_lines'][0]['line']=3
        row['literal_diagnostics']=[{'classification':'LITERAL_CONTENT_DIFFERENCE','kind':'C_STRING','candidate_hex':b'old'.hex(),'original_hex':b'new'.hex(),'candidate_source_lines':[{'line':2}]}]
        pattern=source_pattern(row,text,[])
        self.assertEqual([c['after'] for c in pattern['changes']],['"new"','menu.max'])
        row['literal_diagnostics'][0]['candidate_hex']=b'absent'.hex()
        self.assertIsNone(source_pattern(row,text,[]))

    def test_only_supported_absolute_mov_width_is_interpreted(self):
        for raw,offset,expected in [('a100000000',1,'READ'),('a300000000',1,'WRITE'),('8b0d00000000',2,'READ'),('890d00000000',2,'WRITE'),('c7050000000001000000',2,'WRITE'),('6800000000',1,None),('8d0d00000000',2,None),('668b0d00000000',3,None),('8b0c8500000000',3,None)]:
            self.assertEqual(memory_operand(bytes.fromhex(raw),offset),expected)


if __name__=='__main__': unittest.main()
