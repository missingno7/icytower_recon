"""Compare compiler-recorded declarations across CUs and historical DWARF interfaces."""
import re
from collections import defaultdict
from common import ROOT, read_json, write_json, check_json
from type_graph import graph


def split_params(text):
    result=[]; start=0; depth=0
    for pos,c in enumerate(text):
        depth += (c in '([')-(c in ')]')
        if c==',' and depth==0: result.append(text[start:pos].strip()); start=pos+1
    tail=text[start:].strip()
    if tail and tail!='void': result.append(tail)
    return result


def normalize(text):
    text=re.sub(r'\b(extern|static|inline|__inline__)\b','',text)
    text=re.sub(r'\s+',' ',text).strip()
    return re.sub(r'\s*([*(),\[\]])\s*',r'\1',text)


def parameter_type(text):
    text=re.sub(r'(\*\s*)[A-Za-z_]\w*(\s*\))',r'\1\2',text)
    match=re.search(r'([A-Za-z_]\w*)\s*$',text)
    if match:
        tail=match[1]; before=text[:match.start()].strip()
        if before and tail not in ('int','char','short','long','double','float','void','const','volatile','unsigned','signed') and not before in ('struct','union','enum'):
            text=text[:match.start()]
    return normalize(text)


def declarations(aux):
    for line in aux.splitlines():
        match=re.match(r'/\* (.*?):(\d+):([A-Z]+) \*/\s*(.*?)\s+(\w+)\s*\((.*)\);',line)
        if not match: # return pointer can touch function name
            match=re.match(r'/\* (.*?):(\d+):([A-Z]+) \*/\s*(.*?\*)(\w+)\s*\((.*)\);',line)
        if not match: continue
        params=match[6].split(');',1)[0]
        yield {'file':match[1].replace('\\','/'),'line':int(match[2]),'kind':match[3], 'name':match[5],
               'return_type':normalize(match[4]),'parameter_types':[parameter_type(p) for p in split_params(params)],
               'declaration':line.split('*/',1)[1].split(';',1)[0].strip()+';'}


def collect_interfaces(ledger):
    g=graph(); originals=defaultdict(list); candidate=defaultdict(list)
    for unit in read_json(ROOT/'src/units.json'):
        for f in unit['functions']:
            d=g.dies.get(f.get('die'))
            if not d: continue
            originals[f['name']].append({'cu':unit['source'],'return_type':normalize(g.declaration(d.get('type_ref'))),
                'parameter_types':[normalize(g.declaration(g.dies[p].get('type_ref'))) for p in f.get('parameters',[])],
                'variadic':any(c['tag']=='DW_TAG_unspecified_parameters' for c in g.children[d['offset']]),
                'calling_convention':d['resolved'].get('DW_AT_calling_convention'),'die':d['offset']})
    for source,entry in ledger.items():
        if not entry.get('verified_report'): continue
        report=read_json(ROOT/entry['verified_report'])
        from type_aliases import canonical_aliases,annotate_declaration,layout_checks
        aliases=canonical_aliases(report)
        for d in declarations(report.get('interfaces_aux','')):
            d=annotate_declaration(d,aliases)
            if d['name'] in originals and (d['file'].startswith('src/') or d['file'].startswith('include/')):
                checked=layout_checks(d,originals[d['name']][0],report) if len(originals[d['name']])==1 else []
                candidate[d['name']].append({**d,'cu':source,'game_type_layouts':checked})
    rows=[]; conflicts=[]
    for name,old in sorted(originals.items()):
        current=candidate[name]
        def sig(d): return (d.get('canonical_return_type',d['return_type']),tuple(d.get('canonical_parameter_types',d['parameter_types'])))
        expected={sig(d) for d in old}
        actual={sig(d) for d in current}
        # Variadic marker is part of the compiler declaration's argument list.
        expected={ (d['return_type'],tuple(d['parameter_types'])+(('...',) if d['variadic'] else ())) for d in old }
        layout_issues=[dict(x,cu=d['cu'],file=d['file'],line=d['line']) for d in current for x in d.get('game_type_layouts',[]) if x['status']!='AGREE']
        conflict=bool(actual-expected) or len(actual)>1 or len(expected)>1 or any(x['status']=='MISMATCH' for x in layout_issues)
        incomplete=bool(layout_issues) and not conflict
        row={'function':name,'historical':old,'candidate_declarations':current,
             'status':'CONFLICT' if conflict else 'NO_CANDIDATE' if not current else 'TYPE_EVIDENCE_INCOMPLETE' if incomplete else 'AGREE',
             'type_layout_issues':layout_issues,
             'difficulty':'SUPERVISOR' if conflict or incomplete else None,
             'limit':'Explicit compiled aliases to included generated headers normalize only after complete DWARF layout equality. Same-named game aggregates are also checked by full layout. External library types retain declaration-spelling checks; declaration agreement is not a function or universal type proof.'}
        rows.append(row)
        if conflict or incomplete: conflicts.append(row)
    return rows,conflicts


def publish_interfaces(ledger,check=False):
    rows,conflicts=collect_interfaces(ledger)
    from interface_tasks import plan_interface
    task_cards=[]
    emit=check_json if check else write_json
    for row in rows:
        if row['status'] in ('CONFLICT','TYPE_EVIDENCE_INCOMPLETE'):
            card=plan_interface(row,ledger)
            row['difficulty']=card['difficulty']
            task_cards.append(card)
        else:
            card={'schema':1,'task_kind':'INTERFACE','function':row['function'],'status':row['status'],'body_edit_allowed':False,'historical':row['historical'],'changes':[]}
        emit(ROOT/'docs/current/interfaces'/(row['function']+'.json'),card)
    result={'schema':2,'tasks':[{k:c.get(k) for k in ('function','source','sources','difficulty','priority','reason','begin_command','verification_command','promotion_command','state','status','body_edit_allowed','difference_class')} | {'task_kind':'INTERFACE','candidate_card':'docs/current/interfaces/'+c['function']+'.json','size':0} for c in task_cards],'authority':'DWARF plus historical GCC -aux-info for every included maintained declaration',
            'interfaces':rows,'conflicts':conflicts}
    (check_json if check else write_json)(ROOT/'docs/current/interface-conflicts.json',result)
    return result


if __name__=='__main__':
    print(len(publish_interfaces(read_json(ROOT/'src/recovery.json'))['conflicts']),'interface conflicts')
