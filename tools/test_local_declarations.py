"""Compiler-located local declaration scope, routing and strict acceptance controls."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import ROOT,read_json
from type_graph import graph
from local_declarations import declaration_span,storage_shape,plan,verify_local,emission_effect


class LocalTests(unittest.TestCase):
    def candidate(self,name='n',type='int',line=3):
        return {'name':name,'type':type,'declaration_line':line,'declaration_file':'src/a.c','role':'DW_TAG_variable',
                'function_scope':True,'byte_size':4,'address':None}

    def test_span_excludes_initializer_register_and_other_source(self):
        text='void f(void)\r\n{\r\n    register int n = other(1, 2);\r\n    return;\r\n}\r\n'
        a,b=declaration_span(text,'f',self.candidate())
        self.assertEqual(text[a:b],'int n')
        self.assertEqual(text[:a]+'const int n'+text[b:],text.replace('int n','const int n'))

    def test_pointer_and_explicit_array_declarators(self):
        for decl,type in [('char *p','char *'),('char p[128]','char [128]')]:
            text='void f(void)\n{\n    '+decl+';\n}\n'
            a,b=declaration_span(text,'f',self.candidate('p',type))
            self.assertEqual(text[a:b],decl)

    def test_multi_declarator_macro_wrong_line_or_type_is_refused(self):
        for declaration in ('int n, other;','int n=0, other=0;','DECLARE(int,n);','long n;'):
            with self.assertRaises(ValueError): declaration_span('void f(void)\n{\n    '+declaration+'\n}\n','f',self.candidate())
        with self.assertRaises(ValueError): declaration_span('int n;\nvoid f(void)\n{\n}\n','f',self.candidate(line=1))

    def test_inferred_literal_array_is_not_padded(self):
        text='void f(void)\n{\n    char n[]="abc";\n}\n'
        with self.assertRaisesRegex(ValueError,'initializer content'): declaration_span(text,'f',self.candidate(type='char [4]'))

    def fixture(self,folder):
        root=Path(folder); (root/'src').mkdir()
        text='void main_menu_callback(void)\n{\n    int scroller_step = -1;\n}\n'
        (root/'src/a.c').write_text(text)
        g=graph(); unit=next(u for u in read_json(ROOT/'src/units.json') if u['source']=='src/main.c')
        f=next(f for f in unit['functions'] if f['name']=='main_menu_callback')
        old=next(v for v in g.descendants(f['die']) if v.get('name')=='scroller_step' and v['tag']=='DW_TAG_variable')
        row={'name':f['name'],'status':'DIFFER','workflow':{'body_edit_allowed':True},'first_difference':{'offset':1}}
        return root,g.variable(old),old,row

    def test_unique_builtin_const_local_is_a_generated_task(self):
        import local_declarations
        with tempfile.TemporaryDirectory() as tmp:
            root,old,die,row=self.fixture(tmp)
            with patch.object(local_declarations,'ROOT',root),patch.object(local_declarations,'affected_targets',return_value=['game-a']):
                card=plan('src/a.c',{'build':{'target':'game-a'}},row,old,self.candidate('scroller_step'),die,{})
            self.assertEqual(card['difficulty'],'CHEAP',card.get('reason'))
            self.assertEqual(card['changes'][0]['after'],'const int scroller_step')
            self.assertEqual(card['changes'][0]['before'],'int scroller_step')

    def test_protected_body_parameter_header_and_nested_local_are_not_eligible(self):
        import local_declarations
        for failure in ('protected','parameter','header','nested','width','volatile'):
            with tempfile.TemporaryDirectory() as tmp:
                root,old,die,row=self.fixture(tmp); candidate=self.candidate('scroller_step')
                if failure=='protected': row['workflow']['body_edit_allowed']=False
                elif failure=='parameter': candidate['role']='DW_TAG_formal_parameter'
                elif failure=='header': candidate['declaration_file']='include/a.h'
                elif failure=='nested': candidate['function_scope']=False
                elif failure=='width': candidate['byte_size']=8
                elif failure=='volatile': old['type']='volatile int'
                with patch.object(local_declarations,'ROOT',root),patch.object(local_declarations,'affected_targets',return_value=['game-a']):
                    card=plan('src/a.c',{'build':{'target':'game-a'}},row,old,candidate,die,{})
                self.assertEqual(card['difficulty'],'SUPERVISOR',failure)
                self.assertEqual(card['changes'],[],failure)

    def test_fresh_type_role_and_source_are_required(self):
        import local_declarations
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); p={'target_function':'f','variable':'n','source':'src/a.c','original':{'type':'const int'}}
            candidate=self.candidate(type='const int'); report={'candidate_debug':{'functions':{'f':{'variables':[candidate]}}}}
            with patch.object(local_declarations,'ROOT',root):
                verify_local(report,p)
                candidate['type']='int'
                with self.assertRaises(ValueError): verify_local(report,p)
                candidate['type']='const int'; candidate['declaration_file']='header.h'
                with self.assertRaises(ValueError): verify_local(report,p)

    def fingerprint(self,text='old',data='data'):
        return {'sections':[('.text',0,4,0,text),('.data',0,4,0,data)],'relocations':[],'defined':[],'common':[]}

    def test_neutral_emission_does_not_claim_function_match(self):
        before={}; after={}; p={'target_function':'f'}
        with patch('local_declarations.contribution_fingerprint',return_value=self.fingerprint()):
            self.assertEqual(emission_effect(before,after,p),'EMISSION_PRESERVED')

    def test_changed_code_requires_strict_exact_oracle_and_preserved_data(self):
        p={'target_function':'f'}; row={'name':'f','status':'DIFFER','first_difference':{'offset':3}}
        before={}; after={'functions':[row]}
        with patch('local_declarations.contribution_fingerprint',side_effect=[self.fingerprint(),self.fingerprint('new')]):
            with self.assertRaisesRegex(ValueError,'target remains DIFFER'): emission_effect(before,after,p)
        row.update(status='FUNCTION_MATCH',workflow={'state':'FUNCTION_MATCH'})
        with patch('local_declarations.contribution_fingerprint',side_effect=[self.fingerprint(),self.fingerprint('new')]),patch('promote_function.eligible',side_effect=ValueError('bad byte proof')):
            with self.assertRaisesRegex(ValueError,'bad byte proof'): emission_effect(before,after,p)
        with patch('local_declarations.contribution_fingerprint',side_effect=[self.fingerprint(),self.fingerprint('new','changed')]),patch('promote_function.eligible') as strict:
            with self.assertRaisesRegex(ValueError,'non-code'): emission_effect(before,after,p)
            strict.assert_called_once()
        with patch('local_declarations.contribution_fingerprint',side_effect=[self.fingerprint(),self.fingerprint('new')]),patch('promote_function.eligible') as strict:
            self.assertEqual(emission_effect(before,after,p),'EXACT_FUNCTION'); strict.assert_called_once()


if __name__=='__main__': unittest.main()
