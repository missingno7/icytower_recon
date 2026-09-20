"""Enforce one bounded body edit, preserve proven bodies, and route unknowns away."""
import argparse
import json
from common import ROOT, identity, read_json, write_json
from recovery_pipeline import fresh_verify, card_for, CURRENT, publish_cards
from source_scope import function_span, sanitized
import re

SESSION=ROOT/'build/grinder/session.json'


def snapshot_files():
    return {p.relative_to(ROOT).as_posix():identity(p) for folder in ('src','include','tools') for p in sorted((ROOT/folder).rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}


def validate_scope(session):
    source=session['source']; current=snapshot_files(); before=session['files']
    for path in set(current)|set(before):
        if path!=source and current.get(path)!=before.get(path):
            raise ValueError('Out-of-scope edit: '+path)
    text=(ROOT/source).read_bytes().decode('cp1252')
    old=session['source_text']
    if text!=old:
        if session['verify_only']: raise ValueError('Verify-only session cannot edit source')
        a,b=function_span(old,session['function']); c,d=function_span(text,session['function'])
        if old[:a]!=text[:c] or old[b:]!=text[d:]: raise ValueError('Changed text outside authorized function body')
        forbidden=r'\b(?:asm|__asm__|__asm|__attribute__|volatile)\b|^\s*#'
        if len(re.findall(forbidden,sanitized(text[c:d]),re.M))>len(re.findall(forbidden,sanitized(old[a:b]),re.M)):
            raise ValueError('Body task introduced forbidden code-generation directives or qualifiers')
    return text


def begin(target,name,verify_only=False,medium=False):
    if SESSION.exists(): raise ValueError('A grinder task is active; finish or block it before starting another')
    ledger=read_json(ROOT/'src/recovery.json')
    from refresh_recovery import validate_ledger
    validate_ledger(ledger)
    report=fresh_verify(target); row=next(r for r in report['functions'] if r['name']==name)
    card=card_for(target,report,row)
    if not verify_only:
        if not card['body_edit_allowed'] or card['state']=='BODY_MATCH_LAYOUT_BLOCKED': raise ValueError('Body is protected: '+card['state'])
        if card['difficulty'] not in (('CHEAP','MEDIUM') if medium else ('CHEAP',)): raise ValueError('Grinder skips '+card['difficulty']+' tasks')
    write_json(SESSION,{'target':target,'function':name,'source':card['source'],'source_text':(ROOT/card['source']).read_bytes().decode('cp1252'),
                        'files':snapshot_files(),'ledger':identity(ROOT/'src/recovery.json'),'verify_only':verify_only,
                        'baseline_report':report,'baseline_link':read_json(CURRENT/'link-status.json') if (CURRENT/'link-status.json').exists() else None,'card':card})
    from check_function import record_attempt
    record_attempt(target,name,report,card,'BEGIN_VERIFY_ONLY' if verify_only else 'BEGIN')
    print('Task opened:',card['source'],name,'verify-only' if verify_only else 'body only')
    print(card['verification_command'])


def active_body(target,name):
    session=read_json(SESSION)
    if session.get('kind')=='INTERFACE' or (target,name)!=(session['target'],session['function']):
        raise ValueError('Different task is active')
    validate_scope(session)
    if identity(ROOT/'src/recovery.json')!=session['ledger']: raise ValueError('Ledger changed during task')
    return session


def before_fast(target,name):
    if not SESSION.exists(): return None
    session=active_body(target,name)
    count=session.get('fast_attempts',0)
    if count>=3: raise ValueError('Three FAST attempts exhausted. Promote an exact result or block for supervisor; do not keep guessing.')
    session['fast_attempts']=count+1
    write_json(SESSION,session)
    return session


def block(target,name,reason,blocked=True):
    session=active_body(target,name)
    from check_function import record_attempt, record_compile_failure
    try:
        report=fresh_verify(target)
        row=next(r for r in report['functions'] if r['name']==name)
        card=card_for(target,report,row)
        record_attempt(target,name,report,card,'BLOCKED_SUPERVISOR' if blocked else 'ABORTED',reason)
        failure={'first_difference':card['first_difference'],'difference_class':card['difference_class']}
    except Exception as exc:
        record_compile_failure(target,name,session['source'],exc)
        failure={'compile_or_verification_failure':str(exc),'difference_class':'UNKNOWN_SUPERVISOR'}
    if blocked:
        path=CURRENT/'supervisor-blocks.json'; blocks=read_json(path) if path.exists() else {}
        blocks[session['source']+':'+name]={'state':'BLOCKED_SUPERVISOR','reason':reason,
                                          **failure,'source_identity':identity(ROOT/session['source'])}
        write_json(path,blocks)
    (ROOT/session['source']).write_bytes(session['source_text'].encode('cp1252'))
    SESSION.unlink()
    publish_cards(read_json(ROOT/'src/recovery.json'))
    print('Recorded failure and restored only the task source; task', 'blocked' if blocked else 'aborted')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['begin','block','abort']); ap.add_argument('target'); ap.add_argument('function')
    ap.add_argument('--verify-only',action='store_true'); ap.add_argument('--medium',action='store_true'); ap.add_argument('--reason')
    a=ap.parse_args()
    if a.action=='begin': begin(a.target,a.function,a.verify_only,a.medium)
    elif not a.reason: raise ValueError('Exact failure reason required')
    else: block(a.target,a.function,a.reason,a.action=='block')


if __name__=='__main__': main()
