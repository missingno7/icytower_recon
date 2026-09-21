"""Shared FAST evidence and deterministic grinder publication, using the strict CU oracle."""
import bisect
import json
import re
from functools import lru_cache
from pathlib import Path
from common import ROOT, identity, read_json, write_json, run, check_json,sha
from build import TARGETS, COMPILERS, compile_target, verify_inputs
from experiment import compare
from instructions import decode, window, affected_instructions
from binary import Binary
from type_graph import graph, TypeGraph, number
from source_scope import function_span, body_hash
from audit_signedness import analyze
from classify_diff import workflow
from card_view import compact_card, detail_path
from dwarf_locations import candidate_debug, annotate
from compiler_context import load_context,load_trials
from branch_diagnostics import localized_guards
from data_diagnostics import capture_snapshot,diagnose
from relocation_diagnostics import mismatch_views
from instruction_alignment import analyze as instruction_alignment
from codegen_guidance import select_rules

OBJDUMP = Path('C:/msys64/mingw64/bin/objdump.exe')
CURRENT = ROOT/'docs/current'
VERIFIER_FILES = ['tools/common.py','tools/experiment.py','tools/binary.py','tools/dwarf.py','tools/instructions.py','tools/build.py','tools/data_owners.py','tools/type_graph.py','tools/control_transfers.py']
ANALYSIS_FILES = ['tools/codegen_guidance.py','tools/instruction_alignment.py','tools/typed_interface_tasks.py','tools/interface_type_probe.py','tools/relocation_diagnostics.py','tools/interface_scope.py','tools/classify_diff.py','tools/recovery_pipeline.py','tools/type_graph.py','tools/source_scope.py','tools/audit_signedness.py','tools/interfaces.py','tools/interface_tasks.py','tools/card_view.py','tools/type_tasks.py','tools/dwarf_locations.py','tools/compiler_context.py','tools/source_order.py','tools/array_tasks.py','tools/branch_diagnostics.py',
                  'tools/literal_dependencies.py','tools/global_type_tasks.py','tools/reference_diagnostics.py','tools/literal_diagnostics.py','tools/generate_types.py','tools/storage_diagnostics.py','tools/static_scope_tasks.py','tools/scheduling_diagnostics.py','tools/stack_diagnostics.py','tools/local_declarations.py','tools/type_aliases.py','tools/type_views.py','tools/dwarf_layout.py','tools/data_diagnostics.py','tools/data_tasks.py','tools/initializer_scope.py',
                  'evidence/census/location-lists.json','evidence/census/range-lists.json','evidence/census/line-mappings.json','docs/codegen-rules.json']


def verifier_identity():
    return {p:identity(ROOT/p) for p in VERIFIER_FILES}


def analysis_identity():
    return {p:identity(ROOT/p) for p in ANALYSIS_FILES}


LOADED_VERIFIER_IDENTITY=verifier_identity()
LOADED_ANALYSIS_IDENTITY=analysis_identity()


def check_fixture():
    if identity(ROOT/'assets/icytower15.exe') != read_json(ROOT/'evidence/fixture-lock.json'):
        raise ValueError('Verification fixture identity differs')
    lock=read_json(ROOT/'evidence/census-lock.json')
    for name in ('dwarf-dies.jsonl','functions.json','compilation-units.json','globals.json','location-lists.json','range-lists.json','line-mappings.json'):
        if identity(ROOT/'evidence/census'/name) != lock['outputs'][name]:
            raise ValueError('Census identity differs: '+name)


@lru_cache(maxsize=1)
def original_instructions():
    rows=decode(ROOT/'assets/icytower15.exe',OBJDUMP)
    return rows,[r['address'] for r in rows]


def original_slice(va,size):
    rows,addresses=original_instructions()
    return rows[bisect.bisect_left(addresses,va):bisect.bisect_left(addresses,va+size)]


@lru_cache(maxsize=1)
def debug_tables():
    return ({r['offset']:r for r in read_json(ROOT/'evidence/census/location-lists.json')},
            {r['offset']:r for r in read_json(ROOT/'evidence/census/range-lists.json')},
            read_json(ROOT/'evidence/census/line-mappings.json'))


def relevant_types(variables, offsets):
    g=graph(); names=set(); types=[]
    for variable in variables:
        ref=variable.get('type_die'); seen=set()
        while ref and ref not in seen:
            seen.add(ref); d=g.dies[ref]
            if d['tag']=='DW_TAG_typedef' and d['name'] in g.game_types: names.add(d['name'])
            ref=d.get('type_ref')
    for name in sorted(names):
        d=g.dies[g.game_types[name][0]['type_ref']]
        members=[]
        for m in g.children[d['offset']]:
            if m['tag']=='DW_TAG_member':
                off=g.member_offset(m)
                if off in offsets: members.append({'name':m['name'],'offset':off,'type':g.declaration(m.get('type_ref'))})
        types.append({'name':name,'size':g.size(d['offset']),'header':'include/recovered/'+name+'.h',
                      'members_at_disassembly_offsets':members,
                      'limit':'Offset association only; register-to-variable binding is not inferred.'})
    return types


