"""Bounded typed declarations using visible or newly included canonical types."""
import re
from common import ROOT,read_json,identity
from source_scope import sanitized


GAME_POINTER=re.compile(r'(?:const )?([A-Za-z_]\w*)(\*+)')


def placeholder_for(type_text):
    """The void-pointer spelling that a caller may use for this historical game pointer type."""
    match=GAME_POINTER.fullmatch(type_text)
    return 'void'+match[2] if match else None


def after_leading_includes(text):
    """Offset just after the last #include line that precedes the first function definition."""
    from source_order import definition_spans
    spans=definition_spans(text); first=min((s['start'] for s in spans),default=len(text))
    last=None
    for m in re.finditer(r'(?m)^[ \t]*#[ \t]*include\b[^\n]*\n?',text):
        if m.start()>=first: break
        last=m.end()
    return last


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


def body_has_return_statement(clean,name,line):
    """Return whether a function definition contains any return statement."""
    from interface_tasks import declaration_site
    _,_,params_end=declaration_site(clean,name,line)
    opening=clean.find('{',params_end+1)
    if opening<0: raise ValueError('Definition body is unavailable for return-type review')
    depth=0
    for end in range(opening,len(clean)):
        depth+=(clean[end]=='{')-(clean[end]=='}')
        if depth==0:
            return bool(re.search(r'\breturn\b',clean[opening+1:end]))
    raise ValueError('Definition body is unbalanced')


def void_to_int_is_safe(row,declaration,text,source_texts):
    """Allow only discarded int results and a void definition with no return statement."""
    from interface_tasks import source_text
    name=row['function']
    if declaration['kind']=='NF':
        if body_has_return_statement(sanitized(text),name,declaration['line']): return False
        for caller in row['candidate_declarations']:
            caller_text=source_text(caller['file'],source_texts,ROOT)
            if caller['kind']!='NF' and not call_values_unused(sanitized(caller_text),name): return False
        return True
    return call_values_unused(sanitized(text),name)


