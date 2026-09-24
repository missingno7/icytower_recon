import json, pathlib, hashlib
root=pathlib.Path('build/tu-context/game-main')
labels=['research-20260924-main-load-character-current','research-20260924-main-load-character-accepted-context']
for label in labels:
 d=json.loads((root/label/'comparison.json').read_text())
 f=next(x for x in d['functions'] if x.get('name')=='load_character')
 raw=bytes.fromhex(''.join(i['bytes'] for i in f['instructions']))
 print(label, hashlib.sha256(raw).hexdigest(),len(f['instructions']),len(raw),f['difference_offsets'],f['status'])
