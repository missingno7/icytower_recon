"""Mechanical declaration work items from historical DWARF and compiler source locations.

Eligible work includes evidenced qualifiers, empty/builtin prototypes, and bounded
caller-only canonical pointer interfaces. Bodies and existing type layouts are untouched.
"""
import re
from pathlib import Path
from common import ROOT, identity, read_json, sha
from interfaces import normalize, parameter_type, split_params
from source_scope import sanitized

BUILTINS={'const','volatile','void','char','signed','unsigned','int','short','long','float','double'}


def signature(row):
    return row['return_type'],tuple(row['parameter_types'])+(('...',) if row.get('variadic') else ())


def builtin_signature(row):
    return set(re.findall(r'[A-Za-z_]\w*',row['return_type']+' '+','.join(row['parameter_types']))) <= BUILTINS


def declaration_site(text, name, line):
    clean=sanitized(text)
    sites=[]
    for m in re.finditer(r'\b'+re.escape(name)+r'\s*\(',clean):
        if clean[:m.start()].count('{')!=clean[:m.start()].count('}'): continue
        first=m.end(); depth=1; end=first
        while end<len(clean) and depth:
            depth+=(clean[end]=='(')-(clean[end]==')'); end+=1
        if depth: continue
        low=clean[:m.start()].count('\n')+1; high=clean[:end].count('\n')+1
        if low<=line<=high:
            sites.append((m.start(),first,end-1))
    if len(sites)!=1: raise ValueError('Compiler declaration location is ambiguous: %s:%d'%(name,line))
    return sites[0]


def prototype(row, name):
    args=list(row['parameter_types'])+(['...'] if row.get('variadic') else [])
    return 'extern '+row['return_type']+' '+name+'('+', '.join(args or ['void'])+');'


def patch_text(text, edits):
    previous=len(text)+1
    for edit in sorted(edits,key=lambda e:e['start'],reverse=True):
        start,end=edit['start'],edit['end']
        if end>previous or text[start:end]!=edit['before']:
            raise ValueError('Overlapping/stale declaration edit')
        text=text[:start]+edit['after']+text[end:]
        previous=start
    return text


def affected_targets(ledger, files):
    targets=[]
    for entry in ledger.values():
        report=read_json(ROOT/entry['verified_report'])
        if set(files)&set(report['build']['local_inputs']): targets.append(report['build']['target'])
    return sorted(targets)


def source_text(file, overrides=None, root=None):
    if overrides is not None and file in overrides: return overrides[file]
    return ((root or ROOT)/file).read_bytes().decode('cp1252')


def text_identity(text):
    raw=text.encode('cp1252')
    return {'size':len(raw),'sha256':sha(raw)}


