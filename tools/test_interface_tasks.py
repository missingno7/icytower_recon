"""Negative controls for mechanical interface tasks, scope and contribution preservation."""
import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import ROOT,read_json
from interface_tasks import plan_interface,patch_text,contribution_fingerprint
from source_scope import function_span
from instructions import zero_clear_projection


class InterfaceTests(unittest.TestCase):
    def plan(self,text,expected,actual,kind='NF',line=1,cu=False):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'src').mkdir(); (root/'src/a.c').write_bytes(text.encode('cp1252'))
            row={'function':'f','historical':[{'cu':'src/a.c','return_type':expected[0],'parameter_types':expected[1],'variadic':False,'calling_convention':None}],
                 'candidate_declarations':[{'file':'src/a.c','line':line,'kind':kind,'name':'f','return_type':actual[0],'parameter_types':actual[1],**({'cu':'src/a.c'} if cu else {})}]}
            with patch('interface_tasks.ROOT',root),patch('interface_tasks.affected_targets',return_value=['game-a']):
                return plan_interface(row,{})

    def test_failure_context_is_bound_to_plan_and_durable_diagnostic_identity(self):
        import interface_task
        import json
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);detail=root/'build/difference.json';detail.parent.mkdir()
            session={'function':'repair','plan':{'changes':[{'before':'old','after':'new'}]}}
            with patch.object(interface_task,'ROOT',root):
                detail.write_text(json.dumps({'changed_functions':[{'function':'caller','source_body_unchanged':True}]}))
                archived=interface_task.archive_diagnostic(detail,'repair','game-a')
                interface_task.history(session,'BEGIN',{})
                interface_task.history(session,'FAST_FAILED',{'error':'changed emission','evidence':[archived]})
                context=interface_task.failure_context(session)
                self.assertEqual(context['evidence'][0]['changed_functions'][0]['function'],'caller')
                (root/archived).write_text('{}')
                self.assertEqual(interface_task.failure_context(session)['evidence'],[])
                self.assertIsNone(interface_task.failure_context(dict(session,plan={'different':True})))
                interface_task.history(session,'BEGIN',{})
                self.assertIsNone(interface_task.failure_context(session))

    def test_focused_diagnostic_survives_build_cleanup_without_overwrite(self):
        import interface_task
        import shutil
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);detail=root/'build/difference.json';detail.parent.mkdir()
            with patch.object(interface_task,'ROOT',root):
                detail.write_bytes(b'{"first_difference": 17}\n')
                first=interface_task.archive_diagnostic(detail,'repair','game-a')
                self.assertEqual(first,interface_task.archive_diagnostic(detail,'repair','game-a'))
                detail.write_bytes(b'{"first_difference": 23}\n')
                second=interface_task.archive_diagnostic(detail,'repair','game-a')
            shutil.rmtree(root/'build')
            self.assertNotEqual(first,second)
            self.assertEqual((root/first).read_bytes(),b'{"first_difference": 17}\n')
            self.assertEqual((root/second).read_bytes(),b'{"first_difference": 23}\n')

    def test_implicit_prototype_with_incompatible_call_arity_is_not_cheap(self):
        card=self.plan('void caller(){ f(1,2); }',('int',['int']),('int',['/*???*/']),kind='IC')
        self.assertEqual(card['difficulty'],'SUPERVISOR')
        self.assertEqual(card['state'],'CALLSITE_REPAIR_REQUIRED')
        self.assertEqual(card['callsite_arity_conflicts'][0]['caller'],'caller')
        self.assertEqual(card['callsite_arity_conflicts'][0]['observed_argument_groups'],2)

    def test_const_parameter_changes_only_declaration(self):
        text='int f(char *s) { return *s; }\r\n'
        plan=self.plan(text,('int',['const char*']),('int',['char*']))
        self.assertEqual(plan['difficulty'],'CHEAP')
        new=patch_text(text,plan['changes'])
        self.assertEqual(new,'int f(const char *s) { return *s; }\r\n')
        a,b=function_span(text,'f'); c,d=function_span(new,'f')
        self.assertEqual(text[a:b],new[c:d])

    def test_multiline_declaration_retains_line_count(self):
        text='int f(char *s,\r\n int n) { return n; }\r\n'
        plan=self.plan(text,('int',['const char*','int']),('int',['char*','int']))
        new=patch_text(text,plan['changes'])
        self.assertEqual(new.count('\n'),text.count('\n'))

    def test_const_return(self):
        text='char *f(char *s) { return s; }\n'
        plan=self.plan(text,('const char*',['const char*']),('char*',['char*']))
        self.assertEqual(patch_text(text,plan['changes']),'const char *f(const char *s) { return s; }\n')

    def test_caller_builtin_return_restored_only_when_results_are_discarded(self):
        text='extern void f(int *p);\nvoid caller(int *p) { f(p); if (p) f(p); }\n'
        plan=self.plan(text,('int',['int*']),('void',['int*']),'NC',cu=True)
        self.assertEqual(plan['difficulty'],'CHEAP',plan.get('reason'))
        self.assertEqual(patch_text(text,plan['changes']),'extern int f(int *p);\nvoid caller(int *p) { f(p); if (p) f(p); }\n')
        used='extern void f(int *p);\nint caller(int *p) { return f(p); }\n'
        self.assertEqual(self.plan(used,('int',['int*']),('void',['int*']),'NC',cu=True)['difficulty'],'SUPERVISOR')
        # Definitions, pointer returns and non-CU-local declarations stay with the supervisor.
        self.assertEqual(self.plan('void f(int *p) { }\n',('int',['int*']),('void',['int*']),'NF',cu=True)['difficulty'],'SUPERVISOR')
        self.assertEqual(self.plan('extern void *f(int *p);\n',('int',['int*']),('void*',['int*']),'NC',cu=True)['difficulty'],'SUPERVISOR')
        self.assertEqual(self.plan(text,('int',['int*']),('void',['int*']),'NC')['difficulty'],'SUPERVISOR')

    def test_void_prototype(self):
        plan=self.plan('int f();\n',('int',[]),('int',['/*???*/']),'OC')
        self.assertEqual(patch_text('int f();\n',plan['changes']),'int f(void);\n')

    def test_implicit_builtin_gets_prototype(self):
        text='void caller(void) { f(); }\n'
        plan=self.plan(text,('void',[]),('int',['/*???*/']),'IC')
        self.assertEqual(plan['difficulty'],'CHEAP')
        self.assertEqual(patch_text(text,plan['changes']),'extern void f(void);\n'+text)

    def test_implicit_custom_type_requires_supervisor(self):
        plan=self.plan('void caller(void) { f(0); }\n',('void',['Tcontrol*']),('int',['/*???*/']),'IC')
        self.assertEqual(plan['difficulty'],'SUPERVISOR')

    def test_signedness_and_arity_changes_not_guessed(self):
        for wanted in (['const unsigned char*'],['const char*','int']):
            plan=self.plan('int f(char *s) { return *s; }\n',('int',wanted),('int',['char*']))
            self.assertEqual(plan['difficulty'],'SUPERVISOR')

    def test_stale_location_and_replacement_rejected(self):
        plan=self.plan('int f(char *s) { return *s; }\n',('int',['const char*']),('int',['char*']),line=42)
        self.assertEqual(plan['difficulty'],'SUPERVISOR')
        with self.assertRaises(ValueError): patch_text('abc',[{'start':0,'end':1,'before':'x','after':'y'}])

    def test_semantic_contributions_include_all_layout_dimensions(self):
        report=read_json(ROOT/'docs/current/reports/game-timer.json')
        base=contribution_fingerprint(report)
        for field in ('sha256','raw_size'):
            changed=copy.deepcopy(report)
            section=next(s for s in changed['object_sections'] if s['name']=='.text')
            section[field]='different' if field=='sha256' else section[field]+4
            if field=='sha256' and 'candidate_zero_clear_projection' in changed:
                changed['candidate_zero_clear_projection']['sha256']='different'
            self.assertNotEqual(base,contribution_fingerprint(changed))
        changed=copy.deepcopy(report); changed['common_allocations'][0]['value']+=4
        self.assertNotEqual(base,contribution_fingerprint(changed))
        changed=copy.deepcopy(report)
        debug=next(s for s in changed['object_sections'] if s['name'].startswith('.debug'))
        debug['sha256']='debug may change'; debug['raw_size']+=1
        self.assertEqual(base,contribution_fingerprint(changed))

    def test_independent_register_clear_projection(self):
        def project(codes,**kwargs):
            raw=b''.join(bytes.fromhex(c) for c in codes); rows=[]; off=0
            for code in codes:
                rows.append({'address':off,'bytes':code,'mnemonic':'xor','assembly':'xor registers'})
                off+=len(bytes.fromhex(code))
            return zero_clear_projection(raw,rows,**kwargs)
        base=project(['31f6','31db'])
        self.assertEqual(base['sha256'],project(['31db','31f6'])['sha256'])
        for other in (['31ff','31db'],['31f6','90','31db'],['31f6','31f6']):
            self.assertNotEqual(base['sha256'],project(other)['sha256'])
        for kwargs in ({'protected_targets':[2]},{'forbidden_ranges':[(0,4)]}):
            self.assertNotEqual(project(['31f6','31db'],**kwargs)['sha256'],project(['31db','31f6'],**kwargs)['sha256'])
        for reg in ('31e4','31ed'):
            self.assertNotEqual(project(['31f6',reg])['sha256'],project([reg,'31f6'])['sha256'])

    def test_independent_immediate_write_projection(self):
        def project(codes,**kwargs):
            raw=b''.join(bytes.fromhex(c) for c in codes); rows=[]; off=0
            for code in codes:
                rows.append({'address':off,'bytes':code,'mnemonic':'mov','assembly':'mov immediate'}); off+=len(bytes.fromhex(code))
            return zero_clear_projection(raw,rows,**kwargs)
        ebx='bbf4010000'; slot128='c785d8feffffe8030000'; slot130='c785d0feffff00000000'; slot138='c785c8feffff00000000'
        # The real select_profile permutation: one constant store moved ahead of a register load and other stores.
        self.assertEqual(project([ebx,slot128,slot130,slot138])['sha256'],project([slot138,ebx,slot128,slot130])['sha256'])
        # Same destination twice, overlapping slots, ESP/EBP destinations and mixed widths on one slot are never canonicalized.
        for a,b in ((['bb01000000','bb02000000'],['bb02000000','bb01000000']),
                    ([slot128,'c785dafeffff00000000'],['c785dafeffff00000000',slot128]),
                    (['bc01000000',ebx],[ebx,'bc01000000']),(['bd01000000',ebx],[ebx,'bd01000000']),
                    (['c645f000',slot128.replace('d8feffff','f0ffffff')],[slot128.replace('d8feffff','f0ffffff'),'c645f000'])):
            self.assertNotEqual(project(a)['sha256'],project(b)['sha256'],(a,b))
        # A register clear may join the run; a non-immediate store, a call or a flag reader may not.
        self.assertEqual(project(['31db',slot128])['sha256'],project([slot128,'31db'])['sha256'])
        for other in ('8985ccfeffff','e800000000','7402'):
            rows=[ebx,other,slot128]; swapped=[slot128,other,ebx]
            self.assertNotEqual(project(rows)['sha256'],project(swapped)['sha256'])
        # Entry targets and relocation fields inside the run block it.
        self.assertNotEqual(project([ebx,slot128],protected_targets=[5])['sha256'],project([slot128,ebx],protected_targets=[5])['sha256'])
        self.assertNotEqual(project([ebx,slot128],forbidden_ranges=[(0,5)])['sha256'],project([slot128,ebx],forbidden_ranges=[(0,5)])['sha256'])
        # Byte and word stores to disjoint slots canonicalize; disp8 and disp32 forms both decode.
        self.assertEqual(project(['c645f000','66c745f20100'])['sha256'],project(['66c745f20100','c645f000'])['sha256'])
        self.assertEqual(project(['c745f000000000',slot128])['sha256'],project([slot128,'c745f000000000'])['sha256'])

    def test_indirect_jump_exclusion_distinguishes_tables_from_registers(self):
        import re,inspect,experiment
        source=inspect.getsource(experiment.compare)
        pattern=re.search(r"re\.search\(r'(.*?)',i\['assembly'\]\)",source)[1]
        for table in ('jmp    *0xe8(,%eax,4)','jmp    *(,%edx,4)'):
            self.assertTrue(re.search(pattern,table),table)
        for register in ('jmp    *%eax','jmp    *0x10(%eax)','call   *%edx'):
            self.assertFalse(re.search(pattern,register),register)

    def test_operand_swapped_compare_jump_pairs_canonicalize_only_when_flags_die(self):
        def project(codes,mnems,**kwargs):
            raw=b''.join(bytes.fromhex(c) for c in codes); rows=[]; off=0
            for code,m in zip(codes,mnems):
                rows.append({'address':off,'bytes':code,'mnemonic':m,'assembly':m}); off+=len(bytes.fromhex(code))
            return zero_clear_projection(raw,rows,**kwargs)
        tail=['8d0476','c1e003']; tm=['lea','shl']  # jcc rel 3 lands on the shl boundary
        a=project(['39f0','7e03']+tail,['cmp','jle']+tm); b=project(['39c6','7d03']+tail,['cmp','jge']+tm)
        self.assertEqual(a['sha256'],b['sha256']); self.assertEqual(b['blocks'][0]['kind'],'compare_operand_order'); self.assertEqual(a['blocks'],[])
        # 3b c6 (eax - esi) equals 39 f0 (eax - esi) without any condition change.
        self.assertEqual(project(['3bc6','7e03']+tail,['cmp','jle']+tm)['sha256'],a['sha256'])
        # Memory forms: cmp %esi,mem ; jle  versus  cmp mem,%esi ; jge
        m1=project(['393500000000','0f8e03000000']+tail,['cmp','jle']+tm); m2=project(['3b3500000000','0f8d03000000']+tail,['cmp','jge']+tm)
        self.assertEqual(m1['sha256'],m2['sha256'])
        # A relocation field inside the displacement stays untouched and does not block the pair.
        r1=project(['393500000000','0f8e03000000']+tail,['cmp','jle']+tm,protected_targets=range(2,6)); r2=project(['3b3500000000','0f8d03000000']+tail,['cmp','jge']+tm,protected_targets=range(2,6))
        self.assertEqual(r1['sha256'],r2['sha256'])
        # A flag reader after the jump, at the target, a sign/overflow condition, or an entry target inside blocks it.
        for codes,mnems in ((['39f0','7e03','0f94c0','90'],['cmp','jle','sete','nop']),
                            (['39f0','7803']+tail,['cmp','js']+tm),
                            (['39f0','7e02','7c00','90'],['cmp','jle','jl','nop'])):
            x=project(codes,mnems); y=project([codes[0][:2]+('c6' if codes[0][2:]=='f0' else 'f0')]+[('7d' if codes[1][:2]=='7e' else '79' if codes[1][:2]=='78' else codes[1][:2])+codes[1][2:]]+codes[2:],mnems)
            self.assertNotEqual(x['sha256'],y['sha256'],(codes,mnems))
        self.assertNotEqual(project(['39f0','7e03']+tail,['cmp','jle']+tm,protected_targets=[2])['sha256'],project(['39c6','7d03']+tail,['cmp','jge']+tm,protected_targets=[2])['sha256'])
        # A loop head jumping to the compare itself does not block the pair.
        self.assertEqual(project(['39f0','7e03']+tail,['cmp','jle']+tm,protected_targets=[0])['sha256'],project(['39c6','7d03']+tail,['cmp','jge']+tm,protected_targets=[0])['sha256'])

    def test_projection_respects_decoding_and_cfg(self):
        raw=bytes.fromhex('31f631dbebfc')
        rows=[{'address':0,'bytes':'31f6','mnemonic':'xor','assembly':'xor %esi,%esi'},
              {'address':2,'bytes':'31db','mnemonic':'xor','assembly':'xor %ebx,%ebx'},
              {'address':4,'bytes':'ebfc','mnemonic':'jmp','assembly':'jmp 2 <entry>'}]
        self.assertFalse(zero_clear_projection(raw,rows)['blocks'])
        self.assertFalse(zero_clear_projection(bytes.fromhex('b831f631db'),[
            {'address':0,'bytes':'b831f631db','mnemonic':'mov','assembly':'mov $0xdb31f631,%eax'}])['blocks'])

    def test_relocation_target_changes_rejected(self):
        report=read_json(ROOT/'docs/current/reports/game-timer.json'); changed=copy.deepcopy(report)
        relocation=next(r for r in changed['object_relocations'] if r['section']==1)
        symbol=next(s for s in changed['object_symbols'] if s['index']==relocation['symbol_index'])
        symbol['name']='_wrong_target'
        self.assertNotEqual(contribution_fingerprint(report),contribution_fingerprint(changed))

    def test_only_exact_interface_patch_is_allowed(self):
        import interface_task
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'src').mkdir(); (root/'src/a.c').write_text('int f(const char *s) { return 99; }')
            old='int f(char *s) { return *s; }'
            plan=self.plan(old,('int',['const char*']),('int',['char*']))
            session={'files':{'src/a.c':{}},'sources':{'src/a.c':old},'plan':plan,'ledger':{}}
            with patch.object(interface_task,'ROOT',root),patch.object(interface_task,'snapshot_files',return_value={'src/a.c':{}}):
                with self.assertRaisesRegex(ValueError,'exceeds'): interface_task.validate_interface_scope(session,applied=True)

    def test_canonical_type_requires_exact_members_and_no_tag_users(self):
        import type_tasks
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
            (root/'include/recovered/Titem.h').write_text('typedef struct { int a; unsigned char b; } Titem;')
            source=root/'src/a.c'
            source.write_text('typedef struct Titem { int a; unsigned char b; } Titem;')
            with patch.object(type_tasks,'ROOT',root),patch.object(type_tasks,'affected_targets',return_value=['game-a']):
                card=type_tasks.plans({})[0]
                self.assertEqual(card['difficulty'],'CHEAP')
                self.assertEqual(patch_text(source.read_text(),card['changes']),'#include "recovered/Titem.h"')
                source.write_text('typedef struct Titem { int a; unsigned char b; } Titem; struct Titem *p;')
                self.assertEqual(type_tasks.plans({})[0]['difficulty'],'SUPERVISOR')
                for body in ('int a; signed char b;','unsigned char b; int a;'):
                    source.write_text('typedef struct Titem { '+body+' } Titem;')
                    self.assertEqual(type_tasks.plans({}),[])

    def test_source_order_uses_dwarf_lines_and_preserves_bodies(self):
        import source_order
        from types import SimpleNamespace
        from source_scope import body_hash
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'src').mkdir(); (root/'report.json').write_text('{"build":{"target":"game-a"}}')
            text='#include "x.h"\nint b(void) { return 2; }\nint a(void) { return 1; }\n'
            (root/'src/a.c').write_bytes(text.encode('cp1252'))
            unit={'source':'src/a.c','cu_die':1}
            graph=SimpleNamespace(dies={1:{'tag':'DW_TAG_subprogram','cu':1,'name':'a','decl_file_path':'original/a.c','resolved':{'DW_AT_decl_line':'10'}},
                                       2:{'tag':'DW_TAG_subprogram','cu':1,'name':'b','decl_file_path':'original/a.c','resolved':{'DW_AT_decl_line':'20'}}})
            with patch.object(source_order,'ROOT',root),patch.object(source_order,'graph',return_value=graph):
                plan=source_order.plan_order(unit,{'src/a.c':{'verified_report':'report.json'}})
                self.assertEqual(plan['difficulty'],'CHEAP')
                new=patch_text(text,plan['changes'])
                self.assertLess(new.index('int a('),new.index('int b('))
                for name in ('a','b'): self.assertEqual(body_hash(text,name),body_hash(new,name))
                (root/'src/a.c').write_text(text.replace('\nint a','\nint global;\nint a'))
                self.assertEqual(source_order.plan_order(unit,{'src/a.c':{'verified_report':'report.json'}})['difficulty'],'SUPERVISOR')

    def test_definition_span_ignores_strings_comments_and_calls(self):
        from source_order import definition_spans
        text='/* fake(void) { } */\nint f(void) { puts("g(void) { }"); return 1; }\nint g(void) { return f(); }'
        self.assertEqual([s['name'] for s in definition_spans(text)],['f','g'])

    def test_array_extent_repair_preserves_initializer_and_rejects_ambiguity(self):
        import array_tasks
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); (root/'src').mkdir(); source=root/'src/a.c'
            owner={'name':'values','scope':['GLOBAL'],'dwarf_type':'int [2]','candidate_type':'int [4]'}
            with patch.object(array_tasks,'ROOT',root),patch.object(array_tasks,'affected_targets',return_value=['game-a']):
                source.write_text('int values[4] = { 1, -2 };\n')
                plan=array_tasks.plan_array('src/a.c',owner,{})
                self.assertEqual(plan['difficulty'],'CHEAP',plan['reason'])
                self.assertEqual(patch_text(source.read_text(),plan['changes']),'int values[2] = { 1, -2 };\n')
                for text in ('int values[4] = { 1, 2, 3 };','int values[4] = { MACRO };',
                             'int values[4] = { [1]=2 };','int values[4] = { 1 };\nint values[4] = { 1 };',
                             'int values[SIZE] = { 1 };'):
                    source.write_text(text)
                    self.assertEqual(array_tasks.plan_array('src/a.c',owner,{})['difficulty'],'SUPERVISOR',text)
                source.write_text('char *values[4] = { "hello, world", "brace }" };')
                strings=dict(owner,dwarf_type='char *[2]',candidate_type='char *[4]')
                self.assertEqual(array_tasks.plan_array('src/a.c',strings,{})['difficulty'],'CHEAP')
                (root/'src/b.c').write_text('extern char *values[4];')
                self.assertEqual(array_tasks.plan_array('src/a.c',strings,{})['difficulty'],'SUPERVISOR')


if __name__=='__main__': unittest.main()
