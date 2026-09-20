"""Locate explicit positional initializer fields without evaluating C expressions."""
import re
from source_scope import sanitized


def trim(text,a,b):
    while a<b and text[a].isspace(): a+=1
    while b>a and text[b-1].isspace(): b-=1
    return a,b


def elements(text,a,b):
    a,b=trim(text,a,b); clean=sanitized(text)
    if clean[a:a+1]!='{' or clean[b-1:b]!='}': raise ValueError('Explicit nested braces required')
    start=a+1; stack=[]; spans=[]
    for pos in range(start,b-1):
        token=clean[pos]
        if token in '({[': stack.append(token)
        elif token in ')}]':
            if not stack or '({['[')}]'.index(token)]!=stack.pop(): raise ValueError('Unbalanced initializer')
        elif token==',' and not stack:
            spans.append(trim(text,start,pos)); start=pos+1
    if stack: raise ValueError('Unbalanced initializer')
    last=trim(text,start,b-1)
    if last[0]!=last[1]: spans.append(last)
    for low,high in spans:
        if low==high or clean[low:high].lstrip().startswith(('[','.')) or '=' in clean[low:high]:
            raise ValueError('Missing/designated/computed initializer requires review')
    return spans


def field_span(text,name,steps):
    clean=sanitized(text); sites=[]
    pattern=r'\b'+re.escape(name)+r'\s*(?:\[[^\]]*\]\s*)*=\s*\{'
    for match in re.finditer(pattern,clean):
        if clean[:match.start()].count('{')!=clean[:match.start()].count('}'): continue
        start=match.end()-1; depth=1; end=start+1
        while end<len(clean) and depth:
            depth+=(clean[end]=='{')-(clean[end]=='}'); end+=1
        if depth: raise ValueError('Unbalanced global initializer')
        sites.append((start,end))
    if len(sites)!=1: raise ValueError('Unique initialized global definition not isolated')
    span=sites[0]
    for step in steps:
        children=elements(text,*span); index=step['index']
        if not 0<=index<len(children): raise ValueError('Field is implicit rather than an explicit initializer')
        span=children[index]
    return span
