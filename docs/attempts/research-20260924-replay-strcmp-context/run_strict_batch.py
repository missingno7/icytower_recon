import json, sys
from pathlib import Path
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / 'tools'))
import tu_context_probe as ctx
from experiment import compare
from recovery_pipeline import OBJDUMP
from common import read_json, write_json, identity
from effective_outcomes import effective_identity

research = ROOT / 'docs/attempts/research-20260924-replay-strcmp-context'
base = 'build/tu-context/game-replay/treplay-post-generated-header-20260924/overlay/src/replay.c'
transaction = read_json(ROOT / 'docs/attempts/tu-context/transactions/replay_treplay_post_generated_20260924.json')
order = transaction['plan']['spec']['order']
(research / 'accepted-emission-order.json').write_text(json.dumps(order, indent=2) + '\n', encoding='utf-8')
accepted = read_json(ROOT / 'build/tu-context/game-replay/treplay-post-generated-header-20260924/comparison.json')
accepted_rows = {row['name']: row for row in accepted['functions']}
summary = {'scope':'Strict diagnostics on the accepted generated Treplay_post-header TU overlay; source and ledger untouched.', 'base':base, 'base_sha256':identity(ROOT/base)['sha256'], 'order':order, 'probes':[]}
for name in ['my-strcmp-baseline', 'my-strcmp-outer-equal-switch', 'my-strcmp-explicit-cfg-labels']:
    label='replay-strcmp-context-'+name
    spec={'research_base':base, 'order':order, 'bodies':{'my_strcmp':f'docs/attempts/research-20260924-replay-strcmp-context/{name}.c'}, 'prototypes':'none'}
    text, edits, headers = ctx.build_text('game-replay','src/replay.c',spec)
    out, ref, build, proc = ctx.compile_overlay('game-replay','src/replay.c',text,label,dumps=True,headers=headers)
    if proc.returncode: raise RuntimeError(proc.stderr)
    report=compare(out/'unit.o',ref['historical_cu'],ROOT/'assets/icytower15.exe',OBJDUMP)
    write_json(out/'comparison.json',report)
    rows={row['name']:row for row in report['functions']}
    target=rows['my_strcmp']
    peers=[n for n,r in accepted_rows.items() if r['status']=='FUNCTION_MATCH']
    losses=[n for n in peers if rows.get(n,{}).get('status')!='FUNCTION_MATCH']
    gains=[n for n,r in rows.items() if r['status']=='FUNCTION_MATCH' and accepted_rows.get(n,{}).get('status')!='FUNCTION_MATCH']
    summary['probes'].append({'name':name,'label':label,'compile':'OK','strict_status':target['status'],'candidate_size':target.get('candidate_size'),'historical_size':target.get('original_size'),'first_difference':target.get('first_difference'),'effective_identity':effective_identity(target),'protected_exact_peers':len(peers),'peer_losses':losses,'peer_gains':gains,'matches_after':report.get('function_matches'),'comparison_path':str((out/'comparison.json').relative_to(ROOT)).replace('\\','/')})
write_json(research/'strict-batch-summary.json',summary)
print(json.dumps(summary,indent=2))
