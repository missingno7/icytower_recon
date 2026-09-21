"""Bounded caller-only prototypes using visible or newly included canonical types."""
import re
from common import ROOT,read_json,identity
from source_scope import sanitized


GAME_POINTER=re.compile(r'(?:const )?([A-Za-z_]\w*)(\*+)')


def placeholder_for(type_text):
    """The void-pointer spelling that a caller may use for this historical game pointer type."""
    match=GAME_POINTER.fullmatch(type_text)
    return 'void'+match[2] if match else None


def call_values_unused(clean,name):
    """Every source-spelled call of `name` is a statement whose value is discarded.

    Accepts calls preceded by `;`, `{`, `}`, a label colon, `else`/`do`, or the closing
    parenthesis of an if/while/for/switch header. Casts, assignments, returns and nested
    expression uses are rejected. Declarations are not calls and are skipped.
    """
    for m in re.finditer(r'\b'+re.escape(name)+r'\s*\(',clean):
        if clean[:m.start()].count('{')==clean[:m.start()].count('}'): continue
        before=clean[:m.start()].rstrip()
        if not before: return False
        if before[-1] in ';{}:': continue
        if re.search(r'\b(?:else|do)$',before): continue
        if before[-1]==')':
            depth=0; i=len(before)-1
            while i>=0:
                depth+=(before[i]==')')-(before[i]=='(')
                if depth==0: break
                i-=1
            if i>0 and re.search(r'\b(?:if|while|for|switch)\s*$',before[:i]): continue
        return False
    return True


def plan(row,ledger,source_texts=None):
    from interface_tasks import signature,BUILTINS,prototype,declaration_site,patch_text,affected_targets,source_text,text_identity
    from interfaces import split_params,parameter_type
    from type_graph import graph
    old=row['historical']
    if len({signature(r) for r in old})!=1: raise ValueError('Conflicting historical interfaces')
    expected=old[0];name=row['function']
    if expected.get('calling_convention') is not None or expected.get('variadic'): raise ValueError('Typed prototype needs a fixed default-C interface')
    names=set(); typed_return=None
    if not set(re.findall(r'[A-Za-z_]\w*',expected['return_type']))<=BUILTINS:
        match=GAME_POINTER.fullmatch(expected['return_type'])
        if not match or match[1] not in graph().game_types: raise ValueError('Typed return repair is not supported')
        names.add(match[1]); typed_return=match[1]
    for parameter in expected['parameter_types']:
        tokens=set(re.findall(r'[A-Za-z_]\w*',parameter))-BUILTINS
        if not tokens: continue
        match=GAME_POINTER.fullmatch(parameter)
        if not match or match[1] not in graph().game_types: raise ValueError('Only pointers to generated historical types are supported')
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
        return_repair=None
        if declaration['return_type']!=expected['return_type']:
            if declaration['kind']=='IC':
                # An implicit call declares int; the prototype may restore void or a game pointer only
                # when every spelled call discards its value, so no int-typed use is reinterpreted.
                if declaration['return_type']!='int' or not (expected['return_type']=='void' or typed_return):
                    raise ValueError('Return type change is not a caller-only typed parameter repair')
                return_repair='IMPLICIT_VALUES_UNUSED'
            elif typed_return and declaration['return_type']==placeholder_for(expected['return_type']):
                return_repair=expected['return_type']
            else: raise ValueError('Return type change is not a caller-only typed parameter repair')
        if any(x['status']!='UNAVAILABLE' or x['candidate_type'] not in ('void','/*???*/') for x in issues): raise ValueError('Existing aggregate conflicts require a separate repair')
        file=declaration['file']
        if not file.startswith('src/') or declaration.get('cu')!=file: raise ValueError('Typed repair requires a CU-local declaration')
        if declaration['cu'] not in ledger: raise ValueError('Owning CU proof is unavailable')
        report=read_json(ROOT/ledger[declaration['cu']]['verified_report'])
        text=texts.setdefault(file,source_text(file,source_texts,ROOT));newline='\r\n' if '\r\n' in text else '\n'
        if return_repair=='IMPLICIT_VALUES_UNUSED':
            if not call_values_unused(sanitized(text),name):
                raise ValueError('Implicit call results are used; return type change needs supervisor review')
            return_repair=None
        prefix=''
        for type_name,header in sorted(headers.items()):
            if header not in report['build']['local_inputs']:
                for source in report['build']['local_inputs']:
                    if source.startswith(('src/','include/')) and re.search(r'\b'+re.escape(type_name)+r'\b',sanitized(source_text(source,source_texts,ROOT))):
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
                    if actual_type!=wanted and not (actual_type==placeholder_for(wanted) and GAME_POINTER.fullmatch(wanted)[1] in names):
                        raise ValueError('Only void-pointer placeholders can become named pointers')
            replacement=', '.join(expected['parameter_types'] or ['void'])
            edits=[]
            if replacement!=text[start:end]:
                edits.append({'start':start,'end':end,'before':text[start:end],'after':replacement,'reason':'Restore complete historical caller prototype'})
            if return_repair:
                ret=re.search(r'\bvoid\s*(\*+)\s*$',text[:pos])
                if not ret or len(ret[1])!=return_repair.count('*'): raise ValueError('Cannot safely locate the void-pointer return placeholder')
                edits.append({'start':ret.start(),'end':ret.end(),'before':ret[0],'after':ret[0].replace('void',return_repair.rstrip('*').strip(),1),
                              'reason':'Restore the historical caller return type from its void-pointer placeholder'})
        if prefix: edits.append({'start':insertion,'end':insertion,'before':'','after':prefix,'reason':'Introduce generated historical type visibility and caller prototype'})
        for edit in edits:
            edit.update(file=file,line=declaration['line']);key=(file,edit['start'],edit['end'])
            if key in patches and patches[key]!=edit: raise ValueError('Conflicting typed declaration edits')
            patches[key]=edit
    if not patches: raise ValueError('No bounded typed caller edits')
    changes=sorted(patches.values(),key=lambda e:(e['file'],e['start']));sources=sorted(texts)
    for source in sources: patch_text(texts[source],[e for e in changes if e['file']==source])
    targets=affected_targets(ledger,sources)
    return {'changes':changes,'sources':sources,'source_identities':{p:text_identity(texts[p]) for p in sources},
            'affected_targets':targets,'required_generated_headers':proof_headers,'expected_prototype':prototype(expected,name),
            'difficulty':'CHEAP','priority':250-min(len(targets),10)*3,'state':'INTERFACE_REPAIR','status':'INTERFACE_CONFLICT',
            'difference_class':'INTERFACE_DECLARATION','typed_caller_repair':True,
            'reason':'Unique historical pointer interface; generated type visibility plus caller-only prototype edits. Fresh layout agreement and emission preservation remain mandatory.'}
