"""Typed named-global reference differences; diagnostics never resolve relocations."""
from functools import lru_cache
from common import ROOT,read_json
from dwarf_layout import reference
from data_diagnostics import original_reference


@lru_cache(maxsize=2048)
def owner_info(die):
    from type_graph import graph
    from build import TARGETS
    g=graph(); node=g.dies[die]
    unit=next((u for u in read_json(ROOT/'src/units.json') if u['cu_die']==node['cu']),None)
    source=unit['source'] if unit else None
    target=next((t for t,c in TARGETS.items() if c['source']==source),None)
    spelling=g.declaration(node.get('type_ref'))
    header=ROOT/'include/recovered'/(spelling+'.h') if spelling.isidentifier() else None
    return {'original_type':spelling,'original_size':g.size(node.get('type_ref')),'owner_source':source,
            'owner_card':'docs/current/storage/'+target+'/'+str(die)+'.json' if target else None,
            'generated_header':header.relative_to(ROOT).as_posix() if header and header.is_file() else None}


def historical_reference(address,exe):
    field=original_reference(address,exe)
    return {**field,**owner_info(field['root_die'])} if field else None


def memory_operand(raw,p):
    # Only decoded absolute 32-bit MOV loads/stores. No SIB, prefixes, LEA,
    # pointer immediates or arithmetic operands are interpreted as scalar access.
    if len(raw)==5 and p==1 and raw[0] in (0xa1,0xa3):
        return 'READ' if raw[0]==0xa1 else 'WRITE'
    if len(raw)==6 and p==2 and raw[0] in (0x8b,0x89) and raw[1]&0xc7==5:
        return 'READ' if raw[0]==0x8b else 'WRITE'
    if len(raw)==10 and p==2 and raw[:2]==b'\xc7\x05': return 'WRITE'
    return None


def counterpart(field,globals_):
    rows=[g for g in globals_ if g['name']==field['root']]
    result={'declaration_count':len(rows),'candidate_type':None,'candidate_size':None,'field':None,'agrees':False}
    if len(rows)!=1: return result
    node=rows[0]['layout']; value=reference(node,field['root_offset'],field['root'])
    result.update(candidate_type=node.get('type'),candidate_size=node.get('size'),field=value)
    result['agrees']=bool(value and all(value.get(k)==field.get(k) for k in ('expression','offset','size','kind','type')))
    return result


def diagnose(row,original,globals_,lookup,line_mappings=(),source=None):
    results=[]; base=row.get('candidate_offset',0)
    original_by_offset={i['address']-row['va']:i for i in original}
    for relocation in row.get('relocations',[]):
        if relocation.get('equal') or relocation.get('type')!=6 or relocation.get('target_va') is None: continue
        if not relocation.get('symbol','').startswith('_') or relocation.get('resolution')!='named symbol': continue
        p=relocation['function_offset']
        hits=[i for i in row.get('instructions',[]) if i['address']-base<=p and p+4<=i['address']-base+len(bytes.fromhex(i['bytes']))]
        if len(hits)!=1: continue
        ins=hits[0]; offset=ins['address']-base; old=original_by_offset.get(offset)
        if not old: continue
        raw=bytes.fromhex(ins['bytes']); before=bytes.fromhex(old['bytes']); operand=p-offset
        access=memory_operand(raw,operand)
        if not access or len(raw)!=len(before) or raw[:operand]+raw[operand+4:]!=before[:operand]+before[operand+4:]: continue
        if any(r is not relocation and r['function_offset']<p+4 and p<r['function_offset']+4 for r in row.get('relocations',[])): continue
        if int.from_bytes(raw[operand:operand+4],'little')!=relocation['addend']: continue
        value=int.from_bytes(before[operand:operand+4],'little')
        if value!=relocation['original_value'] or relocation['resolved_value']!=relocation['target_va']: continue
        expected=lookup(value); current=lookup(relocation['target_va'])
        if not expected or not current or any(f['kind']!='base_type' or f['size']!=4 for f in (expected,current)): continue
        if (expected['root'],expected['root_offset'])==(current['root'],current['root_offset']): continue
        # A scalar operand spelling and its independent named binding must agree.
        if relocation['symbol']!='_'+current['root']: continue
        destination=counterpart(expected,globals_); observed=counterpart(current,globals_)
        skeleton=bool(row.get('body_shape_equal',row.get('masked_equal')) and row.get('instruction_boundaries_verified'))
        item={'function_offset':p,'access':access,'access_bytes':4,'candidate_symbol':relocation['symbol'],
              'candidate_reference':current,'expected_reference':expected,'candidate_declaration':observed,
              'expected_declaration_in_candidate':destination,'candidate_instruction':ins,'original_instruction':old,
              'classification':'SYMBOLIC_REFERENCE_DIFFERENCE' if skeleton else 'ALIGNED_REFERENCE_OBSERVATION',
              'prerequisite':('SOURCE_REFERENCE_REPAIR' if destination['agrees'] and observed['agrees'] else 'OWNER_DECLARATION_REPAIR') if skeleton else 'ESTABLISH_INSTRUCTION_CORRESPONDENCE',
              'body_edit_allowed':False,
              'limit':'Original address identifies a diagnostic typed path. No target binding, body equality or automated source edit is granted.'}
        if not skeleton: item['limit']+=' Whole-function instruction shape differs; correspondence of source operations at this offset is unproved.'
        if source:
            from scheduling_diagnostics import source_rows
            item['candidate_source_lines']=source_rows([ins],line_mappings,source)
        results.append(item)
    return results


