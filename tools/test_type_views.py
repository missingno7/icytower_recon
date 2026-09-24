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

    def test_unreferenced_byte_array_signedness_is_restored_by_the_canonical_declaration(self):
        g=graph(); expected=layout(g,g.game_types['Tprofile'][0]['type_ref']); candidate=copy.deepcopy(expected)
        header=next(m for m in candidate['members'] if m['name']=='header'); header['layout']['element']=dict(header['layout']['element'],type='unsigned char',encoding='8\t(unsigned char)')
        header['layout']['type']='unsigned char [6]'
        with self.assertRaises(ValueError): compatible_members(candidate,expected,'')
        repairs=[]; retained,ignored=compatible_members(candidate,expected,'p->handle;',None,None,repairs)
        self.assertEqual([r['member'] for r in repairs],['header']); self.assertEqual(ignored,[])
        for use in ('p->header[0]','memcpy(x.header, y, 6)','header'):
            with self.assertRaises(ValueError): compatible_members(candidate,expected,use,None,None,[])
        # Different dimensions or a non-byte element are not signedness spellings.
        bad=copy.deepcopy(candidate); bad['members'][0]['layout']['dimensions']=[7]
        with self.assertRaises(ValueError): compatible_members(bad,expected,'',None,None,[])
        bad=copy.deepcopy(candidate); bad['members'][0]['layout']['element']['type']='short'; bad['members'][0]['layout']['element']['size']=2
        with self.assertRaises(ValueError): compatible_members(bad,expected,'',None,None,[])

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
        after=member_replacement(source,[repair],'\r\n',{'Trecord'})
        self.assertEqual(after,'#include "recovered/Trecord.h"\r\n'+source.replace('void *data','Trecord *data'))
        for source in ('typedef struct { int *data; } R;', 'typedef struct { void *data; void *data; } R;'):
            with self.assertRaises(ValueError):member_replacement(source,[repair],'\n',{'Trecord'})
        # Several placeholders retype in place; library pointees add no generated include.
        source='typedef struct P { void *font; int h; void *bullet; Tcontrol ctrl; void *data; } P;'
        repairs=[{'member':'font','historical_type':'FONT *'},{'member':'bullet','historical_type':'BITMAP *'},{'member':'data','historical_type':'Trecord *'}]
        after=member_replacement(source,repairs,'\n',{'Trecord'})
        self.assertEqual(after,'#include "recovered/Trecord.h"\ntypedef struct P { FONT *font; int h; BITMAP *bullet; Tcontrol ctrl; Trecord *data; } P;')
        with self.assertRaises(ValueError):member_replacement(source,repairs+[repairs[0]],'\n',{'Trecord'})

    def test_library_pointee_evidence_requires_owning_cu_and_compiled_layout_equality(self):
        from type_views import library_pointees
        from common import ROOT,read_json
        g=graph(); ledger=read_json(ROOT/'src/recovery.json'); report=read_json(ROOT/ledger['src/menu.c']['verified_report'])
        proven=library_pointees('src/menu.c',report,g)
        self.assertIn('BITMAP',proven); self.assertIn('DATAFILE',proven)
        self.assertFalse(proven&set(g.game_types))
        bad=copy.deepcopy(report)
        for t in bad['candidate_debug']['typedefs']:
            if t['name']=='BITMAP': t['layout']['members'][0]['offset']+=4
        self.assertNotIn('BITMAP',library_pointees('src/menu.c',bad,g))
        self.assertEqual(library_pointees('src/missing.c',report,g),set())
        # A compiled typedef absent from the report is not evidence even when the owning CU declares it.
        bad=copy.deepcopy(report); bad['candidate_debug']['typedefs']=[t for t in bad['candidate_debug']['typedefs'] if t['name']!='DATAFILE']
        bad.pop('interface_type_probe',None)
        self.assertNotIn('DATAFILE',library_pointees('src/menu.c',bad,g))

    def test_member_pointee_requires_complete_compiled_layout_and_exact_header_scope(self):
        from type_views import verify_member_pointees
        g=graph();expected=layout(g,g.game_types['Trecord'][0]['type_ref'])
        plan={'repair_mode':'POINTER_MEMBER_ONLY','source':'src/replay.c','pointer_member_repairs':[{'historical_type':'Trecord *'}],
              'compiled_headers':['include/recovered/Trecord.h']}
        report={'candidate_debug':{'typedefs':[{'name':'Trecord','layout':expected}]}}
        verify_member_pointees(report,plan)
        for mutation in ('absent','ambiguous','offset','signedness','header','missing_repair','unknown_library'):
            bad=copy.deepcopy(report);p=copy.deepcopy(plan)
            if mutation=='absent':bad['candidate_debug']['typedefs']=[]
            elif mutation=='ambiguous':bad['candidate_debug']['typedefs']*=2
            elif mutation=='offset':bad['candidate_debug']['typedefs'][0]['layout']['members'][1]['offset']=0
            elif mutation=='signedness':bad['candidate_debug']['typedefs'][0]['layout']['members'][0]['layout']['type']='signed char'
            elif mutation=='header':p['compiled_headers']=[]
            elif mutation=='unknown_library':p['pointer_member_repairs'].append({'historical_type':'FONT *'})
            else:p['pointer_member_repairs']=[]
            with self.assertRaises(ValueError,msg=mutation):verify_member_pointees(bad,p)
        # Library pointees verify against the owning CU's historical typedef and need no generated header.
        import type_views
        with patch.object(type_views,'library_pointees',return_value={'FONT','BITMAP'}):
            verify_member_pointees(report,dict(plan,pointer_member_repairs=[{'historical_type':'Trecord *'},{'historical_type':'FONT *'}]))
            verify_member_pointees(report,dict(plan,pointer_member_repairs=[{'historical_type':'FONT *'},{'historical_type':'BITMAP *'}],compiled_headers=[]))
            with self.assertRaises(ValueError):verify_member_pointees(report,dict(plan,pointer_member_repairs=[{'historical_type':'FONT *'}]))

    def test_scalar_layout_preserves_qualifiers(self):
        a={'kind':'base_type','size':4,'type':'int','encoding':'signed'}
        self.assertNotEqual(shape_key(a),shape_key(dict(a,qualifiers=['volatile'])))

    def fixture_plan(self,extra='',other='',roots=('Tprofile',),tag=True,included=False,child=False,candidate=None):
        import type_views
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
            (root/'include/recovered/Tprofile.h').write_text('#include "Child.h"' if child else 'header')
            if child: (root/'include/recovered/Child.h').write_text('typedef struct { int x; } Child;')
            source='src/example.c'; text='typedef struct '+('View ' if tag else '')+'{ unsigned char before_total_jumps[216]; int total_jumps; } View;\r\nint f(View *p) { return p->total_jumps; }\r\n'+extra
            (root/source).write_bytes(text.encode())
            report={'build':{'target':'game-example','local_inputs':dict([(source,{})]+([('src/other.c',{})] if included else []))},'candidate_debug':{'typedefs':[{'name':'View','layout':candidate or self.candidate()}]}}
            observations=[{'historical_type':r} for r in roots]
            with patch.object(type_views,'ROOT',root),patch.object(type_views,'affected_targets',return_value=['game-example']):
                return plan(source,report,STRUCT.search(text),observations,{},dict([(source,text),('src/other.c',other)])),text

    def test_plan_changes_only_typedef_keeps_alias_and_crlf(self):
        p,text=self.fixture_plan()
        self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
        self.assertEqual(p['changes'][0]['after'],'#include "recovered/Tprofile.h"\r\ntypedef Tprofile View;')
        self.assertNotIn('int f',p['changes'][0]['before'])
        self.assertEqual(p['canonical'],'Tprofile')

    def httpresponse_plan(self,source='src/fld_adspot.c',candidate_mutation=None,source_mutation=None):
        import type_views
        g=graph(); expected=layout(g,g.game_types['HTTPResponse'][0]['type_ref'])
        candidate=copy.deepcopy(expected)
        members={m['name']:m for m in candidate['members']}
        members['iNumHeaders']['layout']=dict(members['iNumHeaders']['layout'],type='int',encoding='5\t(signed)')
        members['pHeaders']['layout']['type']='void *'
        members['iPayloadSize']['layout']=dict(members['iPayloadSize']['layout'],type='int',encoding='5\t(signed)')
        if candidate_mutation:
            if candidate_mutation[0]=='$node':
                candidate[candidate_mutation[1]]=candidate_mutation[2]
            else:
                member=members[candidate_mutation[0]]
                member[candidate_mutation[1]]=candidate_mutation[2] if candidate_mutation[1]!='layout' else member['layout']
                if candidate_mutation[1]=='layout': member['layout']=dict(member['layout'],**candidate_mutation[2])
        declaration=('typedef struct HTTPResponse {\n'
            '    int iStatusCode;\n'
            '    int iNumHeaders;\n'
            '    void *pHeaders;\n'
            '    unsigned char *pPayload;\n'
            '    int iPayloadSize;\n'
            '} HTTPResponse;')
        if source_mutation: declaration=source_mutation(declaration)
        text='#include "recovered/FLDAdSpot.h"\n'+declaration+'\nHTTPResponse *pResponse;\n'
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
            (root/'include/recovered/HTTPResponse.h').write_text('#include "HTTPHeader.h"\ntypedef struct HTTPResponse { /* generated */ } HTTPResponse;')
            (root/'include/recovered/HTTPHeader.h').write_text('typedef struct HTTPHeader { char *pHeader; char *pValue; } HTTPHeader;')
            path=Path(source); source_file=root/path; source_file.parent.mkdir(parents=True,exist_ok=True); source_file.write_text(text)
            report={'build':{'target':'game-fld-adspot','local_inputs':{source:{}}},
                    'candidate_debug':{'typedefs':[{'name':'HTTPResponse','layout':candidate},
                        {'name':'HTTPHeader','layout':layout(g,g.game_types['HTTPHeader'][0]['type_ref'])}]}}
            with patch.object(type_views,'ROOT',root),patch.object(type_views,'affected_targets',return_value=['game-fld-adspot']):
                return plan(source,report,STRUCT.search(text),[{'historical_type':'HTTPResponse'}],{},
                    {source:text,'include/recovered/HTTPResponse.h':(root/'include/recovered/HTTPResponse.h').read_text(),
                     'include/recovered/HTTPHeader.h':(root/'include/recovered/HTTPHeader.h').read_text()})

    def test_fld_adspot_httpresponse_retypes_exact_historical_members_in_place(self):
        p=self.httpresponse_plan()
        self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
        self.assertEqual(p['repair_mode'],'INLINE_MEMBER_TYPES')
        self.assertEqual(p['compiled_headers'],['include/recovered/HTTPHeader.h'])
        self.assertEqual(p['changes'][0]['after'],
            '#include "recovered/HTTPHeader.h"\n'
            'typedef struct HTTPResponse {\n'
            '    int iStatusCode;\n'
            '    unsigned int iNumHeaders;\n'
            '    HTTPHeader *pHeaders;\n'
            '    unsigned char *pPayload;\n'
            '    unsigned int iPayloadSize;\n'
            '} HTTPResponse;')
        self.assertEqual([r['member'] for r in p['member_type_repairs']],
                         ['iNumHeaders','pHeaders','iPayloadSize'])
        from type_views import verify_httpresponse_inline_plan
        verify_httpresponse_inline_plan(p)

    def test_fld_adspot_httpresponse_inline_rule_blocks_nearby_unsafe_layouts(self):
        mutations=(
            {'candidate_mutation':('iNumHeaders','offset',8)},
            {'candidate_mutation':('$node','qualifiers',['const'])},
            {'candidate_mutation':('$node','kind','union_type')},
            {'candidate_mutation':('pHeaders','layout',{'size':8})},
            {'candidate_mutation':('pHeaders','layout',{'qualifiers':['const']})},
            {'candidate_mutation':('iPayloadSize','layout',{'type':'long unsigned int','encoding':'7\t(unsigned)'})},
            {'source_mutation':lambda s:s.replace('void *pHeaders;','int *pHeaders;')},
            {'source_mutation':lambda s:s.replace('int iNumHeaders;','unsigned int iNumHeaders;')},
            {'source_mutation':lambda s:s.replace('    int iStatusCode;\n    int iNumHeaders;','    int iNumHeaders;\n    int iStatusCode;')},
            {'source':'src/other.c'},
        )
        for options in mutations:
            p=self.httpresponse_plan(**options)
            self.assertEqual(p['difficulty'],'SUPERVISOR',p)
            self.assertEqual(p['changes'],[],p)

    def test_inline_httpresponse_acceptance_requires_exact_repair_and_header_scope(self):
        from type_views import verify_httpresponse_inline_plan
        g=graph(); expected=layout(g,g.game_types['HTTPResponse'][0]['type_ref'])
        plan={'source':'src/fld_adspot.c','alias':'HTTPResponse','expected_layout':expected,
              'member_type_repairs':[{'member':'iNumHeaders','offset':4,'size':4,'candidate_type':'int','historical_type':'unsigned int'},
                  {'member':'pHeaders','offset':8,'size':4,'candidate_type':'void *','historical_type':'HTTPHeader *'},
                  {'member':'iPayloadSize','offset':16,'size':4,'candidate_type':'int','historical_type':'unsigned int'}],
              'pointer_member_repairs':[{'member':'pHeaders','offset':8,'size':4,'candidate_type':'void *','historical_type':'HTTPHeader *',
                                         'pointee_evidence':'GENERATED_HISTORICAL_HEADER'}],
              'compiled_headers':['include/recovered/HTTPHeader.h']}
        verify_httpresponse_inline_plan(plan)
        for field,value in [('source','src/other.c'),('compiled_headers',[]),('member_type_repairs',[]),
                            ('expected_layout',self.expected())]:
            bad=copy.deepcopy(plan); bad[field]=value
            with self.assertRaises(ValueError,msg=field): verify_httpresponse_inline_plan(bad)

    def test_by_value_sizeof_and_tag_users_require_supervisor(self):
        for extra,other in [('View x;',''),('int n=sizeof(View);',''),('struct View *x;','')]:
            p,_=self.fixture_plan(extra,other)
            self.assertEqual(p['difficulty'],'SUPERVISOR',p)
            self.assertEqual(p['changes'],[])

    def test_complete_same_shape_view_permits_by_value_array_and_sizeof_uses(self):
        complete=copy.deepcopy(self.expected())
        for extra in ('View x; View arr[3]; int n=sizeof(View);','View copy(View *p) { View v; v=*p; arr2[0]=v; return v; }'):
            p,_=self.fixture_plan(extra,candidate=complete)
            self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
            self.assertEqual(p['view_completeness'],'COMPLETE_LAYOUT')
            self.assertEqual(p['changes'][0]['after'],'#include "recovered/Tprofile.h"\r\ntypedef Tprofile View;')
            self.assertEqual(p['removed_fillers'],[])
        # The same uses stay blocked for a partial view, and a struct tag user still blocks.
        p,_=self.fixture_plan('View x;')
        self.assertEqual(p['view_completeness'],'PARTIAL_LAYOUT'); self.assertEqual(p['difficulty'],'SUPERVISOR')
        p,_=self.fixture_plan('struct View *x;',candidate=complete)
        self.assertEqual(p['difficulty'],'SUPERVISOR'); self.assertEqual(p['changes'],[])

    def test_complete_size_with_renamed_or_reshaped_member_is_not_complete(self):
        renamed=copy.deepcopy(self.expected()); renamed['members'][2]['name']='other_name'
        p,_=self.fixture_plan('View x;',candidate=renamed)
        self.assertEqual(p['difficulty'],'SUPERVISOR'); self.assertEqual(p['view_completeness'],'PARTIAL_LAYOUT')
        self.assertTrue('Non-pointer or size-dependent' in p['reason'] or 'Unmapped or referenced view member' in p['reason'],p['reason'])
        reshaped=copy.deepcopy(self.expected())
        scalar=next(m for m in reshaped['members'] if m['layout']['kind']=='base_type'); scalar['layout']=dict(scalar['layout'],encoding='7\t(unsigned)',type='unsigned int')
        p,_=self.fixture_plan('View x;',candidate=reshaped)
        self.assertEqual(p['difficulty'],'SUPERVISOR'); self.assertEqual(p['changes'],[])

    def test_pointer_member_through_proven_alias_matches_canonical_pointee(self):
        import type_views,type_aliases
        from common import identity
        g=graph(); table=layout(g,g.game_types['Thisc_table'][0]['type_ref']); post=layout(g,g.game_types['Thisc'][0]['type_ref'])
        candidate=copy.deepcopy(table); posts=next(m for m in candidate['members'] if m['name']=='posts'); posts['layout']['type']='Thisc_post *'
        text='#include "recovered/Thisc.h"\ntypedef Thisc Thisc_post;\ntypedef struct { char name[32]; Thisc_post *posts; } Thisc_table;\nint f(Thisc_table *t) { return t->posts[0].value; }\n'
        for proven in (True,False):
            with tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp); (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
                (root/'include/recovered/Thisc_table.h').write_text('#include "Thisc.h"\nheader'); (root/'include/recovered/Thisc.h').write_text('canonical')
                source='src/hisc_like.c'; (root/source).write_bytes(text.encode())
                report={'build':{'target':'game-example','local_inputs':{source:{},'include/recovered/Thisc.h':identity(root/'include/recovered/Thisc.h')}},
                        'candidate_debug':{'typedefs':[{'name':'Thisc_table','alias_of':None,'layout':copy.deepcopy(candidate)},
                            {'name':'Thisc_post','alias_of':'Thisc' if proven else None,'layout':copy.deepcopy(post)},
                            {'name':'Thisc','alias_of':None,'layout':copy.deepcopy(post)}]}}
                with patch.object(type_views,'ROOT',root),patch.object(type_aliases,'ROOT',root),patch.object(type_views,'affected_targets',return_value=['game-example']):
                    p=plan(source,report,list(STRUCT.finditer(text))[0],[{'historical_type':'Thisc_table'}],{},{source:text,'include/recovered/Thisc.h':'canonical'})
            if proven:
                self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
                self.assertEqual(p['alias_normalized_members'][0]['member'],'posts')
                self.assertEqual(p['view_completeness'],'COMPLETE_LAYOUT')
                self.assertEqual(p['changes'][0]['after'],'#include "recovered/Thisc_table.h"')
            else:
                self.assertEqual(p['difficulty'],'SUPERVISOR'); self.assertIn('Member differs',p['reason']); self.assertEqual(p['alias_normalized_members'],[])

    def test_exact_token_duplicates_defer_to_canonical_type_task(self):
        import type_views
        from type_tasks import tokens
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'include/recovered').mkdir(parents=True)
            (root/'include/recovered/Tgd.h').write_text('typedef struct {\n    int start;\n    int end;\n} Tgd;\n')
            card={'canonical':'Tgd','header':'include/recovered/Tgd.h'}
            with patch.object(type_views,'ROOT',root):
                self.assertTrue(type_views.exact_duplicate_tokens(STRUCT.search('typedef struct { int start; int end; } Tgd;'),card,tokens))
                self.assertFalse(type_views.exact_duplicate_tokens(STRUCT.search('typedef struct { int start, end; } Tgd;'),card,tokens))
                self.assertFalse(type_views.exact_duplicate_tokens(STRUCT.search('typedef struct { int start; int end; } Tgd;'),{'canonical':'Tgd'},tokens))

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

    def test_forward_declared_dependency_blocks_without_waiting_state(self):
        for extra in ('typedef struct Child Child;','typedef void Child;'):
            p,_=self.fixture_plan(extra=extra,child=True)
            self.assertEqual(p['difficulty'],'SUPERVISOR',p.get('reason'))
            self.assertNotEqual(p['state'],'WAITING_FOR_CANONICAL_DEPENDENCY')
            self.assertIn('forward-declared',p['reason']); self.assertEqual(p['changes'],[])
            self.assertEqual(p['forward_declared_dependencies'][0]['type'],'Child')
        p,_=self.fixture_plan(extra='struct Child *unrelated_pointer;',child=True)
        self.assertEqual(p['difficulty'],'CHEAP',p.get('reason')); self.assertEqual(p['forward_declared_dependencies'],[])

    def test_forward_declaration_repair_requires_historical_cu_definition(self):
        import type_views
        with patch.object(type_views,'historical_cu_defines',return_value=True):
            p,text=self.fixture_plan(extra='typedef struct Child Child;\r\nChild *child_pointer;',child=True)
            self.assertEqual(p['difficulty'],'CHEAP',p.get('reason'))
            self.assertEqual(len(p['changes']),2)
            self.assertEqual(p['changes'][1]['before'],'typedef struct Child Child;')
            self.assertEqual(p['changes'][1]['after'],'#include "recovered/Child.h"')
            self.assertEqual(p['compiled_headers'],['include/recovered/Tprofile.h','include/recovered/Child.h'])
            self.assertEqual(p['forward_declaration_repairs'][0]['type'],'Child')
            # Two forward declarations of the same name are ambiguous.
            p,_=self.fixture_plan(extra='typedef struct Child Child;\r\ntypedef struct Child Child;',child=True)
            self.assertEqual(p['difficulty'],'SUPERVISOR'); self.assertIn('more than once',p['reason'])
        with patch.object(type_views,'historical_cu_defines',return_value=False):
            p,_=self.fixture_plan(extra='typedef struct Child Child;',child=True)
            self.assertEqual(p['difficulty'],'SUPERVISOR'); self.assertIn('lacks its complete layout',p['reason']); self.assertEqual(p['changes'],[])

    def test_historical_cu_definition_evidence_uses_owning_cu_dwarf(self):
        from type_views import historical_cu_defines
        g=graph()
        self.assertTrue(historical_cu_defines('src/game_data.c','Treplay',g))
        self.assertTrue(historical_cu_defines('src/replay.c','Treplay',g))
        self.assertFalse(historical_cu_defines('src/control.c','Treplay',g))
        self.assertFalse(historical_cu_defines('src/game_data.c','NoSuchType',g))
        self.assertFalse(historical_cu_defines('src/missing.c','Treplay',g))

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

    def test_global_object_layout_proposes_view_only_with_unique_typedef(self):
        from type_views import global_evidence
        from common import ROOT,read_json
        g=graph(); ledger=read_json(ROOT/'src/recovery.json'); report=read_json(ROOT/ledger['src/main.c']['verified_report'])
        unit=next(u for u in read_json(ROOT/'src/units.json') if u['source']=='src/main.c')
        rows=global_evidence(report,unit,g)
        menu=[o for o in rows.get('Tmenu_params',[]) if o['variable']=='menu_params']
        self.assertEqual(len(menu),1); self.assertEqual(menu[0]['historical_type'],'Tmenu_params')
        # Duplicate names, missing historical objects and ambiguous typedef layouts propose nothing.
        bad=copy.deepcopy(report); bad['candidate_debug']['globals']=[r for r in bad['candidate_debug']['globals'] if r['name']=='menu_params']*2
        self.assertNotIn('Tmenu_params',global_evidence(bad,unit,g))
        self.assertNotIn('Tmenu_params',global_evidence(report,{'globals':[]},g))
        bad=copy.deepcopy(report); bad['candidate_debug']['typedefs'].append(copy.deepcopy(next(t for t in bad['candidate_debug']['typedefs'] if t['name']=='Tmenu_params'))); bad['candidate_debug']['typedefs'][-1]['name']='Other'
        self.assertNotIn('Tmenu_params',global_evidence(bad,unit,g))

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
