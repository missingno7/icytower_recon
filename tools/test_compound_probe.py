import unittest
from compound_probe import invert_if
from source_scope import body_hash


class CompoundProbeTests(unittest.TestCase):
    def test_only_unique_target_if_blocks_are_swapped(self):
        source='void peer(){if(x){a();}else{b();}} void f(){if(x){a("}"); if(y){z();}}else{b();} tail();}'
        result,edit=invert_if(source,'f','x')
        self.assertEqual(body_hash(source,'peer'),body_hash(result,'peer'))
        self.assertEqual(source[:edit['start']],result[:edit['start']])
        self.assertIn('if (!(x)) {b();} else {a("}"); if(y){z();}} tail();',result)
        self.assertEqual(source[edit['start']:edit['end']],edit['before'])

    def test_ambiguous_non_scalar_unbraced_and_label_cases_reject(self):
        for body,condition in [('if(x){a();}else{b();} if(x){c();}else{d();}','x'),
                               ('if(x){a();}else if(y){b();}','x'),('if(x) a(); else b();','x'),
                               ('if(x){\nlabel: a();}else{b();}','x'),('if(x){label: a();}else{b();}','x'),
                               ('if(x){\n#if X\na();\n#endif\n}else{b();}','x'),
                               ('if(x){a();}else{b();}','x++')]:
            with self.subTest(body=body),self.assertRaises(ValueError):invert_if('void f(){'+body+'}', 'f',condition)


class CompoundContextTests(unittest.TestCase):
    def test_source_tool_flags_fixture_and_owner_changes_make_history_stale(self):
        import tempfile
        import json
        import copy
        from pathlib import Path
        from unittest.mock import patch
        import compound_context
        from common import identity
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);tool=root/'tools/compound_probe.py';tool.parent.mkdir();tool.write_text('probe')
            path=root/'docs/attempts/compound-probes/game-a/f.json';path.parent.mkdir(parents=True)
            build={'local_inputs':{'src/a.c':{'sha256':'source'}},'candidate_toolchain_lock':'lock','compiler':'tdm-2','config':{'source':'src/a.c'},'flags':['-O2']}
            record={'target':'game-a','function':'f','source_inputs':build['local_inputs'],'toolchain_lock':'lock','compiler':'tdm-2','compiler_config':build['config'],'compiler_flags':['-O2'],'fixture':'pe','verifier':'oracle','probe_tool':identity(tool),'outcome':'COMPLETE','variants':[{'variant':'baseline','status':'DIFFER','candidate_size':20}]}
            with patch.object(compound_context,'ROOT',root):
                path.write_text(json.dumps(record));r=compound_context.load('game-a','f',build,'pe','oracle')
                self.assertEqual(r['baseline_state'],'CURRENT_INPUTS')
                for key in ('source_inputs','toolchain_lock','compiler','compiler_config','compiler_flags','fixture','verifier','probe_tool'):
                    bad=copy.deepcopy(record);bad.pop(key);path.write_text(json.dumps(bad))
                    self.assertEqual(compound_context.load('game-a','f',build,'pe','oracle')['baseline_state'],'HISTORICAL_REQUIRES_REFRESH',key)
                bad=dict(record,function='other');path.write_text(json.dumps(bad))
                self.assertIsNone(compound_context.load('game-a','f',build,'pe','oracle'))
                path.write_text(json.dumps(record));tool.unlink()
                self.assertEqual(compound_context.load('game-a','f',build,'pe','oracle')['baseline_state'],'HISTORICAL_REQUIRES_REFRESH')


if __name__=='__main__':unittest.main()
