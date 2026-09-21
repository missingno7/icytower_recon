"""Worker diagnostics survive build cleanup, including long rejected-stage output."""
import contextlib
import io
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import mechanical_grinder
import pattern_grinder


class RunArtifactTests(unittest.TestCase):
    def exercise(self, module, kind, rejected):
        with tempfile.TemporaryDirectory() as temporary, contextlib.ExitStack() as stack:
            root = Path(temporary)
            (root / 'build').mkdir()
            stack.enter_context(patch.object(module, 'ROOT', root))
            stack.enter_context(patch.object(module, 'SESSION', root / 'build/session.json'))
            stack.enter_context(patch.object(module, 'busy', return_value=False))
            stack.enter_context(patch.object(module, 'read_json', return_value={'tasks': []}))
            task = {'function': 'sample', 'task_kind': 'INTERFACE', 'source': 'src/sample.c',
                    'target': 'game-sample', 'difficulty': 'CHEAP'}
            stack.enter_context(patch.object(module, 'select_task', return_value=task))
            if kind == 'pattern':
                stack.enter_context(patch.object(module, 'command', return_value=['python', 'fixture.py']))
            diagnostic = 'first mismatch: 17\n' + 'instruction detail\n' * 400
            stack.enter_context(patch.object(module.subprocess, 'run', return_value=SimpleNamespace(
                returncode=10 if rejected else 0, stdout='candidate diagnostics\n', stderr=diagnostic)))

            def execute(task, invoke, state, busy):
                result = invoke('check', task['function'])
                self.assertEqual(result['stderr'], diagnostic)
                return {'state': 'BLOCKED_SUPERVISOR' if rejected else 'PROMOTED', 'continue': True}

            stack.enter_context(patch.object(module, 'execute_task', side_effect=execute))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(module.run_batch(1), 0)
            shutil.rmtree(root / 'build')
            history, = (root / 'docs/attempts' / (kind + '-runs')).glob('*.jsonl')
            rows = [json.loads(line) for line in history.read_text().splitlines()]
            stage, = [row for row in rows if row['event'] == 'STAGE']
            self.assertTrue(stage['log'].startswith('docs/attempts/'))
            log = json.loads((root / stage['log']).read_text())
            self.assertEqual(log['stderr'], diagnostic)
            self.assertEqual(log['stdout'], 'candidate diagnostics\n')
            self.assertEqual(log['returncode'], 10 if rejected else 0)
            summary = json.loads((history.with_suffix('') / 'summary.json').read_text())
            self.assertEqual(summary['outcomes'][0]['state'], rows[-1]['state'])

    def test_mechanical_success_and_rejection_survive_cleanup(self):
        for rejected in (False, True):
            with self.subTest(rejected=rejected):
                self.exercise(mechanical_grinder, 'mechanical', rejected)

    def test_pattern_success_and_rejection_survive_cleanup(self):
        for rejected in (False, True):
            with self.subTest(rejected=rejected):
                self.exercise(pattern_grinder, 'pattern', rejected)


if __name__ == '__main__':
    unittest.main()
