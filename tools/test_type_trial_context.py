import json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from common import identity
import type_trial_context


class TypeTrialContextTests(unittest.TestCase):
    def test_unplanned_supervisor_card_has_no_inferred_target(self):
        self.assertEqual(type_trial_context.summaries({"function":"unplanned"}),[])

    def test_source_tool_identity_and_bounded_diagnostics(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            paths=['src/a.c','tools/type_context_probe.py','tools/type_tasks.py','tools/type_views.py','tools/interface_tasks.py']
            for p in paths:(root/p).parent.mkdir(parents=True,exist_ok=True);(root/p).write_text('original')
            build={'compiler':'tdm-2','config':{},'flags':['-O2'],'candidate_toolchain_lock':1,'local_inputs':{'src/a.c':identity(root/'src/a.c')}}
            report={'build':build,'fixture':1,'verifier':1}
            dest=root/'docs/current/reports/cu.json';dest.parent.mkdir(parents=True);dest.write_text(json.dumps(report))
            record={'target':'cu','task':'view','compiler':build,'fixture':1,'verifier':1,'source_inputs':build['local_inputs'],
                    'probe_tools':{p:identity(root/p) for p in paths[1:]},'variants':[{'variant':'canonical','raw_baseline_equal':False,'contribution_diagnostics':{'changed_functions':[{'function':str(i)} for i in range(7)]}}]}
            dest=root/'docs/attempts/type-context-probes/cu/view.json';dest.parent.mkdir(parents=True);dest.write_text(json.dumps(record))
            card={'function':'view','affected_targets':['cu']}
            with patch.object(type_trial_context,'ROOT',root):
                row=type_trial_context.summaries(card)[0]
                self.assertEqual(row['baseline_state'],'CURRENT_INPUTS');self.assertEqual(row['variants'][0]['omitted_changed_functions'],3)
                (root/'src/a.c').write_text('changed')
                self.assertEqual(type_trial_context.summaries(card)[0]['baseline_state'],'HISTORICAL_REQUIRES_REFRESH')
                (root/'src/a.c').write_text('original');(root/'tools/type_tasks.py').write_text('changed')
                self.assertEqual(type_trial_context.summaries(card)[0]['baseline_state'],'HISTORICAL_REQUIRES_REFRESH')


if __name__=='__main__':unittest.main()
