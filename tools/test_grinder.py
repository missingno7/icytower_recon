"""Negative controls for the grinder proof, type graph, scope and transaction boundaries."""
import json
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import ROOT, read_json
from type_graph import graph, TypeGraph
from generate_types import type_header
from source_scope import function_span
from classify_diff import classify,workflow
from build import depfile_inputs
from publication import publication
from interfaces import parameter_type, declarations


class GrinderTests(unittest.TestCase):
    def test_major_types_and_offsets(self):
        g=graph()
        self.assertEqual(g.size(g.game_types['Tprofile'][0]['type_ref']),1360)
        header=type_header(g,'Tprofile')
        self.assertIn('offsetof(Tprofile, jump_hold) == 1248',header)
        for name in ('Tplayer','Tprofile','Treplay','Tmap','Tfloor','Tmenu','Toptions','Tcontrol','Tcharacter'):
            self.assertIn('RECOVERED_STATIC_ASSERT',type_header(g,name))

    def test_conflicting_type_not_silently_merged(self):
        g=graph(); rows=copy.deepcopy(list(g.dies.values()))
        off=g.game_types['Tprofile'][-1]['type_ref']
        for d in rows:
            if d['offset']==off: d['resolved']['DW_AT_byte_size']='1364'
        changed=TypeGraph(rows)
        with self.assertRaisesRegex(ValueError,'Conflicting'): type_header(changed,'Tprofile')

    def test_named_arrays_and_function_pointers(self):
        g=graph()
        self.assertIn('char best_replay_names[32][32]',type_header(g,'Tprofile'))
        fn=next(d for d in g.dies.values() if d['tag']=='DW_TAG_pointer_type' and d.get('type_ref') and g.dies[d['type_ref']]['tag']=='DW_TAG_subroutine_type')
        self.assertIn('(*callback)',g.declaration(fn['offset'],'callback'))

    def test_size_delta_is_not_padding_proof(self):
        for delta in (-2,2):
            self.assertEqual(classify({'status':'DIFFER','candidate_size':100+delta,'original_size':100}),'UNKNOWN_SUPERVISOR')

    def test_masked_equality_does_not_prove_layout(self):
        row={'status':'CODEGEN_SIMILAR','masked_equal':True,'body_shape_equal':True,'relocations':[{'symbol':'.bss','equal':False,'target_va':None}]}
        self.assertEqual(workflow(row)['state'],'CODEGEN_SIMILAR')
        self.assertFalse(workflow(row)['body_edit_allowed'])
        self.assertEqual(classify(row),'COMMON_BSS_LAYOUT')

    def test_verified_same_cu_body_protected(self):
        row={'status':'FUNCTION_MATCH','relocation_resolved_equal':True,'instruction_boundaries_verified':True,
             'direct_transfers':[{'equal':True,'layout_operand_equal':False}]}
        self.assertEqual(workflow(row)['state'],'BODY_MATCH_LAYOUT_BLOCKED')
        self.assertFalse(workflow(row)['body_edit_allowed'])

    def test_unproven_same_cu_body_not_layout_proof(self):
        row={'status':'DIFFER','direct_transfers':[{'equal':False,'layout_operand_equal':False}]}
        self.assertNotEqual(workflow(row)['state'],'BODY_MATCH_LAYOUT_BLOCKED')

    def test_scope_ignores_strings_comments_and_calls(self):
        text='int other(void) { target(); }\nint target(void) { char *s="}"; /* } */ return 1; }\n'
        a,b=function_span(text,'target')
        self.assertEqual(text[a:b],'{ char *s="}"; /* } */ return 1; }')

    def test_outside_body_change_is_rejected(self):
        import grinder_task
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'src').mkdir(); path=root/'src/a.c'
            old='int a(void) { return 1; }\nint b(void) { return 2; }\n'
            path.write_text(old); session={'source':'src/a.c','source_text':old,'function':'a','verify_only':False,'files':{'src/a.c':{}}}
            path.write_text(old.replace('return 2','return 3'))
            with patch.object(grinder_task,'ROOT',root),patch.object(grinder_task,'snapshot_files',return_value={'src/a.c':{}}):
                with self.assertRaisesRegex(ValueError,'outside authorized'): grinder_task.validate_scope(session)

    def test_depfile_continuations_and_escaped_spaces(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'build') as folder:
            path=Path(folder)/'unit.d'
            path.write_text('unit.o: src/timer.c \\\n include/timer.h include/with\\ space.h\n')
            result=[p.relative_to(ROOT).as_posix() for p in depfile_inputs(path)]
            self.assertEqual(result,['src/timer.c','include/timer.h','include/with space.h'])
            self.assertNotIn('include/map.h',result)

    def test_failed_publication_restores_all_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); current=root/'current'; current.mkdir()
            ledger=root/'ledger.json'; ledger.write_bytes(b'old ledger')
            card=current/'card.json'; card.write_bytes(b'old card')
            with self.assertRaises(RuntimeError):
                with publication([ledger,card],current):
                    ledger.write_bytes(b'false exact'); card.write_bytes(b'new card')
                    (current/'new.json').write_text('new')
                    raise RuntimeError('injected generated-status failure')
            self.assertEqual(ledger.read_bytes(),b'old ledger'); self.assertEqual(card.read_bytes(),b'old card')
            self.assertFalse((current/'new.json').exists())

    def test_prototype_parameter_normalization(self):
        self.assertEqual(parameter_type('const char *filename'),'const char*')
        self.assertEqual(parameter_type('unsigned int'),'unsigned int')
        self.assertEqual(parameter_type('Tprofile *'),'Tprofile*')

    def test_depfile_changed_dependency_rejected_unrelated_header_ignored(self):
        from recovery_pipeline import validate_report, verifier_identity, analysis_identity
        from build import TARGETS
        from common import identity
        report={'schema':4,'analysis_identity':analysis_identity(),'verifier':verifier_identity(),'fixture':identity(ROOT/'assets/icytower15.exe'),
                'analysis_tool':identity(Path('C:/msys64/mingw64/bin/objdump.exe')),
                'build':{'inputs_verified_around_compile':True,'target':'game-timer','compiler':'tdm-2','flags':['-O2'],'config':TARGETS['game-timer'],
                'local_inputs':{'src/timer.c':identity(ROOT/'src/timer.c'),'include/timer.h':identity(ROOT/'include/timer.h')},
                'toolchain_lock':identity(ROOT/'toolchain/lock.json'),'candidate_toolchain_lock':identity(ROOT/'toolchain/tdm-2-lock.json')},'functions':[]}
        def changed_unrelated(path):
            return {'sha256':'changed','size':1} if Path(path)==ROOT/'include/map.h' else identity(path)
        with patch('recovery_pipeline.identity',side_effect=changed_unrelated): validate_report(report)
        report['build']['local_inputs']['include/timer.h']={'sha256':'changed','size':1}
        with self.assertRaisesRegex(ValueError,'Stale source/dependency'): validate_report(report)

    def test_ledger_cannot_invent_exact_status(self):
        from refresh_recovery import validate_ledger
        ledger=read_json(ROOT/'src/recovery.json')
        # Current receipts are independently checked; mock only their freshness for this mutation test.
        ledger['src/scroller.c']['functions']['draw_scroller']='FUNCTION_MATCH'
        lock=ROOT/'build/grinder/promotion.lock'
        import os
        owner=int(lock.read_text()) if lock.exists() else os.getpid()
        with patch('refresh_recovery.validate_report'),patch('refresh_recovery.os.getpid',return_value=owner):
            with self.assertRaisesRegex(ValueError,'contradicts verified report'): validate_ledger(ledger)

    def test_signedness_requires_aligned_instruction_evidence(self):
        from audit_signedness import analyze
        original=[{'address':100,'mnemonic':'movsbl','assembly':'movsbl (%eax),%edx'}]
        candidate=[{'address':0,'mnemonic':'movzbl','assembly':'movzbl (%eax),%edx'}]
        self.assertEqual(len(analyze([],[],original,candidate)['instruction_differences']),1)
        candidate[0]['assembly']='movzbl (%ecx),%edx'
        self.assertFalse(analyze([],[],original,candidate)['instruction_differences'])

    def test_failed_exact_promotion(self):
        from promote_function import eligible
        report={'functions':[{'name':'bad','status':'DIFFER','workflow':{'state':'SOURCE_DIFFER'},'first_difference':{'offset':7}}]}
        with patch('promote_function.validate_report'):
            with self.assertRaisesRegex(ValueError,'Promotion denied'): eligible(report,'bad','FUNCTION_MATCH')
            with self.assertRaisesRegex(ValueError,'not mechanically proven'):
                report['functions'][0]['workflow']={'state':'SOURCE_DIFFER'}
                eligible(report,'bad','BODY_MATCH_LAYOUT_BLOCKED')

    def test_layout_proof_requires_explicit_layout_claim(self):
        from promote_function import eligible
        row={'name':'body','status':'FUNCTION_MATCH','workflow':{'state':'BODY_MATCH_LAYOUT_BLOCKED'}}
        with patch('promote_function.validate_report'):
            with self.assertRaisesRegex(ValueError,'CU layout remains blocked'):
                eligible({'functions':[row]},'body','FUNCTION_MATCH')
            self.assertIs(eligible({'functions':[row]},'body','BODY_MATCH_LAYOUT_BLOCKED'),row)

    def test_proven_neighbor_regression_rejected(self):
        from promote_function import no_regressions
        before={'functions':[{'name':'ok','status':'FUNCTION_MATCH','workflow':{'state':'FUNCTION_MATCH'},'source_body_sha256':'a'}]}
        after={'functions':[{'name':'ok','status':'DIFFER'}]}
        with self.assertRaisesRegex(ValueError,'regressed'): no_regressions(before,after)
        after=copy.deepcopy(before); after['functions'][0]['source_body_sha256']='b'
        with self.assertRaisesRegex(ValueError,'Protected'): no_regressions(before,after)

    def test_compile_failure_block_restores_original_bytes(self):
        import grinder_task
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'src').mkdir(); source=root/'src/a.c'; source.write_bytes(b'broken source')
            session_path=root/'session.json'; session_path.write_text('{}')
            session={'source':'src/a.c','source_text':'int a(void) { return 1; }\r\n'}
            with patch.object(grinder_task,'ROOT',root),patch.object(grinder_task,'CURRENT',root/'current'),patch.object(grinder_task,'SESSION',session_path),patch.object(grinder_task,'active_body',return_value=session),patch.object(grinder_task,'fresh_verify',side_effect=RuntimeError('compiler failed')),patch('check_function.record_compile_failure') as recorded,patch.object(grinder_task,'publish_cards'),patch.object(grinder_task,'read_json',return_value={}):
                grinder_task.block('game-a','a','bad experiment')
            self.assertEqual(source.read_bytes(),b'int a(void) { return 1; }\r\n')
            self.assertFalse(session_path.exists()); recorded.assert_called_once()
            self.assertEqual(read_json(root/'current/supervisor-blocks.json')['src/a.c:a']['compile_or_verification_failure'],'compiler failed')

    def test_fast_attempt_limit(self):
        import grinder_task
        with tempfile.TemporaryDirectory() as folder:
            session_path=Path(folder)/'session.json'; session_path.write_text('{}')
            session={'fast_attempts':2}
            with patch.object(grinder_task,'SESSION',session_path),patch.object(grinder_task,'active_body',return_value=session):
                grinder_task.before_fast('game-a','a')
                self.assertEqual(session['fast_attempts'],3)
                with self.assertRaisesRegex(ValueError,'exhausted'): grinder_task.before_fast('game-a','a')

    def test_killed_publication_recovers_durable_snapshot(self):
        import subprocess,sys
        from publication import restore_journal
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); tree=root/'current'; tree.mkdir()
            ledger=root/'ledger.json'; ledger.write_bytes(b'old ledger')
            card=tree/'card.json'; card.write_bytes(b'old card')
            journal=root/'publication.zip'
            code="""import os,sys
from pathlib import Path
from publication import publication
r=Path(sys.argv[1]); t=r/'current'; l=r/'ledger.json'
with publication([l,t/'card.json'],t,r/'publication.zip',r):
 l.write_bytes(b'partial false ledger'); (t/'new.json').write_bytes(b'partial card')
 os._exit(23)
"""
            result=subprocess.run([sys.executable,'-c',code,str(root)],cwd=ROOT/'tools')
            self.assertEqual(result.returncode,23); self.assertTrue(journal.exists())
            restore_journal(journal,root,tree,[ledger])
            self.assertEqual(ledger.read_bytes(),b'old ledger'); self.assertEqual(card.read_bytes(),b'old card')
            self.assertFalse((tree/'new.json').exists()); self.assertFalse(journal.exists())

    def test_journal_rejects_out_of_scope_destinations_before_writing(self):
        from publication import durable_snapshot,restore_journal
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); tree=root/'current'; tree.mkdir()
            forbidden=root/'game.c'; forbidden.write_bytes(b'current source')
            journal=root/'publication.zip'
            durable_snapshot({forbidden:b'unwanted'},tree,journal,root)
            with self.assertRaisesRegex(ValueError,'outside publication scope'): restore_journal(journal,root,tree,[])
            self.assertEqual(forbidden.read_bytes(),b'current source')

    def test_compact_references_rank_groups_and_report_all_omissions(self):
        from card_view import compact_card
        card={'source':'src/example.c','function':'example','parameters':[],'locals':[],
              'lexical_blocks':[],'signedness':{'variables':[]},'first_difference':{'offset':100},
              'relocation_mismatches':[],'direct_transfer_mismatches':[],'original_calls':[],
              'calls':[],'referenced_globals':[]}
        rows=[{'symbol':'unknown','historical_address':1}]
        rows += [{'symbol':'g'+str(i),'historical_address':1000+i,'references':[i*10]} for i in range(12)]
        rows += [{'symbol':'g0','historical_address':1000,'references':[101]}]
        card['referenced_globals']=rows
        card['calls']=copy.deepcopy(rows)
        before=copy.deepcopy(card); compact=compact_card(card)
        self.assertEqual(card,before)
        for key in ('calls','referenced_globals'):
            self.assertEqual(len(compact[key]),8)
            self.assertEqual(compact[key][0]['symbol'],'g10')
            self.assertEqual(compact[key][1]['symbol'],'g0')
            self.assertEqual(compact[key][1]['reference_count'],2)
            self.assertEqual(compact[key][1]['function_offsets'],[101,0])
            self.assertNotIn('unknown',[r['symbol'] for r in compact[key]])
            self.assertEqual(compact['evidence_counts'][key],14)
            self.assertEqual(compact['evidence_counts'][key+'_groups'],13)
            self.assertEqual(compact['evidence_counts'][key+'_omitted_groups'],5)

    def test_compact_card_keeps_proof_and_links_full_target_evidence(self):
        from card_view import compact_card
        card=read_json(ROOT/'docs/current/functions/main/init_game.json')
        if card.get('detailed_evidence'): card=read_json(ROOT/card['detailed_evidence'])
        before=copy.deepcopy(card); compact=compact_card(card)
        self.assertEqual(card,before)
        for key in ('status','state','first_difference','difference_class','body_edit_allowed'):
            self.assertEqual(compact[key],card[key])
        self.assertEqual(compact['evidence_counts']['relocation_mismatches'],len(card['relocation_mismatches']))
        self.assertLessEqual(len(compact['relocation_mismatches']),8)
        self.assertEqual(len(compact['locals']),len(card['locals']))
        self.assertLess(len(json.dumps(compact)),len(json.dumps(card)))


if __name__=='__main__': unittest.main()
