"""Explain fixed-offset relocation failures without inventing original operands.

Diagnostic only: never changes the relocation record or strict match verdict.
"""
from literal_diagnostics import operand_kind
from reference_diagnostics import memory_operand


def mismatch_views(row, original):
    result = []
    base = row.get('candidate_offset', 0)
    old_base = row['va']
    relocations = row.get('relocations', [])
    for relocation in relocations:
        if relocation.get('equal'):
            continue
        offset = relocation['function_offset']
        context = {'state': 'UNALIGNED_BYTE_WINDOW',
                   'original_value_is_operand': False,
                   'reason': 'No matching decoded instruction field at this function offset.',
                   'limit': 'Diagnostic only. Raw original_value is a fixed-offset byte window unless operand alignment is established; never an independent target binding.'}
        item = dict(relocation, comparison_context=context)
        result.append(item)
        candidates = [i for i in row.get('instructions', [])
                      if i['address']-base <= offset < i['address']-base+len(bytes.fromhex(i['bytes']))]
        originals = [i for i in original
                     if i['address']-old_base <= offset < i['address']-old_base+len(bytes.fromhex(i['bytes']))]
        if len(candidates) != 1 or len(originals) != 1:
            continue
        candidate, before = candidates[0], originals[0]
        context.update(candidate_instruction=candidate, original_instruction_at_offset=before)
        at = candidate['address']-base
        raw, old = bytes.fromhex(candidate['bytes']), bytes.fromhex(before['bytes'])
        p = offset-at
        if before['address']-old_base != at or len(raw) != len(old) or p < 1 or p+4 > len(raw):
            continue
        if raw[:p]+raw[p+4:] != old[:p]+old[p+4:]:
            context['reason'] = 'Instruction bytes outside the relocation field differ.'
            continue
        if any(r is not relocation and r['function_offset'] < offset+4 and offset < r['function_offset']+4 for r in relocations):
            context['reason'] = 'Overlapping relocation records; operand interpretation withheld.'
            continue
        kind = None
        if relocation.get('type') == 20 and p == 1 and len(raw) == 5 and raw[0] in (0xe8, 0xe9):
            kind = 'REL32_TRANSFER'
        elif relocation.get('type') == 6:
            kind = 'ABSOLUTE_MEMORY' if memory_operand(raw, p) else 'IMMEDIATE_OR_LITERAL' if operand_kind(raw, p) else None
        if kind is None:
            context.update(state='ALIGNED_FIELD_UNTYPED', reason='Same instruction byte field; this encoding is not supported for operand interpretation.')
            continue
        value = int.from_bytes(old[p:p+4], 'little')
        if value != relocation.get('original_value'):
            context['reason'] = 'Decoded original bytes disagree with the recorded comparison window.'
            continue
        context.update(state='ALIGNED_OPERAND', original_value_is_operand=True,
                       operand_kind=kind, original_operand_value=value,
                       reason='Same decoded instruction extent and encoding outside the supported relocation operand. Ownership and target equality remain separate proofs.')
    return result
