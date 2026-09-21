"""Bounded caller-only prototypes using visible or newly included canonical types."""
import re
from common import ROOT,read_json,identity
from source_scope import sanitized


def plan(row,ledger):
    from interface_tasks import signature,BUILTINS,prototype,declaration_site,patch_text,affected_targets
    from interfaces import split_params,parameter_type
    from type_graph import graph
    old=row['historical']
    if len({signature(r) for r in old})!=1: raise ValueError('Conflicting historical interfaces')
    expected=old[0];name=row['function']
    if expected.get('calling_convention') is not None or expected.get('variadic'): raise ValueError('Typed prototype needs a fixed default-C interface')
    if not set(re.findall(r'[A-Za-z_]\w*',expected['return_type']))<=BUILTINS: raise ValueError('Typed return repair is not supported')
    names=set()
    for parameter in expected['parameter_types']:
        tokens=set(re.findall(r'[A-Za-z_]\w*',parameter))-BUILTINS
        if not tokens: continue
        match=re.fullmatch(r'(?:const )?([A-Za-z_]\w*)\*',parameter)
        if not match or match[1] not in graph().game_types: raise ValueError('Only single pointers to generated historical types are supported')
        names.add(match[1])
    if not names: raise ValueError('No canonical pointer type prerequisite')
    headers={n:'include/recovered/'+n+'.h' for n in names}
    if any(not (ROOT/p).is_file() for p in headers.values()): raise ValueError('Generated type header unavailable')
    patches={};texts={};proof_headers={}
    for declaration in row['candidate_declarations']:
        actual=(declaration.get('canonical_return_type',declaration['return_type']),tuple(declaration.get('canonical_parameter_types',declaration['parameter_types'])))
        issues=[x for x in row.get('type_layout_issues',[]) if x['cu']==declaration['cu'] and x['file']==declaration['file'] and x['line']==declaration['line']]
        if actual==signature(expected):
            if issues: raise ValueError('Already named type has unresolved or conflicting layout')
            continue
        if declaration['kind'] not in ('IC','NC','OC'): raise ValueError('Typed repair cannot change a function definition')
        if declaration['return_type']!=expected['return_type']: raise ValueError('Return type change is not a caller-only typed parameter repair')
        if any(x['status']!='UNAVAILABLE' or x['candidate_type'] not in ('void','/*???*/') for x in issues): raise ValueError('Existing aggregate conflicts require a separate repair')
        file=declaration['file']
        if not file.startswith('src/') or declaration['cu']!=file: raise ValueError('Typed repair requires a CU-local declaration')
        if declaration['cu'] not in ledger: raise ValueError('Owning CU proof is unavailable')
        report=read_json(ROOT/ledger[declaration['cu']]['verified_report'])
        text=texts.setdefault(file,(ROOT/file).read_bytes().decode('cp1252'));newline='\r\n' if '\r\n' in text else '\n'
        prefix=''
        for type_name,header in sorted(headers.items()):
            if header not in report['build']['local_inputs']:
                for source in report['build']['local_inputs']:
                    if source.startswith(('src/','include/')) and re.search(r'\b'+re.escape(type_name)+r'\b',sanitized((ROOT/source).read_bytes().decode('cp1252'))):
                        raise ValueError('Canonical type name already occurs outside its generated header: '+type_name)
            prefix+='#include "recovered/'+type_name+'.h"'+newline
            proof_headers[header]=identity(ROOT/header)
        insertion=len(prefix) if text.startswith(prefix) else 0
        if insertion: prefix=''
        if declaration['kind']=='IC':
            prefix+=prototype(expected,name)+newline
            edits=[]
        else:
            pos,start,end=declaration_site(text,name,declaration['line'])
            if not sanitized(text[end+1:]).lstrip().startswith(';'): raise ValueError('Caller declaration is not a plain prototype')
            parts=split_params(text[start:end]);actual_types=declaration['parameter_types']
            if actual_types==['/*???*/']:
                if text[start:end].strip(): raise ValueError('Old-style argument text is not empty')
            else:
                if len(parts)!=len(expected['parameter_types']): raise ValueError('Typed repair cannot change parameter count')
                for part,actual_type,wanted in zip(parts,actual_types,expected['parameter_types']):
                    if parameter_type(part)!=actual_type: raise ValueError('Compiler/source parameter disagreement')
                    if actual_type!=wanted and not (actual_type=='void*' and any(wanted in (n+'*','const '+n+'*') for n in names)):
                        raise ValueError('Only void-pointer placeholders can become named pointers')
            replacement=', '.join(expected['parameter_types'] or ['void'])
            edits=[{'start':start,'end':end,'before':text[start:end],'after':replacement,'reason':'Restore complete historical caller prototype'}]
        if prefix: edits.append({'start':insertion,'end':insertion,'before':'','after':prefix,'reason':'Introduce generated historical type visibility and caller prototype'})
        for edit in edits:
            edit.update(file=file,line=declaration['line']);key=(file,edit['start'],edit['end'])
            if key in patches and patches[key]!=edit: raise ValueError('Conflicting typed declaration edits')
            patches[key]=edit
    if not patches: raise ValueError('No bounded typed caller edits')
    changes=sorted(patches.values(),key=lambda e:(e['file'],e['start']));sources=sorted(texts)
    for source in sources: patch_text(texts[source],[e for e in changes if e['file']==source])
    targets=affected_targets(ledger,sources)
    return {'changes':changes,'sources':sources,'source_identities':{p:identity(ROOT/p) for p in sources},
            'affected_targets':targets,'required_generated_headers':proof_headers,'expected_prototype':prototype(expected,name),
            'difficulty':'CHEAP','priority':250-min(len(targets),10)*3,'state':'INTERFACE_REPAIR','status':'INTERFACE_CONFLICT',
            'difference_class':'INTERFACE_DECLARATION','typed_caller_repair':True,
            'reason':'Unique historical pointer interface; generated type visibility plus caller-only prototype edits. Fresh layout agreement and emission preservation remain mandatory.'}
