import copy,unittest
from reconsider_type import require_preservation


class ReconsiderTests(unittest.TestCase):
    def test_requires_complete_unique_raw_preserving_baseline_and_candidate(self):
        good={'target':'cu','task':'type','outcome':'COMPLETE','variants':[{'variant':name,'raw_baseline_equal':True} for name in ('baseline','canonical')]}
        require_preservation(good,'cu','type')
        for case in ('failed','missing','duplicate','changed','wrong_target'):
            bad=copy.deepcopy(good)
            if case=='failed':bad['outcome']='COMPILE_FAILED'
            elif case=='missing':bad['variants'].pop()
            elif case=='duplicate':bad['variants'].append(bad['variants'][0])
            elif case=='changed':bad['variants'][1]['raw_baseline_equal']=False
            else:bad['target']='other'
            with self.assertRaises(ValueError):require_preservation(bad,'cu','type')


if __name__=='__main__':unittest.main()
