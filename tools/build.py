"""Compile real historical COFF objects without the original EXE or oracle.

The selected sources are complete CUs; unknown skeletons cannot be targets.
"""
import argparse
import re
from pathlib import Path
from common import ROOT, TC, identity, read_json, run, write_json

TARGETS={
    'game-map': {'source':'src/map.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\map.c','default':'-O2'},
    'game-scroller': {'source':'src/scroller.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\scroller.c','default':'-O2'},
    'game-particle': {'source':'src/particle.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\particle.c','default':'-O2'},
    'game-player': {'source':'src/player.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\player.c','default':'-O2'},
    'game-stars': {'source':'src/stars.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\stars.c','default':'-O2'},
    'game-main': {'source':'src/main.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\main.c','default':'-O2'},
    'game-fld-adspot': {'source':'src/fld_adspot.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\fld_adspot.c','default':'-O2',
                        'flags':['-fno-toplevel-reorder']},
    'game-hisc': {'source':'src/hisc.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\hisc.c','default':'-O2'},
    'game-menu': {'source':'src/menu.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\menu.c','default':'-O2'},
    'game-options': {'source':'src/options.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\options.c','default':'-O2'},
    'game-game-data': {'source':'src/game_data.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\game_data.c','default':'-O2'},
    'game-replay': {'source':'src/replay.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\replay.c','default':'-O2'},
    'game-profile': {'source':'src/profile.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\profile.c','default':'-O2'},
    'allegro-logg': {'source':'third_party/recovered/logg.c','historical_cu':'C:\\Lib\\allegro4\\addons\\logg\\logg.c','default':'-O2',
                     'includes':['third_party/allegro-4.4.1/addons/logg','third_party/libvorbis-1.2.0/include','third_party/libogg-1.1.3/include']},
    'game-directories': {'source':'src/directories.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\directories.c','default':'-O2'},
    'game-custom': {'source':'src/custom.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\custom.c','default':'-O2'},
    'game-csv': {'source':'src/csv.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\csv.c','default':'-O2'},
    'game-httpget': {'source':'src/httpget.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\httpget.c','default':'-O2'},
    'game-loadpng': {'source':'src/loadpng.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\loadpng.c','default':'-O2',
                     'includes':['third_party/libpng-1.2.34','third_party/zlib-1.2.3']},
    'game-savepng': {'source':'src/savepng.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\savepng.c','default':'-O2',
                     'includes':['third_party/libpng-1.2.34','third_party/zlib-1.2.3']},
    'game-regpng': {'source':'src/regpng.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\regpng.c','default':'-O2',
                    'includes':['third_party/libpng-1.2.34','third_party/zlib-1.2.3']},
    'game-strptime': {'source':'src/strptime.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\strptime.c','default':'-O2'},
    'game-timecompat': {'source':'src/timecompat.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\timecompat.c','default':'-O2'},
    'game-beta': {'source':'src/beta.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\beta.c','default':'-O2'},
    'game-control': {'source':'src/control.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\control.c','default':'-O2'},
    'game-timer': {'source':'src/timer.c','historical_cu':'F:\\projects\\icytower\\trunk\\source\\timer.c','default':'-O2'},
    'allegro-timer': {'source':'third_party/allegro-4.4.1/src/timer.c','historical_cu':'C:\\Lib\\allegro4\\src\\timer.c','default':'-O2'},
    'allegro-color': {'source':'third_party/allegro-4.4.1/src/color.c','historical_cu':'C:\\Lib\\allegro4\\src\\color.c','default':'-O2'},
    'allegro-blit': {'source':'third_party/allegro-4.4.1/src/blit.c','historical_cu':'C:\\Lib\\allegro4\\src\\blit.c','default':'-O2'},
}
COMPILERS={'tdm-1':TC,'tdm-2':ROOT/'toolchain/tdm-gcc-4.4.1-tdm-2'}

