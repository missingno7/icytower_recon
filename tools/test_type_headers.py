"""Generated headers import only declaration owners required by their DWARF types."""
import unittest
from common import ROOT,run
from build import COMPILERS,verify_inputs
from generate_types import type_header,header_dependencies
from type_graph import graph


class HeaderTests(unittest.TestCase):
    def test_builtin_profile_and_control_do_not_import_library_interfaces(self):
        for name in ('Tprofile','Tcontrol','Toptions','Tmenu'):
            header=type_header(graph(),name)
            self.assertNotIn('#include <allegro.h>',header)
            self.assertNotIn('#include <stdio.h>',header)
            self.assertIn('RECOVERED_STATIC_ASSERT',header)

    def test_external_declaration_owner_is_still_included(self):
        headers=[type_header(graph(),name) for name in graph().game_types]
        self.assertTrue(any('#include <allegro.h>' in h for h in headers))
        for name in graph().game_types:
            deps,external=header_dependencies(graph(),name)
            header=type_header(graph(),name)
            for dep in deps: self.assertIn('#include "'+dep+'.h"',header)
            for dep in external: self.assertIn('#include <'+dep+'>',header)

    def test_builtin_header_compiles_with_partial_library_interfaces(self):
        verify_inputs('tdm-2'); folder=ROOT/'build/type-header-tests'; folder.mkdir(parents=True,exist_ok=True)
        source=folder/'isolated.c'
        source.write_text('extern void *font;\nextern int rest(int);\n#include "recovered/Tprofile.h"\nint layout_probe(void) { return sizeof(Tprofile)+offsetof(Tprofile,jump_hold); }\n')
        run([COMPILERS['tdm-2']/'bin/gcc.exe','-O2','-g','-DALLEGRO_STATICLINK','-Iinclude','-Ithird_party/allegro-4.4.1/include','-c',source,'-o',folder/'isolated.o'],toolchain=COMPILERS['tdm-2'])

    def test_all_generated_headers_compile_together(self):
        verify_inputs('tdm-2'); folder=ROOT/'build/type-header-tests'; folder.mkdir(parents=True,exist_ok=True)
        source=folder/'all.c'; headers=sorted((ROOT/'include/recovered').glob('*.h'))
        self.assertEqual(len(headers),len(graph().game_types))
        source.write_text('\n'.join('#include "recovered/'+h.name+'"' for h in headers)+'\n')
        run([COMPILERS['tdm-2']/'bin/gcc.exe','-O2','-g','-DALLEGRO_STATICLINK','-Iinclude','-Ithird_party/allegro-4.4.1/include','-c',source,'-o',folder/'all.o'],toolchain=COMPILERS['tdm-2'])


if __name__=='__main__': unittest.main()
