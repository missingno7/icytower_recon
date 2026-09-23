from pathlib import Path
import re

root = Path('docs/attempts/research-20260923-draw-next')
for directory in ['passes-tree-all', 'passes-tree-rtl-all']:
    print('##', directory)
    for path in sorted((root/directory).glob('main.c.*')):
        text = path.read_text(errors='replace')
        match = re.search(r'Function draw_frame.*?(?=\n;; Function |\Z)', text, re.S)
        if not match:
            continue
        body = match.group(0)
        frame0 = len(re.findall(r'custom\.frame(?:\+0)?', body))
        height = len(re.findall(r'<variable>\.h\+0', body))
        if frame0 or height:
            print('%-30s frame0=%d height=%d' % (path.name, frame0, height))
        if directory == 'passes-tree-rtl-all' and path.name.endswith('r.' + path.name.split('r.', 1)[-1]):
            if 'expand' in path.name or any(x in path.name for x in ['dse2','csa','peephole2','ce3','cprop_hardreg','dce','bbro','mach']):
                blocks = re.split(r'(?=\n\((?:insn|jump_insn|call_insn) )', body)
                ptr = [b for b in blocks if '[23 custom.frame+0 ' in b]
                hs = [b for b in blocks if '[2 <variable>.h+0 ' in b]
                print('  rtl_insns frame0=%d bitmap_height=%d' % (len(ptr), len(hs)))
                if 'dse2' in path.name or 'csa' in path.name or 'peephole2' in path.name or 'ce3' in path.name or 'cprop_hardreg' in path.name or 'dce' in path.name:
                    for block in ptr:
                        first = next((line.strip() for line in block.splitlines() if line.lstrip().startswith(('(insn ', '(jump_insn ', '(call_insn '))), '')
                        src = re.search(r'main\.c:(\d+)', first)
                        print('   ', first[:80], 'line=' + (src.group(1) if src else '?'))
