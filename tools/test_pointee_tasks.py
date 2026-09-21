import copy,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from common import identity
from pointee_tasks import verify


class PointeeGateTests(unittest.TestCase):
    def test_complete_parent_pointee_and_generated_dependency_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);header=root/'Record.h';header.write_text('historical declaration')
            node={'kind':'structure_type','size':4,'members':[{'name':'value','offset':0,'bitfield':False,'layout':{'kind':'base_type','type':'int','size':4}}]}
            types=[{'name':name,'layout':copy.deepcopy(node)} for name in ('Parent','Record')]
            card={'headers':{'Record.h':identity(header)},'parent':'Parent','canonical':'Record'}
            report={'build':{'local_inputs':{'Record.h':identity(header)}}}
            g=SimpleNamespace(game_types={name:[{'type_ref':name}] for name in ('Parent','Record')})
            with patch('pointee_tasks.ROOT',root),patch('pointee_tasks.graph',return_value=g),patch('pointee_tasks.layout',return_value=node),patch('pointee_tasks.interface_typedefs',return_value=types),patch('generate_types.outputs',return_value={header:'historical declaration'}):
                verify(report,card)
                types[1]['layout']['members'][0]['offset']=1
                with self.assertRaisesRegex(ValueError,'Complete compiled'):verify(report,card)
                types[1]['layout']=copy.deepcopy(node)
                report['build']['local_inputs']={}
                with self.assertRaisesRegex(ValueError,'header unverified'):verify(report,card)


if __name__=='__main__':unittest.main()
