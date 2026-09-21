"""Numbered RTL trace comparisons; textual observations are never matching proof."""
import difflib
import re
from pathlib import Path
from common import identity


def pass_identity(path):
    match=re.search(r'\.(\d+)r\.([A-Za-z0-9_-]+)$',Path(path).name)
    if not match: raise ValueError('Unrecognized numbered RTL dump: '+str(path))
    return int(match[1]),match[2]


def normalize(text,source):
    # Only the exact scratch filename and compiler heap addresses are incidental.
    # Preserve register IDs, alias sets, labels, operands and source line numbers.
    text=text.replace(str(source),'<source>').replace(str(source).replace('\\','/'),'<source>')
    return re.sub(r'(<[A-Za-z_]*decl) 0x[0-9a-f]+',r'\1 <compiler-address>',text)


def compare_passes(baseline,variant,root):
    def index(record):
        result={}
        for item in record.get('focused_rtl_passes',[]):
            key=(item['number'],item['phase'])
            if key in result: raise ValueError('Duplicate numbered RTL pass')
            path=root/item['path']
            if identity(path)!=item['identity']: raise ValueError('RTL evidence changed: '+item['path'])
            if pass_identity(path)!=key: raise ValueError('RTL filename contradicts pass identity')
            result[key]=item
        return result
    a,b=index(baseline),index(variant)
    if not a or not b:return {'state':'NUMBERED_TRACE_UNAVAILABLE'}
    changed=[];equal=0;missing=[]
    for key in sorted(a.keys()|b.keys()):
        if key not in a or key not in b:
            missing.append({'number':key[0],'phase':key[1],'absent_from':'baseline' if key not in a else 'variant'});continue
        x=normalize((root/a[key]['path']).read_text(encoding='utf8'),root/baseline['source'])
        y=normalize((root/b[key]['path']).read_text(encoding='utf8'),root/variant['source'])
        if x==y:equal+=1;continue
        excerpt=[]
        for line in difflib.unified_diff(x.splitlines(),y.splitlines(),n=2):
            excerpt.append(line[:240])
            if len(excerpt)==20:break
        changed.append({'number':key[0],'phase':key[1],'baseline':a[key]['path'],'variant':b[key]['path'],
                        'diff_excerpt':excerpt,'excerpt_limit':{'lines':20,'characters_per_line':240}})
    return {'state':'DIAGNOSTIC_RTL_COMPARISON','equal_passes':equal,'changed_passes':len(changed),
            'first_changed_passes':changed[:3],'omitted_changed_passes':max(0,len(changed)-3),
            'missing_passes':missing,'limit':'Numbered textual trace comparison only. Heap declaration addresses and exact scratch filenames are normalized; register IDs, alias sets and labels are retained. First textual divergence is not proof of a code-generation cause or semantic difference.'}
