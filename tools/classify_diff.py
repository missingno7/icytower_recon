"""Conservative function-scoped classification; hypotheses never grant proof."""
import argparse
import json
from pathlib import Path
from common import read_json, write_json
from instructions import affected_instructions

CLASSES = {'SOURCE_INCOMPLETE', 'REGISTER_OR_INSTRUCTION_SELECTION', 'SIGNEDNESS_OR_PROMOTION',
           'FLOAT_OR_X87_SHAPE', 'ALIGNMENT_OR_PADDING', 'SAME_CU_CALL_LAYOUT', 'STATIC_DATA_LAYOUT',
           'RELOCATION_OR_LITERAL_LAYOUT', 'COMMON_BSS_LAYOUT', 'SOURCE_CONTROL_FLOW_SHAPE', 'UNKNOWN_SUPERVISOR', 'COMPILER_CONTEXT_DEPENDENCY', 'STACK_FRAME_LAYOUT', 'INSTRUCTION_ORDER', 'LITERAL_CONTENT_DIFFERENCE', 'SYMBOLIC_REFERENCE_DIFFERENCE', 'EXACT'}


def classify(row):
    if row['status'] == 'FUNCTION_MATCH':
        return 'EXACT'
    if row.get('tail_jump_layout'): return 'SAME_CU_CALL_LAYOUT'
    if any(d['classification']=='SYMBOLIC_REFERENCE_DIFFERENCE' for d in row.get('reference_diagnostics',[])): return 'SYMBOLIC_REFERENCE_DIFFERENCE'
    if any(d['classification']=='LITERAL_CONTENT_DIFFERENCE' for d in row.get('literal_diagnostics',[])): return 'LITERAL_CONTENT_DIFFERENCE'
    if row.get('compiler_context'): return 'COMPILER_CONTEXT_DEPENDENCY'
    if row['status'] == 'MISSING':
        return 'SOURCE_INCOMPLETE'
    if (row.get('frame_layout') or {}).get('first_mismatch_is_frame_allocation'): return 'STACK_FRAME_LAYOUT'
    if (row.get('instruction_order') or {}).get('all_other_resolved_bytes_equal'): return 'INSTRUCTION_ORDER'
    if row.get('signedness', {}).get('instruction_differences'):
        return 'SIGNEDNESS_OR_PROMOTION'
    relocs = [r for r in row.get('relocations', []) if not r.get('equal')]
    # Relocation hypotheses apply only when all non-relocation bytes are proven equal.
    if row.get('body_shape_equal', row.get('masked_equal')):
        symbols = {r.get('symbol') for r in relocs}
        if symbols and symbols <= {'.bss'}:
            return 'COMMON_BSS_LAYOUT'
        if symbols and symbols <= {'.data'}:
            return 'STATIC_DATA_LAYOUT'
        return 'RELOCATION_OR_LITERAL_LAYOUT'
    diffs = row.get('difference_offsets', [])
    if row.get('candidate_size') == row.get('original_size') and not relocs and diffs:
        if row.get('register_only_instruction_shape'):
            return 'REGISTER_OR_INSTRUCTION_SELECTION'
        affected = affected_instructions(row)
        if any(i['mnemonic'].startswith('f') for i in affected):
            return 'FLOAT_OR_X87_SHAPE'
        if any(i['mnemonic'].startswith('j') for i in affected):
            return 'SOURCE_CONTROL_FLOW_SHAPE'
        if len(affected) <= 4:
            return 'REGISTER_OR_INSTRUCTION_SELECTION'
    pair=row.get('first_instruction_pair',{})
    old,new=pair.get('original'),pair.get('candidate')
    if old and new:
        if old['mnemonic'].startswith('f') or new['mnemonic'].startswith('f'):
            return 'FLOAT_OR_X87_SHAPE'
        if old['mnemonic'].startswith('j') or new['mnemonic'].startswith('j'):
            return 'SOURCE_CONTROL_FLOW_SHAPE'
        if old['mnemonic']==new['mnemonic'] and old['mnemonic'] in ('mov','lea','add','sub','test','cmp'):
            return 'REGISTER_OR_INSTRUCTION_SELECTION'
    # A size delta alone does not establish padding, missing source, or control flow.
    return 'UNKNOWN_SUPERVISOR'


