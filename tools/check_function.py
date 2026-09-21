"""FAST: fresh owning-CU compile, strict comparison, target-only diagnostics."""
import argparse
import json
from common import ROOT, write_json, identity
from recovery_pipeline import fresh_verify, card_for
from task_outcomes import fast_exit
from card_view import compact_card


def diagnostic(card):
    keys=('function','source','status','state','interface_scope','source_pattern_prerequisites','body_edit_allowed','difference_class','current_candidate_size','historical_size','first_difference','disassembly','instruction_alignment','relocation_mismatches','direct_transfer_mismatches','prototype','parameters','locals','lexical_blocks','signedness','compiler_context','localized_guards','frame_layout','tail_jump_layout','literal_diagnostics','literal_dependencies','reference_diagnostics','instruction_order','source_patterns','storage_declarations','local_declaration_tasks','neighbor_layout','known_rules','difficulty','promotion_command')
    return {k:card[k] for k in keys}


def record_attempt(target,name,report,card,outcome='FAST',failure=None):
    path=ROOT/'docs/attempts'/target/(name+'.jsonl')
    path.parent.mkdir(parents=True,exist_ok=True)
    from source_scope import function_span
    text=(ROOT/card['source']).read_bytes().decode('cp1252')
    try:
        a,b=function_span(text,name); body=text[a:b]
    except ValueError: body=None
    row={'source_body':body,'disassembly':card['disassembly'],'outcome':outcome,'source_inputs':report['build']['local_inputs'],'flags':report['build']['flags'],
         'status':card['status'],'state':card['state'],'first_difference':card['first_difference'],
         'difference_class':card['difference_class'],'instruction_alignment':card.get('instruction_alignment'),'localized_guards':card.get('localized_guards'),
         'reference_diagnostics':card.get('reference_diagnostics'),'literal_diagnostics':card.get('literal_diagnostics'),'tail_jump_layout':card.get('tail_jump_layout'),'instruction_order':card.get('instruction_order'),'source_patterns':card.get('source_patterns'),'storage_declarations':card.get('storage_declarations'),'compiler_context':card.get('compiler_context'),'frame_layout':card.get('frame_layout'),'difficulty':card.get('difficulty'),
         'routing_reason':card.get('routing_reason'),'failure':failure}
    from grinder_task import SESSION
    if SESSION.exists():
        from common import read_json
        session=read_json(SESSION)
        if (session.get('target'),session.get('function'))==(target,name): row['applied_pattern']=session.get('applied_pattern')
    with path.open('a',encoding='utf-8') as stream:
        stream.write(json.dumps(row,separators=(',',':'))+'\n')