def update_game_menu_voidpp_evidence(row, expected, declaration, text, report, g, typed_names):
    """Prove the one menu CU's int* spelling is a historical void** output slot.

    The result authorizes declaration spans only. It is specific to this recovered
    interface and requires the original aggregate/local DIEs plus the current store
    and caller flow; integer/pointer width equivalence is not evidence.
    """
    if (row.get('function')!='update_game_menu' or len(row.get('historical',[]))!=1
            or declaration.get('file')!='src/menu.c' or declaration.get('cu')!='src/menu.c'
            or declaration.get('kind') not in ('NC','NF')):
        return False
    from interfaces import normalize, split_params
    expected_signature=('int',('BITMAP*','Tmenu*','Tmenu_params*','Tcontrol*','int','int','void**'))
    if (expected.get('return_type'),tuple(expected.get('parameter_types',())))!=expected_signature:
        return False
    if expected.get('variadic') or expected.get('calling_convention') is not None:
        return False
    if declaration.get('parameter_types')!=['void*','Tmenu*','Tmenu_params*','Tcontrol*','int','int','int*']:
        return False
    if 'BITMAP' not in typed_names or report.get('build',{}).get('target')!='game-menu':
        return False
    if 'include/recovered/Tmenu.h' not in report.get('build',{}).get('local_inputs',{}):
        return False
    declarations=row.get('candidate_declarations',[])
    if (len(declarations)!=2 or {d.get('kind') for d in declarations}!={'NC','NF'}
            or any(d.get('file')!='src/menu.c' or d.get('cu')!='src/menu.c' for d in declarations)):
        return False

    # Bind the rule to the unique historical definition and complete Tmenu in
    # the same CU. Tmenu.data is the pointer value stored through the output slot.
    die=g.dies.get(expected.get('die'))
    if not die or die.get('tag')!='DW_TAG_subprogram' or die.get('name')!='update_game_menu':
        return False
    cu=die.get('cu')
    updates=[d for d in g.dies.values() if d.get('tag')=='DW_TAG_subprogram'
             and d.get('name')=='update_game_menu' and d.get('cu')==cu]
    if len(updates)!=1 or updates[0]['offset']!=die['offset']:
        return False
    historical_params=[d for d in g.children.get(die['offset'],[]) if d.get('tag')=='DW_TAG_formal_parameter']
    if (normalize(g.declaration(die.get('type_ref')))!='int'
            or [normalize(g.declaration(p.get('type_ref'))) for p in historical_params]
            !=list(expected_signature[1])):
        return False
    menus=[d for d in g.game_types.get('Tmenu',[]) if d.get('cu')==cu]
    if len(menus)!=1:
        return False
    struct=g.dies.get(menus[0].get('type_ref'))
    if not struct or struct.get('tag')!='DW_TAG_structure_type' or g.size(struct['offset'])!=148:
        return False
    members=[m for m in g.children.get(struct['offset'],[]) if m.get('tag')=='DW_TAG_member' and m.get('name')=='data']
    if (len(members)!=1 or g.member_offset(members[0])!=144
            or normalize(g.declaration(members[0].get('type_ref')))!='void*'):
        return False
    handles=[d for d in g.dies.values() if d.get('tag')=='DW_TAG_subprogram'
             and d.get('name')=='handle_menu' and d.get('cu')==cu]
    if len(handles)!=1:
        return False
    data_locals=[d for d in g.children.get(handles[0]['offset'],[])
                 if d.get('tag')=='DW_TAG_variable' and d.get('name')=='data']
    if len(data_locals)!=1 or normalize(g.declaration(data_locals[0].get('type_ref')))!='void*':
        return False

    # Match unique source definitions and the exact pointer flow. The store is
    # evidence only; it is not edited or reinterpreted by this interface task.
    from source_order import definition_spans
    spans=definition_spans(text)
    if sum(s['name']=='update_game_menu' for s in spans)!=1 or sum(s['name']=='handle_menu' for s in spans)!=1:
        return False
    by_name={s['name']:s for s in spans}
    update,handle=by_name['update_game_menu'],by_name['handle_menu']
    clean=sanitized(text)
    update_body=clean[update['body_start']:update['end']]
    handle_body=clean[handle['body_start']:handle['end']]
    try:
        from interface_tasks import declaration_site
        _,param_start,param_end=declaration_site(text,'update_game_menu',declaration['line'])
    except ValueError:
        return False
    params=split_params(clean[param_start:param_end])
    if len(params)!=7 or not re.fullmatch(r'int\s*\*\s*data',params[6].strip()):
        return False
    stores=list(re.finditer(r'\*\s*data\s*=\s*(?:\(\s*int\s*\)\s*)?m\s*\[\s*pos\s*\]\s*\.\s*data\s*;',update_body))
    if len(stores)!=1 or len(re.findall(r'\bvoid\s*\*\s*data\s*;',handle_body))!=1:
        return False
    calls=list(re.finditer(r'\bupdate_game_menu\s*\(',handle_body))
    if len(calls)!=1:
        return False
    opening=handle_body.find('(',calls[0].start()); depth=1; end=opening+1
    while end<len(handle_body) and depth:
        depth+=(handle_body[end]=='(')-(handle_body[end]==')'); end+=1
    if depth:
        return False
    args=split_params(handle_body[opening+1:end-1])
    return len(args)==7 and args[6].strip()=='&data'


