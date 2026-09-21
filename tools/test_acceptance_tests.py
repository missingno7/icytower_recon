import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import acceptance_tests as gate


class AcceptanceRunnerTests(unittest.TestCase):
    def test_empty_module_and_duplicate_inventory_are_rejected(self):
        with patch.dict(gate.GROUPS,{'probe':('a',)}),patch.object(unittest.TestLoader,'loadTestsFromName',return_value=unittest.TestSuite()):
            with self.assertRaises(ValueError):gate.load_group('probe')
        with patch.dict(gate.GROUPS,{'probe':('a','a')}):
            with self.assertRaises(ValueError):gate.load_group('probe')

    def test_import_failure_is_a_failing_test_not_success(self):
        with patch.dict(gate.GROUPS,{'probe':('deliberately_missing_acceptance_module',)}):
            suite,counts=gate.load_group('probe')
            result=unittest.TextTestRunner(stream=io.StringIO()).run(suite)
            self.assertFalse(result.wasSuccessful());self.assertEqual(len(result.errors),1)

    def run_case(self,*,failure=False,changed=False,executed=1):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            result=SimpleNamespace(testsRun=executed,failures=[('case','failure')] if failure else [],errors=[],skipped=[],unexpectedSuccesses=[],wasSuccessful=lambda:not failure)
            runner=SimpleNamespace(run=lambda suite:result)
            identities=iter([{'sha256':'before'},{'sha256':'after' if changed else 'before'}])
            with patch.object(gate,'ROOT',root),patch.dict(gate.GROUPS,{'probe':('a',)}),patch.object(gate,'identity',side_effect=lambda p:next(identities)),patch.object(gate,'load_group',return_value=(unittest.TestSuite(),{'a':1})),contextlib.redirect_stdout(io.StringIO()):
                code=gate.execute('probe',runner)
            report=json.loads((root/'build/acceptance/tests/probe.json').read_text())
            return code,report

    def test_success_records_actual_count_and_selected_input_identity(self):
        code,report=self.run_case()
        self.assertEqual(code,0);self.assertTrue(report['passed']);self.assertEqual(report['tests_run'],1)
        self.assertEqual(report['module_identities'],{'a':{'sha256':'before'}})

    def test_failure_short_execution_and_changed_tests_are_rejected(self):
        for kwargs in ({'failure':True},{'executed':0},{'changed':True}):
            code,report=self.run_case(**kwargs)
            self.assertEqual(code,1);self.assertFalse(report['passed'])

    def test_preflight_failure_removes_stale_success_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);out=root/'build/acceptance/tests/probe.json';out.parent.mkdir(parents=True);out.write_text('{"passed":true}')
            with patch.object(gate,'ROOT',root),patch.dict(gate.GROUPS,{'probe':('missing',)}):
                with self.assertRaises(FileNotFoundError):gate.execute('probe')
            self.assertFalse(out.exists())


if __name__=='__main__':unittest.main()
