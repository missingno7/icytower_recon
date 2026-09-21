import tempfile
from pathlib import Path
import unittest
from common import identity
from rtl_evidence import normalize,compare_passes,pass_identity


class RTLTests(unittest.TestCase):
    def test_normalization_keeps_semantic_and_allocator_details(self):
        a='x.c:12 <var_decl 0x123 abc> (reg:SI 59) [89 object] (const_int 0x123)'
        b='y.c:12 <var_decl 0x456 abc> (reg:SI 59) [89 object] (const_int 0x123)'
        self.assertEqual(normalize(a,'x.c'),normalize(b,'y.c'))
        for old,new in [('59','60'),('89','90'),(':12',':13'),('const_int 0x123','const_int 0x456')]:
            self.assertNotEqual(normalize(a,'x.c'),normalize(b.replace(old,new),'y.c'))

    def test_repeated_phases_keep_numbered_order_and_missing_passes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            def record(prefix,passes):
                result={'source':prefix+'.c','focused_rtl_passes':[]}
                for number,phase,body in passes:
                    p=root/(prefix+'.'+str(number)+'r.'+phase);p.write_text(body)
                    result['focused_rtl_passes'].append({'number':number,'phase':phase,'path':p.name,'identity':identity(p)})
                return result
            a=record('a',[(186,'dce','later'),(158,'dce','early'),(140,'jump','only-a')])
            b=record('b',[(186,'dce','changed later'),(158,'dce','changed early')])
            result=compare_passes(a,b,root)
            self.assertEqual([p['number'] for p in result['first_changed_passes']],[158,186])
            self.assertEqual(result['missing_passes'],[{'number':140,'phase':'jump','absent_from':'variant'}])
            b['focused_rtl_passes'].append(b['focused_rtl_passes'][0])
            with self.assertRaisesRegex(ValueError,'Duplicate'):compare_passes(a,b,root)
            b['focused_rtl_passes'].pop()
            (root/b['focused_rtl_passes'][0]['path']).write_text('tampered')
            with self.assertRaisesRegex(ValueError,'changed'):compare_passes(a,b,root)

    def test_empty_trace_is_not_equal_and_unknown_names_fail(self):
        self.assertEqual(compare_passes({}, {},Path('.'))['state'],'NUMBERED_TRACE_UNAVAILABLE')
        self.assertEqual(pass_identity('probe.c.156r.init-regs'),(156,'init-regs'))
        with self.assertRaises(ValueError):pass_identity('unversioned.dce')


if __name__=='__main__':unittest.main()