def verify_inputs(compiler='tdm-1'):
    lock=read_json(ROOT/'toolchain/lock.json')
    for row in lock['inputs']:
        # Runtime assets do not participate in object generation.
        if row['path'].startswith('assets/'): continue
        actual=identity(ROOT/row['path'])
        if actual!={k:row[k] for k in ['size','sha256']}:
            raise ValueError('Build input hash differs: '+row['path'])
    xiph=ROOT/'third_party/xiph-lock.json'
    if xiph.exists():
        for dependency in read_json(xiph)['dependencies']:
            for row in dependency['files']:
                if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                    raise ValueError('Xiph input hash differs: '+row['path'])
    png=ROOT/'third_party/png-lock.json'
    if png.exists():
        for dependency in read_json(png)['dependencies']:
            for row in dependency['files']:
                if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                    raise ValueError('PNG input hash differs: '+row['path'])
        candidate=read_json(png)['link_candidate']
        for key in ['definition','import_library']:
            row=candidate[key]
            path=ROOT/'third_party/libpng-1.2.34'/('libpng3-derived.def' if key=='definition' else 'libpng3.a')
            if identity(path)!=row:
                raise ValueError('PNG link candidate differs: '+str(path))
    if compiler!='tdm-1':
        for row in read_json(ROOT/'toolchain'/f'{compiler}-lock.json')['inputs']:
            if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                raise ValueError('Candidate toolchain input differs: '+row['path'])
    dx=ROOT/'third_party/directx-lock.json'
    if dx.exists():
        for row in read_json(dx)['files']:
            if identity(ROOT/row['path'])!={k:row[k] for k in ['size','sha256']}:
                raise ValueError('DirectX input differs: '+row['path'])

def depfile_inputs(path):
    """Read GCC make dependencies, including continuations and escaped spaces."""
    text = Path(path).read_text().replace('\\\n', '').replace('\\\r\n', '')
    match = re.search(r':\s', text)
    if not match:
        raise ValueError('Invalid GCC dependency file: ' + str(path))
    tokens = re.findall(r'(?:\\[ #\\]|[^\s])+', text[match.end():])
    paths = []
    for token in tokens:
        token = re.sub(r'\\([ #\\])', r'\1', token)
        p = (ROOT / token).resolve()
        p.relative_to(ROOT)  # no untracked external include inputs
        if p not in paths:
            paths.append(p)
    if not paths:
        raise ValueError('Empty GCC dependency set')
    return paths


def compile_target(target,flags=None,dest=None,compiler='tdm-1'):
    tc=COMPILERS[compiler]
    config=TARGETS[target]
    flags=[*(flags or [config['default']]),*config.get('flags',[])]
    out=dest or ROOT/'build/objects'/compiler/target
    out.mkdir(parents=True,exist_ok=True)
    obj=out/'unit.o'
    # Remove the old object before invoking the compiler: failed builds must
    # not leave a stale successful object in the expected output location.
    obj.unlink(missing_ok=True)
    (out/'build.json').unlink(missing_ok=True)
    args=[tc/'bin/gcc.exe',*flags,'-g','-mfpmath=387','-DALLEGRO_STATICLINK',
          '-Iinclude','-Ithird_party/allegro-4.4.1/include','-MMD','-MF',out/'unit.d','-aux-info',out/'interfaces.aux',
          *['-I'+p for p in config.get('includes',[])],'-c',config['source'],'-o',obj]
    # Establish the actual include closure before compilation, then reject races.
    dep_args=[tc/'bin/gcc.exe',*flags,'-g','-mfpmath=387','-DALLEGRO_STATICLINK',
              '-Iinclude','-Ithird_party/allegro-4.4.1/include',*['-I'+p for p in config.get('includes',[])],
              '-MM','-MF',out/'before.d',config['source']]
    run(dep_args,toolchain=tc)
    before={p.relative_to(ROOT).as_posix():identity(p) for p in depfile_inputs(out/'before.d')}
    run(args,toolchain=tc)
    after={p.relative_to(ROOT).as_posix():identity(p) for p in depfile_inputs(out/'unit.d')}
    if before!=after:
        obj.unlink(missing_ok=True)
        raise ValueError('Source/dependency changed during compilation: '+target)
    run([tc/'bin/objdump.exe','-drt',obj],out/'object.txt',toolchain=tc)
    local_files=depfile_inputs(out/'unit.d')
    report={'target':target,'historical_cu':config['historical_cu'],'flags':flags,'compiler':compiler,
            'command':[str(x) for x in args],'object':identity(obj),
            'dependency_file':identity(out/'unit.d'), 'config':config, 'inputs_verified_around_compile':True,
            'toolchain_lock':identity(ROOT/'toolchain/lock.json'),
            'local_inputs':{p.relative_to(ROOT).as_posix():identity(p) for p in local_files}}
    if compiler!='tdm-1': report['candidate_toolchain_lock']=identity(ROOT/'toolchain'/f'{compiler}-lock.json')
    write_json(out/'build.json',report)
    return obj,report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('targets',nargs='*',choices=list(TARGETS),default=['game-timer'])
    ap.add_argument('--opt',default=None)
    ap.add_argument('--compiler',choices=list(COMPILERS),default='tdm-1')
    a=ap.parse_args()
    verify_inputs(a.compiler)
    for target in a.targets:
        obj,_=compile_target(target,[a.opt] if a.opt else None,compiler=a.compiler)
        print(obj)

if __name__=='__main__': main()
