"""Bounded DWARF interface repairs: preview, apply, focused check and verified acceptance."""
import argparse
import json
import sys
from task_outcomes import CandidateRejected, CANDIDATE_REJECTED_EXIT, candidate_check
from common import ROOT, read_json, write_json, identity, run, sha, write_bytes_if_changed
from build import verify_inputs
from recovery_pipeline import CURRENT, fresh_verify, validate_report, check_fixture
from refresh_recovery import validate_ledger
from grinder_task import SESSION, snapshot_files
from interface_tasks import plan_interface, patch_text, signature, contribution_fingerprint
from interfaces import declarations, collect_interfaces
from source_scope import body_hash
from promote_function import promotion_lock, no_regressions, commit_reports


def active(name):
    session=read_json(SESSION)
    if session.get('kind')!='INTERFACE' or session['function']!=name: raise ValueError('Different task is active')
    return session


def validate_interface_scope(session, applied=None):
    if session['plan']['task_kind'] not in {'INTERFACE','CANONICAL_TYPE','TYPE_VIEW','SOURCE_ORDER','ARRAY_EXTENT','DATA_POINTER','LOCAL_DECLARATION','STATIC_SCOPE','GLOBAL_TYPE','POINTEE_TYPE'}:
        raise ValueError('Unknown mechanical task kind')
    current=snapshot_files(); before=session['files']; sources=session['sources']
    for path in set(current)|set(before):
        if path not in sources and current.get(path)!=before.get(path): raise ValueError('Out-of-scope edit: '+path)
    changed=False
    for path,old in sources.items():
        new=patch_text(old,[e for e in session['plan']['changes'] if e['file']==path])
        text=(ROOT/path).read_bytes().decode('cp1252')
        if text not in (old,new): raise ValueError('Edit exceeds the planned declaration spans: '+path)
        if applied is True and text!=new: raise ValueError('Not all planned interface edits have been applied')
        if applied is False and text!=old: raise ValueError('Task has already changed source')
        changed|=text!=old
    if identity(ROOT/'src/recovery.json')!=session['ledger']: raise ValueError('Ledger changed during task')
    ledger=read_json(ROOT/'src/recovery.json')
    validate_ledger(ledger,check_sources=False)
    validate_baseline_sources(session,ledger)
    if session['plan']['task_kind']=='INTERFACE':
        _,conflicts=collect_interfaces(ledger)
        row=next((r for r in conflicts if r['function']==session['function']),None)
        if row is None: raise ValueError('No receipt-derived interface conflict for this task')
        expected=plan_interface(row,ledger,session['sources'])
        if expected!=session['plan']: raise ValueError('Interface plan differs from DWARF/receipt-derived repair')
    if session['plan']['task_kind']=='POINTEE_TYPE':
        from pointee_tasks import plans as pointee_plans
        expected=next((p for p in pointee_plans(ledger,session['sources']) if p['function']==session['function']),None)
        if expected!=session['plan']: raise ValueError('Pointee plan differs from compiled/DWARF evidence')
    return changed


def validate_baseline_sources(session,ledger):
    from interface_tasks import text_identity
    evidence={}
    for entry in ledger.values():
        report=read_json(ROOT/entry['verified_report'])
        for path,value in report['build']['local_inputs'].items():
            if path in session['sources']:
                if path in evidence and evidence[path]!=value: raise ValueError('Conflicting source receipts: '+path)
                evidence[path]=value
    for path,text in session['sources'].items():
        if evidence.get(path)!=text_identity(text): raise ValueError('Saved task source does not match baseline receipt: '+path)


def archive_diagnostic(path, task, target):
    data=path.read_bytes()
    destination=ROOT/'docs/attempts/interface-diagnostics'/task/(target+'-'+sha(data)+'.json')
    write_bytes_if_changed(destination,data)
    return destination.relative_to(ROOT).as_posix()