def workflow(row):
    if row.get('tail_jump_layout'):
        return {'state':'BODY_MATCH_LAYOUT_BLOCKED','difference_class':'SAME_CU_CALL_LAYOUT','body_edit_allowed':False,
                'reason':'Exact independently resolved prefix and identical terminal same-CU JMP target; only a range-forced short/near encoding differs. Raw function bytes and sizes do not match.'}
    if row['status']!='FUNCTION_MATCH' and row.get('compiler_context'):
        return {'state':'SOURCE_DIFFER','difference_class':'COMPILER_CONTEXT_DEPENDENCY','body_edit_allowed':False,'reason':'Route compiler-context sensitivity to supervisor; no body or layout match is claimed.'}
    if row['status']!='FUNCTION_MATCH' and row.get('reference_source_pattern'):
        return {'state':'SOURCE_DIFFER','difference_class':'SYMBOLIC_REFERENCE_DIFFERENCE','body_edit_allowed':True,
                'reason':'A regenerated compiler-mapped assignment recipe satisfies the recorded declaration/reference prerequisites. Only a bounded experiment is authorized; no layout or match proof is claimed.'}
    if row['status']!='FUNCTION_MATCH' and any(d['classification']=='SYMBOLIC_REFERENCE_DIFFERENCE' for d in row.get('reference_diagnostics',[])):
        return {'state':'SOURCE_DIFFER','difference_class':'SYMBOLIC_REFERENCE_DIFFERENCE','body_edit_allowed':False,
                'reason':'Aligned scalar references select different named global/field paths. Resolve the recorded declaration/reference prerequisites before body-only grinding; no layout-only proof is claimed.'}
    if row['status']!='FUNCTION_MATCH' and any(d['classification']=='LITERAL_CONTENT_DIFFERENCE' for d in row.get('literal_diagnostics',[])):
        return {'state':'SOURCE_DIFFER','difference_class':'LITERAL_CONTENT_DIFFERENCE','body_edit_allowed':True,
                'reason':'Aligned reference instructions address different literal content. Masked body equality does not prove correct source or layout-only blocking.'}
    proven = row.get('relocation_resolved_equal') and row.get('instruction_boundaries_verified') and row['status'] == 'FUNCTION_MATCH'
    displaced = [t for t in row.get('direct_transfers', []) if not t.get('layout_operand_equal', True)]
    if proven and displaced:
        return {'state': 'BODY_MATCH_LAYOUT_BLOCKED', 'difference_class': 'SAME_CU_CALL_LAYOUT',
                'body_edit_allowed': False, 'reason': 'Every function byte equals after independent relocation/target resolution; decoded same-CU displacement depends on other function placement.'}
    return {'state': 'FUNCTION_MATCH' if row['status'] == 'FUNCTION_MATCH' else 'MISSING' if row['status'] == 'MISSING' else 'CODEGEN_SIMILAR' if row.get('body_shape_equal',row.get('masked_equal')) else 'SOURCE_DIFFER',
            'difference_class': classify(row), 'body_edit_allowed': row['status'] not in ('FUNCTION_MATCH', 'MISSING') and not row.get('body_shape_equal',row.get('masked_equal')),
            'reason': 'Proof verdict retained separately; unresolved ownership never proves layout-only equality.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report', type=Path)
    ap.add_argument('--output', type=Path)
    a = ap.parse_args()
    report = read_json(a.report)
    result = {'report': str(a.report), 'functions': [{'name': row['name'], 'proof_status': row['status'], **workflow(row)} for row in report['functions']]}
    if a.output:
        write_json(a.output, result)
    else:
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