def unit_for_target(target):
    return next(u for u in read_json(ROOT/'src/units.json') if u['source']==TARGETS[target]['source'])


def evidence_for_function(unit,f,row,candidate=None):
    g=graph()
    d=g.dies.get(f.get('die'))
    descendants=list(g.descendants(d['offset'])) if d else []
    parameters=[g.variable(g.dies[p]) for p in f.get('parameters',[])]
    locals_=[g.variable(v) for v in descendants if v['tag']=='DW_TAG_variable']
    lexical=[{'die':b['offset'],'parent':b['parent'],'low_pc':b.get('low_pc'),'high_pc':b.get('high_pc'),
              'ranges':b['resolved'].get('DW_AT_ranges')} for b in descendants if b['tag'] in ('DW_TAG_lexical_block','DW_TAG_inlined_subroutine')]
    locations,ranges,lines=debug_tables()
    for variable in parameters+locals_:
        loc=variable.get('location') or ''
        variable['location_list']=locations.get(number(loc)) if 'location list' in loc else None
    for block in lexical:
        block['range_list']=ranges.get(number(block['ranges'])) if block['ranges'] else None
    ret=g.declaration(d.get('type_ref')) if d else None
    variadic=bool(d and any(c['tag']=='DW_TAG_unspecified_parameters' for c in g.children[d['offset']]))
    prototype=ret+' '+f['name']+'('+', '.join([g.declaration(g.dies[p]['type_ref'],g.dies[p].get('name') or '') for p in f.get('parameters',[])]+(['...'] if variadic else []) or ['void'])+');' if ret else None
    text=(ROOT/unit['source']).read_text(encoding='cp1252')
    try:
        lo,hi=function_span(text,f['name']); body=text[lo:hi]
        scope={'body_start_line':text[:lo].count('\n')+1,'body_end_line':text[:hi].count('\n')+1,'body_sha256':body_hash(text,f['name'])}
    except ValueError:
        body=''; scope=None
    original=original_slice(f['va'],f['size'])
    context={'original':{'variables':parameters+locals_,'frame_location':d['resolved'].get('DW_AT_frame_base') if d else None,
                         'locations':locations,'base':unit['low_pc'],'scopes':{b['die']:b for b in lexical}}}
    if candidate and row['name'] in candidate['functions']:
        c=candidate['functions'][row['name']]
        context['candidate']={'variables':c['variables'],'frame_location':c['frame_location'],'base':c['base'],
                              'scopes':{int(k):v for k,v in c['scopes'].items()},'locations':{r['offset']:r for r in candidate['location_lists']}}
    signedness=analyze(parameters,locals_,original,row.get('instructions',[]),body,context)
    row['signedness']=signedness
    offset=(row.get('first_difference') or {}).get('offset',0)
    old_first=next((i for i in original if i['address']-f['va']<=offset<i['address']-f['va']+len(bytes.fromhex(i['bytes']))),None)
    new_first=next((i for i in row.get('instructions',[]) if i['address']-row['candidate_offset']<=offset<i['address']-row['candidate_offset']+len(bytes.fromhex(i['bytes']))),None)
    row['first_instruction_pair']={'original':old_first,'candidate':new_first}
    original_by_offset={i['address']-f['va']:i for i in original}
    affected=affected_instructions(row)
    def register_shape(i):
        return re.sub(r'%[a-z][a-z0-9]*', '%REG', i['assembly'])
    row['register_only_instruction_shape']=bool(affected) and all(
        (i['address']-row['candidate_offset']) in original_by_offset and
        register_shape(i)==register_shape(original_by_offset[i['address']-row['candidate_offset']]) for i in affected)
    row['localized_guards']=localized_guards(row,original)
    from scheduling_diagnostics import analyze as scheduling_analysis,assignment_patterns
    row['instruction_order']=scheduling_analysis(row,original,(candidate or {}).get('line_mappings',[]),unit['source'])
    patterns=assignment_patterns(row['instruction_order'],(ROOT/unit['source']).read_bytes().decode('cp1252')) if scope else []
    from literal_diagnostics import patterns as literal_patterns
    patterns+=literal_patterns(row,(ROOT/unit['source']).read_bytes().decode('cp1252')) if scope else []
    from reference_diagnostics import source_pattern
    row['reference_source_pattern']=source_pattern(row,(ROOT/unit['source']).read_bytes().decode('cp1252'),context.get('candidate',{}).get('variables',[])) if scope else None
    if row['reference_source_pattern']:
        patterns=[p for p in patterns if p['id']!='repair_literal_content']+[row['reference_source_pattern']]
    from stack_diagnostics import analyze as stack_analysis
    row['frame_layout']=stack_analysis(row,original,parameters+locals_,context.get('candidate',{}).get('variables',[]))
    return {'prototype':prototype,'return_type':ret,'parameters':parameters,'locals':locals_,
            'lexical_blocks':lexical,'variadic':variadic,'calling_convention':d['resolved'].get('DW_AT_calling_convention','not recorded (i386 C default candidate)') if d else None,
            'source_scope':scope,'reference_diagnostics':row.get('reference_diagnostics',[]),'literal_diagnostics':row.get('literal_diagnostics',[]),'tail_jump_layout':row.get('tail_jump_layout'),'instruction_order':row['instruction_order'],'source_patterns':patterns,'frame_layout':row['frame_layout'],'signedness':signedness,'location_context':context,'localized_guards':row['localized_guards']},original


