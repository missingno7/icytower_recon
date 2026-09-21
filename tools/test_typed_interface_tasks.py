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
        with self.assertRaises(ValueError):self.run_plan('void f(void *p) {}\n',kind='NF')
        with self.assertRaises(ValueError):self.run_plan(kind='IC',actual_return='int')

    def test_existing_name_or_layout_conflict_requires_supervisor(self):
        with self.assertRaises(ValueError):self.run_plan(collision=True)
        with self.assertRaises(ValueError):self.run_plan(mutate=lambda r:r['type_layout_issues'][0].update(status='MISMATCH'))

    def test_other_pointer_topologies_and_nondefault_abi_are_rejected(self):
        for change in (lambda r:r['historical'][0].update(parameter_types=['Tcontrol**']),
                       lambda r:r['historical'][0].update(calling_convention='stdcall'),
                       lambda r:r['historical'][0].update(variadic=True),
                       lambda r:r['candidate_declarations'][0].update(file='include/shared.h')):
            with self.assertRaises(ValueError):self.run_plan(mutate=change)

    def test_nonplaceholder_scalar_pointer_is_not_reinterpreted(self):
        with self.assertRaises(ValueError):self.run_plan('extern void f(int *p);\n',params=['int*'])

    def test_named_type_with_missing_layout_is_not_bypassed(self):
        with self.assertRaises(ValueError):self.run_plan('extern void f(Tcontrol *p);\n',params=['Tcontrol*'])


if __name__=='__main__':unittest.main()
