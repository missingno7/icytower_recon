"""Conservative source-spelled call arity; never a replacement for compiler typing."""
import re
from source_scope import sanitized
from source_order import definition_spans
from literal_diagnostics import TOKEN


def conflicts(text,name,expected):
    clean=list(sanitized(text))
    # Literal arguments remain nonempty; commas/braces inside them stay masked.
    for token in TOKEN.finditer(text):
        if token[0].startswith(('"',"'")):clean[token.start()]='0'
    clean=''.join(clean);functions=definition_spans(text);result=[]
    fixed=len(expected['parameter_types']);variadic=expected.get('variadic',False)
    for match in re.finditer(r'\b'+re.escape(name)+r'\s*\(',clean):
        owners=[f for f in functions if f['body_start']<match.start()<f['end']]
        if len(owners)!=1:continue
        if re.search(r'(?:\.|->)\s*$',clean[:match.start()]):continue
        line_start=clean.rfind('\n',0,match.start())+1
        if clean[line_start:match.start()].lstrip().startswith('#'):continue
        stack=[')'];at=match.end();start=at;spans=[];valid=True
        while at<owners[0]['end'] and stack:
            c=clean[at]
            if c in '([{':stack.append({'(':')','[':']','{':'}'}[c])
            elif c in ')]}':
                if c!=stack.pop():valid=False;break
                if not stack:
                    if clean[start:at].strip():spans.append((start,at))
                    elif spans:valid=False
                    break
            elif c==',' and len(stack)==1:
                if not clean[start:at].strip():valid=False;break
                spans.append((start,at));start=at+1
            at+=1
        if stack or not valid:continue
        count=len(spans)
        if count==fixed or variadic and count>=fixed:continue
        result.append({'caller':owners[0]['name'],'line':text.count('\n',0,match.start())+1,
            'callee':name,'observed_argument_groups':count,'historical_fixed_parameters':fixed,'historical_variadic':variadic,
            'arguments':[text[a:b].strip()[:160] for a,b in spans[:8]],'omitted_arguments':max(0,count-8),
            'state':'SOURCE_ARGUMENT_COUNT_CONFLICT',
            'limit':'Source spelling before macro expansion; review macros and caller semantics. This blocks a mechanical prototype edit, never proves argument types or authorizes removing arguments.'})
    return result
