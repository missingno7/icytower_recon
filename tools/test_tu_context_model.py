import os, re, subprocess, tempfile, unittest
from pathlib import Path
from tu_context_model import emission_order, callees_from_dump, object_order
from build import COMPILERS

GCC = COMPILERS['tdm-2'] / 'bin' / 'gcc.exe'


def compile_and_dump(src_text, tmp):
    src = Path(tmp) / 't.c'; src.write_text(src_text)
    r = subprocess.run([str(GCC), '-O2', '-mfpmath=387', '-fdump-ipa-cgraph', '-c', 't.c', '-o', 't.o'], cwd=tmp, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    dump = (Path(tmp) / 't.c.000i.cgraph').read_text(errors='replace')
    return dump, Path(tmp) / 't.o'


def defs_of(src_text):
    out = []
    for m in re.finditer(r'(?m)^(static )?(?:void|int) (\w+)\(', src_text): out.append((m.group(2), bool(m.group(1))))
    return out


class EmissionOrderModel(unittest.TestCase):
    def check(self, src_text):
        with tempfile.TemporaryDirectory() as tmp:
            dump, obj = compile_and_dump(src_text, tmp)
            callees, meta = callees_from_dump(dump)
            defs = [(n, s) for n, s in defs_of(src_text)]
            defined = {n for n, (body, flags) in meta.items() if body >= 0 and 'needed' in flags}
            predicted = [n for n in emission_order(defs, callees) if n in defined]
            actual = object_order(obj, defined)
            self.assertEqual(predicted, actual)

    def test_roots_reverse_definition_order(self):
        self.check('int g; void h(void);\n' + '\n'.join('void f%d(void){ if (g) h(); }' % i for i in range(6)) + '\n')

    def test_callers_callees_and_statics(self):
        self.check('int g; void h(void);\n' + '\n'.join('void f%d(void){ if (g) h(); }' % i for i in range(6)) +
                   '\nvoid caller_a(void){ f3(); f1(); }\nvoid f6(void){ if (g) h(); }\nvoid caller_b(void){ caller_a(); f6(); f0(); }\n'
                   'static void s1(void){ if (g) h(); }\nvoid caller_c(void){ s1(); }\n')

    def test_external_first_reference_order(self):
        self.check('int g; void h1(void); void h2(void);\nvoid a(void){ h1(); }\nvoid b(void){ h2(); a(); }\nvoid c(void){ h1(); h2(); }\nvoid d(void){ b(); c(); }\n')


class ScratchCursor(unittest.TestCase):
    def test_peephole_scratch_rotates_across_functions(self):
        src = 'int g; void h(void);\n' + '\n'.join('void f%d(void){ if (g) h(); }' % i for i in range(6)) + '\n'
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 't.c').write_text(src)
            r = subprocess.run([str(GCC), '-O2', '-mfpmath=387', '-S', 't.c', '-o', 't.s'], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            regs = re.findall(r'movl\s+_g, %(e[a-z]x)', (Path(tmp) / 't.s').read_text())
            self.assertEqual(len(regs), 6)
            self.assertEqual(regs, ['eax', 'edx', 'ecx', 'eax', 'edx', 'ecx'])


if __name__ == '__main__':
    unittest.main()
