import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from common import write_bytes_if_changed,write_json
from publication import restore


class AtomicWriteTests(unittest.TestCase):
    def test_unchanged_json_never_opens_a_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'row.json'; self.assertTrue(write_json(path,{'a':1}))
            stamp=path.stat().st_mtime_ns
            with patch('common.tempfile.mkstemp',side_effect=AssertionError('Unexpected write')):
                self.assertFalse(write_json(path,{'a':1}))
            self.assertEqual(path.stat().st_mtime_ns,stamp)

    def test_failed_replace_keeps_original_and_removes_temporary(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'row.json'; path.write_bytes(b'original')
            with patch('common.os.replace',side_effect=OSError(22,'injected publication failure')):
                with self.assertRaises(OSError): write_bytes_if_changed(path,b'new')
            self.assertEqual(path.read_bytes(),b'original'); self.assertEqual(list(Path(folder).iterdir()),[path])

    def test_partial_write_failure_never_truncates_published_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'row.json'; path.write_bytes(b'original')
            with patch('common.os.fsync',side_effect=OSError('injected disk failure')):
                with self.assertRaises(OSError): write_bytes_if_changed(path,b'new')
            self.assertEqual(path.read_bytes(),b'original'); self.assertEqual(list(Path(folder).iterdir()),[path])

    def test_restore_changes_only_different_files(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder).resolve(); a=root/'a'; b=root/'b'; extra=root/'extra'
            a.write_bytes(b'same'); b.write_bytes(b'changed'); extra.write_bytes(b'unpublished')
            stamp=a.stat().st_mtime_ns
            restore({a:b'same',b:b'old'},root)
            self.assertEqual(a.stat().st_mtime_ns,stamp); self.assertEqual(b.read_bytes(),b'old'); self.assertFalse(extra.exists())


if __name__=='__main__': unittest.main()
