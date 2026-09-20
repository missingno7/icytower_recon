import copy
import unittest
from literal_diagnostics import diagnose,patterns,decode_string,quote,c_string
from classify_diff import workflow


class Image:
    image_base=0x400000
    sections=[{'name':'.rdata','rva':0x1000,'raw_size':16}]
    def section_bytes(self,section): return b'wb\0'+b'\0'*13


def fixture():
    ins={'address':0,'bytes':'6800000000','mnemonic':'push','assembly':'push $0'}
    old={'address':0x100,'bytes':'6800104000','mnemonic':'push','assembly':'push $0x401000'}
    row={'name':'f','va':0x100,'candidate_offset':0,'instructions':[ins],'status':'DIFFER','masked_equal':True,
         'relocations':[{'symbol':'.rdata','type':6,'equal':False,'function_offset':1,'addend':0,'original_value':0x401000}]}
    return row,[old],{'sections':{'2':b'w\0'.hex()},'relocations':[]},[{'name':'.rdata','index':2}],Image()


class LiteralTests(unittest.TestCase):
    def test_wrong_content_is_source_difference_not_layout(self):
        args=fixture(); row=args[0]; row['literal_diagnostics']=diagnose(*args)
        d=row['literal_diagnostics'][0]
        self.assertEqual((d['candidate_text'],d['original_text']),('w','wb'))
        self.assertEqual(workflow(row)['state'],'SOURCE_DIFFER')
        self.assertTrue(workflow(row)['body_edit_allowed'])
        self.assertEqual(row['status'],'DIFFER')

    def test_equal_payload_is_not_owner_proof(self):
        args=fixture(); args[2]['sections']['2']=b'wb\0'.hex(); row=args[0]
        row['literal_diagnostics']=diagnose(*args)
        self.assertEqual(row['literal_diagnostics'][0]['classification'],'CONTENT_EQUAL_OWNER_UNPROVEN')
        self.assertEqual(workflow(row)['state'],'CODEGEN_SIMILAR')
        self.assertFalse(workflow(row)['body_edit_allowed'])

    def test_misaligned_changed_or_untyped_instructions_reject(self):
        for mutation in ('start','opcode','extent','address','addend','type','overlap','table','duplicate-section'):
            args=fixture(); row,old,snapshot,sections,_=args
            if mutation=='start': old[0]['address']+=1
            elif mutation=='opcode': old[0]['bytes']='b800104000'
            elif mutation=='extent': old[0]['bytes']='68001040'
            elif mutation=='address': old[0]['bytes']='6800105000'; row['relocations'][0]['original_value']=0x501000
            elif mutation=='addend': row['relocations'][0]['addend']=1
            elif mutation=='type': row['relocations'][0]['type']=20
            elif mutation=='overlap': row['relocations'].append(dict(row['relocations'][0],symbol='.data'))
            elif mutation=='table': snapshot['relocations']=[{'section':2,'offset':0}]
            else: sections.append(dict(sections[0],index=3))
            self.assertEqual(diagnose(*args)[0]['classification'],'UNALIGNED_OR_UNTYPED',mutation)

    def test_float_payload_uses_instruction_width_not_string_guess(self):
        args=fixture(); row,old,snapshot,_,exe=args
        row['instructions'][0]['bytes']='d90500000000'; old[0]['bytes']='d90500104000'; row['relocations'][0]['function_offset']=2
        snapshot['sections']['2']=b'\0\0\x80?'.hex()
        exe.section_bytes=lambda s:b'\0\0\x80?'+b'\0'*12
        self.assertEqual(diagnose(*args)[0]['kind'],'FLOAT32')
        snapshot['sections']['2']='0000'
        self.assertEqual(diagnose(*args)[0]['classification'],'UNALIGNED_OR_UNTYPED')

    def test_unique_token_repair_excludes_comments_and_other_bodies(self):
        args=fixture(); row=args[0]; row['literal_diagnostics']=diagnose(*args)
        text='void g(){ h("w"); } void f(){ /* "w" */ h("w"); }'
        p=patterns(row,text)[0]
        self.assertEqual(p['changes'][0]['before'],'"w"'); self.assertEqual(p['changes'][0]['after'],'"wb"')
        self.assertEqual(text[p['changes'][0]['start']:p['changes'][0]['end']],'"w"')

    def test_ambiguous_prefixed_or_concatenated_source_is_not_cheap(self):
        args=fixture(); row=args[0]; row['literal_diagnostics']=diagnose(*args)
        for body in ('h("w"); h("w");','h(L"w");','h("w" "b");','h("w" /* x */ "b");','h(MODE);'):
            self.assertEqual(patterns(row,'void f(){'+body+'}'),[],body)
        row['status']='FUNCTION_MATCH'; self.assertEqual(patterns(row,'void f(){h("w");}'),[])
        row['status']='DIFFER'; row['masked_equal']=False; self.assertEqual(patterns(row,'void f(){h("w");}'),[])

    def test_conflicting_original_payloads_require_supervisor(self):
        args=fixture(); row=args[0]; row['literal_diagnostics']=diagnose(*args)
        d=copy.deepcopy(row['literal_diagnostics'][0]); d['original_hex']=b'rb'.hex(); row['literal_diagnostics'].append(d)
        self.assertEqual(patterns(row,'void f(){h("w");}'),[])

    def test_repeated_tokens_require_distinct_compiler_line_evidence(self):
        args=fixture(); row=args[0]; row['literal_diagnostics']=diagnose(*args)
        row['literal_diagnostics'][0]['candidate_source_lines']=[{'line':2}]
        other=copy.deepcopy(row['literal_diagnostics'][0]); other['candidate_source_lines']=[{'line':3}]
        row['literal_diagnostics'].append(other)
        text='void f(){\n h("w");\n h("w");\n}'
        self.assertEqual(len(patterns(row,text)[0]['changes']),2)
        other['candidate_source_lines']=[{'line':99}]
        self.assertFalse(patterns(row,text))

    def test_c_escapes_and_bounds(self):
        self.assertEqual(decode_string(r'"a\n\t\r\\\"\101\x42"'),b'a\n\t\r\\"AB')
        for token in (r'"\x100"',r'"\400"',r'"a\0b"',r'"\q"'): self.assertIsNone(decode_string(token))
        raw=b'line\n"\\\t'; self.assertEqual(decode_string(quote(raw)),raw)
        self.assertIsNone(c_string(b'a'*4096+b'\0',0)); self.assertIsNone(c_string(b'abc',0))
        self.assertIsNone(c_string(b'a\0',-1)); self.assertIsNone(c_string(b'\x01\0',0))


if __name__=='__main__': unittest.main()
