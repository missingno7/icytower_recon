import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import link_object_cache as cache
from common import identity,write_json


class LinkCacheTests(unittest.TestCase):
    def test_reuse_requires_inputs_object_and_report_identities(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);inputs={'dependencies':{'header':'first'}}
            def compile_fake(target,dest,compiler):
                obj=dest/'unit.o';obj.write_bytes(b'compiled object')
                report={'object':identity(obj),'compiler':compiler}
                write_json(dest/'build.json',report);return obj,report
            with patch.object(cache,'snapshot',side_effect=lambda *a:dict(inputs)),patch.object(cache,'compile_target',side_effect=compile_fake) as build:
                self.assertEqual(cache.obtain('unit',out)[2]['state'],'COMPILED')
                self.assertEqual(cache.obtain('unit',out)[2]['state'],'REUSED')
                inputs['dependencies']={'header':'changed'}
                self.assertEqual(cache.obtain('unit',out)[2]['state'],'COMPILED')
                (out/'unit.o').write_bytes(b'tampered')
                self.assertEqual(cache.obtain('unit',out)[2]['state'],'COMPILED')
                (out/'build.json').write_text('{}')
                self.assertEqual(cache.obtain('unit',out)[2]['state'],'COMPILED')
                self.assertEqual(build.call_count,4)

    def test_compile_race_removes_object_and_never_publishes_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)
            def compile_fake(*args,**kwargs):
                obj=out/'unit.o';obj.write_bytes(b'object');return obj,{}
            with patch.object(cache,'snapshot',side_effect=[{'input':1},{'input':2}]),patch.object(cache,'compile_target',side_effect=compile_fake):
                with self.assertRaisesRegex(ValueError,'changed during compilation'):cache.obtain('unit',out)
            self.assertFalse((out/'unit.o').exists());self.assertFalse((out/'link-cache.json').exists())

    def test_post_link_input_change_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder);(out/'unit.o').write_bytes(b'object')
            receipt={'object':identity(out/'unit.o'),'inputs':{'header':1}}
            with patch.object(cache,'snapshot',return_value={'header':2}):
                with self.assertRaisesRegex(ValueError,'changed during link'):cache.verify('unit',out,receipt)


if __name__=='__main__':unittest.main()