def plan_interface(row, ledger, source_texts=None):
    name=row['function']; old=row['historical']
    card={'schema':1,'task_kind':'INTERFACE','function':name,'source':old[0]['cu'],
          'body_edit_allowed':False,'difference_class':'INTERFACE_DECLARATION','status':'INTERFACE_CONFLICT',
          'state':'INTERFACE_REPAIR','difficulty':'SUPERVISOR','historical':old,'type_layout_issues':row.get('type_layout_issues',[]),'changes':[],
          'verification_command':'python tools/interface_task.py check '+name,
          'begin_command':'python tools/interface_task.py begin '+name,
          'apply_command':'python tools/interface_task.py apply '+name,
          'promotion_command':'python tools/interface_task.py promote '+name,
          'edit_scope':'Only the exact generated declaration edits. Preserve exact functions, all data/BSS/relocations and layout. Candidate text may only reorder proven independent adjacent register clears; this never proves an original byte match.'}
    if row.get('type_layout_issues'):
        missing=all(x['status']=='UNAVAILABLE' for x in row['type_layout_issues'])
        card.update(status='TYPE_EVIDENCE_INCOMPLETE' if missing else 'TYPE_LAYOUT_CONFLICT',
                    difference_class='TYPE_LAYOUT_INCOMPLETE' if missing else 'TYPE_LAYOUT_CONFLICT',state='TYPE_LAYOUT_BLOCKED')
    try:
        if row.get('type_layout_issues'): raise ValueError('Repair or establish the named aggregate layouts before editing this interface')
        if len({signature(r) for r in old})!=1: raise ValueError('Conflicting historical interfaces')
        expected=old[0]
        if expected.get('calling_convention') is not None: raise ValueError('Calling convention requires explicit supervisor review')
        patches={}; texts={}
        for declaration in row['candidate_declarations']:
            desired=(expected['return_type'],tuple(expected['parameter_types'])+(('...',) if expected.get('variadic') else ()))
            actual=declaration.get('canonical_return_type',declaration['return_type']),tuple(declaration.get('canonical_parameter_types',declaration['parameter_types']))
            if actual==desired: continue
            file=declaration['file']
            if not file.startswith(('src/','include/')): raise ValueError('External declaration cannot be changed')
            text=texts.setdefault(file,source_text(file,source_texts))
            if declaration['kind']=='IC':
                if not builtin_signature(expected): raise ValueError('Implicit prototype needs non-builtin type visibility')
                newline='\r\n' if '\r\n' in text else '\n'
                edits=[{'start':0,'end':0,'before':'','after':prototype(expected,name)+newline,'reason':'Replace implicit int/unprototyped call with the complete DWARF interface'}]
            else:
                pos,start,end=declaration_site(text,name,declaration['line'])
                params=text[start:end]
                if declaration['parameter_types']==['/*???*/']:
                    if expected['parameter_types'] or expected.get('variadic'): raise ValueError('Nonempty old-style prototype needs a separate review')
                    if params.strip(): raise ValueError('Old-style declaration has unexpected parameter text')
                    replacement='void'
                else:
                    parts=split_params(params)
                    if len(parts)!=len(desired[1]): raise ValueError('Parameter count change is not a mechanical qualifier repair')
                    changed=[]
                    for part,actual_type,expected_type in zip(parts,declaration['parameter_types'],desired[1]):
                        if actual_type==expected_type: changed.append(part); continue
                        if actual_type!='char*' or expected_type!='const char*':
                            raise ValueError('Requires type/return/body interpretation: '+actual_type+' -> '+expected_type)
                        if parameter_type(part)!=actual_type: raise ValueError('Parameter spelling does not match compiler evidence')
                        changed.append('const '+part)
                    # Preserve whitespace and source line count: insert const in each original parameter span.
                    replacement=params
                    if changed!=parts:
                        cursor=0; chunks=[]
                        for part,new in zip(parts,changed):
                            at=params.find(part,cursor)
                            if at<0: raise ValueError('Cannot locate parameter text')
                            chunks += [params[cursor:at],new]; cursor=at+len(part)
                        replacement=''.join(chunks)+params[cursor:]
                edits=[]
                if replacement!=params:
                    edits.append({'start':start,'end':end,'before':params,'after':replacement,'reason':'Use the DWARF parameter qualifiers/prototype'})
                if declaration['return_type']!=expected['return_type']:
                    if declaration['return_type']=='char*' and expected['return_type']=='const char*':
                        ret=re.search(r'\bchar\s*\*\s*$',text[:pos])
                        if not ret: raise ValueError('Cannot safely locate the return type')
                        edits.append({'start':ret.start(),'end':ret.end(),'before':ret[0],'after':'const '+ret[0],'reason':'Use the DWARF return qualifier'})
                    elif (declaration['kind'] in ('NC','OC') and declaration['file'].startswith('src/') and declaration.get('cu')==declaration['file']
                          and set(re.findall(r'[A-Za-z_]\w*',declaration['return_type']+' '+expected['return_type']))<=BUILTINS
                          and '*' not in declaration['return_type']+expected['return_type']):
                        # A caller-CU prototype spells a builtin scalar/void return differently. When every
                        # spelled call in that CU discards the value, no use is reinterpreted; restore the
                        # historical return type in place. Emission preservation is still checked freshly.
                        from typed_interface_tasks import call_values_unused
                        if not call_values_unused(sanitized(text),name): raise ValueError('Return type change requires supervisor interpretation: call results are used')
                        ret=re.search(r'\b('+r'\s+'.join(map(re.escape,declaration['return_type'].split()))+r')\s+$',text[:pos])
                        if not ret: raise ValueError('Cannot safely locate the return type')
                        edits.append({'start':ret.start(1),'end':ret.end(1),'before':ret[1],'after':expected['return_type'],'reason':'Restore the historical builtin return type in a caller prototype whose call results are all discarded'})
                    else: raise ValueError('Return type change requires supervisor interpretation')
            for edit in edits:
                edit.update(file=file,line=declaration['line'])
                key=(file,edit['start'],edit['end'])
                if key in patches and patches[key]['after']!=edit['after']: raise ValueError('Conflicting compiler locations')
                patches[key]=edit
        if not patches: raise ValueError('No mechanical edits identified')
        changes=sorted(patches.values(),key=lambda e:(e['file'],e['start']))
        files=sorted({p['file'] for p in changes})
        for file in files: patch_text(texts[file],[p for p in changes if p['file']==file])
        targets=affected_targets(ledger,files)
        card.update(changes=changes,sources=files,source_identities={f:text_identity(texts[f]) for f in files},
                    affected_targets=targets,difficulty='CHEAP',priority=260-min(len(targets),10)*3,
                    expected_prototype=prototype(expected,name),reason='Unique DWARF signature and exact compiler locations; body edits prohibited.')
    except ValueError as exc:
        card.update(reason=str(exc),priority=-20)
        from typed_interface_tasks import plan as typed_plan
        try: card.update(typed_plan(row,ledger,source_texts))
        except ValueError: pass
    if card.get('difficulty')=='CHEAP':
        from call_arity import conflicts as arity_conflicts
        edited=set(card.get('sources',[]))
        owners=sorted({d.get('cu') or d['file'] for d in row['candidate_declarations'] if d['file'] in edited})
        observations=[]
        for owner in owners:
            if owner.startswith('src/') and owner.endswith('.c'):
                observations.extend(dict(r,source=owner) for r in arity_conflicts(source_text(owner,source_texts),name,old[0]))
        if observations:
            card.update(difficulty='SUPERVISOR',priority=-25,state='CALLSITE_REPAIR_REQUIRED',
                status='CALLSITE_ARITY_CONFLICT',difference_class='SOURCE_CALL_ARGUMENT_COUNT',
                callsite_arity_conflicts=observations[:8],callsite_arity_conflict_count=len(observations),
                omitted_callsite_arity_conflicts=max(0,len(observations)-8),
                reason='Caller argument counts must be reviewed before installing the historical prototype: '+', '.join(r['source']+':'+str(r['line']) for r in observations[:3]))
    blocked=ROOT/'docs/current/interface-blocks.json'
    if blocked.exists() and name in read_json(blocked):
        card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
    return card


