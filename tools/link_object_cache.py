"""Verified object reuse for ordinary link only; never function-oracle evidence."""
import hashlib
import json
import os
from common import ROOT, identity, read_json, run, write_json
from build import COMPILERS, TARGETS, compile_target, depfile_inputs


def snapshot(target, compiler, out):
    config=TARGETS[target];tc=COMPILERS[compiler]
    flags=[config['default'],*config.get('flags',[])]
    out.mkdir(parents=True,exist_ok=True)
    dep=out/'cache-scan.d';preprocessed=out/'cache-scan.i'
    args=[tc/'bin/gcc.exe',*flags,'-g','-mfpmath=387','-DALLEGRO_STATICLINK',
          '-Iinclude','-Ithird_party/allegro-4.4.1/include',
          *['-I'+p for p in config.get('includes',[])],
          '-E','-MD','-MF',dep,config['source'],'-o',preprocessed]
    # Real preprocessing also detects include shadowing and environment macros.
    run(args,toolchain=tc)
    dependencies={p.relative_to(ROOT).as_posix():identity(p) for p in depfile_inputs(dep)}
    locks=['toolchain/lock.json']
    if compiler!='tdm-1':locks.append('toolchain/'+compiler+'-lock.json')
    return {'target':target,'compiler':compiler,'config':config,'flags':flags,
            'preprocessed':identity(preprocessed),'dependencies':dependencies,
            'tools':{p:identity(ROOT/p) for p in ['tools/build.py','tools/common.py','tools/link_object_cache.py']},
            'locks':{p:identity(ROOT/p) for p in locks},
            # Hash only: never persist environment values (possibly credentials).
            'environment':hashlib.sha256(json.dumps(dict(os.environ),sort_keys=True).encode()).hexdigest()}


def obtain(target, out, compiler='tdm-2'):
    stamp=out/'link-cache.json';obj=out/'unit.o';report_path=out/'build.json'
    before=snapshot(target,compiler,out)
    try:
        saved=read_json(stamp);report=read_json(report_path)
        reusable=(saved['inputs']==before and saved['object']==identity(obj)==report['object']
                  and saved['report']==identity(report_path))
    except (OSError,ValueError,KeyError,TypeError):reusable=False
    if reusable:
        return obj,report,{'state':'REUSED','inputs':before,'object':identity(obj)}
    stamp.unlink(missing_ok=True)
    obj,report=compile_target(target,dest=out,compiler=compiler)
    after=snapshot(target,compiler,out)
    if before!=after:
        obj.unlink(missing_ok=True)
        raise ValueError('Link inputs changed during compilation: '+target)
    saved={'inputs':after,'object':identity(obj),'report':identity(report_path)}
    write_json(stamp,saved)
    return obj,report,{'state':'COMPILED','inputs':after,'object':saved['object']}


def verify(target,out,receipt,compiler='tdm-2'):
    if identity(out/'unit.o')!=receipt['object'] or snapshot(target,compiler,out)!=receipt['inputs']:
        raise ValueError('Link object or inputs changed during link: '+target)
