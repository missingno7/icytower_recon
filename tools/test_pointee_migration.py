import unittest
from types import SimpleNamespace
from unittest.mock import patch
from pointee_migration import plan


class PointeeMigrationTests(unittest.TestCase):
    def run_plan(self,text):
        scalar={'kind':'base_type','type':'int','size':4}
        def struct(name,field):return {'kind':'structure_type','type':name,'size':4,'members':[{'name':field,'offset':0,'bitfield':False,'layout':scalar}]}
        def parent(pointee):return {'kind':'structure_type','size':4,'members':[{'name':'data','offset':0,'bitfield':False,'layout':{'kind':'pointer_type','type':pointee+' *','size':4}}]}
        report={'candidate_debug':{'functions':{'f':{'variables':[{'name':'r','type':'Parent *','function_scope':True}]}}}}
        types=[{'name':'View','layout':struct('View','old')},{'name':'Parent','layout':parent('View')}]
        graph=SimpleNamespace(game_types={'Parent':[{'type_ref':'parent'}],'Record':[{'type_ref':'record'}]})
        with patch('pointee_migration.graph',return_value=graph),patch('pointee_migration.layout',side_effect=lambda g,r:parent('Record') if r=='parent' else struct('Record','new')),patch('pointee_migration.interface_typedefs',return_value=types):return plan(report,text,'Parent','data')
    def source(self):return 'typedef struct { int old; } View; typedef struct { View *data; } Parent; int f(Parent *r){return r->data[0].old + sizeof(View);}'
    def test_only_typed_access_and_declarations_change(self):
        text,recipe=self.run_plan(self.source())
        self.assertIn('r->data[0].new',text);self.assertIn('typedef Record View;',text)
        self.assertIn('Record *data;',text);self.assertIn('sizeof(View)',text)
        self.assertEqual(len(recipe['changes']),3)
    def test_unknown_root_and_other_alias_uses_rejected(self):
        with self.assertRaisesRegex(ValueError,'compiled parent'):self.run_plan(self.source().replace('r->','other->'))
        with self.assertRaisesRegex(ValueError,'outside supported'):self.run_plan(self.source()+' View other;')
    def test_unsupported_member_expression_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unsupported renamed'):self.run_plan(self.source().replace('r->data[0].old','r->data[0+1].old'))


if __name__=='__main__':unittest.main()
