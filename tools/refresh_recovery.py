"""Publish fresh evidence for all 25 CUs. Never reuse historical status claims."""
import argparse
import os
from common import ROOT, read_json, write_json, identity, check_json
from build import TARGETS, verify_inputs
from recovery_pipeline import fresh_verify, check_fixture, CURRENT, publish_cards, validate_report, reanalyze_report
from classify_diff import workflow
from interfaces import publish_interfaces


def entry_from_report(report, report_path, prior=None):
    entry=dict(prior or {})
    if entry.get('report','').startswith('docs/experiments/'):
        entry['historical_report']=entry.pop('report')
    entry.update(functions={r['name']:r['status'] for r in report['functions']},
                 function_complete=all(r['status']=='FUNCTION_MATCH' for r in report['functions']),
                 text_contribution_equal=report['whole_text_contribution_equal'],object_match=False,cu_match=False,
                 verified_report=report_path.relative_to(ROOT).as_posix(),verified_report_identity=identity(report_path),
                 state='VERIFIED_FUNCTION_EVIDENCE',
                 function_dimensions={r['name']:{'source':'RECOVERED' if r['status']=='FUNCTION_MATCH' else 'INCOMPLETE' if r['status']=='MISSING' else 'CANDIDATE',
                   'semantic':'VERIFIED' if r['status']=='FUNCTION_MATCH' else 'UNVERIFIED','difference':workflow(r)['difference_class']} for r in report['functions']},
                 workflow={r['name']:workflow(r) for r in report['functions']})
    return entry


def validate_ledger(ledger,check_sources=True):
    lock=ROOT/'build/grinder/promotion.lock'
    if lock.exists() and lock.read_text().strip()!=str(os.getpid()):
        raise ValueError('Promotion transaction in progress; retry after it finishes')
    units={u['source']:u for u in read_json(ROOT/'src/units.json')}
    if set(ledger)!=set(units): raise ValueError('Ledger must cover all 25 historical CUs')
    for source,entry in ledger.items():
        if not entry.get('verified_report'): raise ValueError('Ledger has no verified receipt: '+source)
        path=ROOT/entry['verified_report']
        if identity(path)!=entry['verified_report_identity']: raise ValueError('Report receipt changed: '+source)
        report=read_json(path); validate_report(report,check_sources)
        if report['build']['config']['source']!=source: raise ValueError('Wrong report owner: '+source)
        if {r['name']:r['status'] for r in report['functions']}!=entry['functions']: raise ValueError('Ledger status contradicts verified report: '+source)
        if {r['name']:workflow(r) for r in report['functions']}!=entry.get('workflow'): raise ValueError('Ledger workflow contradicts verified report: '+source)
        if set(entry['functions'])!={f['name'] for f in units[source]['functions']}: raise ValueError('Incomplete function inventory: '+source)
        if entry.get('function_dimensions')!={r['name']:{'source':'RECOVERED' if r['status']=='FUNCTION_MATCH' else 'INCOMPLETE' if r['status']=='MISSING' else 'CANDIDATE','semantic':'VERIFIED' if r['status']=='FUNCTION_MATCH' else 'UNVERIFIED','difference':workflow(r)['difference_class']} for r in report['functions']}: raise ValueError('False persistent classification')
        if entry.get('object_match') or entry.get('cu_match'): raise ValueError('Unproven object/CU claim')
        if entry.get('function_complete')!=all(r['status']=='FUNCTION_MATCH' for r in report['functions']): raise ValueError('False CU function completion')
        if entry.get('text_contribution_equal')!=report['whole_text_contribution_equal']: raise ValueError('False text contribution claim')


def publish_status(ledger,check=False):
    emit=check_json if check else write_json
    from progress import blocker_summary
    from recovery_state import progress_document
    progress=progress_document(ledger)
    for path in ('docs/progress.json','docs/current/progress.json'): emit(ROOT/path,progress)
    emit(ROOT/'docs/blocker-summary.json',blocker_summary(ledger))
    publish_interfaces(ledger,check)
    from type_tasks import publish_types
    publish_types(ledger,check)
    from type_views import publish_views
    publish_views(ledger,check)
    from local_declarations import publish_locals
    publish_locals(ledger,check)
    from source_order import publish_orders
    publish_orders(ledger,check)
    from array_tasks import publish_arrays
    publish_arrays(ledger,check)
    from data_tasks import publish_data_tasks
    publish_data_tasks(ledger,check)
    from storage_diagnostics import publish_storage
    publish_storage(ledger,check)
    from static_scope_tasks import publish_scopes
    publish_scopes(ledger,check)
    from global_type_tasks import publish as publish_globals
    publish_globals(ledger,check)
    publish_cards(ledger,check)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--verify-all',action='store_true',help='Fresh-compile all historical game CUs and rebuild verified ledger receipts.')
    ap.add_argument('--reanalyze',action='store_true',help='Refresh diagnostics from source-current proofs without recompiling.')
    ap.add_argument('--check',action='store_true',help='Verify every current derived document without changing it.')
    a=ap.parse_args()
    if sum((a.check,a.verify_all,a.reanalyze))>1: raise ValueError('Choose check, verify-all or reanalyze')
    ledger=read_json(ROOT/'src/recovery.json')
    if a.verify_all or a.reanalyze:
        staged=[]
        verify_inputs('tdm-2'); check_fixture()
        for target,config in TARGETS.items():
            if not config['source'].startswith('src/'): continue
            report=reanalyze_report(read_json(ROOT/ledger[config['source']]['verified_report'])) if a.reanalyze else fresh_verify(target,locked=True)
            prior=ledger.get(config['source'],{})
            if prior.get('verified_report'):
                from promote_function import no_regressions
                no_regressions(read_json(ROOT/prior['verified_report']),report)
            staged.append((target,config,report))
            print(target,report['function_matches'],'/',report['functions_total'],flush=True)
        from promote_function import promotion_lock, JOURNAL
        from publication import publication
        with promotion_lock(), publication([ROOT/'src/recovery.json',ROOT/'docs/progress.json',ROOT/'docs/blocker-summary.json',*CURRENT.rglob('*')],CURRENT,JOURNAL,ROOT):
            for target,config,report in staged:
                path=CURRENT/'reports'/(target+'.json'); write_json(path,report)
                ledger[config['source']]=entry_from_report(report,path,ledger.get(config['source']))
            validate_ledger(ledger)
            path=ROOT/'src/recovery.pending.json'; write_json(path,ledger); os.replace(path,ROOT/'src/recovery.json')
            publish_status(ledger)
        print('Published fresh verified state atomically.')
        return
    else:
        validate_ledger(ledger)
    publish_status(ledger,a.check)
    print('Published authoritative cards, queue, interfaces, progress and blockers.')


if __name__=='__main__': main()
