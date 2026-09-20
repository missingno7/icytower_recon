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

    def test_rtl_excerpt_is_only_requested_function(self):
        text='preamble\n;; Function first (first)\nfirst body\n;; Function second (second)\nsecond body\n'
        excerpt=scoped_dump(text,'first')
        self.assertIn('first body',excerpt)
        self.assertNotIn('second',excerpt)
        self.assertIsNone(scoped_dump(text,'absent'))


if __name__=='__main__': unittest.main()
