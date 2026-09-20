"""Apply one evidence-generated body experiment inside an existing grinder session."""
import argparse
from common import ROOT,read_json,write_json,identity
from grinder_task import SESSION,validate_scope
from recovery_pipeline import card_for,validate_report
from interface_tasks import patch_text
from source_scope import function_span


def apply(target,name,pattern_id):
    if not SESSION.exists(): raise ValueError('Begin the target body task before applying a source pattern')
    session=read_json(SESSION)
    if session.get('kind')=='INTERFACE' or (session['target'],session['function'])!=(target,name): raise ValueError('A different task is active')
    if session['verify_only']: raise ValueError('Verification-only sessions cannot edit source')
    validate_scope(session)
    path=ROOT/session['source']; text=path.read_bytes().decode('cp1252')
    if text!=session['source_text']: raise ValueError('A source experiment is already applied; verify or block/abort before another pattern')
    if identity(ROOT/'src/recovery.json')!=session['ledger']: raise ValueError('Ledger changed during task')
    ledger=read_json(ROOT/'src/recovery.json'); report=read_json(ROOT/ledger[session['source']]['verified_report']); validate_report(report)
    row=next(r for r in report['functions'] if r['name']==name); card=card_for(target,report,row)
    if card['difficulty']!='CHEAP' or not card['body_edit_allowed']: raise ValueError('Current evidence does not authorize a cheap body experiment')
    # Recompute from the receipt and source; generated JSON is not an edit authority.
    patterns=[p for p in card.get('source_patterns',[]) if p['id']==pattern_id]
    if len(patterns)!=1: raise ValueError('No unique current evidence-generated pattern '+pattern_id)
    pattern=patterns[0]; lo,hi=function_span(text,name)
    if not pattern['changes'] or any(not lo<e['start']<=e['end']<hi for e in pattern['changes']): raise ValueError('Pattern exceeds the target function body')
    changed=patch_text(text,pattern['changes']); path.write_bytes(changed.encode('cp1252'))
    try: validate_scope(session)
    except Exception:
        if path.read_bytes()==changed.encode('cp1252'): path.write_bytes(text.encode('cp1252'))
        raise
    session['applied_pattern']={'id':pattern_id,'changes':pattern['changes'],'reason':pattern['reason']}; write_json(SESSION,session)
    print('Applied',pattern_id,'inside',session['source']+':'+name)
    print('Run python tools/check_function.py',target,name,'; this edit is not a match claim.')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('target'); ap.add_argument('function'); ap.add_argument('pattern')
    a=ap.parse_args(); apply(a.target,a.function,a.pattern)


if __name__=='__main__': main()
