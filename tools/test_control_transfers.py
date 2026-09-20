import copy,struct,unittest
from control_transfers import relative,resolve,tail_layout
from classify_diff import workflow
from promote_function import no_regressions


def instruction(address,raw,asm='jmp target'):
    return {'address':address,'bytes':raw.hex(),'mnemonic':asm.split()[0],'assembly':asm}


def fixture():
    old=[instruction(0x1000,b'\x90','nop'),instruction(0x1001,b'\xe9'+struct.pack('<i',0x700-0x1006))]
    new=[instruction(0x100,b'\x90','nop'),instruction(0x101,b'\xeb'+struct.pack('<b',0x90-0x103))]
    candidates=[{'name':'callee','low_pc':0x90},{'name':'f','low_pc':0x100}]
    originals=[{'name':'callee','va':0x700},{'name':'f','va':0x1000}]
    row={'name':'f','va':0x1000,'candidate_offset':0x100,'candidate_size':3,'original_size':6,'status':'DIFFER',
         'instructions':new,'relocations':[],'direct_transfers':[],'instruction_boundaries_verified':True,'source_body_sha256':'body'}
    return row,old,candidates,originals


class TransferTests(unittest.TestCase):
    def test_all_supported_relative_widths(self):
        for raw,width,kind in [(b'\xe8\0\0\0\0',4,'call'),(b'\xe9\0\0\0\0',4,'jmp'),(b'\xeb\0',1,'jmp'),(b'\x75\0',1,'conditional'),(b'\x0f\x85\0\0\0\0',4,'conditional'),(b'\xe3\0',1,'conditional')]:
            d=relative(instruction(100,raw)); self.assertEqual(d['operand_size'],width); self.assertEqual(d['kind'],kind); self.assertEqual(d['target'],100+len(raw))

    def test_short_transfer_byte_equality_is_not_target_proof(self):
        code=bytearray(b'\xeb\0'); reference=bytes(code); rows=[instruction(0x10,bytes(code))]
        transfers=resolve(code,reference,0x10,0x12,0x1000,rows,[{'name':'wrong','low_pc':0x12}],[{'name':'wrong','va':0x1005}],[])
        self.assertFalse(transfers[0]['equal']); self.assertEqual(transfers[0]['resolved_value'],3)
        self.assertNotEqual(bytes(code),reference)
        code=bytearray(reference)
        transfers=resolve(code,reference,0x10,0x12,0x1000,rows,[{'name':'wrong','low_pc':0x12}],[{'name':'wrong','va':0x2000}],[])
        self.assertEqual(bytes(code),reference); self.assertFalse(all(t['equal'] for t in transfers))

    def test_short_exact_target_and_ambiguous_or_unknown_entries(self):
        rows=[instruction(0x10,b'\xeb\0')]; target={'name':'g','low_pc':0x12}
        def check(candidates,originals):
            return resolve(bytearray(b'\xeb\0'),b'\xeb\0',0x10,0x12,0x1000,rows,candidates,originals,[])[0]
        self.assertTrue(check([target],[{'name':'g','va':0x1002}])['equal'])
        self.assertFalse(check([target,dict(target,name='alias')],[{'name':'g','va':0x1002}])['equal'])
        self.assertFalse(check([],[])['equal'])

    def test_internal_edges_and_real_coff_relocations_are_not_reinterpreted(self):
        self.assertEqual(resolve(bytearray(b'\xeb\0\xc3'),b'\xeb\0\xc3',0,3,0x1000,[instruction(0,b'\xeb\0')],[],[],[]),[])
        self.assertEqual(resolve(bytearray(b'\xe8\0\0\0\0'),b'\xe8\0\0\0\0',0,5,0x1000,[instruction(0,b'\xe8\0\0\0\0')],[],[],[{'function_offset':1}]),[])

    def test_unknown_encoding_and_extent_crossing_are_not_silent(self):
        row=instruction(0,b'\x66\xe9\0\0','data16 jmp 4')
        result=resolve(bytearray(b'\x66\xe9\0\0'),b'\x66\xe9\0\0',0,4,0x1000,[row],[],[],[])
        self.assertFalse(result[0]['equal']); self.assertEqual(result[0]['operand_size'],0)
        code=bytearray(b'\xeb'); result=resolve(code,b'\xeb',0,1,0x1000,[instruction(0,b'\xeb\0')],[],[],[])
        self.assertFalse(result[0]['equal']); self.assertEqual(len(code),1)

    def test_range_forced_tail_is_layout_blocked_not_function_match(self):
        row,old,candidates,originals=fixture(); proof=tail_layout(row,old,candidates,originals)
        self.assertIsNotNone(proof); self.assertEqual(proof['prefix_size'],1)
        row['tail_jump_layout']=proof; row['workflow']=workflow(row)
        self.assertEqual(row['status'],'DIFFER'); self.assertEqual(row['workflow']['state'],'BODY_MATCH_LAYOUT_BLOCKED'); self.assertFalse(row['workflow']['body_edit_allowed'])
        before={'functions':[{'name':'f','status':'FUNCTION_MATCH','workflow':{'state':'FUNCTION_MATCH'},'source_body_sha256':'body'}]}
        no_regressions(before,{'functions':[row]})
        row['source_body_sha256']='edited'
        with self.assertRaises(ValueError): no_regressions(before,{'functions':[row]})

    def test_wrong_prefix_target_call_or_reference_cannot_claim_layout(self):
        for mutation in ('prefix','target','call','reference','prefix-relocation','ambiguous','boundaries'):
            row,old,candidates,originals=fixture(); reference=None
            if mutation=='prefix': row['instructions'][0]['bytes']='cc'
            elif mutation=='target': row['instructions'][-1]['bytes']='eb8e'
            elif mutation=='call': old[-1]['bytes']='e8'+old[-1]['bytes'][2:]
            elif mutation=='reference': reference=b'bad'
            elif mutation=='prefix-relocation': row['relocations']=[{'function_offset':0,'equal':False,'resolved_value':None}]
            elif mutation=='ambiguous': candidates.append(dict(candidates[0],name='alias'))
            else: row['instruction_boundaries_verified']=False
            self.assertIsNone(tail_layout(row,old,candidates,originals,reference=reference),mutation)

    def test_long_encoding_that_could_have_been_short_is_not_a_layout_proof(self):
        row,old,candidates,originals=fixture(); originals[0]['va']=0xff0
        old[-1]['bytes']=(b'\xe9'+struct.pack('<i',0xff0-0x1006)).hex()
        self.assertIsNone(tail_layout(row,old,candidates,originals))
        # A rel32 self-loop's encoded displacement is -130, but its hypothetical
        # short displacement is -127. The apparent size difference is not proof.
        old=[instruction(0x1000+i,b'\x90','nop') for i in range(125)]+[instruction(0x107d,b'\xe9'+struct.pack('<i',-130))]
        row.update(instructions=[instruction(0x100+i,b'\x90','nop') for i in range(125)]+[instruction(0x17d,b'\xeb\x81')],candidate_size=127,original_size=130)
        self.assertIsNone(tail_layout(row,old,[{'name':'f','low_pc':0x100}],[{'name':'f','va':0x1000}]))

    def test_reverse_short_to_near_relaxation_has_the_same_strict_contract(self):
        old=[instruction(0x1000,b'\x90','nop'),instruction(0x1001,b'\xeb'+struct.pack('<b',0xff0-0x1003))]
        new=[instruction(0x100,b'\x90','nop'),instruction(0x101,b'\xe9'+struct.pack('<i',0x400-0x106))]
        row={'va':0x1000,'candidate_offset':0x100,'candidate_size':6,'original_size':3,'instructions':new,'instruction_boundaries_verified':True}
        proof=tail_layout(row,old,[{'name':'g','low_pc':0x400}],[{'name':'g','va':0xff0}])
        self.assertIsNotNone(proof); self.assertEqual(proof['original_encoding_bytes'],2); self.assertEqual(proof['candidate_encoding_bytes'],5)

    def test_diagnostic_resolver_handles_one_byte_fields(self):
        from compiler_context import resolved_candidate
        row={'candidate_size':2,'candidate_offset':0,'instructions':[instruction(0,b'\xeb\0')],
             'direct_transfers':[{'function_offset':1,'operand_size':1,'resolved_value':127}]}
        self.assertEqual(resolved_candidate(row),'eb7f')


if __name__=='__main__': unittest.main()
