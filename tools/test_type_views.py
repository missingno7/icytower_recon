"""Negative controls for DWARF-driven partial type migrations."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import ROOT,read_json
from dwarf_layout import layout
from type_graph import graph
from type_views import STRUCT,shape_key,compatible_members,plan,evidence,verify_view


class ViewTests(unittest.TestCase):
    def expected(self):
        g=graph(); return layout(g,g.game_types['Tprofile'][0]['type_ref'])

    def candidate(self):
        node=copy.deepcopy(self.expected()); node['size']=220
        node['members']=[{'name':'before_total_jumps','offset':0,'bitfield':False,'layout':{'kind':'array_type','size':216,'type':'unsigned char [216]','dimensions':[216],'element':{'kind':'base_type','size':1,'type':'unsigned char','encoding':'8\t(unsigned char)'}}},next(m for m in node['members'] if m['name']=='total_jumps')]
        return node

    def test_partial_field_is_proven_at_original_offset(self):
        retained,ignored=compatible_members(self.candidate(),self.expected(),'return p->total_jumps;')
        self.assertEqual((retained[0]['offset'],retained[0]['size']),(216,4))
        self.assertEqual(ignored[0]['size'],216)

    def test_accessed_filler_is_never_discarded(self):
        for source in ('return p->before_total_jumps[1];','offsetof(View, before_total_jumps)'):
            with self.assertRaises(ValueError): compatible_members(self.candidate(),self.expected(),source)

    def test_another_view_filler_declaration_is_not_a_field_access(self):
        compatible_members(self.candidate(),self.expected(),'typedef struct { char before_total_jumps[20]; } Other;')
        with self.assertRaises(ValueError):
            compatible_members(self.candidate(),self.expected(),'typedef struct { char x[sizeof(p->before_total_jumps)]; } Other;')

    def test_renamed_or_wrong_signedness_offset_and_qualifier_is_not_merged(self):
        for field,value in (('name','guessed_total'),('offset',212),('type','unsigned int'),('qualifiers',['const'])):
            node=self.candidate(); member=node['members'][1]
            if field in ('name','offset'): member[field]=value
            else: member['layout'][field]=value
            with self.assertRaises(ValueError): compatible_members(node,self.expected(),'')

    def test_overlaps_bitfields_and_unknown_sizes_are_blocked(self):
        for mutation in ('overlap','bitfield','unknown'):
            node=self.candidate()
            if mutation=='overlap': node['members'][1]['offset']=0
            elif mutation=='bitfield': node['members'][1]['bitfield']=True
            else: node['members'][1]['layout']['size']=None
            with self.assertRaises(ValueError): compatible_members(node,self.expected(),'')

    def test_void_pointer_member_repair_is_explicit_and_extent_preserving(self):
        g=graph();expected=layout(g,g.game_types['Treplay'][0]['type_ref']);candidate=copy.deepcopy(expected)
        candidate['members'][-1]['layout']['type']='void *'
        with self.assertRaises(ValueError): compatible_members(candidate,expected,'')
        repairs=[];compatible_members(candidate,expected,'',{'Trecord'},repairs)
        self.assertEqual(repairs[0]['member'],'data')
        self.assertEqual(repairs[0]['historical_type'],'Trecord *')
        self.assertEqual(repairs[0]['offset'],2216)
        for mutation in ('offset','size','qualifier','typed','nested','unknown'):
            bad=copy.deepcopy(candidate);member=bad['members'][-1];pointees={'Trecord'}
            if mutation=='offset':member['offset']-=4
            elif mutation=='size':member['layout']['size']=8
            elif mutation=='qualifier':member['layout']['qualifiers']=['volatile']
            elif mutation=='typed':member['layout']['type']='int *'
            elif mutation=='nested':member['layout']['type']='void **'
            else:pointees=set()
            with self.assertRaises(ValueError,msg=mutation): compatible_members(bad,expected,'',pointees,[])

    def test_member_only_replacement_keeps_tag_and_other_source_bytes(self):
        from type_views import member_replacement
        source='typedef struct Replay { int n; /* keep */ void *data; } Replay;'
        repair={'member':'data','historical_type':'Trecord *'}
        after=member_replacement(source,repair,'\r\n')
        self.assertEqual(after,'#include "recovered/Trecord.h"\r\n'+source.replace('void *data','Trecord *data'))
        for source in ('typedef struct { int *data; } R;', 'typedef struct { void *data; void *data; } R;'):
            with self.assertRaises(ValueError):member_replacement(source,repair,'\n')

    def test_member_pointee_requires_complete_compiled_layout_and_exact_header_scope(self):
        from type_views import verify_member_pointees
        g=graph();expected=layout(g,g.game_types['Trecord'][0]['type_ref'])
        plan={'repair_mode':'POINTER_MEMBER_ONLY','pointer_member_repairs':[{'historical_type':'Trecord *'}],
              'compiled_headers':['include/recovered/Trecord.h']}
        report={'candidate_debug':{'typedefs':[{'name':'Trecord','layout':expected}]}}
        verify_member_pointees(report,plan)
        for mutation in ('absent','ambiguous','offset','signedness','header','missing_repair'):
            bad=copy.deepcopy(report);p=copy.deepcopy(plan)
            if mutation=='absent':bad['candidate_debug']['typedefs']=[]
            elif mutation=='ambiguous':bad['candidate_debug']['typedefs']*=2
            elif mutation=='offset':bad['candidate_debug']['typedefs'][0]['layout']['members'][1]['offset']=0
            elif mutation=='signedness':bad['candidate_debug']['typedefs'][0]['layout']['members'][0]['layout']['type']='signed char'
            elif mutation=='header':p['compiled_headers']=[]
            else:p['pointer_member_repairs']=[]
            with self.assertRaises(ValueError,msg=mutation):verify_member_pointees(bad,p)

    def test_scalar_layout_preserves_qualifiers(self):
        a={'kind':'base_type','size':4,'type':'int','encoding':'signed'}
        self.assertNotEqual(shape_key(a),shape_key(dict(a,qualifiers=['volatile'])))

    def fixture_plan(self,extra='',other='',roots=('Tprofile',),tag=True,included=False,child=False):
        import type_views
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
            (root/'include/recovered/Tprofile.h').write_text('#include "Child.h"' if child else 'header')
            if child: (root/'include/recovered/Child.h').write_text('typedef struct { int x; } Child;')
            source='src/example.c'; text='typedef struct '+('View ' if tag else '')+'{ unsigned char before_total_jumps[216]; int total_jumps; } View;\r\nint f(View *p) { return p->total_jumps; }\r\n'+extra
            (root/source).write_bytes(text.encode())
            report={'build':{'target':'game-example','local_inputs':dict([(source,{})]+([('src/other.c',{})] if included else []))},'candidate_debug':{'typedefs':[{'name':'View','layout':self.candidate()}]}}
            observations=[{'historical_type':r} for r in roots]
            with patch.object(type_views,'ROOT',root),patch.object(type_views,'affected_targets',return_value=['game-example']):
                return plan(source,report,STRUCT.search(text),observations,{},dict([(source,text),('src/other.c',other)])),text

    def test_plan_changes_only_typedef_keeps_alias_and_crlf(self):
        p,text=self.fixture_plan()
        self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
        self.assertEqual(p['changes'][0]['after'],'#include "recovered/Tprofile.h"\r\ntypedef Tprofile View;')
        self.assertNotIn('int f',p['changes'][0]['before'])
        self.assertEqual(p['canonical'],'Tprofile')

    def test_by_value_sizeof_and_tag_users_require_supervisor(self):
        for extra,other in [('View x;',''),('int n=sizeof(View);',''),('struct View *x;','')]:
            p,_=self.fixture_plan(extra,other)
            self.assertEqual(p['difficulty'],'SUPERVISOR',p)
            self.assertEqual(p['changes'],[])

    def test_other_cu_spelling_is_not_external_type_identity(self):
        p,_=self.fixture_plan(other='typedef struct { int unrelated; } View; View *other;')
        self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
        self.assertEqual(p['type_scope']['basis'],'GCC_DEPFILE')

    def test_included_source_uses_still_require_supervisor(self):
        p,_=self.fixture_plan(other='View *other;',included=True)
        self.assertEqual(p['difficulty'],'SUPERVISOR')
        self.assertIn('another compiled input',p['reason'])
        self.assertEqual(p['changes'],[])

    def test_generated_parent_waits_for_local_child_declaration(self):
        p,_=self.fixture_plan(extra='typedef struct { int x; } Child;',child=True)
        self.assertEqual(p['difficulty'],'SUPERVISOR')
        self.assertEqual(p['state'],'WAITING_FOR_CANONICAL_DEPENDENCY')
        self.assertEqual(p['canonical_dependencies'][0]['type'],'Child')
        self.assertEqual(p['changes'],[])
        p,_=self.fixture_plan(other='typedef struct { int x; } Child;',child=True)
        self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))

    def test_conflicting_historical_correspondence_is_blocked(self):
        p,_=self.fixture_plan(roots=('Tprofile','Tcontrol'))
        self.assertEqual(p['difficulty'],'SUPERVISOR')
        self.assertIn('conflicting',p['reason'])

    def test_return_only_view_uses_explicit_compiled_declaration(self):
        from type_views import return_evidence
        g=graph(); units=read_json(ROOT/'src/units.json')
        report={'interfaces_aux':'/* src/map.c:10:NC */ extern ReplayView *get_demo (void);'}
        rows=return_evidence(report,units,g)
        self.assertEqual(rows['ReplayView'][0]['historical_type'],'Treplay')
        self.assertEqual(rows['ReplayView'][0]['position'],'return')
        report['candidate_debug']={'functions':{}}
        self.assertEqual(evidence(report,{'functions':[]})['ReplayView'],rows['ReplayView'])
        for declaration in (
            '/* third_party/x.h:1:NC */ extern ReplayView *get_demo (void);',
            '/* src/map.c:1:IC */ extern ReplayView *get_demo (void);',
            '/* src/map.c:1:NC */ extern ReplayView **get_demo (void);',
            '/* src/map.c:1:NC */ extern ReplayView *unknown_function (void);'):
            self.assertFalse(return_evidence({'interfaces_aux':declaration},units,g))
        main=next(u for u in units if u['source']=='src/main.c')
        self.assertFalse(return_evidence(report,[*units,main],g))

    def test_original_function_variable_correspondence_is_required(self):
        unit=next(u for u in read_json(ROOT/'src/units.json') if u['source']=='src/profile.c')
        report={'candidate_debug':{'functions':{'profile_data_page_extra':{'variables':[{'name':'p','type':'View *','die':1}]}}}}
        self.assertEqual(evidence(report,unit)['View'][0]['historical_type'],'Tprofile')
        report['candidate_debug']['functions']['profile_data_page_extra']['variables'].append({'name':'p','type':'View *','die':2})
        self.assertNotIn('View',evidence(report,unit))

    def test_full_layout_and_included_generated_header_required_at_acceptance(self):
        import type_views
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); header=root/'canonical.h'; header.write_text('expected')
            p={'alias':'View','expected_layout':self.expected(),'header':'canonical.h'}
            report={'candidate_debug':{'typedefs':[{'name':'View','layout':self.candidate()}]},'build':{'local_inputs':{'canonical.h':{}}}}
            with patch.object(type_views,'ROOT',root),patch('generate_types.outputs',return_value={header:'expected'}):
                with self.assertRaises(ValueError): verify_view(report,p)
                report['candidate_debug']['typedefs'][0]['layout']=self.expected(); verify_view(report,p)
                report['build']['local_inputs']={}
                with self.assertRaises(ValueError): verify_view(report,p)


class AliasTests(unittest.TestCase):
    def fixture(self,root):
        from common import identity
        g=graph(); expected=layout(g,g.game_types['Tprofile'][0]['type_ref'])
        header=root/'include/recovered/Tprofile.h'; header.parent.mkdir(parents=True); header.write_text('canonical')
        return {'build':{'local_inputs':{'include/recovered/Tprofile.h':identity(header)}},'candidate_debug':{'typedefs':[
            {'name':'View','alias_of':'Tprofile','layout':copy.deepcopy(expected)},
            {'name':'Tprofile','alias_of':None,'layout':copy.deepcopy(expected)}]}}

    def test_explicit_alias_to_compiled_canonical_type_normalizes(self):
        import type_aliases
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); report=self.fixture(root)
            with patch.object(type_aliases,'ROOT',root): self.assertEqual(type_aliases.canonical_aliases(report),{'View':'Tprofile'})
        self.assertEqual(type_aliases.canonical_type('const View*',{'View':'Tprofile'}),'const Tprofile*')
        self.assertEqual(type_aliases.canonical_type('struct View*',{'View':'Tprofile'}),'struct View*')
        self.assertEqual(type_aliases.canonical_type('void (*)(View*)',{'View':'Tprofile'}),'void (*)(View*)')
        self.assertEqual(type_aliases.canonical_type('struct { int View; }',{'View':'Tprofile'}),'struct { int View; }')

    def test_same_shape_without_alias_or_dependency_never_normalizes(self):
        import type_aliases
        for failure in ('no alias','missing header','changed header','wrong member','duplicate','cycle'):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); report=self.fixture(root); rows=report['candidate_debug']['typedefs']
                if failure=='no alias': rows[0]['alias_of']=None
                elif failure=='missing header': report['build']['local_inputs']={}
                elif failure=='changed header': (root/'include/recovered/Tprofile.h').write_text('changed')
                elif failure=='wrong member': rows[0]['layout']['members'][0]['name']='other'
                elif failure=='duplicate': rows.append(copy.deepcopy(rows[1]))
                elif failure=='cycle': rows[0]['alias_of']='View'
                with patch.object(type_aliases,'ROOT',root): self.assertEqual(type_aliases.canonical_aliases(report),{},failure)


class InterfaceLayoutTests(unittest.TestCase):
    def test_same_name_does_not_hide_unsigned_profile_header(self):
        from type_aliases import layout_checks
        g=graph(); node=layout(g,g.game_types['Tprofile'][0]['type_ref'])
        declaration={'return_type':'Tprofile*','parameter_types':['char*','int']}
        report={'candidate_debug':{'typedefs':[{'name':'Tprofile','layout':node}]}}
        self.assertEqual(layout_checks(declaration,declaration,report)[0]['status'],'AGREE')
        node['members'][0]['layout']['element']['type']='unsigned char'
        node['members'][0]['layout']['type']='unsigned char [6]'
        result=layout_checks(declaration,declaration,report)[0]
        self.assertEqual(result['status'],'MISMATCH')
        self.assertEqual(result['first_member_differences'][0]['member'],'header')

    def test_missing_layout_is_unavailable_not_a_proven_conflict(self):
        from type_aliases import layout_checks
        declaration={'return_type':'Tprofile*','parameter_types':[]}
        result=layout_checks(declaration,declaration,{'candidate_debug':{'typedefs':[]}})[0]
        self.assertEqual(result['status'],'UNAVAILABLE')

    def test_field_conflict_blocks_signature_only_repair(self):
        from interface_tasks import plan_interface
        row={'function':'f','historical':[{'cu':'src/a.c','return_type':'Tprofile*','parameter_types':[],'variadic':False}],
             'candidate_declarations':[],'type_layout_issues':[{'status':'MISMATCH','historical_type':'Tprofile'}]}
        card=plan_interface(row,{})
        self.assertEqual(card['difficulty'],'SUPERVISOR'); self.assertEqual(card['changes'],[])
        self.assertEqual(card['type_layout_issues'],row['type_layout_issues'])


if __name__=='__main__': unittest.main()