def record_compile_failure(target,name,source,error):
    path=ROOT/'docs/attempts'/target/(name+'.jsonl'); path.parent.mkdir(parents=True,exist_ok=True)
    row={'outcome':'COMPILE_OR_VERIFICATION_FAILED','failure':str(error),'source':source,
         'source_identity':identity(ROOT/source),'source_text':(ROOT/source).read_bytes().decode('cp1252')}
    with path.open('a',encoding='utf-8') as stream: stream.write(json.dumps(row,separators=(',',':'))+'\n')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('target'); ap.add_argument('function')
    ap.add_argument('--json',action='store_true')
    a=ap.parse_args()
    from grinder_task import before_fast
    from build import TARGETS
    before_fast(a.target,a.function)
    try: report=fresh_verify(a.target)
    except Exception as exc:
        record_compile_failure(a.target,a.function,TARGETS[a.target]['source'],exc)
        raise
    row=next((r for r in report['functions'] if r['name']==a.function),None)
    if row is None: raise ValueError('Function does not belong to selected CU')
    card=card_for(a.target,report,row)
    from literal_dependencies import publish_function
    card['literal_dependencies']=publish_function(report,a.function,ROOT,'build/fast/'+a.target+'/'+a.function+'-literals',write_json)
    detail='build/fast/'+a.target+'/'+a.function+'-evidence.json'
    write_json(ROOT/detail,card)
    write_json(ROOT/'build/fast'/a.target/(a.function+'.json'),compact_card(card,detail))
    record_attempt(a.target,a.function,report,card)
    if a.json:
        print(json.dumps(diagnostic(compact_card(card,detail)) | {'detailed_evidence':detail,'evidence_counts':compact_card(card,detail)['evidence_counts']},indent=2))
    else:
        print('%s:%s %s / %s'%(a.target,a.function,card['status'],card['state']))
        print('size %s / %s; %s; body edit %s'%(card['current_candidate_size'],card['historical_size'],card['difference_class'],card['body_edit_allowed']))
        print('first difference:',card['first_difference'])
        print(card['prototype'])
        for scope in card.get('interface_scope',[])[:4]:
            print('  interface:',scope['state'],';',scope['reason'])
        for prerequisite in card.get('source_pattern_prerequisites',[])[:4]:
            print('  recipe prerequisite +%#x %s: %s'%(prerequisite['function_offset'],prerequisite['symbol'],prerequisite['reason']))

        print('locals:',', '.join(v['type']+' '+str(v['name']) for v in card['locals']))
        for side,rows in card['disassembly'].items():
            print(side+':')
            for i in rows:
                bindings=', '.join(v['name']+': '+v['type'] for v in i.get('dwarf_variables',[]) if v.get('name'))
                print('  %08x  %-22s %s%s'%(i['address'],i['bytes'],i['assembly'],' ; '+bindings if bindings else ''))
        alignment=card.get('instruction_alignment') or {}
        if alignment.get('state')=='DIAGNOSTIC_SEQUENCE_ALIGNMENT':
            print('Instruction-sequence diagnostic:',alignment['changed_group_count'],'changed groups; heuristic, not proof')
            for hunk in alignment['hunks']:
                print('  %s: original instructions %d:%d at +%#x; candidate %d:%d at +%#x'%(hunk['kind'],hunk['original']['instruction_start'],hunk['original']['instruction_end'],hunk['original']['function_offset'],hunk['candidate']['instruction_start'],hunk['candidate']['instruction_end'],hunk['candidate']['function_offset']))
        print('relocation mismatches:',len(card['relocation_mismatches']),'direct-transfer/layout differences:',len(card['direct_transfer_mismatches']))
        for r in card['relocation_mismatches'][:4]:
            print('  relocation +%#x %s: %s; independently resolved target %s'%(r['function_offset'],r['symbol'],r['resolution'],r.get('target_va')))
            context=r.get('comparison_context',{})
            print('    comparison:',context.get('state','UNINTERPRETED'),';',context.get('reason','Original byte window has not been interpreted.'))
        for reference in card.get('reference_diagnostics',[])[:4]:
            print('  reference +%#x: %s -> %s; %s'%(reference['function_offset'],reference['candidate_reference']['expression'],reference['expected_reference']['expression'],reference['prerequisite']))
        for pool in card.get('literal_dependencies',[])[:4]:
            print('  shared literal .rdata+%#x: %d peer functions; owner unproven; %s'%(pool['candidate_addend'],pool['peer_function_count'],pool['candidate_card']))
        for literal in card.get('literal_diagnostics',[])[:4]:
            print('  literal +%#x: %s; candidate %r; original %r'%(literal['function_offset'],literal['classification'],literal.get('candidate_text',literal.get('candidate_hex')),literal.get('original_text',literal.get('original_hex'))))
        for t in card['direct_transfer_mismatches'][:4]:
            print('  transfer +%#x %s: target proof %s; original layout operand %s'%(t['function_offset'],t['target_function'],t['equal'],t.get('layout_operand_equal')))
        for t in card['signedness']['declaration_differences'][:4]:
            print('  DWARF declaration %s: original %s; candidate %s (cause unproven)'%(t['variable'],t['original_type'],t['candidate_type']))
        for task in card.get('local_declaration_tasks',[])[:3]:
            print('  local declaration evidence:',task['candidate_card'],'('+task['difficulty']+')')
        for item in card.get('storage_declarations',[])[:4]:
            print('  storage %s: %s; %s'%(item['name'],item['state'],item['candidate_card']))
        if card.get('tail_jump_layout'):
            tail=card['tail_jump_layout']
            print('  tail-jump layout: %d-byte candidate / %d-byte original; independently resolved target %s; raw function does not match'%(tail['candidate_encoding_bytes'],tail['original_encoding_bytes'],tail['target_function']))
        if card.get('instruction_order'):
            for window in card['instruction_order']['windows'][:3]:
                print('  instruction-order window +%#x; candidate source lines %s'%(window['function_offset'],[r['line'] for r in window['candidate_source_lines']]))
            for pattern in card['source_patterns']:
                print('  bounded source experiment:',pattern['application_command'])
        if card.get('frame_layout'):
            frame=card['frame_layout']
            print('  stack allocation: original %d; candidate %d; source cause not proven'%(frame['original']['reserved_bytes'],frame['candidate']['reserved_bytes']))
            for local in frame['local_width_differences']:
                print('  local width %s: original %d; candidate %d'%(local['variable'],local['original_bytes'],local['candidate_bytes']))
        if card.get('compiler_context'):
            print('Compiler context:',card['compiler_context']['state'],';',card['compiler_context']['evidence'])
        if card.get('localized_guards'):
            for guard in card['localized_guards']['guards']:
                print('  guard +%#x: original %s; candidate %s; same target +%#x'%(guard['function_offset'],guard['original_condition'],guard['candidate_condition'],guard['target_offset']))
        neighbors=[n for n in card['neighbor_layout'] if n['size_delta']]
        if neighbors: print('Neighbor size deltas:',', '.join(n['function']+': '+str(n['size_delta']) for n in neighbors[:5]))
        print('Focused card: build/fast/%s/%s.json'%(a.target,a.function))
        print(card['promotion_command'])
    return fast_exit(card['state'])


if __name__=='__main__': raise SystemExit(main())
