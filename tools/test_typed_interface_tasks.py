import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from typed_interface_tasks import plan
from interface_tasks import patch_text


class TypedCallerTests(unittest.TestCase):
    def run_plan(self,text='extern void f(void *p);\n',kind='NC',expected_return='void',actual_return='void',params=None,mutate=None,collision=False,included=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'src').mkdir();(root/'include/recovered').mkdir(parents=True)
            (root/'src/a.c').write_bytes(text.encode());(root/'include/recovered/Tcontrol.h').write_text('typedef struct { int x; } Tcontrol;\n')
            report={'build':{'local_inputs':{'src/a.c':{}}}}
            if included:report['build']['local_inputs']['include/recovered/Tcontrol.h']={}
            if collision:
                (root/'include/old.h').write_text('typedef int Tcontrol;\n');report['build']['local_inputs']['include/old.h']={}
            (root/'report.json').write_text(json.dumps(report))
            row={'function':'f','historical':[{'cu':'src/original.c','return_type':expected_return,'parameter_types':['Tcontrol*'],'calling_convention':None,'variadic':False}],
                 'candidate_declarations':[{'cu':'src/a.c','file':'src/a.c','kind':kind,'line':1,'return_type':actual_return,'parameter_types':params or ['void*']}],
                 'type_layout_issues':[{'cu':'src/a.c','file':'src/a.c','line':1,'status':'UNAVAILABLE','candidate_type':'void'}]}
            if mutate:mutate(row)
            with patch('typed_interface_tasks.ROOT',root),patch('type_graph.graph',return_value=SimpleNamespace(game_types={'Tcontrol':[]})),patch('interface_tasks.affected_targets',return_value=['game-a']):
                result=plan(row,{'src/a.c':{'verified_report':'report.json'}})
            return result,patch_text(text,result['changes'])

    def test_definition_placeholder_parameter_is_retyped_in_place(self):
        import typed_interface_tasks
        with patch.object(typed_interface_tasks,'plan',typed_interface_tasks.plan):
            text='void f(void *p, int n)\n{\n    use(p, n);\n}\n'
            result,new=self.run_plan(text,kind='NF',expected_return='void',actual_return='void',params=['void*','int'],
                                     mutate=lambda r:r['historical'][0].update(parameter_types=['Tcontrol*','int']))
            self.assertEqual(new,'#include "recovered/Tcontrol.h"\nvoid f(Tcontrol *p, int n)\n{\n    use(p, n);\n}\n')
            self.assertEqual([e['before'] for e in result['changes'] if e['before']],['void'])
        # Return changes, typed non-placeholder parameters and count changes stay out of definitions.
        with self.assertRaises(ValueError):self.run_plan('void *f(void *p) {}\n',kind='NF',expected_return='Tcontrol*',actual_return='void*')
        with self.assertRaises(ValueError):self.run_plan('void f(int *p) {}\n',kind='NF',params=['int*'])
        with self.assertRaises(ValueError):self.run_plan('void f(void *p, int n) {}\n',kind='NF',params=['void*','int'])

    def test_cross_cu_void_to_int_typed_interface_is_bounded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
            (root/'include/recovered/Tcontrol.h').write_text('typedef struct { int x; } Tcontrol;\n')
            profile='#include "recovered/Tcontrol.h"\nvoid f(void *p);\nvoid f(void *p) { use(p); }\n'
            menu='extern void f(void *p);\nvoid caller(void *p) { f(p); }\n'
            (root/'src/profile.c').write_bytes(profile.encode())
            (root/'src/menu.c').write_bytes(menu.encode())
            for target,inputs in (('game-profile',{'src/profile.c':{},'include/recovered/Tcontrol.h':{}}),
                                  ('game-menu',{'src/menu.c':{}})):
                (root/(target+'.json')).write_text(json.dumps({'build':{'target':target,'local_inputs':inputs}}))
            row={'function':'f','historical':[{'cu':'src/profile.c','return_type':'int','parameter_types':['Tcontrol*'],'variadic':False,'calling_convention':None}],
                 'candidate_declarations':[
                     {'cu':'src/profile.c','file':'src/profile.c','line':2,'kind':'NC','return_type':'void','parameter_types':['void*']},
                     {'cu':'src/profile.c','file':'src/profile.c','line':3,'kind':'NF','return_type':'void','parameter_types':['void*']},
                     {'cu':'src/menu.c','file':'src/menu.c','line':1,'kind':'OC','return_type':'void','parameter_types':['void*']}],
                 'type_layout_issues':[{'cu':d['cu'],'file':d['file'],'line':d['line'],'status':'UNAVAILABLE','candidate_type':'void'} for d in [
                     {'cu':'src/profile.c','file':'src/profile.c','line':2},
                     {'cu':'src/profile.c','file':'src/profile.c','line':3},
                     {'cu':'src/menu.c','file':'src/menu.c','line':1}]]}
            ledger={'src/profile.c':{'verified_report':'game-profile.json'},'src/menu.c':{'verified_report':'game-menu.json'}}
            def targets(_ledger,files): return ['game-menu','game-profile']
            with patch('typed_interface_tasks.ROOT',root), patch('type_graph.graph',return_value=SimpleNamespace(game_types={'Tcontrol':[]})), \
                 patch('interface_tasks.affected_targets',side_effect=targets):
                result=plan(row,ledger)
            edits={file:[] for file in result['sources']}
            for edit in result['changes']: edits[edit['file']].append(edit)
            self.assertEqual(result['sources'],['src/menu.c','src/profile.c'])
            self.assertEqual(result['affected_targets'],['game-menu','game-profile'])
            self.assertEqual(patch_text(menu,edits['src/menu.c']),
                             '#include "recovered/Tcontrol.h"\nextern int f(Tcontrol*);\nvoid caller(void *p) { f(p); }\n')
            self.assertEqual(patch_text(profile,edits['src/profile.c']),
                             '#include "recovered/Tcontrol.h"\nint f(Tcontrol*);\nint f(Tcontrol *p) { use(p); }\n')
            # Neither a returned value nor a definition return statement is authorized.
            (root/'src/menu.c').write_bytes(b'extern void f(void *p);\nint caller(void *p) { return f(p); }\n')
            with patch('typed_interface_tasks.ROOT',root), patch('type_graph.graph',return_value=SimpleNamespace(game_types={'Tcontrol':[]})), \
                 patch('interface_tasks.affected_targets',side_effect=targets):
                with self.assertRaises(ValueError): plan(row,ledger)
            (root/'src/menu.c').write_bytes(menu.encode())
            (root/'src/profile.c').write_bytes(profile.replace('{ use(p); }','{ use(p); return; }').encode())
            with patch('typed_interface_tasks.ROOT',root), patch('type_graph.graph',return_value=SimpleNamespace(game_types={'Tcontrol':[]})), \
                 patch('interface_tasks.affected_targets',side_effect=targets):
                with self.assertRaises(ValueError): plan(row,ledger)

    def test_library_typed_prototype_follows_the_includes(self):
        mutate=lambda r:r['historical'][0].update(parameter_types=['BITMAP*'])
        text='/* banner */\n#include <stdio.h>\nextern int z;\n#include <allegro.h>\nint caller(void) { f(0); return 0; }\n'
        with patch('type_views.library_pointees',return_value={'BITMAP'}):
            result,new=self.run_plan(text,kind='IC',expected_return='void',actual_return='int',params=['/*???*/'],mutate=mutate)
        self.assertEqual(new,'/* banner */\n#include <stdio.h>\nextern int z;\n#include <allegro.h>\nextern void f(BITMAP*);\nint caller(void) { f(0); return 0; }\n')
        with patch('type_views.library_pointees',return_value={'BITMAP'}):
            with self.assertRaises(ValueError):self.run_plan('int caller(void) { f(0); return 0; }\n',kind='IC',expected_return='void',actual_return='int',params=['/*???*/'],mutate=mutate)

    def test_library_pointee_needs_owning_cu_layout_evidence(self):
        import typed_interface_tasks
        mutate=lambda r:r['historical'][0].update(parameter_types=['BITMAP*'])
        with patch('type_views.library_pointees',return_value={'BITMAP'}):
            result,new=self.run_plan('extern void f(void *p);\n',mutate=mutate)
            self.assertEqual(new,'extern void f(BITMAP*);\n'); self.assertEqual(result['required_generated_headers'],{})
            result,new=self.run_plan('void f(void *bmp) { draw(bmp); }\n',kind='NF',mutate=mutate)
            self.assertEqual(new,'void f(BITMAP *bmp) { draw(bmp); }\n')
        with patch('type_views.library_pointees',return_value=set()):
            with self.assertRaises(ValueError):self.run_plan('extern void f(void *p);\n',mutate=mutate)
            with self.assertRaises(ValueError):self.run_plan('void f(void *bmp) { draw(bmp); }\n',kind='NF',mutate=mutate)

    def test_void_placeholder_gets_header_and_historical_caller_type(self):
        result,text=self.run_plan()
        self.assertEqual(text,'#include "recovered/Tcontrol.h"\nextern void f(Tcontrol*);\n')
        self.assertTrue(result['typed_caller_repair']);self.assertEqual(result['difficulty'],'CHEAP')
        self.assertIn('include/recovered/Tcontrol.h',result['required_generated_headers'])

    def test_implicit_int_gets_typed_forward_prototype(self):
        result,text=self.run_plan('int caller(void) { return f(0); }\n',kind='IC',expected_return='int',actual_return='int',params=['/*???*/'])
        self.assertIn('extern int f(Tcontrol*);',text)
        self.assertTrue(text.endswith('int caller(void) { return f(0); }\n'))

    def test_existing_header_precedes_implicit_prototype(self):
        text='#include "recovered/Tcontrol.h"\nint caller(void) { return f(0); }\n'
        result,new=self.run_plan(text,kind='IC',expected_return='int',actual_return='int',params=['/*???*/'],included=True)
        self.assertTrue(new.startswith('#include "recovered/Tcontrol.h"\nextern int f(Tcontrol*);\n'))
        self.assertEqual(new.count('#include'),1)

    def test_definitions_and_return_changes_are_not_supported(self):
        # A named non-placeholder return is never reinterpreted.
        with self.assertRaises(ValueError):self.run_plan('extern int f(void *p);\n',actual_return='int')
        with self.assertRaises(ValueError):self.run_plan('extern int f(void *p);\n',expected_return='Tcontrol*',actual_return='int')

    def test_implicit_call_to_void_or_typed_return_requires_discarded_values(self):
        text='void caller(void *x) { f(x); if (x) f(x); else f(x); while (x) { f(x); } }\n'
        result,new=self.run_plan(text,kind='IC',expected_return='void',actual_return='int',params=['/*???*/'])
        self.assertTrue(new.startswith('#include "recovered/Tcontrol.h"\nextern void f(Tcontrol*);\n'))
        result,new=self.run_plan(text,kind='IC',expected_return='Tcontrol*',actual_return='int',params=['/*???*/'])
        self.assertIn('extern Tcontrol* f(Tcontrol*);',new)
        for used in ('int caller(void *x) { return f(x); }\n','void caller(void *x) { int y = f(x); }\n',
                     'void caller(void *x) { (void)f(x); }\n','void caller(void *x) { g(f(x)); }\n','void caller(void *x) { x = (void*)f(x); }\n'):
            with self.assertRaises(ValueError):self.run_plan(used,kind='IC',expected_return='void',actual_return='int',params=['/*???*/'])
        # Implicit int to a builtin non-void return is still not a typed repair.
        with self.assertRaises(ValueError):self.run_plan(text,kind='IC',expected_return='long',actual_return='int',params=['/*???*/'])

    def test_void_pointer_return_placeholder_becomes_historical_pointer(self):
        result,new=self.run_plan('extern void *f(void *p);\n',expected_return='Tcontrol*',actual_return='void*')
        self.assertEqual(new,'#include "recovered/Tcontrol.h"\nextern Tcontrol *f(Tcontrol*);\n')
        result,new=self.run_plan('extern void * f(char *name);\n',expected_return='Tcontrol*',actual_return='void*',params=['char*'],
                                 mutate=lambda r:r['historical'][0].update(parameter_types=['char*']))
        self.assertEqual(new,'#include "recovered/Tcontrol.h"\nextern Tcontrol * f(char*);\n')
        # Depth must agree and the placeholder must be spelled void.
        with self.assertRaises(ValueError):self.run_plan('extern void **f(void *p);\n',expected_return='Tcontrol*',actual_return='void**')
        with self.assertRaises(ValueError):self.run_plan('extern char *f(void *p);\n',expected_return='Tcontrol*',actual_return='char*')

    def test_multi_level_pointer_placeholders_follow_depth(self):
        result,new=self.run_plan('extern void f(void **p);\n',params=['void**'],mutate=lambda r:r['historical'][0].update(parameter_types=['Tcontrol**']))
        self.assertEqual(new,'#include "recovered/Tcontrol.h"\nextern void f(Tcontrol**);\n')
        with self.assertRaises(ValueError):self.run_plan('extern void f(void *p);\n',params=['void*'],mutate=lambda r:r['historical'][0].update(parameter_types=['Tcontrol**']))

    def test_existing_name_or_layout_conflict_requires_supervisor(self):
        with self.assertRaises(ValueError):self.run_plan(collision=True)
        with self.assertRaises(ValueError):self.run_plan(mutate=lambda r:r['type_layout_issues'][0].update(status='MISMATCH'))

    def test_other_pointer_topologies_and_nondefault_abi_are_rejected(self):
        for change in (lambda r:r['historical'][0].update(parameter_types=['Tcontrol']),
                       lambda r:r['historical'][0].update(parameter_types=['Tcontrol (*)[3]']),
                       lambda r:r['historical'][0].update(calling_convention='stdcall'),
                       lambda r:r['historical'][0].update(variadic=True),
                       lambda r:r['candidate_declarations'][0].update(file='include/shared.h')):
            with self.assertRaises(ValueError):self.run_plan(mutate=change)

    def test_nonplaceholder_scalar_pointer_is_not_reinterpreted(self):
        with self.assertRaises(ValueError):self.run_plan('extern void f(int *p);\n',params=['int*'])

    def test_named_type_with_missing_layout_is_not_bypassed(self):
        with self.assertRaises(ValueError):self.run_plan('extern void f(Tcontrol *p);\n',params=['Tcontrol*'])


if __name__=='__main__':unittest.main()