def plan(row,ledger,source_texts=None):
    from interface_tasks import signature,BUILTINS,prototype,declaration_site,patch_text,affected_targets,source_text,text_identity
    from interfaces import split_params,parameter_type
    from type_graph import graph
    old=row['historical']
    if len({signature(r) for r in old})!=1: raise ValueError('Conflicting historical interfaces')
    expected=old[0];name=row['function']
    if expected.get('calling_convention') is not None or expected.get('variadic'): raise ValueError('Typed prototype needs a fixed default-C interface')
    from type_views import library_pointees
    g=graph(); names=set(); library_names=set(); typed_return=None
    if not set(re.findall(r'[A-Za-z_]\w*',expected['return_type']))<=BUILTINS:
        match=GAME_POINTER.fullmatch(expected['return_type'])
        if not match or match[1] not in g.game_types: raise ValueError('Typed return repair is not supported')
        names.add(match[1]); typed_return=match[1]
    for parameter in expected['parameter_types']:
        tokens=set(re.findall(r'[A-Za-z_]\w*',parameter))-BUILTINS
        if not tokens: continue
        match=GAME_POINTER.fullmatch(parameter)
        if not match: raise ValueError('Only pointers to named types are supported')
        if match[1] in g.game_types: names.add(match[1])
        else: library_names.add(match[1])
    if not names and not library_names: raise ValueError('No canonical pointer type prerequisite')
    headers={n:'include/recovered/'+n+'.h' for n in names}
    if any(not (ROOT/p).is_file() for p in headers.values()): raise ValueError('Generated type header unavailable')
    patches={};texts={};proof_headers={}
    for declaration in row['candidate_declarations']:
        actual=(declaration.get('canonical_return_type',declaration['return_type']),tuple(declaration.get('canonical_parameter_types',declaration['parameter_types'])))
        issues=[x for x in row.get('type_layout_issues',[]) if x['cu']==declaration['cu'] and x['file']==declaration['file'] and x['line']==declaration['line']]
        if actual==signature(expected):
            if issues: raise ValueError('Already named type has unresolved or conflicting layout')
            continue
        if declaration['kind'] not in ('IC','NC','OC','NF'): raise ValueError('Unsupported declaration kind for a typed repair')
        return_repair=None
        declared_return=declaration.get('canonical_return_type',declaration['return_type'])
        if declared_return!=expected['return_type']:
            if declaration['kind']=='IC':
                # An implicit call declares int; the prototype may restore void or a game pointer only
                # when every spelled call discards its value, so no int-typed use is reinterpreted.
                if declaration['return_type']!='int' or not (expected['return_type']=='void' or typed_return):
                    raise ValueError('Return type change is not a caller-only typed parameter repair')
                return_repair='IMPLICIT_VALUES_UNUSED'
            elif typed_return and declaration['return_type']==placeholder_for(expected['return_type']):
                return_repair=expected['return_type']
            elif (expected['return_type']=='int' and declaration['return_type']=='void'
                  and void_to_int_is_safe(row,declaration,source_text(declaration['file'],source_texts,ROOT),source_texts)):
                return_repair='int'
            else: raise ValueError('Return type change is not a caller-only typed parameter repair')
        if any(x['status']!='UNAVAILABLE' or x['candidate_type'] not in ('void','/*???*/') for x in issues): raise ValueError('Existing aggregate conflicts require a separate repair')
        file=declaration['file']
        if not file.startswith('src/') or declaration.get('cu')!=file: raise ValueError('Typed repair requires a CU-local declaration')
        if declaration['cu'] not in ledger: raise ValueError('Owning CU proof is unavailable')
        report=read_json(ROOT/ledger[declaration['cu']]['verified_report'])
        # Library pointees (BITMAP, PACKFILE, ...) need the owning CU's historical typedef layout,
        # reproduced by the compiled CU; a spelled name alone is not evidence.
        library=library_pointees(declaration['cu'],report,g) if library_names else set()
        typed_names=names|(library_names&library)
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
            if library_names-library: raise ValueError('Library pointee lacks owning-CU layout evidence: '+', '.join(sorted(library_names-library)))
            if not prefix:
                # A canonical type already supplied by an include must be visible before this prototype.
                insertion=after_leading_includes(text)
                if insertion is None: raise ValueError('No include precedes the first definition for a typed prototype')
            prefix+=prototype(expected,name)+newline
            edits=[]
        elif declaration['kind']=='NF':
            # Definition: retype only void-pointer placeholder parameters. A narrowly checked
            # void-to-int repair is allowed when all calls discard the result and no return occurs.
            pos,start,end=declaration_site(text,name,declaration['line'])
            if not sanitized(text[end+1:]).lstrip().startswith('{'): raise ValueError('Definition is not followed by its body')
            params=text[start:end];parts=split_params(params);actual_types=declaration['parameter_types']
            if len(parts)!=len(expected['parameter_types']) or len(actual_types)!=len(parts): raise ValueError('Typed repair cannot change parameter count')
            edits=[];cursor=0
            menu_voidpp_slot=update_game_menu_voidpp_evidence(row,expected,declaration,text,report,g,typed_names)
            for index,(part,actual_type,wanted) in enumerate(zip(parts,actual_types,expected['parameter_types'])):
                at=params.find(part,cursor)
                if at<0: raise ValueError('Cannot locate parameter text')
                cursor=at+len(part)
                if actual_type==wanted: continue
                if parameter_type(part)!=actual_type: raise ValueError('Compiler/source parameter disagreement')
                if index==6 and actual_type=='int*' and wanted=='void**' and menu_voidpp_slot:
                    spellings=list(re.finditer(r'\bint\s*\*',sanitized(part)))
                    if len(spellings)!=1: raise ValueError('Output-slot parameter spelling is ambiguous')
                    span_start=start+at+spellings[0].start()
                    span_end=start+at+spellings[0].end()
                    edits.append({'start':span_start,'end':span_end,'before':text[span_start:span_end],'after':'void **',
                                  'reason':'Restore update_game_menu historical void ** output slot from unique DWARF member/local and caller-store evidence'})
                    continue
                pointee=GAME_POINTER.fullmatch(wanted)
                if actual_type!=placeholder_for(wanted) or not pointee or pointee[1] not in typed_names:
                    raise ValueError('Only evidenced void-pointer placeholders can become named pointers in a definition')
                voids=list(re.finditer(r'\bvoid\b',sanitized(part)))
                if len(voids)!=1: raise ValueError('Placeholder parameter spelling is ambiguous')
                span_start=start+at+voids[0].start()
                edits.append({'start':span_start,'end':span_start+4,'before':'void','after':pointee[1],
                              'reason':'Restore the historical parameter type from its void-pointer placeholder; parameter name and body unchanged'})
            if return_repair:
                ret=re.search(r'\bvoid\s+$',text[:pos])
                if not ret: raise ValueError('Cannot safely locate the void definition return type')
                edits.append({'start':ret.start(),'end':ret.end(),'before':ret[0],'after':'int ',
                              'reason':'Restore the historical int return type; all callers discard it and the body has no return statement'})
            if not edits: raise ValueError('No definition placeholder to repair')
        else:
            pos,start,end=declaration_site(text,name,declaration['line'])
            if not sanitized(text[end+1:]).lstrip().startswith(';'): raise ValueError('Caller declaration is not a plain prototype')
            parts=split_params(text[start:end]);actual_types=declaration['parameter_types']
            if actual_types==['/*???*/']:
                if text[start:end].strip(): raise ValueError('Old-style argument text is not empty')
            else:
                if len(parts)!=len(expected['parameter_types']): raise ValueError('Typed repair cannot change parameter count')
                menu_voidpp_slot=update_game_menu_voidpp_evidence(row,expected,declaration,text,report,g,typed_names)
                for index,(part,actual_type,wanted) in enumerate(zip(parts,actual_types,expected['parameter_types'])):
                    if parameter_type(part)!=actual_type: raise ValueError('Compiler/source parameter disagreement')
                    menu_slot=(index==6 and actual_type=='int*' and wanted=='void**' and menu_voidpp_slot)
                    if actual_type!=wanted and not (menu_slot or (actual_type==placeholder_for(wanted) and GAME_POINTER.fullmatch(wanted)[1] in typed_names)):
                        raise ValueError('Only evidenced void-pointer placeholders can become named pointers')
            replacement=', '.join(expected['parameter_types'] or ['void'])
            edits=[]
            if replacement!=text[start:end]:
                edits.append({'start':start,'end':end,'before':text[start:end],'after':replacement,'reason':'Restore complete historical caller prototype'})
            if return_repair:
                pointer_return=bool(typed_return and return_repair==expected['return_type'])
                ret=re.search(r'\bvoid\s*(\*+)\s*$' if pointer_return else r'\bvoid\s+$',text[:pos])
                if not ret or (pointer_return and len(ret[1])!=return_repair.count('*')):
                    raise ValueError('Cannot safely locate the void caller return placeholder')
                after=ret[0].replace('void',return_repair.rstrip('*').strip(),1)
                edits.append({'start':ret.start(),'end':ret.end(),'before':ret[0],'after':after,
                              'reason':'Restore the historical caller return type after proving the call result is discarded'})
        if prefix: edits.append({'start':insertion,'end':insertion,'before':'','after':prefix,'reason':'Introduce generated historical type visibility and caller prototype'})
        for edit in edits:
            edit.update(file=file,line=declaration['line']);key=(file,edit['start'],edit['end'])
            same=lambda a,b:{k:v for k,v in a.items() if k!='line'}=={k:v for k,v in b.items() if k!='line'}
            if key in patches and not same(patches[key],edit): raise ValueError('Conflicting typed declaration edits')
            patches.setdefault(key,edit)
    if not patches: raise ValueError('No bounded typed caller edits')
    changes=sorted(patches.values(),key=lambda e:(e['file'],e['start']));sources=sorted(texts)
    for source in sources: patch_text(texts[source],[e for e in changes if e['file']==source])
    targets=affected_targets(ledger,sources)
    return {'changes':changes,'sources':sources,'source_identities':{p:text_identity(texts[p]) for p in sources},
            'affected_targets':targets,'required_generated_headers':proof_headers,'expected_prototype':prototype(expected,name),
            'difficulty':'CHEAP','priority':250-min(len(targets),10)*3,'state':'INTERFACE_REPAIR','status':'INTERFACE_CONFLICT',
            'difference_class':'INTERFACE_DECLARATION','typed_caller_repair':True,
            'reason':'Unique historical pointer interface; generated type visibility plus caller-only prototype edits. Fresh layout agreement and emission preservation remain mandatory.'}
