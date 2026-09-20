"""Bounded canonicalization of exact duplicate DWARF-derived struct declarations."""
import re
from common import ROOT,identity,read_json,write_json,check_json
from source_scope import sanitized
from interface_tasks import affected_targets


def tokens(text): return re.findall(r'\w+|[^\s]',text)


def plans(ledger):
    files=[*sorted((ROOT/'src').glob('*.c')),*sorted((ROOT/'include').glob('*.h'))]
    texts={p:p.read_bytes().decode('cp1252') for p in files}; cards=[]
    for header in sorted((ROOT/'include/recovered').glob('*.h')):
        name=header.stem
        expected=re.search(r'typedef struct\s*\{([^{}]*)\}\s*'+re.escape(name)+r'\s*;',header.read_text())
        if not expected: continue
        pattern=re.compile(r'\btypedef struct(?:\s+(\w+))?\s*\{([^{}]*)\}\s*'+re.escape(name)+r'\s*;')
        changes=[]; tags=set()
        for path,text in texts.items():
            clean=sanitized(text)
            for match in pattern.finditer(clean):
                if clean[:match.start()].count('{')!=clean[:match.start()].count('}'): continue
                if tokens(match[2])!=tokens(expected[1]): continue
                if match[1]: tags.add(match[1])
                changes.append({'file':path.relative_to(ROOT).as_posix(),'start':match.start(),'end':match.end(),
                    'before':text[match.start():match.end()],'after':'#include "recovered/'+name+'.h"',
                    'reason':'Member declaration tokens equal the generated historical type exactly; use its canonical declaration and assertions'})
        if not changes: continue
        reason=None
        for path,text in texts.items():
            clean=sanitized(text)
            for edit in changes:
                if ROOT/edit['file']==path: clean=clean[:edit['start']]+' '*(edit['end']-edit['start'])+clean[edit['end']:]
            if any(re.search(r'\bstruct\s+'+re.escape(tag)+r'\b',clean) for tag in tags): reason='Tagged struct is used outside the replaceable declarations'
        sources=sorted({e['file'] for e in changes}); targets=affected_targets(ledger,sources)
        card={'schema':1,'task_kind':'CANONICAL_TYPE','function':name,'source':sources[0],'sources':sources,
              'changes':changes,'header':header.relative_to(ROOT).as_posix(),'header_identity':identity(header),
              'source_identities':{p:identity(ROOT/p) for p in sources},'expected_declaration':expected[0],
              'affected_targets':targets,'difficulty':'SUPERVISOR' if reason else 'CHEAP','priority':-20 if reason else 245-len(targets)*3,
              'state':'CANONICAL_TYPE_REPAIR','status':'DUPLICATE_TYPE','difference_class':'CANONICAL_TYPE_DECLARATION','body_edit_allowed':False,
              'reason':reason or 'Exact duplicate member declarations; replace only the complete typedef with its generated header.',
              'begin_command':'python tools/interface_task.py begin '+name,'apply_command':'python tools/interface_task.py apply '+name,
              'verification_command':'python tools/interface_task.py check '+name,'promotion_command':'python tools/interface_task.py promote '+name,
              'edit_scope':'Generated typedef replacement only. Preserve all function bodies, exact statuses and allocated contributions using the interface gate.'}
        blocked=ROOT/'docs/current/interface-blocks.json'
        if blocked.exists() and name in read_json(blocked): card.update(difficulty='SUPERVISOR',priority=-100,supervisor_block=read_json(blocked)[name])
        cards.append(card)
    return cards


def publish_types(ledger,check=False):
    emit=check_json if check else write_json; cards=plans(ledger); tasks=[]
    for card in cards:
        path=ROOT/'docs/current/types'/(card['function']+'.json'); emit(path,card)
        tasks.append({k:card[k] for k in ('task_kind','function','source','sources','difficulty','priority','reason','state','status','body_edit_allowed','difference_class','begin_command','verification_command','promotion_command')} | {'size':0,'candidate_card':path.relative_to(ROOT).as_posix()})
    active={card['function'] for card in cards}
    for header in sorted((ROOT/'include/recovered').glob('*.h')):
        if header.stem not in active:
            emit(ROOT/'docs/current/types'/(header.stem+'.json'),{'schema':1,'task_kind':'CANONICAL_TYPE','function':header.stem,'state':'NOT_QUEUED','status':'NO_MECHANICAL_DUPLICATE_TASK','body_edit_allowed':False,'changes':[],'header':header.relative_to(ROOT).as_posix()})
    emit(ROOT/'docs/current/type-tasks.json',{'authority':'Exact member-token equality with generated DWARF declarations plus verified affected-CU acceptance','tasks':tasks})
    return tasks
