from pathlib import Path
p=Path('src/main.c')
s=p.read_text(encoding='cp1252')
needle='void main_menu_callback(void)\n{'
a=s.index(needle)
depth=0; end=None; in_str=False; esc=False; line_comment=False; block_comment=False
for i in range(s.index('{',a),len(s)):
    c=s[i]; n=s[i+1] if i+1<len(s) else ''
    if line_comment:
        if c=='\n': line_comment=False
        continue
    if block_comment:
        if c=='*' and n=='/': block_comment=False
        continue
    if in_str:
        if esc: esc=False
        elif c=='\\': esc=True
        elif c=='"': in_str=False
        continue
    if c=='/' and n=='/': line_comment=True; continue
    if c=='/' and n=='*': block_comment=True; continue
    if c=='"': in_str=True; continue
    if c=='{': depth+=1
    elif c=='}':
        depth-=1
        if depth==0: end=i+1; break
body=s[a:end]+'\n'
root=Path('docs/attempts/research-20260924-main-menu-callback-next')
(root/'control.c').write_text(body,encoding='cp1252',newline='')
old='''    if (new_rand() % 198 == 1) {                                     /* 5143 */\n        face++;                                                      /* 5144 */\n        if (face == 3)\n            face = 0;\n    }\n'''
new='''    if (new_rand() % 198 == 1)                                       /* 5143 */\n        face++;                                                      /* 5144 */\n    if (face == 3)\n        face = 0;\n'''
assert old in body
(root/'face-wrap-after-rng.c').write_text(body.replace(old,new,1),encoding='cp1252',newline='')
