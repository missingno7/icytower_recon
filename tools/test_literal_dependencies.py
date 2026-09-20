import copy
import unittest
from literal_dependencies import groups,for_function,publish_function,pattern_prerequisites
from pathlib import Path


def fixture():
    def row(name,addend,original,equal=False,diagnostic=True):
        r={'name':name,'body_shape_equal':True,'instruction_boundaries_verified':True,'relocations':[{'type':6,'symbol':'.rdata','addend':addend,'function_offset':1,'original_value':original,'target_va':99,'equal':equal,'resolution':'independent evidence'}]}
        if diagnostic: r['literal_diagnostics']=[{'function_offset':1,'kind':'C_STRING','candidate_hex':'','historical_operand_va':original,'classification':'CONTENT_EQUAL_OWNER_UNPROVEN','candidate_source_lines':[]}]
        return r
    report={'object_sections':[{'name':'.rdata','index':3}], 'build':{'target':'game-example','config':{'source':'src/example.c'}},
            'functions':[row('target',4,100),row('peer',4,100,True,False),row('other_pool',8,200)]}
    return report


class LiteralDependencyTests(unittest.TestCase):
    def test_groups_by_candidate_section_addend_not_equal_payload(self):
        report=fixture(); before=copy.deepcopy(report); result=groups(report)
        self.assertEqual(len(result),2)
        self.assertEqual(result[0]['consumer_functions'],['peer','target'])
        self.assertEqual(result[0]['candidate_payloads'],[{'kind':'C_STRING','hex':'','bytes':1}])
        self.assertEqual(result[0]['placement_confidence'],'UNPROVEN')
        self.assertEqual(report,before)
        summary=for_function(result,'target')[0]
        self.assertEqual(summary['peer_functions'],['peer'])
        self.assertEqual(summary['historical_address_count'],1)
        self.assertFalse(for_function(result,'peer'))

    def test_conflicting_historical_addresses_are_observations_not_bindings(self):
        report=fixture(); report['functions'][1]['relocations'][0]['original_value']=101
        result=groups(report)[0]
        self.assertTrue(result['multiple_historical_addresses'])
        self.assertEqual(result['historical_observed_addresses'],[100,101])
        self.assertEqual(result['placement_confidence'],'UNPROVEN')
        self.assertNotIn('binding',result)

    def test_ambiguous_sections_unsupported_fields_and_no_payload_fail_closed(self):
        report=fixture(); report['object_sections']*=2; self.assertFalse(groups(report))
        for change in ('type','symbol','untyped'):
            report=fixture()
            for row in report['functions']:
                if change=='type': row['relocations'][0]['type']=20
                elif change=='symbol': row['relocations'][0]['symbol']='named_string'
                else: row['literal_diagnostics']=[]
            self.assertFalse(groups(report),change)

    def test_unaligned_peer_bytes_are_not_historical_addresses(self):
        report=fixture(); peer=report['functions'][1]
        peer['body_shape_equal']=False; peer['relocations'][0]['original_value']=0xdeadbeef
        group=groups(report)[0]
        self.assertEqual(group['historical_observed_addresses'],[100])
        row=next(r for r in group['consumers'] if r['function']=='peer')
        self.assertIsNone(row['historical_operand_va'])
        self.assertEqual(row['unaligned_original_field_value'],0xdeadbeef)
        self.assertEqual(row['historical_operand_alignment'],'UNPROVEN')
        self.assertEqual(for_function([group],'target')[0]['unaligned_reference_count'],1)

    def test_fast_cards_are_published_separately_from_canonical_state(self):
        emitted=[]; report=fixture()
        report['build']['local_inputs']={'src/example.c':{'sha256':'source-identity'}}
        summaries=publish_function(report,'target',Path('root'),'build/fast/target/literals',lambda p,d:emitted.append((p,d)))
        self.assertEqual(len(emitted),1)
        self.assertEqual(summaries[0]['candidate_card'],'build/fast/target/literals/4.json')
        self.assertEqual(emitted[0][1]['source_identity'],{'sha256':'source-identity'})
        self.assertEqual(emitted[0][0],Path('root/build/fast/target/literals/4.json'))
        self.assertTrue(groups(report)[0]['candidate_card'].startswith('docs/current/'))

    def test_generated_literal_repair_does_not_hide_unproved_owner(self):
        row={'relocations':[{'function_offset':1,'symbol':'.rdata','equal':False},{'function_offset':9,'symbol':'.rdata','equal':False}],
             'literal_diagnostics':[{'function_offset':1,'classification':'LITERAL_CONTENT_DIFFERENCE','kind':'C_STRING'},
                                    {'function_offset':9,'classification':'CONTENT_EQUAL_OWNER_UNPROVEN'}]}
        patterns=[{'id':'repair_literal_content'}]
        pending=pattern_prerequisites(row,patterns)
        self.assertEqual([p['function_offset'] for p in pending],[9])
        self.assertEqual(pending[0]['reason'],'CONTENT_EQUAL_OWNER_UNPROVEN')
        row['relocations'][1]['equal']=True
        self.assertFalse(pattern_prerequisites(row,patterns))
        self.assertFalse(pattern_prerequisites(row,[]))

    def test_summary_bounds_peer_context_and_never_grants_body_edits(self):
        report=fixture()
        for i in range(12):
            row=copy.deepcopy(report['functions'][1]);row['name']='peer'+str(i);report['functions'].append(row)
        summary=for_function(groups(report),'target')[0]
        self.assertEqual(summary['peer_function_count'],13)
        self.assertEqual(len(summary['peer_functions']),6)
        self.assertNotIn('body_edit_allowed',summary)
        self.assertNotIn('resolved_value',summary)


if __name__=='__main__': unittest.main()
