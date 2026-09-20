"""ACCEPTANCE: fresh proof, bounded source gate, tests, link, atomic ledger publication."""
import argparse
import os
import shutil
import sys
from contextlib import contextmanager
from common import ROOT, identity, read_json, write_json, run
from recovery_pipeline import fresh_verify, card_for, CURRENT, validate_report
from refresh_recovery import entry_from_report, validate_ledger, publish_status
from grinder_task import SESSION, validate_scope
from check_function import record_attempt
from publication import publication

LOCK=ROOT/'build/grinder/promotion.lock'
JOURNAL=ROOT/'build/grinder/publication.zip'


@contextmanager
def promotion_lock():
    if (LOCK.parent/'recovery.lock').exists(): raise ValueError('Publication recovery in progress')
    if JOURNAL.exists(): raise ValueError('Interrupted publication: run python tools/recover_promotion.py')
    LOCK.parent.mkdir(parents=True,exist_ok=True)
    with LOCK.open('x') as stream: stream.write(str(os.getpid()))
    try:
        if (LOCK.parent/'recovery.lock').exists(): raise ValueError('Publication recovery in progress')
        yield
    finally: LOCK.unlink()


def eligible(report,name,claim):
    validate_report(report)
    row=next((r for r in report['functions'] if r['name']==name),None)
    if row is None: raise ValueError('Function is absent from owning CU')
    if claim=='FUNCTION_MATCH' and row['workflow']['state']=='BODY_MATCH_LAYOUT_BLOCKED':
        raise ValueError('Promotion denied: the body is proven but CU layout remains blocked. Use --claim BODY_MATCH_LAYOUT_BLOCKED explicitly.')
    if claim=='FUNCTION_MATCH' and row['status']!='FUNCTION_MATCH':
        raise ValueError('Promotion denied: '+name+' is '+row['status']+'; first mismatch '+str(row.get('first_difference')))
    if claim=='BODY_MATCH_LAYOUT_BLOCKED' and row['workflow']['state']!=claim:
        raise ValueError('Layout-only status is not mechanically proven')
    return row


def no_regressions(before,after):
    current={r['name']:r for r in after['functions']}
    for old in before['functions']:
        new=current[old['name']]
        layout_preserved=old.get('source_body_sha256') and new.get('tail_jump_layout') and new.get('workflow',{}).get('state')=='BODY_MATCH_LAYOUT_BLOCKED' and old.get('source_body_sha256')==new.get('source_body_sha256')
        if old['status']=='FUNCTION_MATCH' and new['status']!='FUNCTION_MATCH' and not layout_preserved:
            raise ValueError('Exact neighbor regressed: '+old['name'])
        if old['workflow']['state'] in ('FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED') and old.get('source_body_sha256')!=new.get('source_body_sha256'):
            raise ValueError('Protected function body changed: '+old['name'])



def commit_reports(ledger,reports,link=None):
    """Publish a verified dependency closure, with rollback and a global audit."""
    protected=[ROOT/'src/recovery.json',ROOT/'docs/progress.json',ROOT/'docs/blocker-summary.json',*CURRENT.rglob('*')]
    with publication(protected,CURRENT,JOURNAL,ROOT):
        for report in reports.values():
            target=report['build']['target']; source=report['build']['config']['source']
            path=CURRENT/'reports'/(target+'.json')
            write_json(path,report)
            ledger[source]=entry_from_report(report,path,ledger[source])
        validate_ledger(ledger)
        pending=ROOT/'src/recovery.pending.json'
        try:
            write_json(pending,ledger); os.replace(pending,ROOT/'src/recovery.json')
        finally:
            pending.unlink(missing_ok=True)
        if link is not None: write_json(CURRENT/'link-status.json',link)
        publish_status(ledger)
        from audit import main as audit
        audit(allow_transaction=True)


def promote(target,name,claim='FUNCTION_MATCH'):
    with promotion_lock():
        session=read_json(SESSION) if SESSION.exists() else None
        ledger=read_json(ROOT/'src/recovery.json')
        if session:
            if (session['target'],session['function'])!=(target,name): raise ValueError('Different task is active')
            validate_scope(session)
            if identity(ROOT/'src/recovery.json')!=session['ledger']: raise ValueError('Ledger changed during task')
        else:
            # Unedited functions may be re-certified without a task. Every input must still match its receipt.
            validate_ledger(ledger)
        report=fresh_verify(target,dest=ROOT/'build/acceptance'/target)
        card=card_for(target,report,next(r for r in report['functions'] if r['name']==name))
        try:
            row=eligible(report,name,claim)
            source=report['build']['config']['source']
            old=read_json(ROOT/ledger[source]['verified_report'])
            no_regressions(old,report)
            print(run([sys.executable,'tools/test_grinder.py']),end='')
            print(run([sys.executable,'tools/test_data_owners.py']),end='')
            print(run([sys.executable,'tools/test_dwarf_locations.py']),end='')
            print(run([sys.executable,'tools/test_compiler_context.py']),end='')
            print(run([sys.executable,'tools/test_branch_diagnostics.py']),end='')
            print(run([sys.executable,'tools/test_data_tasks.py']),end='')
            source_changed=report['build']['local_inputs']!=old['build']['local_inputs']
            link=None
            if source_changed:
                print(run([sys.executable,'tools/recovered_game_link.py']),end='')
                link=read_json(ROOT/'build/recovered-game/tdm-2/link.json')
                baseline=session.get('baseline_link') if session else None
                if not link['linked'] and (not baseline or baseline.get('linked') or link['unresolved_symbols']!=baseline.get('unresolved_symbols')):
                    raise ValueError('Ordinary source link regressed or has no baseline: '+str(link['unresolved_symbols']))
            # Detect edits that raced verification or the acceptance checks.
            validate_report(report)
            if session: validate_scope(session)
            commit_reports(ledger,{source:report},link)
            record_attempt(target,name,report,card,'PROMOTED_'+claim)
            if session: SESSION.unlink()
            print('PROMOTED',target,name,claim,'(exact function proof; no object/CU claim)')
        except Exception as exc:
            record_attempt(target,name,report,card,'PROMOTION_REJECTED',str(exc))
            raise


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('target'); ap.add_argument('function')
    ap.add_argument('--claim',choices=['FUNCTION_MATCH','BODY_MATCH_LAYOUT_BLOCKED'],default='FUNCTION_MATCH')
    a=ap.parse_args(); promote(a.target,a.function,a.claim)


if __name__=='__main__': main()