def failure_context(session):
    """Retain the last failure from this exact plan, never another task attempt."""
    path=ROOT/'docs/attempts/interfaces'/(session['function']+'.jsonl')
    if not path.exists(): return None
    for line in reversed(path.read_text(encoding='utf-8').splitlines()):
        row=json.loads(line)
        if row.get('plan')!=session['plan']: continue
        if row['outcome']=='BEGIN': return None
        if row['outcome'] not in ('FAST_FAILED','PROMOTION_REJECTED'): continue
        details=row['details']; evidence=[]
        for name in details.get('evidence',[]):
            diagnostic=ROOT/name
            if not diagnostic.resolve().is_relative_to((ROOT/'docs/attempts/interface-diagnostics').resolve()): continue
            if not diagnostic.is_file(): continue
            ident=identity(diagnostic)
            if not diagnostic.stem.endswith('-'+ident['sha256']): continue
            data=read_json(diagnostic); changed=data.get('changed_functions',[])
            evidence.append({'path':name,'identity':ident,'changed_function_count':len(changed),
                'changed_functions':[{k:f[k] for k in ('function','source_body_unchanged','size_before','size_after','original_comparison') if k in f} for f in changed[:4]],
                'omitted_changed_functions':max(0,len(changed)-4)})
        return {'outcome':row['outcome'],'error':details.get('error'),
            'evidence':evidence[:3],'omitted_evidence':max(0,len(evidence)-3),
            'limit':'Historical rejected attempt for this source plan; not current proof or permission to edit bodies.'}
    return None


def history(session,outcome,details):
    path=ROOT/'docs/attempts/interfaces'/(session['function']+'.jsonl')
    path.parent.mkdir(parents=True,exist_ok=True)
    row={'outcome':outcome,'function':session['function'],'plan':session['plan'],'details':details}
    with path.open('a',encoding='utf-8') as stream: stream.write(json.dumps(row,separators=(',',':'))+'\n')


def begin(name):
    if SESSION.exists(): raise ValueError('Finish the active task first')
    ledger=read_json(ROOT/'src/recovery.json'); validate_ledger(ledger)
    _,conflicts=collect_interfaces(ledger)
    row=next((r for r in conflicts if r['function']==name),None)
    if row is None:
        from type_tasks import plans
        plan=next((p for p in plans(ledger) if p['function']==name),None)
        if plan is None:
            from source_order import plans as order_plans
            plan=next((p for p in order_plans(ledger) if p['function']==name and p['state']!='NOT_QUEUED'),None)
        if plan is None:
            from array_tasks import plans as array_plans
            plan=next((p for p in array_plans(ledger) if p['function']==name),None)
        if plan is None:
            from data_tasks import plans as data_plans
            plan=next((p for p in data_plans(ledger) if p['function']==name),None)
        if plan is None:
            from type_views import plans as view_plans
            plan=next((p for p in view_plans(ledger) if p['function']==name),None)
        if plan is None:
            from local_declarations import plans as local_plans
            plan=next((p for p in local_plans(ledger) if p['function']==name),None)
        if plan is None:
            from static_scope_tasks import plans as scope_plans
            plan=next((p for p in scope_plans(ledger) if p['function']==name),None)
        if plan is None:
            from global_type_tasks import plans as global_plans
            plan=next((p for p in global_plans(ledger) if p['function']==name),None)
        if plan is None:
            from pointee_tasks import plans as pointee_plans
            plan=next((p for p in pointee_plans(ledger) if p['function']==name),None)
        if plan is None: raise ValueError('No current mechanical task for '+name)
    else: plan=plan_interface(row,ledger)
    if plan['difficulty']!='CHEAP': raise ValueError('Supervisor required: '+plan['reason'])
    session={'kind':'INTERFACE','function':name,'plan':plan,'files':snapshot_files(),'ledger':identity(ROOT/'src/recovery.json'),
             'sources':{p:(ROOT/p).read_bytes().decode('cp1252') for p in plan['sources']},
             'baseline_link':read_json(CURRENT/'link-status.json') if (CURRENT/'link-status.json').exists() else None}
    write_json(SESSION,session)
    history(session,'BEGIN',{'affected_targets':plan['affected_targets']})
    print(plan['task_kind'],name,';',len(plan['changes']),'bounded source edits;',', '.join(plan['affected_targets']))
    print(plan['apply_command'])


def apply(name):
    session=active(name); validate_interface_scope(session,applied=False)
    for path,text in session['sources'].items():
        edits=[e for e in session['plan']['changes'] if e['file']==path]
        (ROOT/path).write_bytes(patch_text(text,edits).encode('cp1252'))
    validate_interface_scope(session,applied=True)
    print('Applied only the planned source spans; all other source is untouched.')


