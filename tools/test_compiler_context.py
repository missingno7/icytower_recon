"""Compiler observations may restrict work, but cannot supply original-match proof."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import compiler_context as context
from classify_diff import workflow
from compiler_probe import scoped_dump


class CompilerContextTests(unittest.TestCase):
    def row(self):
        return {'candidate_size':5,'candidate_offset':16,'source_body_sha256':'body',
                'instructions':[{'address':16,'bytes':'e800000000'}],
                'relocations':[{'function_offset':1,'resolved_value':0x12345678}]}

    def test_only_complete_unambiguous_resolved_code(self):
        row=self.row()
        self.assertEqual(context.resolved_candidate(row),'e878563412')
        for mutation in ('gap','overlap','unresolved','direct_unresolved','field_overlap','outside'):
            bad=copy.deepcopy(row)
            if mutation=='gap': bad['instructions'][0]['bytes']='e8000000'
            elif mutation=='overlap': bad['instructions']*=2
            elif mutation=='unresolved': bad['relocations'][0]['resolved_value']=None
            elif mutation=='direct_unresolved': bad['direct_transfers']=[{'function_offset':1,'resolved_value':None}]
            elif mutation=='field_overlap': bad['relocations']*=2
            else: bad['relocations'][0]['function_offset']=2
            self.assertIsNone(context.resolved_candidate(bad),mutation)

    def test_history_observation_does_not_disappear_after_negative_trial(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); path=root/'docs/attempts/compiler-context/game-a/f.json'; path.parent.mkdir(parents=True)
            record={'probe_tool':{},'source_inputs':{'a':'old'},'toolchain_lock':{},'target_body_sha256':'body','variants':[
                {'variant':'baseline','resolved_code':'e878563412'},
                {'variant':'omit-peer','context_changed_offsets':[2],'target_body_sha256':'body'}]}
            path.with_suffix('.jsonl').write_text(json.dumps(record)+'\n')
            path.write_text(json.dumps({**record,'variants':[record['variants'][0]]}))
            with patch.object(context,'ROOT',root),patch.object(context,'identity',return_value={}):
                found=context.load_context('game-a','f',self.row(),{'a':'new'})
                self.assertEqual(found['state'],'CONTEXT_EVIDENCE_NEEDS_REFRESH')
                self.assertTrue(found['evidence'].endswith('.jsonl'))
                self.assertEqual(context.load_context('game-a','f',self.row(),{'a':'old'})['state'],'CONFIRMED_CONTEXT_DEPENDENCY')
                changed=self.row(); changed['source_body_sha256']='newbody'
                self.assertIsNone(context.load_context('game-a','f',changed,{'a':'old'}))

    def test_body_modified_trial_never_claims_context_dependency(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); path=root/'docs/attempts/compiler-context/game-a/f.json'; path.parent.mkdir(parents=True)
            path.write_text(json.dumps({'target_body_sha256':'body','variants':[
                {'variant':'omit-peer','context_changed_offsets':[2],'target_body_sha256':'changed'}]}))
            with patch.object(context,'ROOT',root): self.assertIsNone(context.load_context('game-a','f',self.row(),{}))

    def test_context_blocks_body_without_granting_layout_or_exact(self):
        row={'status':'DIFFER','compiler_context':{'state':'CONFIRMED_CONTEXT_DEPENDENCY'}}
        state=workflow(row)
        self.assertFalse(state['body_edit_allowed'])
        self.assertEqual(state['state'],'SOURCE_DIFFER')
        self.assertEqual(state['difference_class'],'COMPILER_CONTEXT_DEPENDENCY')
        row.update(status='FUNCTION_MATCH',relocation_resolved_equal=True,instruction_boundaries_verified=True)
        self.assertEqual(workflow(row)['state'],'FUNCTION_MATCH')

    def test_extent_changes_include_inserted_or_removed_bytes(self):
        a={'candidate_size':2,'resolved_code':'90c3'}
        b={'candidate_size':3,'resolved_code':'9090c3'}
        d=context.variant_difference(a,b)
        self.assertTrue(d['extent_changed']);self.assertEqual(d['size_delta'],1)
        self.assertEqual(d['first_changed_offsets'],[1,2]);self.assertEqual(d['changed_byte_count'],2)
        self.assertEqual(context.variant_difference(b,a)['size_delta'],-1)
        self.assertEqual(context.variant_difference(a,a)['changed_byte_count'],0)

    def test_unresolved_bytes_do_not_hide_observed_extent_changes(self):
        record={'target_body_sha256':'body','variants':[
            {'variant':'baseline','candidate_size':2,'resolved_code':None},
            {'variant':'omit-peer','target_body_sha256':'body','candidate_size':3,'resolved_code':None}]}
        changes=context.dependencies(record)
        self.assertEqual(len(changes),1)
        self.assertIsNone(changes[0][1]['changed_byte_count'])
        self.assertFalse(changes[0][1]['resolved_bytes_comparable'])
        record['variants'][1]['target_body_sha256']='edited'
        self.assertEqual(context.dependencies(record),[])

    def test_extent_only_history_blocks_editing_without_exact_claim(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'docs/attempts/compiler-context/game-a/f.json';path.parent.mkdir(parents=True)
            record={'probe_tool':{},'source_inputs':{},'toolchain_lock':{},'target_body_sha256':'body','variants':[
                {'variant':'baseline','candidate_size':5,'resolved_code':'e878563412'},
                {'variant':'omit-peer','target_body_sha256':'body','candidate_size':6,'resolved_code':'e87856341290'}]}
            path.write_text(json.dumps(record))
            with patch.object(context,'ROOT',root),patch.object(context,'identity',return_value={}):
                found=context.load_context('game-a','f',self.row(),{})
            self.assertEqual(found['dependencies'][0]['context_difference']['size_delta'],1)
            state=workflow({'status':'DIFFER','compiler_context':found})
            self.assertEqual(state['state'],'SOURCE_DIFFER');self.assertFalse(state['body_edit_allowed'])

    def test_context_delta_is_bounded_and_checks_recorded_sizes(self):
        a={'candidate_size':100,'resolved_code':'00'*100};b={'candidate_size':100,'resolved_code':'01'*100}
        result=context.variant_difference(a,b)
        self.assertEqual(result['changed_byte_count'],100);self.assertEqual(len(result['first_changed_offsets']),16)
        b['candidate_size']=101
        self.assertFalse(context.variant_difference(a,b)['resolved_bytes_comparable'])

    def test_negative_trial_memory_is_visible_and_unresolved_baseline_not_current(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'docs/attempts/compiler-context/game-a/f.json';path.parent.mkdir(parents=True)
            record={'probe_tool':{},'source_inputs':{},'toolchain_lock':{},'target_body_sha256':'body','variants':[
                {'variant':'baseline','candidate_size':5,'resolved_code':'e878563412'},
                {'variant':'omit-peer','target_body_sha256':'body','candidate_size':5,'resolved_code':'e878563412'}]}
            path.write_text(json.dumps(record))
            with patch.object(context,'ROOT',root),patch.object(context,'identity',return_value={}):
                self.assertIsNone(context.load_context('game-a','f',self.row(),{}))
                trials=context.load_trials('game-a','f',self.row(),{})
                self.assertEqual(trials['state'],'CURRENT_BASELINE')
                self.assertEqual(trials['trials'][0]['difference']['changed_byte_count'],0)
                record['variants'][0]['resolved_code']=None;record['variants'][1].update(resolved_code=None,candidate_size=6)
                path.write_text(json.dumps(record))
                row=self.row();row['relocations'][0]['resolved_value']=None
                self.assertEqual(context.load_context('game-a','f',row,{})['state'],'CONTEXT_EVIDENCE_NEEDS_REFRESH')
                self.assertEqual(context.load_trials('game-a','f',row,{})['state'],'BASELINE_REQUIRES_REVIEW')

    def test_exact_flag_trial_is_diagnostic_and_not_peer_dependency(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'docs/attempts/compiler-context/game-a/f.json';path.parent.mkdir(parents=True)
            record={'probe_tool':{},'source_inputs':{},'toolchain_lock':{},'target_body_sha256':'body','variants':[
                {'variant':'baseline','candidate_size':5,'resolved_code':'e878563412'},
                {'variant':'flag-fno-unit-at-a-time','target_body_sha256':'body','candidate_size':5,'resolved_code':'9090909090',
                 'comparison_verdict':'FUNCTION_MATCH','difference_offsets':[]}]}
            path.write_text(json.dumps(record))
            with patch.object(context,'ROOT',root),patch.object(context,'identity',return_value={}):
                self.assertIsNone(context.load_context('game-a','f',self.row(),{}))
                trial=context.load_trials('game-a','f',self.row(),{})['trials'][0]
            self.assertEqual(trial['diagnostic_original_comparison'],{'verdict':'FUNCTION_MATCH','mismatch_count':0,'acceptance_input':False})

    def test_archive_negatives_survive_narrower_followup_with_own_freshness(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'docs/attempts/compiler-context/game-a/f.json';path.parent.mkdir(parents=True)
            base={'variant':'baseline','candidate_size':5,'resolved_code':'e878563412'}
            def trial(name,code='e878563412'):
                return {'variant':name,'target_body_sha256':'body','candidate_size':5,'resolved_code':code}
            latest={'probe_tool':{},'source_inputs':{},'toolchain_lock':{},'target_body_sha256':'body',
                    'variants':[base,trial('flag-a','9090909090')]}
            archive=copy.deepcopy(latest);archive['probe_tool']={'old':True}
            archive['variants']=[base,trial('flag-a'),trial('flag-b'),trial('flag-c'),trial('flag-d')]
            path.write_text(json.dumps(latest));path.with_suffix('.jsonl').write_text(json.dumps(archive)+'\n')
            with patch.object(context,'ROOT',root),patch.object(context,'identity',return_value={}):
                found=context.load_trials('game-a','f',self.row(),{})
            self.assertEqual(found['state'],'CURRENT_BASELINE')
            self.assertEqual(found['trial_count'],4);self.assertEqual(found['omitted_trial_count'],1)
            a,b,c=found['trials']
            self.assertEqual(a['variant'],'flag-a');self.assertGreater(a['difference']['changed_byte_count'],0)
            self.assertEqual(a['baseline_state'],'CURRENT_BASELINE');self.assertIsNone(a['archive_line'])
            self.assertEqual(b['variant'],'flag-b');self.assertEqual(b['difference']['changed_byte_count'],0)
            self.assertEqual(b['baseline_state'],'BASELINE_REQUIRES_REVIEW');self.assertEqual(b['archive_line'],1)
            self.assertEqual(c['variant'],'flag-c');self.assertTrue(b['evidence'].endswith('.jsonl'))
            self.assertEqual(found['records_considered'],2)

    def test_rtl_excerpt_is_only_requested_function(self):
        text='preamble\n;; Function first (first)\nfirst body\n;; Function second (second)\nsecond body\n'
        excerpt=scoped_dump(text,'first')
        self.assertIn('first body',excerpt)
        self.assertNotIn('second',excerpt)
        self.assertIsNone(scoped_dump(text,'absent'))


if __name__=='__main__': unittest.main()
