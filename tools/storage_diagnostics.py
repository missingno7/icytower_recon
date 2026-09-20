"""Complete static-storage declaration census. Diagnostics never resolve relocations."""
import re
from collections import Counter
from functools import lru_cache
from common import ROOT,read_json,write_json,check_json
from binary import Binary
from type_graph import graph,number
from dwarf_layout import layout
from data_owners import scope_identity


def storage_rows(g,binary,source_tables=None,cu_path=None):
    rows=[]; sections={s['index']:s for s in binary.sections}
    for d in g.dies.values():
        if d['tag']!='DW_TAG_variable' or not d.get('name') or d.get('address') is None: continue
        if cu_path and g.dies[d['cu']]['name']!=cu_path: continue
        scope=scope_identity(g,d)
        if scope is None: scope=('UNRESOLVED_LEXICAL_SCOPE',d.get('parent'))
        pattern=re.compile(r'^_'+re.escape(d['name'])+r'(?:\.\d+)?$')
        symbols=[s for s in binary.symbols if s['storage_class'] in (2,3) and pattern.fullmatch(s['name']) and
                 ((s['section']>0 and s.get('va',s['value'])==d['address']) or
                  (not binary.pe and s['section']==0 and s['value']>0 and s['storage_class']==2))]
        table=(source_tables or {}).get(number(g.dies[d['cu']]['resolved'].get('DW_AT_stmt_list')),{})
        file=table.get('files',{}).get(number(d['resolved'].get('DW_AT_decl_file')),{})
        coff=[{k:s[k] for k in ('name','section','value','storage_class','index')} for s in symbols]
        for s in coff:
            s['section_name']=sections[s['section']]['name'] if s['section']>0 else 'COMMON'
        row={'name':d['name'],'die':d['offset'],'scope':list(scope),'type':g.declaration(d.get('type_ref')),
             'size':g.size(d.get('type_ref')),'layout':layout(g,d.get('type_ref')),'coff':coff,
             'declaration_line':number(d['resolved'].get('DW_AT_decl_line')),'declaration_file':file.get('path') or d.get('decl_file_path')}
        # A relocatable DW_OP_addr can encode a common-size addend, never a VA.
        if binary.pe: row['historical_va']=d['address']
        elif len(coff)==1 and coff[0]['section']>0: row['candidate_offset']=coff[0]['value']
        if len(coff)==1:
            row['section']=coff[0]['section_name']
            if binary.pe and row['section'] in ('.data','.rdata') and row['size']:
                row['initial_value_prefix']=binary.at_va(d['address'],min(64,row['size'])).hex()
        rows.append(row)
    return rows


@lru_cache(maxsize=32)
def historical_rows(cu):
    return storage_rows(graph(),Binary(ROOT/'assets/icytower15.exe'),cu_path=cu)


def correlate(original,candidate,owners):
    """Never pair by address, similar spelling, raw bytes or layout alone."""
    result=[]; used=set()
    for old in original:
        matches=[v for v in candidate if v['name']==old['name'] and v['scope']==old['scope']]
        if not matches: matches=[v for v in candidate if v['name']==old['name']]
        new=matches[0] if len(matches)==1 else None
        if new: used.add(new['die'])
        proof=[v for v in owners.get('accepted',[]) if v['original_die']==old['die']]
        reasons=[v['reason'] for v in owners.get('rejected',[]) if v.get('original_die')==old['die']]
        if len(proof)==1: state='EXACT_OWNER'
        elif not matches: state='CANDIDATE_DECLARATION_MISSING'
        elif len(matches)!=1: state='AMBIGUOUS_CANDIDATE_DECLARATION'
        elif old['scope']!=new['scope']: state='SOURCE_SCOPE_DIFFERS'
        elif old['layout']!=new['layout']: state='STORAGE_TYPE_DIFFERS'
        elif len(new['coff'])!=1 or len(old['coff'])!=1: state='COFF_OWNER_UNRESOLVED'
        elif new.get('section')=='COMMON': state='COMMON_DECLARATION_AGREES'
        elif old.get('section')!=new.get('section'): state='STORAGE_SECTION_DIFFERS'
        else: state='INITIALIZER_OR_OWNER_UNPROVEN'
        result.append({'name':old['name'],'original':old,'candidate':new,'state':state,'owner_rejection':reasons,
                       'candidate_alternatives':[{'die':v['die'],'scope':v['scope'],'type':v['type']} for v in matches] if len(matches)>1 else []})
    return {'objects':result,'unpaired_candidates':[v for v in candidate if v['die'] not in used],
            'counts':dict(sorted(Counter(r['state'] for r in result).items())),
            'limit':'Declaration correspondence and ownership gaps only. Common declarations do not prove allocation order. Missing names are never silently paired by similar content.'}


def diagnose(report):
    return correlate(historical_rows(report['historical_cu']),report['candidate_debug']['storage'],report.get('object_ownership',{}))


def publish_storage(ledger,check=False):
    emit=check_json if check else write_json; index=[]
    for source,entry in ledger.items():
        report=read_json(ROOT/entry['verified_report']); target=report['build']['target']; detail=diagnose(report)
        path=ROOT/'docs/current/storage'/(target+'.json')
        emit(path,{'source':source,'target':target,**detail})
        for item in detail['objects']:
            emit(ROOT/'docs/current/storage'/target/(str(item['original']['die'])+'.json'),{'source':source,'target':target,**item})
        index.append({'source':source,'target':target,'counts':detail['counts'],'candidate_card':path.relative_to(ROOT).as_posix()})
    emit(ROOT/'docs/current/storage-status.json',{'authority':'Original DWARF and source-current compiled DWARF/COFF; exact ownership still comes exclusively from the strict verifier','units':index})


def function_storage(report,name,references):
    names={r.get('symbol') for r in references}; result=[]
    for item in diagnose(report)['objects']:
        old=item['original']
        if old['name'] not in names and old['scope']!=['FUNCTION_STATIC',name]: continue
        if item['state']=='EXACT_OWNER': continue
        new=item['candidate'] or {}
        result.append({'name':old['name'],'state':item['state'],'original_scope':old['scope'],'candidate_scope':new.get('scope'),
                       'original_type':old['type'],'candidate_type':new.get('type'),
                       'candidate_card':'docs/current/storage/'+report['build']['target']+'/'+str(old['die'])+'.json'})
    return result