def verify_interface(session,acceptance=False):
    validate_interface_scope(session,applied=True)
    ledger=read_json(ROOT/'src/recovery.json'); reports={}; scheduling=[]; order_effects=[]; local_effect=None
    verify_inputs('tdm-2'); check_fixture()
    for target in session['plan']['affected_targets']:
        report=fresh_verify(target,dest=ROOT/('build/acceptance/interfaces' if acceptance else 'build/fast/interfaces')/session['function']/target,locked=True)
        source=report['build']['config']['source']; old=read_json(ROOT/ledger[source]['verified_report'])
        from contribution_diagnostics import compare as contribution_changes
        detail=ROOT/('build/acceptance/interfaces' if acceptance else 'build/fast/interfaces')/session['function']/target/'contribution-difference.json'
        write_json(detail,contribution_changes(old,report))
        session.setdefault('verification_diagnostics',[]).append(archive_diagnostic(detail,session['function'],target))

        if session['plan']['task_kind']=='GLOBAL_TYPE':
            from global_type_tasks import verify as verify_global
            adaptations=candidate_check(verify_global,old,report,session['plan'],session['sources'][source],(ROOT/source).read_bytes().decode('cp1252'))
            candidate_check(no_regressions,old,report,adaptations)
        else: candidate_check(no_regressions,old,report)
        if session['plan']['task_kind']=='GLOBAL_TYPE':
            pass  # Full declaration, source, allocation and contribution checks ran above.
        elif session['plan']['task_kind']=='SOURCE_ORDER':
            original=session['sources'][source]; current=(ROOT/source).read_bytes().decode('cp1252')
            for name in session['plan']['current_order']:
                if body_hash(original,name)!=body_hash(current,name): raise CandidateRejected('Source-order task modified a function body: '+name)
            before_implicit={d['name'] for d in declarations(old['interfaces_aux']) if d['kind']=='IC'}
            after_implicit={d['name'] for d in declarations(report['interfaces_aux']) if d['kind']=='IC'}
            if after_implicit-before_implicit: raise CandidateRejected('Source order needs explicit interface prerequisites: '+', '.join(sorted(after_implicit-before_implicit)))
            for section in old['initialized_data_comparison']:
                if section['content_equal'] and not any(s['section']==section['section'] and s['content_equal'] for s in report['initialized_data_comparison']):
                    raise CandidateRejected('Previously exact initialized contribution regressed: '+section['section'])
            old_owners={(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in old.get('object_ownership',{}).get('accepted',[])}
            new_owners={(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in report.get('object_ownership',{}).get('accepted',[])}
            if old_owners-new_owners: raise CandidateRejected('Previously proven data owner regressed')
            if contribution_fingerprint(old)['common']!=contribution_fingerprint(report)['common']: raise CandidateRejected('Common allocation changed')
            order_effects.append({'target':target,'exact_functions_before':old['function_matches'],'exact_functions_after':report['function_matches'],
                                  'text_contribution_equal':report['whole_text_contribution_equal'],'bodies_unchanged':True})
        elif session['plan']['task_kind']=='DATA_POINTER':
            from data_tasks import fingerprint,verify_owner
            if fingerprint(old,session['plan'])!=fingerprint(report,session['plan']):
                raise CandidateRejected('Data repair changed code/layout/data/relocations outside its authorized pointer field')
            candidate_check(verify_owner,report,session['plan'])
            old_owners={(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in old.get('object_ownership',{}).get('accepted',[])}
            new_owners={(tuple(o['scope']),o['name'],o['original_va'],o['size']) for o in report.get('object_ownership',{}).get('accepted',[])}
            if old_owners-new_owners: raise CandidateRejected('Data repair regressed a previously proven owner')
        elif session['plan']['task_kind']=='STATIC_SCOPE':
            from static_scope_tasks import verify_scope
            candidate_check(verify_scope,old,report,session['plan'])
        elif session['plan']['task_kind']=='LOCAL_DECLARATION':
            from local_declarations import verify_local,emission_effect
            candidate_check(verify_local,report,session['plan']); local_effect=candidate_check(emission_effect,old,report,session['plan'])
        elif contribution_fingerprint(old)!=contribution_fingerprint(report):
            raise CandidateRejected('Interface repair changed emitted code/data/BSS/symbol/relocation contribution: '+target)
        old_text=next(s['sha256'] for s in old['object_sections'] if s['name']=='.text')
        new_text=next(s['sha256'] for s in report['object_sections'] if s['name']=='.text')
        if old_text!=new_text and session['plan']['task_kind'] not in ('SOURCE_ORDER','LOCAL_DECLARATION'):
            scheduling.append({'target':target,'before':old['candidate_zero_clear_projection'],'after':report['candidate_zero_clear_projection']})
        reports[source]=report
    observed=[]; state='INTERFACE_MATCH'
    if session['plan']['task_kind']=='GLOBAL_TYPE':
        expected=session['plan']['original']['type']; state='GLOBAL_TYPE_MATCH'
    elif session['plan']['task_kind']=='SOURCE_ORDER':
        expected=session['plan']['definition_order']; state='HISTORICAL_SOURCE_ORDER'
    elif session['plan']['task_kind']=='DATA_POINTER':
        expected=session['plan']['changes'][0]['after']; state='DATA_POINTER_MATCH'
    elif session['plan']['task_kind']=='ARRAY_EXTENT':
        plan=session['plan']; owner=plan['historical_owner']; expected=plan['expected_count']; state='ARRAY_EXTENT_MATCH'
        matching=[o for o in reports[plan['source']].get('object_ownership',{}).get('accepted',[])
                  if o['name']==plan['object'] and tuple(o['scope'])==tuple(owner['scope']) and o['original_die']==owner['original_die']]
        if len(matching)!=1: raise CandidateRejected('Array still lacks exact original DWARF type and complete independently resolved initializer')
        result_owner=matching[0]
        if result_owner['dwarf_type']!=owner['dwarf_type']: raise CandidateRejected('Historical array type changed')
    elif session['plan']['task_kind']=='LOCAL_DECLARATION':
        expected=session['plan']['original']['type']; state='LOCAL_DECLARATION_MATCH'
    elif session['plan']['task_kind']=='STATIC_SCOPE':
        expected=session['plan']['original']['scope']; state='STATIC_SCOPE_MATCH'
    elif session['plan']['task_kind']=='POINTEE_TYPE':
        from pointee_tasks import verify as verify_pointee
        candidate_check(verify_pointee,reports[session['plan']['source']],session['plan'])
        expected=session['plan']['canonical']; state='CANONICAL_POINTEE_MATCH'
    elif session['plan']['task_kind']=='TYPE_VIEW':
        from type_views import verify_view
        candidate_check(verify_view,reports[session['plan']['source']],session['plan'])
        expected=session['plan']['canonical']; state='DWARF_MEMBER_MATCH' if session['plan'].get('repair_mode')=='POINTER_MEMBER_ONLY' else 'CANONICAL_VIEW_MATCH'
    elif session['plan']['task_kind']=='CANONICAL_TYPE':
        from generate_types import outputs
        header=ROOT/session['plan']['header']
        if header.read_text(encoding='utf-8')!=outputs()[header]: raise CandidateRejected('Canonical header differs from DWARF generation')
        expected=session['plan']['expected_declaration']; state='CANONICAL_TYPE_MATCH'
    else:
        expected=signature(session['plan']['historical'][0])
        for source,entry in ledger.items():
            report=reports.get(source) or read_json(ROOT/entry['verified_report'])
            for decl in declarations(report['interfaces_aux']):
                if decl['name']==session['function'] and decl['file'].startswith(('src/','include/')):
                    observed.append(decl)
                    if session['plan'].get('typed_caller_repair'):
                        from type_aliases import layout_checks
                        if any(x['status']!='AGREE' for x in layout_checks(decl,session['plan']['historical'][0],report)):
                            raise CandidateRejected('Typed caller interface lacks complete historical layout agreement')
        if not observed or any(signature(d)!=expected for d in observed):
            raise CandidateRejected('Compiler declarations still disagree with the DWARF interface')
    validate_interface_scope(session,applied=True)
    for report in reports.values(): validate_report(report)
    result={'state':state,'function':session['function'],'expected':expected,
            'declarations':observed,'affected_targets':session['plan']['affected_targets'],
            'allocated_layout_and_data_unchanged':session['plan']['task_kind'] not in ('SOURCE_ORDER','DATA_POINTER','GLOBAL_TYPE') and local_effect!='EXACT_FUNCTION',
            'local_declaration_effect':local_effect,
            'local_function_proof':({k:next(r for r in reports[session['plan']['source']]['functions'] if r['name']==session['plan']['target_function'])[k] for k in ('name','status','workflow','original_size','candidate_size','first_difference')} if session['plan']['task_kind']=='LOCAL_DECLARATION' else None),
            'authorized_data_field':({k:session['plan'][k] for k in ('object','field_offset','field_size','section_index','section_offset')} if session['plan']['task_kind']=='DATA_POINTER' else None),
            'source_order_effects':order_effects,'independent_register_clear_reordering':scheduling,
            'function_match_claim':'Function statuses come only from the fresh exact oracle; mechanical task completion is a separate claim.'}
    write_json(ROOT/'build/fast/interfaces'/session['function']/'result.json',result)
    return ledger,reports,result


def check(name):
    session=active(name)
    try:
        _,_,result=verify_interface(session)
        history(session,'FAST_'+result['state'],result)
        print(result['state'],name,'; planned source scope and existing exact proofs preserved')
        print(session['plan']['promotion_command'])
    except Exception as exc:
        history(session,'FAST_FAILED',{'error':str(exc),'failure_kind':'CANDIDATE_REJECTED' if isinstance(exc,CandidateRejected) else 'INFRASTRUCTURE_OR_UNKNOWN','exception':type(exc).__name__,'evidence':session.get('verification_diagnostics',[])})
        for path in session.get('verification_diagnostics',[]): print('Focused contribution evidence:',path,file=sys.stderr)
        raise


def promote(name):
    with promotion_lock():
        session=active(name)
        try:
            ledger,reports,result=verify_interface(session,acceptance=True)
            print(run([sys.executable,'tools/acceptance_tests.py','interface']),end='')
            run([sys.executable,'tools/recovered_game_link.py'])
            link=read_json(ROOT/'build/recovered-game/tdm-2/link.json'); old=session['baseline_link']
            if not link['linked'] and (not old or old.get('linked') or set(link['unresolved_symbols'])!=set(old['unresolved_symbols'])):
                raise ValueError('Ordinary link regressed or lacks a baseline')
            validate_interface_scope(session,applied=True)
            for report in reports.values(): validate_report(report)
            commit_reports(ledger,reports,link)
            history(session,'PROMOTED_'+result['state'],result)
            SESSION.unlink()
            print('PROMOTED '+result['state'],name,'; planned source scope and exact matches preserved')
        except Exception as exc:
            history(session,'PROMOTION_REJECTED',{'error':str(exc),'evidence':session.get('verification_diagnostics',[])})
            raise


def stop(name,reason,blocked=True):
    session=active(name); validate_interface_scope(session)
    history(session,'BLOCKED_SUPERVISOR' if blocked else 'ABORTED',{'reason':reason})
    for path,text in session['sources'].items(): (ROOT/path).write_bytes(text.encode('cp1252'))
    if blocked:
        path=CURRENT/'interface-blocks.json'; blocks=read_json(path) if path.exists() else {}
        blocks[name]={'reason':reason,'changes':session['plan']['changes'],'failure_context':failure_context(session)}; write_json(path,blocks)
    SESSION.unlink()
    from refresh_recovery import publish_status
    ledger=read_json(ROOT/'src/recovery.json'); validate_ledger(ledger); publish_status(ledger)
    print('Restored the exact original source bytes; task', 'blocked for supervisor' if blocked else 'aborted')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('action',choices=['begin','apply','check','promote','block','abort']); ap.add_argument('function'); ap.add_argument('--reason')
    a=ap.parse_args()
    if a.action in ('block','abort'):
        if not a.reason: raise ValueError('A precise failure/reason is required')
        stop(a.function,a.reason,a.action=='block')
    else: globals()[a.action](a.function)


if __name__=='__main__':
    try: main()
    except CandidateRejected as exc:
        print('CANDIDATE_REJECTED:',exc,file=sys.stderr)
        raise SystemExit(CANDIDATE_REJECTED_EXIT)
