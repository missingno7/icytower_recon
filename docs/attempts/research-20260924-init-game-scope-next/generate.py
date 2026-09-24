from pathlib import Path
import hashlib
srcpath=Path('src/main.c'); src=srcpath.read_text(encoding='cp1252'); lines=src.splitlines(keepends=True)
body=''.join(lines[2290:2720])
if not body.startswith('int init_game(int argc, char **argv)') or not body.rstrip().endswith('return -1;\n}'):
 raise SystemExit('focused current-card source range failed validation: '+repr(body[:20])+' '+repr(body[-20:]))
body=body.replace('    Tgamepad *pad;\n','',1)
mark='        if (exists("gamepad.txt")) { /* 1763 */\n'
if mark not in body: raise SystemExit('joystick if not found')
body=body.replace(mark,mark+'            Tgamepad *gp;\n            int i;\n',1)
mark='        } else {\n            log2file(" gamepad.txt is missing, setting defaults"); /* 1780 */\n'
if mark not in body: raise SystemExit('joystick else not found')
body=body.replace(mark,'        } else {\n            Tgamepad *gp;\n            log2file(" gamepad.txt is missing, setting defaults"); /* 1780 */\n',1)
a=body.index('if (exists("gamepad.txt"))'); b=body.index('log2file(" no gamepad or joystick found',a)
frag=body[a:b].replace('pad=get_gamepad()','gp=get_gamepad()').replace('pad->','gp->')
body=body[:a]+frag+body[b:]
if 'Tgamepad *pad;' in body or 'pad->' in frag or 'pad=get_gamepad()' in frag: raise SystemExit('incomplete rename')
out=Path('docs/attempts/research-20260924-init-game-scope-next'); out.mkdir(parents=True,exist_ok=True)
(out/'candidate.c').write_text(body,encoding='cp1252')
print('source_sha256='+hashlib.sha256(srcpath.read_bytes()).hexdigest())
print('candidate_sha256='+hashlib.sha256((out/'candidate.c').read_bytes()).hexdigest())
print('candidate_bytes='+str(len(body.encode('cp1252'))))
