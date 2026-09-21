import copy
import json
import unittest
from interface_type_probe import FLAG, fingerprint, report_fingerprint, validate, interface_typedefs


def fixture():
    build={'target':'test','compiler':'tdm-2','config':{'flags':['-fno-toplevel-reorder']},'flags':['-O2','-fno-toplevel-reorder'],
           'local_inputs':{'src/example.c':{'sha256':'source'}},'toolchain_lock':'locked','candidate_toolchain_lock':'candidate',
           'inputs_verified_around_compile':True,'object':'primary'}
    report={'build':build,'object_sections':[{'index':1,'name':'.text','virtual_size':0,'raw_size':4,'characteristics':1,'sha256':'code'},
                                            {'index':2,'name':'.debug_info','virtual_size':0,'raw_size':4,'characteristics':2,'sha256':'debug'}],
            'object_symbols':[{'index':0,'name':'object','section':0,'value':4,'type':0,'storage_class':2}],
            'object_relocations':[{'section':1,'offset':0,'type':6,'symbol_index':0}],
            'candidate_debug':{'typedefs':[{'name':'Existing','layout':{'size':4}}]}}
    pb=copy.deepcopy(build);pb['flags']=['-O2',FLAG,'-fno-toplevel-reorder'];pb['object']='probe'
    report['interface_type_probe']={'build':pb,'object':'probe','fingerprint':report_fingerprint(report),
                                   'typedefs':[{'name':'Unused','layout':{'size':12}},{'name':'Existing','layout':{'size':99}}]}
    return report


class InterfaceTypeProbeTests(unittest.TestCase):
    def test_compiled_local_aliases_are_requested_without_inventing_correspondence(self):
        from interface_type_probe import requested_types
        report=fixture()
        report['interfaces_aux']='\n'.join([
            '/* src/map.c:12:NC */ extern LocalReplay *get_demo (void);',
            '/* include/control.h:4:NC */ extern int poll (const LocalControl *);',
            '/* third_party/sdk.h:8:NC */ extern ExternalType *external (void);'])
        self.assertEqual(requested_types(report,{'Treplay','Existing','Unrelated'}, {'Treplay','Existing'}),
                         {'Treplay','LocalReplay','LocalControl'})

    def test_member_pointee_names_follow_pointer_members_only(self):
        from interface_type_probe import member_pointee_names
        from type_graph import graph
        g=graph()
        names=member_pointee_names(g,{'Tmenu_params'})
        self.assertTrue({'FONT','BITMAP','DATAFILE'}<=names,names)
        self.assertNotIn('Tcontrol',names)  # by-value member, not a pointee
        self.assertEqual(member_pointee_names(g,{'Tcontrol'}),set())
        self.assertEqual(member_pointee_names(g,{'NoSuchType'}),set())

    def test_interface_pointee_names_follow_historical_pointer_parameters_and_returns(self):
        from interface_type_probe import interface_pointee_names
        from type_graph import graph
        g=graph()
        names=interface_pointee_names(g,{'blit_to_screen','load_options','get_controls'})
        self.assertTrue({'BITMAP','PACKFILE','Toptions','Tcontrol'}<=names,names)
        self.assertEqual(interface_pointee_names(g,{'no_such_function'}),set())

    def test_existing_ambiguous_typedefs_are_not_replaced_by_probe(self):
        from interface_type_probe import requested_types
        report=fixture()
        report['candidate_debug']['typedefs'].append({'name':'Existing','layout':{'size':99}})
        report['interfaces_aux']='/* src/example.c:1:NC */ extern Existing *f (void);'
        self.assertEqual(requested_types(report,{'Existing'},{'Existing'}),set())

    def test_json_receipt_roundtrip(self):
        validate(json.loads(json.dumps(fixture())))

    def test_adds_missing_only_and_keeps_provenance(self):
        report=fixture();before=copy.deepcopy(report);rows=interface_typedefs(report)
        self.assertEqual([(t['name'],t['layout']['size']) for t in rows],[('Existing',4),('Unused',12)])
        self.assertEqual(rows[1]['evidence_source'],'EMISSION_PRESERVING_DEBUG_PROBE')
        self.assertEqual(report,before)

    def test_no_probe_preserves_legacy_missing_evidence(self):
        report=fixture();del report['interface_type_probe']
        self.assertEqual(len(interface_typedefs(report)),1)

    def test_rejects_changed_inputs_flags_object_and_race_checks(self):
        for key,value in [('target','other'),('compiler','other'),('config',{}),('local_inputs',{}),
                          ('flags',['-O3',FLAG]),('toolchain_lock','other'),('candidate_toolchain_lock','other'),
                          ('object','wrong'),('inputs_verified_around_compile',False)]:
            report=fixture();report['interface_type_probe']['build'][key]=value
            with self.assertRaises(ValueError,msg=key): validate(report)

    def test_byte_symbol_and_relocation_changes_are_rejected(self):
        for change in ('code','common','target','type'):
            report=fixture()
            if change=='code':report['object_sections'][0]['sha256']='different'
            elif change=='common':report['object_symbols'][0]['value']=8
            elif change=='target':report['object_symbols'][0]['name']='different'
            else:report['object_relocations'][0]['type']=20
            with self.assertRaises(ValueError,msg=change): interface_typedefs(report)

    def test_debug_only_changes_do_not_change_fingerprint(self):
        report=fixture();report['object_sections'][1]['sha256']='more-debug';report['object_sections'][1]['raw_size']=100
        validate(report)

    def test_ambiguous_supplemental_types_remain_ambiguous(self):
        report=fixture();report['interface_type_probe']['typedefs'].append({'name':'Unused','layout':{'size':8}})
        rows=interface_typedefs(report)
        self.assertEqual(sum(t['name']=='Unused' for t in rows),2)

    def test_raw_section_fingerprint_has_no_instruction_projection(self):
        report=fixture();before=report_fingerprint(report)
        report['candidate_zero_clear_projection']={'sha256':'code'}
        report['object_sections'][0]['sha256']='reordered-code'
        self.assertNotEqual(before,report_fingerprint(report))


if __name__=='__main__': unittest.main()
