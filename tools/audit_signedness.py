"""Function-scoped signedness evidence; instruction correlations are hypotheses."""
import argparse
import json
import re
from common import ROOT, write_json

PAIRS = [('movsbl','movzbl'), ('movswl','movzwl'), ('movsbw','movzbw'), ('sar','shr'),
         ('sarl','shrl'), ('jl','jb'), ('jle','jbe'), ('jg','ja'), ('jge','jae')]


def type_differences(original,candidate):
    """Unique-name builtin declarations only; shadowed locals and aliases are not guessed."""
    result=[]
    words={'signed','unsigned','char','short','int','long','const','volatile','float','double','void'}
    names={v.get('name') for v in original}&{v.get('name') for v in candidate}-{None}
    for name in sorted(names):
        old=[v for v in original if v.get('name')==name]; new=[v for v in candidate if v.get('name')==name]
        if len(old)!=1 or len(new)!=1: continue
        old,new=old[0],new[0]
        if old['type']==new['type']: continue
        if set(re.findall(r'[A-Za-z_]\w*',old['type']+' '+new['type']))-words: continue
        result.append({'variable':name,'original_type':old['type'],'candidate_type':new['type'],
                       'original_die':old['die'],'candidate_die':new['die'],
                       'confidence':'UNIQUE_NAME_BUILTIN_DECLARATIONS','limit':'Type evidence only; not a demonstrated instruction mismatch cause.'})
    return result


def analyze(parameters, locals_, original, candidate, source_text='',location_context=None):
    old = [i['mnemonic'] for i in original]
    new = [i['mnemonic'] for i in candidate]
    differences = []
    for signed, unsigned in PAIRS:
        if (old.count(signed), old.count(unsigned)) != (new.count(signed), new.count(unsigned)) and any(x in old+new for x in (signed,unsigned)):
            differences.append({'signed_instruction': signed, 'unsigned_instruction': unsigned,
                                'original_counts': [old.count(signed),old.count(unsigned)],
                                'candidate_counts': [new.count(signed),new.count(unsigned)]})
    count_differences=differences
    differences=[]
    if original and candidate:
        old_offsets={i['address']-original[0]['address']:i for i in original}
        for i in candidate:
            offset=i['address']-candidate[0]['address']; previous=old_offsets.get(offset)
            if not previous: continue
            for signed,unsigned in PAIRS:
                if (previous['mnemonic'],i['mnemonic']) in ((signed,unsigned),(unsigned,signed)):
                    before=previous['assembly'].split(None,1)[1:]
                    after=i['assembly'].split(None,1)[1:]
                    equivalent=before==after
                    if previous['mnemonic'].startswith('j'):
                        old_target=re.match(r'\S+\s+([0-9a-f]+)',previous['assembly'])
                        new_target=re.match(r'\S+\s+([0-9a-f]+)',i['assembly'])
                        equivalent=bool(old_target and new_target and int(old_target[1],16)-original[0]['address']==int(new_target[1],16)-candidate[0]['address'])
                    if equivalent:
                        differences.append({'function_offset':offset,'original':previous,'candidate':i,'confidence':'ALIGNED_SAME_OPERANDS'})
    if location_context:
        from dwarf_locations import annotate
        for difference in differences:
            for side in ('original','candidate'):
                if side in location_context:
                    difference[side]=annotate([difference[side]],**location_context[side])[0]
            difference['attribution']='Live DWARF locations associate variables with operands; this does not prove the source cause.'
    variables = [v for v in parameters+locals_ if re.search(r'\b(char|short|int|long)\b',v['type'])]
    type_conflicts=type_differences(parameters+locals_,location_context.get('candidate',{}).get('variables',[])) if location_context else []
    return {'variables': variables, 'instruction_differences': differences, 'instruction_count_hypotheses':count_differences,
            'declaration_differences':type_conflicts,
            'cast_chains': re.findall(r'(?:\(\s*(?:(?:unsigned|signed|const)\s+)*(?:char|short|int|long|float|double)\s*\*?\s*\)\s*)+',source_text),
            'shifts': [l.strip() for l in source_text.splitlines() if '>>' in l or '<<' in l],
            'confidence': 'HYPOTHESIS' if differences else 'NO_INSTRUCTION_EVIDENCE',
            'limit': 'DWARF variable types and function instruction counts; variable-to-instruction attribution requires location evidence. Char encoding is available through type DIE.'}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('target',nargs='?')
    ap.add_argument('function',nargs='?')
    ap.add_argument('--output')
    a=ap.parse_args()
    paths=(ROOT/'docs/current/functions').rglob('*.json')
    rows=[]
    for p in paths:
        card=json.loads(p.read_text())
        if a.target and card['target']!=a.target: continue
        if a.function and card['function']!=a.function: continue
        rows.append({'source':card['source'],'function':card['function'],**card['signedness']})
    result={'functions':rows}
    if a.output: write_json(a.output,result)
    else: print(json.dumps(result,indent=2))


if __name__=='__main__': main()
