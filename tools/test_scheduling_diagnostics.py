import copy,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from scheduling_diagnostics import analyze,assignment_patterns,source_rows
from classify_diff import workflow


def fixture(extra=None):
    a=[('8b7270','mov','mov    0x70(%edx),%esi'),('8b5a6c','mov','mov    0x6c(%edx),%ebx')]
    def instructions(items,base):
        result=[]
        for raw,mnemonic,asm in items:
            result.append({'address':base,'bytes':raw,'mnemonic':mnemonic,'assembly':asm}); base+=len(bytes.fromhex(raw))
        return result
    tail=extra or [('c3','ret','ret')]
    old=instructions(a+tail,0x1000); new=instructions(a[::-1]+tail,0)
    size=sum(len(bytes.fromhex(r['bytes'])) for r in old)
    row={'status':'DIFFER','va':0x1000,'candidate_offset':0,'candidate_size':size,'original_size':size,
         'instructions':new,'instruction_boundaries_verified':True,'relocations':[],'direct_transfers':[]}
    return row,old


class SchedulingTests(unittest.TestCase):
    def test_permutation_is_observation_not_match(self):
        row,old=fixture(); result=analyze(row,old)
        self.assertTrue(result['cheap_routing_eligible']); self.assertEqual(result['windows'][0]['byte_length'],6)
        row['instruction_order']=result
        self.assertEqual(workflow(row)['state'],'SOURCE_DIFFER')
        self.assertEqual(workflow(row)['difference_class'],'INSTRUCTION_ORDER')
        self.assertTrue(workflow(row)['body_edit_allowed'])

    def test_changed_operand_is_not_an_instruction_permutation(self):
        row,old=fixture(); row['instructions'][0]['bytes']='8b5a68'
        self.assertIsNone(analyze(row,old))

    def test_remaining_code_or_unresolved_fields_prevent_cheap_routing(self):
        row,old=fixture([('b800000000','mov','mov $0x0,%eax'),('c3','ret','ret')])
        row['instructions'][-1]['bytes']='90'
        result=analyze(row,old); self.assertFalse(result['cheap_routing_eligible']); self.assertEqual(result['remaining_difference_offsets'],[11])
        row,old=fixture([('b800000000','mov','mov $0x0,%eax'),('c3','ret','ret')])
        row['relocations']=[{'function_offset':7,'resolved_value':None,'equal':False}]
        result=analyze(row,old); self.assertFalse(result['cheap_routing_eligible']); self.assertEqual(result['unresolved_relocation_offsets'],[7])

    def test_relocated_windows_and_internal_entries_are_excluded(self):
        row,old=fixture(); row['relocations']=[{'function_offset':1,'resolved_value':0,'equal':False}]
        self.assertIsNone(analyze(row,old))
        row,old=fixture([('ebfb','jmp','jmp 1003')]); row['instructions'][-1]['assembly']='jmp 3'
        self.assertIsNone(analyze(row,old))

    def test_indirect_jump_keeps_observation_but_requires_supervisor(self):
        row,old=fixture([('ffe0','jmp','jmp *%eax')]); result=analyze(row,old)
        self.assertTrue(result['indirect_jump_present']); self.assertFalse(result['cheap_routing_eligible'])

    def test_source_lines_do_not_confuse_header_context_or_end_sequence(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'a.c').write_text('one\ntwo\nthree\n')
            instructions=[{'address':10},{'address':20},{'address':30}]
            lines=[{'address':10,'context':'a.c','line':1},{'address':20,'context':'inline.h','line':2},{'address':30,'context':'a.c','line':3,'end_sequence':True}]
            with patch('scheduling_diagnostics.ROOT',root):
                result=source_rows(instructions,lines,'a.c')
            self.assertEqual(result,[{'file':'a.c','line':1,'text':'one'}])

    def test_adjacent_assignments_preserve_exact_spans(self):
        text='    w=p->w;\r\n    h=p->h;\r\n'
        diag={'cheap_routing_eligible':True,'windows':[{'function_offset':12,'candidate_source_lines':[{'line':1},{'line':2}]}]}
        patterns=assignment_patterns(diag,text); self.assertEqual(len(patterns),1)
        self.assertEqual(patterns[0]['changes'][0]['after'],'    h=p->h;\r\n    w=p->w;\r\n')
        for bad in ['w=h;\nh=p->h;\n','w=f();\nh=p->h;\n','*w=p->w;\nh=p->h;\n','w=p++;\nh=p->h;\n','int w=1;\nh=2;\n']:
            self.assertFalse(assignment_patterns(diag,bad))
        diag['cheap_routing_eligible']=False
        self.assertFalse(assignment_patterns(diag,text))

    def test_pattern_application_is_bounded_and_records_the_actual_change(self):
        import apply_pattern
        text='int f(void) {\n a=x;\n b=y;\n}\nint g(void) { return 1; }\n'
        start=text.index(' a=x;'); end=text.index('}',start)
        change={'start':start,'end':end,'before':text[start:end],'after':' b=y;\n a=x;\n'}
        session={'target':'t','function':'f','verify_only':False,'source':'a.c','source_text':text}
        card={'difficulty':'CHEAP','body_edit_allowed':True,'source_patterns':[{'id':'p','changes':[change],'reason':'fixture'}]}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); path=root/'session.json'; path.write_text('{}'); source=root/'a.c'; source.write_bytes(text.encode('cp1252'))
            (root/'src').mkdir(); ledger_file=root/'src/recovery.json'; ledger_file.write_text('{}')
            from common import identity
            session['ledger']=identity(ledger_file)
            inputs=[session,{'a.c':{'verified_report':'report.json'}},{'functions':[{'name':'f'}]}]
            with patch.object(apply_pattern,'ROOT',root),patch.object(apply_pattern,'SESSION',path),patch.object(apply_pattern,'read_json',side_effect=inputs),patch.object(apply_pattern,'validate_scope'),patch.object(apply_pattern,'validate_report'),patch.object(apply_pattern,'card_for',return_value=card):
                apply_pattern.apply('t','f','p')
            self.assertIn(' b=y;\n a=x;',source.read_text()); self.assertIn('int g(void) { return 1; }',source.read_text())
            self.assertIn('applied_pattern',path.read_text())
            source.write_bytes(text.encode('cp1252')); change.update(start=0,end=3,before='int',after='bad')
            with patch.object(apply_pattern,'ROOT',root),patch.object(apply_pattern,'SESSION',path),patch.object(apply_pattern,'read_json',side_effect=inputs),patch.object(apply_pattern,'validate_scope'),patch.object(apply_pattern,'validate_report'),patch.object(apply_pattern,'card_for',return_value=card):
                with self.assertRaisesRegex(ValueError,'exceeds'): apply_pattern.apply('t','f','p')
            self.assertEqual(source.read_text(),text)

    def test_diagnostic_refresh_refuses_tool_changes_before_or_during_run(self):
        import recovery_pipeline as pipeline
        with patch.object(pipeline,'analysis_identity',return_value={'changed':True}):
            with self.assertRaisesRegex(ValueError,'startup'): pipeline.reanalyze_report({})
        report={'build':{'target':'t'},'functions':[],'candidate_debug':{'schema':7},'data_snapshot':{'present':True}}
        with patch.object(pipeline,'analysis_identity',side_effect=[pipeline.LOADED_ANALYSIS_IDENTITY,{'changed':True}]),patch.object(pipeline,'verifier_identity',return_value=pipeline.LOADED_VERIFIER_IDENTITY),patch.object(pipeline,'validate_report'),patch.object(pipeline,'diagnose',return_value={}),patch.object(pipeline,'unit_for_target',return_value={'functions':[]}):
            with self.assertRaisesRegex(ValueError,'regeneration'): pipeline.reanalyze_report(report)

    def test_apply_rejects_verification_only_and_edited_sessions(self):
        import apply_pattern
        session={'target':'t','function':'f','verify_only':True,'source':'a.c','source_text':'old'}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); path=root/'session.json'; path.write_text('{}'); (root/'a.c').write_text('changed')
            with patch.object(apply_pattern,'ROOT',root),patch.object(apply_pattern,'SESSION',path),patch.object(apply_pattern,'read_json',return_value=session),patch.object(apply_pattern,'validate_scope'):
                with self.assertRaisesRegex(ValueError,'Verification-only'): apply_pattern.apply('t','f','p')
                session['verify_only']=False
                with self.assertRaisesRegex(ValueError,'already applied'): apply_pattern.apply('t','f','p')


if __name__=='__main__': unittest.main()
