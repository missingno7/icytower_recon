import copy,unittest
from unittest.mock import patch
from static_scope_tasks import edits,verify_scope
from interface_tasks import patch_text


class ScopeTests(unittest.TestCase):
    def test_move_preserves_declaration_and_expressions(self):
        text='static char buf[8];\nint f(void) { return buf[0]; }\n'
        changes,_=edits(text,'f',{'name':'buf'},{'declaration_line':1},{'functions':{}})
        new=patch_text(text,changes)
        self.assertEqual(new,'int f(void) {\n    static char buf[8]; return buf[0]; }\n')

    def test_external_use_is_rejected(self):
        text='static char buf[8];\nint f(void) { return buf[0]; }\nint g(void) { return buf[1]; }\n'
        with self.assertRaisesRegex(ValueError,'outside target'): edits(text,'f',{'name':'buf'},{'declaration_line':1},{'functions':{}})

    def test_later_locals_are_not_mistaken_for_global_uses(self):
        text='static char buf[8];\nint f(void) { return buf[0]; }\nint g(void) {\n int buf = 2;\n return buf;\n}\n'
        debug={'functions':{'g':{'variables':[{'name':'buf','type':'int','function_scope':True,'address':None,'declaration_line':4}]}}}
        changes,shadows=edits(text,'f',{'name':'buf'},{'declaration_line':1},debug)
        self.assertEqual(shadows,['g']); self.assertEqual(len(changes),2)
        for replacement in [' int buf = buf;',' return buf; int buf = 2;']:
            with self.assertRaisesRegex(ValueError,'outside target'):
                edits(text.replace(' int buf = 2;',replacement),'f',{'name':'buf'},{'declaration_line':1},debug)

    def test_lexical_shadow_does_not_cover_uses_after_its_block(self):
        text='static int buf;\nint f(void) { return buf; }\nint g(void) {\n if (1) {\n int buf = 2;\n return buf;\n }\n return 0;\n}\n'
        debug={'functions':{'g':{'variables':[{'name':'buf','type':'int','function_scope':False,'address':None,'declaration_line':5}]}}}
        changes,shadows=edits(text,'f',{'name':'buf'},{'declaration_line':1},debug)
        self.assertEqual(shadows,['g'])
        with self.assertRaisesRegex(ValueError,'outside target'):
            edits(text.replace('return 0','return buf'),'f',{'name':'buf'},{'declaration_line':1},debug)

    def test_initializer_or_multiple_declarator_refused(self):
        for declaration in ['static int buf=3;','static int buf, other;','int buf;']:
            with self.assertRaisesRegex(ValueError,'simple uninitialized'):
                edits(declaration+'\nint f(void) { return buf; }','f',{'name':'buf'},{'declaration_line':1},{'functions':{}})

    def test_layout_failure_records_concrete_symbol_offsets(self):
        with patch('static_scope_tasks.contribution_fingerprint',side_effect=[{'defined':[('_face','.bss',1072,3)]},{'defined':[('_face','.bss',1068,3)]}]):
            with self.assertRaisesRegex(ValueError,r'_face.*1072.*_face.*1068|_face.*1068.*_face.*1072'):
                verify_scope({}, {}, {})

    def test_acceptance_requires_owner_and_raw_code(self):
        before={'object_sections':[{'name':'.text','sha256':'same'}],'object_ownership':{'accepted':[]}}
        after=copy.deepcopy(before); plan={'original_die':1,'object':'buf','target_function':'f'}
        with patch('static_scope_tasks.contribution_fingerprint',return_value={}):
            with self.assertRaisesRegex(ValueError,'ownership proof'): verify_scope(before,after,plan)
            after['object_ownership']['accepted']=[{'original_die':1,'name':'buf','scope':('FUNCTION_STATIC','f'),'original_va':100,'size':8}]
            verify_scope(before,after,plan)
            after['object_sections'][0]['sha256']='changed'
            with self.assertRaisesRegex(ValueError,'raw machine text'): verify_scope(before,after,plan)


if __name__=='__main__': unittest.main()
