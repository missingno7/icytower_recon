import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import interface_task as task
from interface_tasks import plan_interface,patch_text,text_identity


class InterfaceAdmissionTests(unittest.TestCase):
    def fixture(self,root):
        (root/'src').mkdir();source='extern int f(char *p);\n';(root/'src/a.c').write_bytes(source.encode())
        report={'build':{'local_inputs':{'src/a.c':text_identity(source)}}}
        (root/'report.json').write_text(json.dumps(report));ledger={'src/a.c':{'verified_report':'report.json'}}
        (root/'src/recovery.json').write_text(json.dumps(ledger))
        row={'function':'f','historical':[{'cu':'src/a.c','return_type':'int','parameter_types':['const char*'],'variadic':False,'calling_convention':None}],
             'candidate_declarations':[{'cu':'src/a.c','file':'src/a.c','line':1,'kind':'NC','name':'f','return_type':'int','parameter_types':['char*']}],
             'type_layout_issues':[]}
        return source,ledger,row

    def test_plan_regenerates_from_bound_baseline_after_source_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,ledger,row=self.fixture(root)
            with patch('interface_tasks.ROOT',root),patch('interface_tasks.affected_targets',return_value=['game-a']):
                plan=plan_interface(row,ledger)
                (root/'src/a.c').write_bytes(patch_text(source,plan['changes']).encode())
                self.assertEqual(plan_interface(row,ledger,{'src/a.c':source}),plan)

    def test_saved_source_forgery_and_missing_receipt_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,ledger,row=self.fixture(root)
            with patch.object(task,'ROOT',root):
                task.validate_baseline_sources({'sources':{'src/a.c':source}},ledger)
                for sources in ({'src/a.c':source+' '},{'src/unknown.c':source}):
                    with self.assertRaisesRegex(ValueError,'baseline receipt'):task.validate_baseline_sources({'sources':sources},ledger)

    def test_cached_conflict_cannot_supply_admission_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,ledger,row=self.fixture(root)
            fake=root/'docs/current/interface-conflicts.json';fake.parent.mkdir(parents=True);fake.write_text('{"conflicts":[{"function":"f","historical":"forged"}]}')
            session=root/'session.json'
            with patch.object(task,'ROOT',root),patch.object(task,'CURRENT',fake.parent),patch.object(task,'SESSION',session),patch.object(task,'validate_ledger'),patch.object(task,'collect_interfaces',return_value=([row],[row])) as collect,patch('interface_tasks.ROOT',root),patch('interface_tasks.affected_targets',return_value=['game-a']),patch.object(task,'snapshot_files',return_value={}),patch.object(task,'history'):
                task.begin('f')
            recorded=json.loads(session.read_text())
            self.assertEqual(recorded['plan']['historical'],row['historical']);collect.assert_called_once_with(ledger)

    def test_unknown_task_kind_cannot_bypass_interface_plan_checks(self):
        with self.assertRaisesRegex(ValueError,'Unknown mechanical'):
            task.validate_interface_scope({'plan':{'task_kind':'UNVERIFIED'}})

    def test_changed_session_plan_is_rejected_before_apply(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source,ledger,row=self.fixture(root)
            with patch('interface_tasks.ROOT',root),patch('interface_tasks.affected_targets',return_value=['game-a']):
                good=plan_interface(row,ledger)
            bad=copy.deepcopy(good);bad['historical'][0]['return_type']='void'
            session={'function':'f','files':{},'sources':{'src/a.c':source},'plan':bad,'ledger':task.identity(root/'src/recovery.json')}
            with patch.object(task,'ROOT',root),patch.object(task,'snapshot_files',return_value={}),patch.object(task,'validate_ledger'),patch.object(task,'collect_interfaces',return_value=([row],[row])),patch('interface_tasks.ROOT',root),patch('interface_tasks.affected_targets',return_value=['game-a']):
                with self.assertRaisesRegex(ValueError,'plan differs'):task.validate_interface_scope(session,applied=False)
            self.assertEqual((root/'src/a.c').read_text(),source)


if __name__=='__main__':unittest.main()
