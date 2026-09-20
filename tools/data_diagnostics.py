"""Typed initializer differences and symbolic dependencies; never function match proof."""
import struct
from functools import lru_cache
from common import ROOT,identity
from binary import Binary
from type_graph import graph
from dwarf_layout import layout,locate,reference


@lru_cache(maxsize=1)
def original_globals():
    g=graph(); rows=[]
    for d in g.dies.values():
        if d['tag']!='DW_TAG_variable' or d.get('address') is None or not d.get('name'): continue
        if g.dies.get(d.get('parent'),{}).get('tag')!='DW_TAG_compile_unit': continue
        shape=layout(g,d.get('type_ref'))
        if shape.get('size'): rows.append({'name':d['name'],'address':d['address'],'layout':shape,'die':d['offset']})
    return rows


def original_reference(address,exe):
    hits={}
    for variable in original_globals():
        delta=address-variable['address']
        if not 0<=delta<variable['layout']['size']: continue
        # A named COFF base must independently confirm the original global.
        symbols=[s for s in exe.symbols if s['name']=='_'+variable['name'] and s.get('va')==variable['address']]
        if len(symbols)!=1: continue
        field=reference(variable['layout'],delta,variable['name'])
        if field:
            value={**field,'root':variable['name'],'root_va':variable['address'],'root_die':variable['die'],'root_offset':delta}
            hits[(value['expression'],value['root_va'],value['size'],value['type'])]=value
    return next(iter(hits.values())) if len(hits)==1 else None


def candidate_reference(symbol,addend,owners,globals_):
    if symbol['name'].startswith('.'):
        hits=[o for o in owners if o.get('section_index')==symbol['section'] and o.get('size') and
              o.get('scope') in (['GLOBAL'],('GLOBAL',)) and o['candidate_offset']<=addend<o['candidate_offset']+o['size']]
        if len(hits)!=1: return None
        root=hits[0]['name']; offset=addend-hits[0]['candidate_offset']
    else:
        if not symbol['name'].startswith('_') or '.' in symbol['name']: return None
        root=symbol['name'][1:]; offset=addend-(symbol['value'] if symbol['section']>0 else 0)
    declarations=[g for g in globals_ if g['name']==root]
    if len(declarations)!=1: return None
    field=reference(declarations[0]['layout'],offset,root)
    return {**field,'root':root,'root_offset':offset} if field else None


def capture_snapshot(report):
    path=report['build']['command'][-1]
    if identity(path)!=report['build']['object']: raise ValueError('Data diagnostics require the receipt object; fresh-verify '+report['build']['target'])
    obj=Binary(path)
    sections={str(s['index']):obj.section_bytes(s).hex() for s in obj.sections if s['name'] in ('.data','.rdata')}
    relocations=[{**r,'symbol':{k:obj.by_index[r['symbol_index']][k] for k in ('name','section','value')}}
                 for r in obj.relocations if str(r['section']) in sections]
    if identity(path)!=report['build']['object']: raise ValueError('Object changed during data snapshot')
    return {'schema':1,'object':report['build']['object'],'sections':sections,'relocations':relocations}


def diagnose(report):
    snapshot=report['data_snapshot']; exe=Binary(ROOT/'assets/icytower15.exe'); g=graph(); rows=[]
    owners=report.get('object_ownership',{}); all_owners=owners.get('accepted',[])+owners.get('rejected',[])
    globals_=report['candidate_debug']['globals']
    for owner in owners.get('rejected',[]):
        if owner['reason'] not in ('Initialized object bytes differ after independent relocation resolution','Initializer target not independently resolved'): continue
        old=g.dies[owner['original_die']]; shape=layout(g,old['type_ref']); size=owner['size']
        start=owner['candidate_offset']
        content=bytearray(bytes.fromhex(snapshot['sections'][str(owner['section_index'])])[start:start+size]); reference_bytes=exe.at_va(owner['original_va'],size)
        known={r['object_offset']:r for r in owner.get('initializer_relocations',[])}; unknown=set(); relocations={}; errors=[]; occupied=set()
        for relocation in snapshot['relocations']:
            if relocation['section']!=owner['section_index'] or not start<=relocation['offset']<start+size: continue
            offset=relocation['offset']-start; record=known.get(offset); symbol=relocation['symbol']
            slots=set(range(offset,min(offset+4,size)))
            if relocation['type']!=6 or offset+4>size or occupied.intersection(slots):
                errors.append({'offset':offset,'reason':'Unsupported, boundary-crossing or overlapping initializer relocation'})
                unknown.update(slots); occupied.update(slots); continue
            occupied.update(slots)
            addend=struct.unpack_from('<I',content,offset)[0]
            relocations[offset]={'symbol':symbol['name'],'addend':addend,'candidate_reference':candidate_reference(symbol,addend,all_owners,globals_)}
            if record and record.get('target_va') is not None: struct.pack_into('<I',content,offset,record['target_va'])
            else: unknown.update(range(offset,offset+4))
        differences=[n for n,(a,b) in enumerate(zip(content,reference_bytes)) if a!=b and n not in unknown]
        fields={}
        for offset in differences+sorted(unknown):
            field=locate(shape,offset,owner['name'])
            if field: fields[field['offset']]=field
        details=[]
        for offset,field in sorted(fields.items()):
            item=dict(field); end=offset+field['size']; unresolved=bool(unknown.intersection(range(offset,end)))
            item.update(original_hex=reference_bytes[offset:end].hex(),candidate_hex=None if unresolved else content[offset:end].hex(),unresolved=unresolved)
            if field['kind']=='pointer_type' and field['size']==4:
                address=struct.unpack_from('<I',reference_bytes,offset)[0]
                expected=original_reference(address,exe); observed=relocations.get(offset,{})
                item.update(original_value=address,expected_reference=expected,**observed)
                current=observed.get('candidate_reference')
                same=bool(expected and current and (expected['root'],expected['root_offset'])==(current['root'],current['root_offset']))
                item['classification']='OWNER_CONTENT_DEPENDENCY' if unresolved and same else 'SYMBOLIC_POINTER_DIFFERENCE' if not unresolved and expected and current and not same else 'UNKNOWN_SUPERVISOR'
                if expected:
                    declared=[v for v in globals_ if v['name']==expected['root']]
                    counterpart=reference(declared[0]['layout'],expected['root_offset'],expected['root']) if len(declared)==1 else None
                    item['candidate_target_path_agrees']=bool(counterpart and all(counterpart.get(k)==expected.get(k) for k in ('expression','offset','size','kind','type')))
            details.append(item)
        rows.append({'name':owner['name'],'scope':owner['scope'],'original_die':owner['original_die'],'section_index':owner['section_index'],
                     'candidate_offset':start,'size':size,'reason':owner['reason'],'mismatch_byte_count':len(differences),
                     'unresolved_byte_count':len(unknown),'errors':errors,'fields':details})
    return {'schema':1,'object':report['build']['object'],'objects':rows,
            'limit':'Typed byte paths and symbolic dependencies are diagnostics. Only fresh independent full initializer comparison grants ownership.'}
