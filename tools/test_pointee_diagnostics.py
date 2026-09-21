import copy
import unittest
from pointee_diagnostics import correspondence,pointer_names


class PointeeDiagnosticsTests(unittest.TestCase):
    def member(self,name,offset,spelling='int',size=4):
        return {'name':name,'offset':offset,'bitfield':False,'layout':{'kind':'base_type','type':spelling,'size':size,'encoding':'signed' if spelling=='int' else 'unsigned'}}
    def test_renames_do_not_hide_extra_fields_or_grant_identity(self):
        old={'kind':'structure_type','size':8,'members':[self.member('key_flags',0,'unsigned char',1),self.member('cycle_count',4)]}
        new=copy.deepcopy(old);new['members'][0]['name']='type';new['members'][1]['name']='value'
        new['members'].append(self.member('reserved',1,'char',3))
        r=correspondence(new,old)
        self.assertEqual(r['state'],'FIELD_CORRESPONDENCE_ONLY')
        self.assertEqual([m['state'] for m in r['members']],['RENAMED_FIELD_SHAPE']*2)
        self.assertEqual(r['unmatched_candidate_members'][0]['member'],'reserved')
    def test_signedness_and_overlap_are_not_correspondence(self):
        old={'kind':'structure_type','size':4,'members':[self.member('value',0)]}
        new=copy.deepcopy(old);new['members'][0]['layout']['type']='unsigned int'
        self.assertEqual(correspondence(new,old)['members'][0]['state'],'NO_UNIQUE_CORRESPONDENCE')
        new['members'].append(self.member('other',0))
        self.assertEqual(correspondence(new,old)['state'],'UNPROVEN')
    def test_only_simple_unqualified_pointers_are_followed(self):
        p=lambda t:{'kind':'pointer_type','size':4,'type':t}
        self.assertEqual(pointer_names(p('A *'),p('B *')),('A','B'))
        self.assertIsNone(pointer_names(p('A **'),p('B *')))
        self.assertIsNone(pointer_names(p('const A *'),p('B *')))


if __name__=='__main__':unittest.main()
