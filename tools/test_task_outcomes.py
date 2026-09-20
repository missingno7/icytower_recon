import unittest
from unittest.mock import patch
from contextlib import ExitStack
from task_outcomes import CandidateRejected,candidate_check,CANDIDATE_REJECTED_EXIT,fast_exit
import interface_task


class TaskOutcomeTests(unittest.TestCase):
    def test_only_known_predicate_value_errors_become_candidate_rejections(self):
        self.assertEqual(candidate_check(lambda: 'ok'),'ok')
        def reject(): raise ValueError('exact neighbor regressed')
        with self.assertRaisesRegex(CandidateRejected,'neighbor'): candidate_check(reject)
        for error in (OSError('disk unavailable'),RuntimeError('compiler failed'),KeyError('missing evidence')):
            def fail(): raise error
            with self.assertRaises(type(error)) as caught: candidate_check(fail)
            self.assertIs(caught.exception,error)
        self.assertNotIn(CANDIDATE_REJECTED_EXIT,(0,1,2,127))

    def test_fast_success_distinguishes_proof_state_from_raw_byte_status(self):
        for state in ('FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED'):
            self.assertEqual(fast_exit(state),0)
        for state in ('SOURCE_DIFFER','CODEGEN_SIMILAR','MISSING','UNKNOWN',''):
            self.assertEqual(fast_exit(state),CANDIDATE_REJECTED_EXIT)

    def verify_with_failure(self,compile_error=None,proof_error=None):
        session={'function':'task','plan':{'task_kind':'INTERFACE','affected_targets':['target']}}
        with ExitStack() as stack:
            for name in ('validate_interface_scope','verify_inputs','check_fixture'):
                stack.enter_context(patch.object(interface_task,name))
            stack.enter_context(patch.object(interface_task,'read_json',side_effect=[{'src/a.c':{'verified_report':'before.json'}},{}]))
            stack.enter_context(patch.object(interface_task,'fresh_verify',side_effect=compile_error,return_value={'build':{'config':{'source':'src/a.c'}}}))
            stack.enter_context(patch.object(interface_task,'no_regressions',side_effect=proof_error))
            stack.enter_context(patch('contribution_diagnostics.compare',return_value={}))
            stack.enter_context(patch.object(interface_task,'write_json'))
            interface_task.verify_interface(session)

    def test_compile_or_input_value_error_is_not_candidate_rejection(self):
        for error in (ValueError('toolchain identity changed'),OSError('cannot open object'),RuntimeError('gcc failed')):
            with self.assertRaises(type(error)) as caught: self.verify_with_failure(compile_error=error)
            self.assertIs(caught.exception,error)
            self.assertNotIsInstance(caught.exception,CandidateRejected)

    def test_fresh_comparison_rejection_is_explicit(self):
        with self.assertRaisesRegex(CandidateRejected,'exact neighbor'):
            self.verify_with_failure(proof_error=ValueError('exact neighbor regressed'))
        error=OSError('comparison evidence unreadable')
        with self.assertRaises(OSError) as caught: self.verify_with_failure(proof_error=error)
        self.assertIs(caught.exception,error)


if __name__=='__main__': unittest.main()
