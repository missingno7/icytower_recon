"""Canonical headers must not reintroduce still-local dependency typedefs."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from type_tasks import plans


class TypeDependencyTests(unittest.TestCase):
    def fixture(self, root):
        (root/'src').mkdir(); (root/'include/recovered').mkdir(parents=True)
        for name,member,dependency in [('Child','int x;',None),('Parent','Child child;','Child'),('Outer','Parent parent;','Parent')]:
            declaration='typedef struct { '+member+' } '+name+';'
            (root/'include'/ (name+'.h')).write_text(declaration)
            (root/'include/recovered'/(name+'.h')).write_text(('#include "'+dependency+'.h"\n' if dependency else '')+declaration)

    def test_transitive_prerequisites_and_automatic_unblocking(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); self.fixture(root)
            with patch('type_tasks.ROOT',root),patch('type_tasks.affected_targets',return_value=['game-example']):
                cards={c['function']:c for c in plans({})}
                self.assertEqual(cards['Child']['difficulty'],'CHEAP')
                self.assertEqual(cards['Parent']['state'],'WAITING_FOR_CANONICAL_DEPENDENCY')
                self.assertEqual({p['function'] for p in cards['Outer']['canonical_dependencies']},{'Child','Parent'})
                (root/'include/Child.h').write_text('#include "recovered/Child.h"')
                cards={c['function']:c for c in plans({})}
                self.assertEqual(cards['Parent']['difficulty'],'CHEAP')
                self.assertEqual([p['function'] for p in cards['Outer']['canonical_dependencies']],['Parent'])

    def test_disjoint_cus_do_not_create_false_prerequisite(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); self.fixture(root)
            with patch('type_tasks.ROOT',root),patch('type_tasks.affected_targets',side_effect=lambda ledger,sources:sources):
                self.assertTrue(all(c['difficulty']=='CHEAP' for c in plans({})))


if __name__=='__main__': unittest.main()