def contribution_fingerprint(report):
    """All allocated contributions, symbols and non-debug relocations, independent of COFF indices."""
    sections={s['index']:s['name'] for s in report['object_sections']}
    allocated={i for i,name in sections.items() if not name.startswith('.debug')}
    # Include .comment/directives. The sole code projection is explicitly recorded;
    # it preserves candidate scheduling and never participates in original matching.
    section_rows=[(s['name'],s['virtual_size'],s['raw_size'],s['characteristics'],report.get('candidate_zero_clear_projection',{}).get('sha256',s['sha256']) if s['name']=='.text' else s['sha256']) for s in report['object_sections'] if s['index'] in allocated]
    symbols={s['index']:s for s in report['object_symbols']}
    def stable_name(symbol):
        return re.sub(r'\.\d+$','',symbol['name']) if symbol['storage_class']==3 else symbol['name']
    relocations=[]
    for r in report['object_relocations']:
        if r['section'] not in allocated: continue
        symbol=symbols[r['symbol_index']]
        relocations.append((sections[r['section']],r['offset'],r['type'],stable_name(symbol),sections.get(symbol['section'],symbol['section']),symbol['value']))
    common=[(s['name'],s['value'],s['storage_class']) for s in report['common_allocations']]
    defined=[(stable_name(s),sections[s['section']],s['value'],s['storage_class']) for s in report['object_symbols'] if s['section'] in allocated and not s['name'].startswith('.')]
    return {'sections':sorted(section_rows),'relocations':sorted(relocations,key=str),'common':sorted(common),'defined':sorted(defined)}
