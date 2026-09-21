import unittest
from predicate_probe import plan


class PredicateTests(unittest.TestCase):
    def test_unique_condition_only(self):
        text='int f(P *a){ if (a->flag) return 1; return 0; } int g(){return 2;}'
        changed,edit=plan(text,'f','a->flag')
        self.assertEqual(changed,text.replace('if (a->flag)','if ((a->flag) == 1)'))
        self.assertEqual(edit['before'],'a->flag')
    def test_ambiguous_complex_or_negated_condition_rejected(self):
        for text,expression in [('int f(){if(x){} if(x){}}','x'),('int f(){if(!x){}}','x'),('int f(){if(f()){}}','f()')]:
            with self.assertRaises(ValueError):plan(text,'f',expression)


class ReturnGuardTests(unittest.TestCase):
    def test_moves_only_returning_guard_and_function_tail(self):
        from predicate_probe import invert_return_guard
        text='int f(P*a,P*b){ int x=0; if(a->v != b->v){if(a->v)return -1;return 1;} return g(x); } int h(){return 4;}'
        changed,edit=invert_return_guard(text,'f','a->v != b->v')
        self.assertIn('if (!(a->v != b->v)) { return g(x); } else {if(a->v)return -1;return 1;}',changed)
        self.assertTrue(changed.endswith('} int h(){return 4;}'))
        self.assertEqual(text[:edit['start']],changed[:edit['start']])
    def test_fallthrough_nested_else_and_labels_rejected(self):
        from predicate_probe import invert_return_guard
        for body in ['if(a!=b){x++;} return 1;', 'if(a!=b){if(x)return 1;}return 2;',
                     'if(a!=b){return 1;}else{return 2;}', 'if(x){if(a!=b){return 1;}}return 2;',
                     'if(a!=b){return 1;} label: return 2;']:
            with self.assertRaises(ValueError):invert_return_guard('int f(){'+body+'}','f','a!=b')


class PredicateMemoryTests(unittest.TestCase):
    def test_changed_tool_or_source_marks_trial_historical(self):
        import tempfile,json
        from pathlib import Path
        from unittest.mock import patch
        from common import identity
        import predicate_context
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'tools').mkdir()
            paths=['tools/predicate_probe.py','tools/source_scope.py']
            for p in paths:(root/p).write_text('tool')
            build={'local_inputs':{'src/a.c':1},'compiler':'tdm-2','config':{},'flags':['-O2'],'candidate_toolchain_lock':1}
            record={'target':'a','function':'f','compiler':build,'source_inputs':build['local_inputs'],'fixture':1,'verifier':1,'probe_tools':{p:identity(root/p) for p in paths},'variants':[]}
            path=root/'docs/attempts/predicate-probes/a/f.json';path.parent.mkdir(parents=True);path.write_text(json.dumps(record))
            with patch.object(predicate_context,'ROOT',root):
                self.assertEqual(predicate_context.load('a','f',build,1,1)['baseline_state'],'CURRENT_INPUTS')
                (root/paths[0]).write_text('changed')
                self.assertEqual(predicate_context.load('a','f',build,1,1)['baseline_state'],'HISTORICAL_REQUIRES_REFRESH')
                (root/paths[0]).write_text('tool');build['local_inputs']={'src/a.c':2}
                self.assertEqual(predicate_context.load('a','f',build,1,1)['baseline_state'],'HISTORICAL_REQUIRES_REFRESH')


if __name__=='__main__':unittest.main()
