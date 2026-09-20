"""Location range, scope and signedness attribution negative controls."""
import unittest
from dwarf_locations import expression_at,decode_location,annotate
from audit_signedness import analyze,type_differences


class LocationTests(unittest.TestCase):
    def test_builtin_type_difference_does_not_guess_shadowed_or_alias_identity(self):
        old=[{'die':1,'name':'c','type':'signed char'},{'die':2,'name':'p','type':'Tview *'}]
        new=[{'die':3,'name':'c','type':'unsigned char'},{'die':4,'name':'p','type':'Tprofile *'}]
        result=type_differences(old,new)
        self.assertEqual([r['variable'] for r in result],['c'])
        self.assertFalse(type_differences(old,new+[new[0]]))
        self.assertFalse(type_differences(old,old))

    def test_register_memory_and_signed_leb(self):
        self.assertEqual(decode_location('53'),{'kind':'register','register':'ebx'})
        self.assertEqual(decode_location('75d477'),{'kind':'memory','register':'ebp','offset':-1068})
        self.assertEqual(decode_location('9104',{'kind':'memory','register':'esp','offset':8}),{'kind':'memory','register':'esp','offset':12})
        self.assertIsNone(decode_location('9104'))

    def test_compound_piece_cfa_and_truncation_not_guessed(self):
        for code in ('539304','9c','7580','539f','53ff',''):
            self.assertIsNone(decode_location(code),code)

    def test_half_open_ranges_and_explicit_base_selection(self):
        tables={5:{'entries':[{'kind':'range','begin':10,'end':20,'expression_hex':'53'},
                             {'kind':'base_address_selection','begin':0xffffffff,'end':200},
                             {'kind':'range','begin':1,'end':5,'expression_hex':'56'}]}}
        self.assertEqual(expression_at('0x5 (location list)',tables,110,100),'53')
        self.assertIsNone(expression_at('0x5 (location list)',tables,120,100))
        self.assertEqual(expression_at('0x5 (location list)',tables,202,100),'56')
        tables[5]['entries'].insert(1,{'kind':'range','begin':10,'end':20,'expression_hex':'51'})
        self.assertIsNone(expression_at('0x5 (location list)',tables,110,100))

    def test_inline_expression(self):
        self.assertEqual(expression_at('3 byte block: 75 d4 77 \t(DW_OP_breg5 (ebp): -1068)',{},0,0),'75d477')
        self.assertEqual(expression_at('2 byte block: 91 4 \t(DW_OP_fbreg: 4)',{},0,0),'9104')

    def test_frame_location_changes_and_scope_gate(self):
        variables=[{'die':1,'name':'c','type':'signed char','base_encoding':'6 (signed char)','scope':9,'location':'1 byte block: 50'}]
        instruction={'address':110,'bytes':'0fbec0','mnemonic':'movsbl','assembly':'movsbl %al,%eax'}
        uses=annotate([instruction],variables,None,{},100,{9:{'low_pc':110,'high_pc':120}})[0]['dwarf_variables']
        self.assertEqual([v['name'] for v in uses],['c'])
        self.assertFalse(annotate([instruction],variables,None,{},100,{9:{'low_pc':90,'high_pc':110}})[0]['dwarf_variables'])
        variables[0]['location']='2 byte block: 91 04'
        instruction['assembly']='movsbl 0xc(%esp),%eax'
        self.assertTrue(annotate([instruction],variables,'2 byte block: 74 08',{},100)[0]['dwarf_variables'])
        self.assertFalse(annotate([instruction],variables,'1 byte block: 9c',{},100)[0]['dwarf_variables'])

    def test_wrong_frame_address_not_attributed(self):
        variable={'die':1,'name':'p','type':'int','location':'2 byte block: 75 08'}
        instruction={'address':20,'bytes':'90','mnemonic':'mov','assembly':'mov 0xc(%ebp),%eax'}
        self.assertFalse(annotate([instruction],[variable],None,{},0)[0]['dwarf_variables'])

    def test_signedness_with_evidenced_variable(self):
        variable={'die':1,'name':'c','type':'signed char','base_encoding':'6 (signed char)','location':'1 byte block: 50'}
        old=[{'address':100,'mnemonic':'movsbl','assembly':'movsbl %al,%eax'}]
        new=[{'address':0,'mnemonic':'movzbl','assembly':'movzbl %al,%eax'}]
        contexts={side:{'variables':[variable],'frame_location':None,'locations':{},'base':base} for side,base in [('original',100),('candidate',0)]}
        row=analyze([variable],[],old,new,location_context=contexts)['instruction_differences'][0]
        self.assertEqual(row['original']['dwarf_variables'][0]['name'],'c')
        self.assertEqual(row['candidate']['dwarf_variables'][0]['name'],'c')

    def test_signed_jump_targets_compare_relative_offsets(self):
        old=[{'address':100,'mnemonic':'jl','assembly':'jl 70 <target>'}]
        new=[{'address':0,'mnemonic':'jb','assembly':'jb c <target>'}]
        self.assertEqual(len(analyze([],[],old,new)['instruction_differences']),1)
        new[0]['assembly']='jb d <different>'
        self.assertFalse(analyze([],[],old,new)['instruction_differences'])


if __name__=='__main__': unittest.main()