def fresh_verify(target, dest=None, locked=False):
    if verifier_identity()!=LOADED_VERIFIER_IDENTITY or analysis_identity()!=LOADED_ANALYSIS_IDENTITY: raise ValueError('Tools changed since process startup')
    if not locked:
        verify_inputs('tdm-2'); check_fixture()
    out=dest or ROOT/'build/fast'/target
    obj,build=compile_target(target,dest=out,compiler='tdm-2')
    report=compare(obj,TARGETS[target]['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
    report.update(build=build,fixture=identity(ROOT/'assets/icytower15.exe'),analysis_tool=identity(OBJDUMP),
                  verifier=LOADED_VERIFIER_IDENTITY,analysis_identity=LOADED_ANALYSIS_IDENTITY,schema=4)
    report['candidate_debug']=candidate_debug(build,OBJDUMP)
    from interface_type_probe import supplement
    supplement(report,out,OBJDUMP)
    report['data_snapshot']=capture_snapshot(report)
    report['data_diagnostics']=diagnose(report)
    unit=unit_for_target(target)
    originals={f['name']:f for f in unit['functions']}
    from literal_diagnostics import diagnose as diagnose_literals
    from reference_diagnostics import diagnose as diagnose_references,historical_reference
    literal_exe=Binary(ROOT/'assets/icytower15.exe')
    for row in report['functions']:
        row['literal_diagnostics']=diagnose_literals(row,original_slice(row['va'],row['original_size']),report['data_snapshot'],report['object_sections'],literal_exe,report['candidate_debug'].get('line_mappings',[]),unit['source'])
        row['reference_diagnostics']=diagnose_references(row,original_slice(row['va'],row['original_size']),report['candidate_debug']['globals'],lambda address:historical_reference(address,literal_exe),report['candidate_debug'].get('line_mappings',[]),unit['source'])
        ev,_=evidence_for_function(unit,originals[row['name']],row,report.get('candidate_debug'))
        row['source_body_sha256']=ev['source_scope']['body_sha256'] if ev['source_scope'] else None
        row['compiler_context']=load_context(report['build']['target'],row['name'],row,report['build']['local_inputs'])
        row['workflow']=workflow(row)
    report['interfaces_aux']= (out/'interfaces.aux').read_text(errors='replace')
    report['candidate_dwarf_path']=(out/'dwarf.txt').relative_to(ROOT).as_posix()
    if verifier_identity()!=LOADED_VERIFIER_IDENTITY or analysis_identity()!=LOADED_ANALYSIS_IDENTITY: raise ValueError('Tools changed during compilation/comparison')
    write_json(out/'comparison.json',report)
    return report


def validate_report(report, check_sources=True, check_analysis=True):
    build=report['build']
    from interface_type_probe import validate as validate_type_probe
    validate_type_probe(report)
    if not build.get('inputs_verified_around_compile'): raise ValueError('Compile lacks dependency race check')
    if report.get('schema') not in (3,4) or {p:report.get('verifier',{}).get(p) for p in VERIFIER_FILES}!=verifier_identity():
        raise ValueError('Stale verifier identity; refresh '+build['target'])
    if report.get('candidate_debug') and report['candidate_debug']['object']!=build['object']: raise ValueError('Diagnostic object identity differs')
    if report.get('data_snapshot'):
        snapshot=report['data_snapshot']
        if snapshot['object']!=build['object']: raise ValueError('Data snapshot object identity differs')
        sections={str(s['index']):s for s in report['object_sections']}
        for index,content in snapshot['sections'].items():
            if sha(bytes.fromhex(content))!=sections[index]['sha256']: raise ValueError('Data snapshot section identity differs')
    if check_analysis and (report.get('schema')!=4 or report.get('analysis_identity')!=analysis_identity()):
        raise ValueError('Stale diagnostics; run refresh_recovery.py --reanalyze')
    if build.get('flags')!=[TARGETS[build['target']]['default'],*TARGETS[build['target']].get('flags',[])]:
        raise ValueError('Unapproved compiler flags in proof')
    if build.get('compiler')!='tdm-2': raise ValueError('Unexpected compiler in grinder proof')
    if build.get('config')!=TARGETS[build['target']]:
        raise ValueError('Compiler configuration changed')
    if report['fixture']!=identity(ROOT/'assets/icytower15.exe') or report['analysis_tool']!=identity(OBJDUMP):
        raise ValueError('Fixture/analysis identity changed')
    if check_sources:
        for p,expected in build['local_inputs'].items():
            if identity(ROOT/p)!=expected:
                raise ValueError('Stale source/dependency: '+p)
    for key,path in [('toolchain_lock','toolchain/lock.json'),('candidate_toolchain_lock','toolchain/tdm-2-lock.json')]:
        if build.get(key)!=identity(ROOT/path):
            raise ValueError('Toolchain lock changed')
    for row in report['functions']:
        if row.get('tail_jump_layout'):
            from control_transfers import tail_layout
            unit=unit_for_target(build['target']); original=next(f for f in unit['functions'] if f['name']==row['name'])
            if (row['va'],row['original_size'])!=(original['va'],original['size']): raise ValueError('Historical branch-layout extent differs')
            candidates=[{'name':f['name'],'low_pc':f['candidate_offset']} for f in report['functions'] if f.get('candidate_offset') is not None]
            # Compare also against the original bytes, not just saved disassembly.
            proof=tail_layout(row,original_slice(row['va'],row['original_size']),candidates,unit['functions'],reference=original_binary().at_va(row['va'],row['original_size']))
            if proof is None or proof!=row['tail_jump_layout']: raise ValueError('Invalid terminal branch-layout proof: '+row['name'])
        if row['status']=='FUNCTION_MATCH' and not (row.get('relocation_resolved_equal') and row.get('candidate_size')==row['original_size'] and row.get('first_difference') is None and all(r['equal'] for r in row.get('relocations',[])) and all(t['equal'] for t in row.get('direct_transfers',[])) and row.get('instruction_boundaries_verified')):
            raise ValueError('Invalid exact claim: '+row['name'])
        if check_analysis and row.get('workflow')!=workflow(row):
            raise ValueError('Invalid workflow claim: '+row['name'])



def reanalyze_report(report):
    """Refresh diagnostics using immutable, source-current byte proof; no compilation."""
    import copy
    if verifier_identity()!=LOADED_VERIFIER_IDENTITY or analysis_identity()!=LOADED_ANALYSIS_IDENTITY: raise ValueError('Tools changed since diagnostic process startup')
    validate_report(report,check_analysis=False)
    report=copy.deepcopy(report)
    if report.get('candidate_debug',{}).get('schema')!=7: report['candidate_debug']=candidate_debug(report['build'],OBJDUMP)
    if not report.get('data_snapshot'): report['data_snapshot']=capture_snapshot(report)
    report['data_diagnostics']=diagnose(report)
    unit=unit_for_target(report['build']['target'])
    originals={f['name']:f for f in unit['functions']}
    from literal_diagnostics import diagnose as diagnose_literals
    from reference_diagnostics import diagnose as diagnose_references,historical_reference
    literal_exe=Binary(ROOT/'assets/icytower15.exe')
    for row in report['functions']:
        row['literal_diagnostics']=diagnose_literals(row,original_slice(row['va'],row['original_size']),report['data_snapshot'],report['object_sections'],literal_exe,report['candidate_debug'].get('line_mappings',[]),unit['source'])
        row['reference_diagnostics']=diagnose_references(row,original_slice(row['va'],row['original_size']),report['candidate_debug']['globals'],lambda address:historical_reference(address,literal_exe),report['candidate_debug'].get('line_mappings',[]),unit['source'])
        ev,_=evidence_for_function(unit,originals[row['name']],row,report.get('candidate_debug'))
        row['source_body_sha256']=ev['source_scope']['body_sha256'] if ev['source_scope'] else None
        row['compiler_context']=load_context(report['build']['target'],row['name'],row,report['build']['local_inputs'])
        row['workflow']=workflow(row)
    if verifier_identity()!=LOADED_VERIFIER_IDENTITY or analysis_identity()!=LOADED_ANALYSIS_IDENTITY: raise ValueError('Tools changed during diagnostic regeneration')
    report.update(schema=4,verifier=LOADED_VERIFIER_IDENTITY,analysis_identity=LOADED_ANALYSIS_IDENTITY)
    return report


@lru_cache(maxsize=1)
def original_binary():
    return Binary(ROOT/'assets/icytower15.exe')


def ownership(report,row,original):
    g=graph(); results=[]
    exe=original_binary()
    globals_=[d for d in g.dies.values() if d['tag']=='DW_TAG_variable' and d.get('address') is not None]
    by_name={}
    for d in globals_: by_name.setdefault(d.get('name'),[]).append(d)
    references={}
    for i in original:
        for token in re.findall(r'0x([0-9a-f]+)',i['assembly']):
            references.setdefault(int(token,16),[]).append(hex(i['address']))
    symbols={r.get('symbol') for r in row.get('relocations',[])}
    candidates=[d for d in globals_ if d['address'] in references or ('_'+(d.get('name') or '')) in symbols]
    seen=set()
    for d in candidates:
        key=(d['name'],d['address'])
        if key in seen: continue
        seen.add(key)
        cu=g.dies.get(d['cu'],{}).get('name')
        sym=[s for s in report.get('object_symbols',[]) if s['name']=='_'+d['name']]
        sec=next((s['name'] for s in report.get('object_sections',[]) if sym and s['index']==sym[0]['section']),None)
        old_section=next((s for s in exe.sections if exe.image_base+s['rva']<=d['address']<exe.image_base+s['rva']+s['virtual_size']),None)
        size=g.size(d.get('type_ref'))
        initial=exe.at_va(d['address'],min(size,64)).hex() if size and old_section and old_section['name'] in ('.data','.rdata') else None
        original_symbols=[s for s in exe.symbols if s.get('va')==d['address'] and not s['name'].startswith('.')]
        results.append({'symbol':d['name'],'cu':cu,'historical_address':hex(d['address']),'dwarf_type':g.declaration(d.get('type_ref')),
                        'size':size,'section':old_section['name'] if old_section else sec,'references':references.get(d['address'],[]),
                        'coff_symbols':[{k:s.get(k) for k in ('index','name','section','value','storage_class')} for s in sym],'placement_confidence':'DWARF_ADDRESS; candidate COFF section when present',
                        'original_coff_symbols':[{k:s.get(k) for k in ('index','name','section','va','storage_class')} for s in original_symbols],'initial_value':initial,'initial_value_status':'first 64 bytes maximum, hexadecimal historical data' if initial else 'BSS/unknown; no initializer claimed'})
    section_references={}
    for r in row.get('relocations',[]):
        if not (r.get('symbol') or '').startswith('.'): continue
        key=(r['symbol'],r.get('addend'),r.get('target_va'))
        if key in section_references:
            section_references[key]['references'].append(r['function_offset']); continue
        contributions=[x for x in report.get('initialized_data_comparison',[]) if x['section']==r['symbol']]
        owners=[o for group in ('accepted','rejected') for o in report.get('object_ownership',{}).get(group,[])
                if o.get('section')==r['symbol'] and o.get('size') and o['candidate_offset']<=r.get('addend',-1)<o['candidate_offset']+o['size']]
        item={'symbol':r['symbol'],'cu':report['historical_cu'],'section':r['symbol'],'size':None,
              'historical_address':hex(r['target_va']) if r.get('target_va') is not None else None,
              'candidate_addend':r.get('addend'),'dwarf_type':None,'references':[r['function_offset']],
              'placement_confidence':r['resolution'],'object_owners':owners,
              'initial_value':None,'coff_contribution_evidence':[{
                  'logical_size':x['logical_size'],'content_equal':x['content_equal'],
                  'unresolved_initializer_relocations':len(x.get('unresolved_relocations',[])),
                  'independent_section_bases':x.get('section_bases',[]),
                  'detail_report':'docs/current/reports/'+report['build']['target']+'.json#initialized_data_comparison'} for x in contributions],
              'blocker':'RELOCATION_OWNER_BLOCKED' if r.get('target_va') is None else None}
        section_references[key]=item; results.append(item)
    diagnostics={o['name']:o for o in report.get('data_diagnostics',{}).get('objects',[])}
    for item in results:
        names={item.get('symbol','').lstrip('_')}|{o['name'] for o in item.get('object_owners',[])}
        item['initializer_blockers']=[{'object':name,'reason':diagnostics[name]['reason'],
                                      'fields':[{'expression':f['expression'],'classification':f.get('classification','UNKNOWN_SUPERVISOR')} for f in diagnostics[name]['fields'][:8]],
                                      'candidate_card':'docs/current/data-tasks/pointer_'+Path(report['build']['config']['source']).stem+'_'+name+'.json'}
                                     for name in sorted(names&diagnostics.keys())]
    return results


def card_for(target,report,row,ledger=None,interface_index=None):
    unit=unit_for_target(target); f=next(f for f in unit['functions'] if f['name']==row['name'])
    ev,old=evidence_for_function(unit,f,row,report.get('candidate_debug'))
    location_context=ev.pop('location_context')
    wf=workflow(row)
    diff=row.get('first_difference'); offset=diff['offset'] if diff else 0
    old_window=window(old,f['va']+offset)
    new_window=window(row.get('instructions',[]),row.get('candidate_offset',0)+offset)
    old_window=annotate(old_window,**location_context['original'])
    if location_context.get('candidate'): new_window=annotate(new_window,**location_context['candidate'])
    offsets={int(x,16) for i in old_window+new_window for x in re.findall(r'0x([0-9a-f]+)\(%',i['assembly'])}
    types=relevant_types(ev['parameters']+ev['locals'],offsets)
    line_rows=[l for l in debug_tables()[2] if f['va']<=l['address']<f['va']+f['size']]
    nearest=sorted(line_rows,key=lambda l:abs(l['address']-(f['va']+offset)))[:8]
    calls=[{'symbol':r.get('symbol'),'function_offset':r['function_offset'],'target_va':r.get('target_va'),'verified':r['equal']} for r in row.get('relocations',[]) if r.get('type')==20]
    calls += [{'symbol':t['target_function'],'function_offset':t['function_offset'],'target_va':t['target_va'],'verified':t['equal']} for t in row.get('direct_transfers',[])]
    original_calls=[i for i in old if i['mnemonic'].startswith('call') or (i['mnemonic']=='jmp' and '*' in i['assembly'])]
    rules=read_json(ROOT/'docs/codegen-rules.json')['rules']
    relevant=select_rules(rules,row,ev,wf,old,report['build'])
    for pattern in ev['source_patterns']:
        pattern['application_command']='python tools/apply_pattern.py '+target+' '+row['name']+' '+pattern['id']
    from literal_dependencies import groups as literal_groups,for_function as literal_dependencies
    data=ownership(report,row,old)
    from storage_diagnostics import function_storage
    storage=function_storage(report,row['name'],data)
    unresolved=sum(c['target_va'] is None for c in calls)
    indirect=sum('*' in i['assembly'] for i in original_calls)
    localized=len(row.get('difference_offsets',[]))<=12 and row.get('candidate_size')==row['original_size']
    difficulty='SUPERVISOR'
    if wf['body_edit_allowed'] and wf['difference_class']!='UNKNOWN_SUPERVISOR' and ev['source_scope'] and not unresolved and (not indirect or f['size']<=1200):
        difficulty='CHEAP' if localized and not indirect and f['size']<=900 and wf['difference_class'] in ('REGISTER_OR_INSTRUCTION_SELECTION','SIGNEDNESS_OR_PROMOTION','SOURCE_CONTROL_FLOW_SHAPE') else 'MEDIUM'
    if wf['state']=='MISSING': difficulty='MEDIUM' if f['size']<=200 and ev['prototype'] else 'SUPERVISOR'
    priority=(150 if difficulty=='CHEAP' else 60 if difficulty=='MEDIUM' else 0)+max(0,30-f['size']//32)+10*localized+5*any(r['applicability']['priority_bonus_eligible'] for r in relevant)-5*unresolved-10*indirect
    blocked=(CURRENT/'supervisor-blocks.json')
    key=unit['source']+':'+row['name']
    supervisor=read_json(blocked).get(key) if blocked.exists() else None
    if supervisor: difficulty='SUPERVISOR'; priority=-100
    interface_path=CURRENT/'interface-conflicts.json'
    local_task_path=CURRENT/'local-declaration-tasks.json'
    local_tasks=[t for t in read_json(local_task_path)['tasks'] if t['source']==unit['source'] and t['target_function']==row['name']] if local_task_path.exists() else []
    interface_conflicts=[]
    if interface_index is not None:
        interface_conflicts=interface_index.get(row['name'],[])
    elif interface_path.exists():
        interface_conflicts=[r for r in read_json(interface_path)['conflicts'] if r['function']==row['name']]
    from interface_scope import partition as scoped_interfaces
    local_interface_conflicts,interface_scope=scoped_interfaces(interface_conflicts,unit['source'])
    routing_reason='Conservative size, mismatch, dependency and control-flow ranking.'
    if not supervisor and wf['body_edit_allowed'] and ev.get('localized_guards') and not local_interface_conflicts and ev['source_scope'] and f['size']<=1200:
        difficulty='CHEAP'; priority=180+max(0,30-f['size']//32)
        routing_reason='Only up to four decoded conditional-branch opcodes differ; targets and all other independently resolved bytes agree. Unchanged indirect calls do not obstruct this bounded guard task.'
    if not supervisor and wf['body_edit_allowed'] and (ev.get('instruction_order') or {}).get('cheap_routing_eligible') and ev['source_patterns'] and not local_interface_conflicts:
        difficulty='CHEAP'; priority=185
        routing_reason='All differences are bounded decoded instruction permutations; emitted line mappings supply an adjacent-assignment experiment. Strict exact verification is still required.'
    if not supervisor and wf['body_edit_allowed'] and wf['difference_class']=='LITERAL_CONTENT_DIFFERENCE' and any(p['id']=='repair_literal_content' for p in ev['source_patterns']) and not local_interface_conflicts:
        difficulty='CHEAP'; priority=190
        routing_reason='Aligned literal operands and unique explicit source tokens supply a bounded string repair; fresh strict proof is mandatory.'
    if not supervisor and wf['body_edit_allowed'] and row.get('reference_source_pattern') and not local_interface_conflicts:
        difficulty='CHEAP'; priority=195
        routing_reason='A typed, uniquely mapped scalar assignment and any explicit literal repairs have one generated recipe; exact acceptance remains mandatory.'
    if not supervisor and wf['body_edit_allowed'] and local_interface_conflicts:
        difficulty='SUPERVISOR'; priority=-30
        routing_reason='This CU has an unresolved declaration/type prerequisite; repair that interface before body grinding.'
    from literal_dependencies import pattern_prerequisites
    source_pattern_prerequisites=pattern_prerequisites(row,ev['source_patterns'])
    if not supervisor and source_pattern_prerequisites:
        difficulty='SUPERVISOR'; priority=-25
        routing_reason='Known source recipe leaves independent relocation/owner prerequisites unresolved; do not run a knowingly incomplete automatic body repair.'
    position=next(i for i,x in enumerate(report['functions']) if x['name']==row['name'])
    adjacent={x['name'] for x in report['functions'][max(0,position-1):position+2]}
    related=adjacent|{t['target_function'] for t in row.get('direct_transfers',[])}|{x['name'] for x in report['functions'] if any(t['target_function']==row['name'] for t in x.get('direct_transfers',[]))}
    exact_neighbors=sum(x['status']=='FUNCTION_MATCH' and x['name']!=row['name'] for x in report['functions'] if x['name'] in adjacent)
    priority+=5*exact_neighbors
    neighbors=[{'function':x['name'],'status':x['status'],'historical_offset':x['va']-unit['low_pc'],'candidate_offset':x.get('candidate_offset'),'size_delta':x.get('candidate_size',0)-x['original_size']} for x in report['functions'] if x['name']!=row['name'] and x['name'] in related]
    return {'schema':1,'source':unit['source'],'target':target,'historical_cu':unit['historical_path'],'function':row['name'],
            'historical_va':hex(f['va']),'historical_size':f['size'],'status':row['status'],**wf,**ev,
            'compiler':report['build']['compiler'],'compiler_flags':report['build']['flags'],'current_candidate_size':row.get('candidate_size'),
            'first_difference':diff,'mismatch_count':len(row.get('difference_offsets',[])),'classification_confidence':'MECHANICAL_PROOF' if row['status']=='FUNCTION_MATCH' else 'OBSERVED_ALLOCATION; SOURCE_CAUSE_UNPROVEN' if (row.get('frame_layout') or {}).get('first_mismatch_is_frame_allocation') else 'CONSERVATIVE_HYPOTHESIS',
            'instruction_alignment':instruction_alignment(row,old),'disassembly':{'original':old_window,'candidate':new_window},'relevant_types':types,'original_line_window':sorted(nearest,key=lambda l:l['address']),
            'referenced_globals':data,'literal_dependencies':literal_dependencies(literal_groups(report),row['name']),'calls':calls,'original_calls':original_calls,'indirect_control_flow':indirect,
            'relocation_mismatches':mismatch_views(row,old),
            'direct_transfer_mismatches':[t for t in row.get('direct_transfers',[]) if not t['equal'] or not t.get('layout_operand_equal',True)],
            'unresolved_call_symbols':unresolved,'exact_adjacent_functions':exact_neighbors,'neighbor_layout':neighbors,'known_rules':relevant,'difficulty':difficulty,'priority':priority,
            'compiler_context':row.get('compiler_context'),'compiler_trials':load_trials(target,row['name'],row,report['build']['local_inputs']),'routing_reason':routing_reason,'supervisor_block':supervisor,'evidence_report':'docs/current/reports/'+target+'.json',
            'verification_command':'python tools/check_function.py '+target+' '+row['name'],
            'begin_command':'python tools/grinder_task.py begin '+target+' '+row['name'],
            'promotion_command':'python tools/promote_function.py '+target+' '+row['name']+(' --claim BODY_MATCH_LAYOUT_BLOCKED' if wf['state']=='BODY_MATCH_LAYOUT_BLOCKED' else ''),
            'storage_declarations':storage,
            'local_declaration_tasks':[{k:t[k] for k in ('function','status','state','difficulty','candidate_card')} for t in local_tasks],
            'source_pattern_prerequisites':source_pattern_prerequisites,'interface_scope':interface_scope,'interface_conflicts':[{'function':c['function'],'historical':c['historical'],'type_layout_issues':c.get('type_layout_issues',[]),'candidate_signatures':sorted({str((d['return_type'],d['parameter_types'])) for d in c['candidate_declarations']}),'candidate_card':'docs/current/interfaces/'+c['function']+'.json'} for c in interface_conflicts],
            'edit_scope':'Function body only; use supervisor for prototypes/data/headers or missing implementations.'}


def publish_cards(ledger,check=False):
    emit=check_json if check else write_json
    queue=[]; statuses={}; classes={}; reference_index=[]
    interface_index={}
    path=CURRENT/'interface-conflicts.json'
    if path.exists():
        for conflict in read_json(path)['conflicts']: interface_index.setdefault(conflict['function'],[]).append(conflict)
    for source,entry in ledger.items():
        if not entry.get('verified_report'): continue
        report=read_json(ROOT/entry['verified_report']); target=report['build']['target']
        emit(CURRENT/'objects'/(target+'.json'),{'source':source,**report.get('object_ownership',{}),'typed_initializer_diagnostics':report.get('data_diagnostics',{}).get('objects',[])})
        from literal_dependencies import publish as publish_literals
        publish_literals(report,ROOT,emit)
        for row in report['functions']:
            card=card_for(target,report,row,ledger,interface_index)
            path=CURRENT/'functions'/Path(source).stem/(row['name']+'.json')
            emit(ROOT/detail_path(card),card)
            emit(path,compact_card(card))
            for observation in card.get('reference_diagnostics',[]):
                reference_index.append({'source':source,'target':target,'function':row['name'],'candidate_card':path.relative_to(ROOT).as_posix(),
                                        **{k:observation[k] for k in ('function_offset','classification','prerequisite','candidate_reference','expected_reference','expected_declaration_in_candidate')}})
            statuses[card['state']]=statuses.get(card['state'],0)+1
            classes[card['difference_class']]=classes.get(card['difference_class'],0)+1
            if card['state']!='FUNCTION_MATCH':
                queue.append({k:card[k] for k in ('source','target','function','status','state','priority','difficulty','difference_class','first_difference','verification_command','begin_command','promotion_command','body_edit_allowed')} | {'size':card['historical_size'],'candidate_card':path.relative_to(ROOT).as_posix()})
    interface_tasks=read_json(CURRENT/'interface-conflicts.json').get('tasks',[])
    queue.extend(interface_tasks)
    queue.extend(read_json(CURRENT/'type-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'type-view-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'local-declaration-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'source-order-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'array-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'data-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'static-scope-tasks.json').get('tasks',[]))
    queue.extend(read_json(CURRENT/'global-type-tasks.json').get('tasks',[]))
    for task in queue: task.setdefault('task_kind','FUNCTION_BODY')
    queue.sort(key=lambda x:(-x['priority'],x['size'],x['source'],x['function']))
    emit(CURRENT/'grinder-queue.json',{'authority':'src/recovery.json','default_difficulty':'CHEAP','tasks':queue})
    emit(CURRENT/'blockers.json',{'workflow_states':statuses,'difference_classes':classes,'tasks':[r for r in queue if r['difficulty']=='SUPERVISOR'],
                                     'historical_hypotheses':'docs/blockers.json'})
    emit(CURRENT/'reference-status.json',{'scope':'Supported aligned named-global mismatch observations only; absence is not proof of correct references. No source edit or relocation binding is granted.','observations':reference_index})
    emit(CURRENT/'codegen-rules.json',read_json(ROOT/'docs/codegen-rules.json'))
    return queue
