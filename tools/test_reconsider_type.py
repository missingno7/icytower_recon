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

    def test_candidate_variant_may_satisfy_the_projection_preservation_predicate(self):
        good={'target':'cu','task':'type','outcome':'COMPLETE','variants':[
            {'variant':'baseline','raw_baseline_equal':True},
            {'variant':'canonical','raw_baseline_equal':False,'contribution_diagnostics':{'preservation_fingerprint_equal':True}}]}
        require_preservation(good,'cu','type')
        bad=copy.deepcopy(good); bad['variants'][1]['contribution_diagnostics']['preservation_fingerprint_equal']=False
        with self.assertRaises(ValueError):require_preservation(bad,'cu','type')
        # An interface recipe may reopen when the declaration emission policy accepts the canonical variant.
        ok=copy.deepcopy(good); ok['variants'][1]['contribution_diagnostics']['preservation_fingerprint_equal']=False; ok['variants'][1]['interface_emission']={'effect':'HISTORICAL_DECLARATION_EMISSION_CHANGED','functions':[]}
        require_preservation(ok,'cu','type')
        ok['variants'][1]['interface_emission']={'effect':'REJECTED','error':'away'}
        with self.assertRaises(ValueError):require_preservation(ok,'cu','type')
        # The overlay baseline itself must reproduce raw contributions; a projected match is not enough there.
        bad=copy.deepcopy(good); bad['variants'][0]['raw_baseline_equal']=False; bad['variants'][0]['contribution_diagnostics']={'preservation_fingerprint_equal':True}
        with self.assertRaises(ValueError):require_preservation(bad,'cu','type')


if __name__=='__main__':unittest.main()