def source_pattern(row,text,variables):
    """One plain scalar assignment destination, mapped by compiler lines and DWARF.

    This supplies a bounded source experiment, never a relocation binding.
    Reads, complex lvalues, macros and ambiguous/shadowed names are unsupported.
    """
    import re
    from source_scope import function_span,sanitized
    from literal_diagnostics import patterns as literal_patterns
    refs=row.get('reference_diagnostics',[])
    if row['status']=='FUNCTION_MATCH' or not refs or not row.get('body_shape_equal',row.get('masked_equal')) or not row.get('instruction_boundaries_verified'): return None
    try: lo,hi=function_span(text,row['name'])
    except ValueError: return None
    clean=sanitized(text); changes=[]; occupied=set()
    lines=text.splitlines(keepends=True); starts=[]; offset=0
    for line in lines: starts.append(offset); offset+=len(line)
    for d in refs:
        if d['classification']!='SYMBOLIC_REFERENCE_DIFFERENCE' or d['prerequisite']!='SOURCE_REFERENCE_REPAIR' or d['access']!='WRITE': return None
        old,new=d['candidate_reference'],d['expected_reference']
        if old['expression']!=old['root'] or old['root_offset']!=0: return None
        if not re.fullmatch(r'[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+',new['expression']): return None
        if any(old.get(k)!=new.get(k) for k in ('kind','size','type')) or old.get('size')!=4: return None
        roots={old['root'],new['root']}
        if any(v.get('name') in roots for v in variables): return None
        if any(re.search(r'^\s*#\s*define\s+'+re.escape(root)+r'\b',clean,re.M) for root in roots): return None
        if re.search(r'^\s*#',clean[lo:hi],re.M): return None
        # One bare occurrence ensures no competing store/use shares this mapping.
        if len(re.findall(r'\b'+re.escape(old['root'])+r'\b',clean[lo:hi]))!=1: return None
        mappings=d.get('candidate_source_lines',[])
        if len(mappings)!=1: return None
        mapping=mappings[0]; number=mapping.get('line',0)
        if not 1<=number<=len(lines): return None
        line=lines[number-1]
        if line.rstrip('\r\n')!=mapping.get('text'): return None
        match=re.fullmatch(r'[ \t]*('+re.escape(old['root'])+r')[ \t]*=(?!=)[^;{}\r\n]+;[ \t]*(?:\r?\n)?',line)
        if not match: return None
        start=starts[number-1]+match.start(1); end=start+len(old['root'])
        if not lo<start<end<hi or start in occupied: return None
        occupied.add(start)
        changes.append({'start':start,'end':end,'before':old['root'],'after':new['expression'],
                        'reason':'Compiler-mapped plain assignment selects the wrong evidenced scalar global path; fresh strict verification required.'})
    literals=[d for d in row.get('literal_diagnostics',[]) if d['classification']=='LITERAL_CONTENT_DIFFERENCE']
    if literals:
        patterns=literal_patterns(row,text)
        if len(patterns)!=1: return None
        changes+=patterns[0]['changes']
    changes.sort(key=lambda c:c['start'])
    if any(a['end']>b['start'] for a,b in zip(changes,changes[1:])): return None
    return {'id':'repair_symbolic_assignment','changes':changes,
            'reason':'Typed global paths, whole-function instruction correspondence and a unique compiler-mapped assignment supply one bounded experiment, including independently generated literal fixes. No original operand becomes an acceptance binding.'}
