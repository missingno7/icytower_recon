"""Run each existing acceptance test group once in a fresh shared interpreter."""
import argparse
import sys
import time
import unittest
from common import ROOT,identity,write_json

GROUPS={
    'function':('test_grinder','test_control_transfers','test_scheduling_diagnostics',
                'test_literal_diagnostics','test_literal_dependencies','test_queue_dependencies','test_interface_scope','test_reference_diagnostics','test_atomic_writes',
                'test_data_owners','test_dwarf_locations','test_compiler_context',
                'test_branch_diagnostics','test_data_tasks'),
    'interface':('test_grinder','test_contribution_diagnostics','test_scheduling_diagnostics','test_control_transfers',
                 'test_literal_diagnostics','test_literal_dependencies','test_queue_dependencies','test_interface_scope','test_reference_diagnostics','test_global_type_tasks',
                 'test_atomic_writes','test_data_owners','test_interface_tasks','test_interface_admission','test_typed_interface_tasks',
                 'test_interface_type_probe','test_dwarf_locations','test_compiler_context',
                 'test_branch_diagnostics','test_data_tasks','test_type_views','test_type_headers','test_type_dependencies',
                 'test_local_declarations','test_stack_diagnostics','test_storage_diagnostics','test_static_scope_tasks')}


def load_group(name,loader=None):
    modules=GROUPS[name]
    if not modules or len(set(modules))!=len(modules): raise ValueError('Empty or duplicate acceptance test inventory')
    loader=loader or unittest.TestLoader();suite=unittest.TestSuite();counts={}
    for module in modules:
        tests=loader.loadTestsFromName(module);counts[module]=tests.countTestCases()
        if not counts[module]: raise ValueError('Acceptance test module has no tests: '+module)
        suite.addTests(tests)
    return suite,counts


def execute(name,runner=None):
    modules=GROUPS[name]
    output=ROOT/'build/acceptance/tests'/(name+'.json')
    output.unlink(missing_ok=True)
    paths={m:'tools/'+m+'.py' for m in modules}
    before={m:identity(ROOT/p) for m,p in paths.items()}
    started=time.perf_counter();suite,counts=load_group(name)
    result=(runner or unittest.TextTestRunner(verbosity=1,buffer=True)).run(suite)
    after={m:identity(ROOT/p) for m,p in paths.items()}
    passed=result.wasSuccessful() and result.testsRun==sum(counts.values()) and before==after
    report={'group':name,'module_test_counts':counts,'module_identities':before,'tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'unexpected_successes':len(result.unexpectedSuccesses),'test_inputs_unchanged':before==after,
            'seconds':round(time.perf_counter()-started,3),'passed':passed,
            'scope':'Fresh process execution; no cached test success. Existing acceptance modules are retained; compilation, link and global audit remain separate gates.'}
    write_json(output,report)
    print('%s acceptance tests: %d tests in %d modules; %.3fs; %s'%(name,result.testsRun,len(counts),report['seconds'],'PASS' if passed else 'FAIL'),flush=True)
    return 0 if passed else 1


def main():
    ap=argparse.ArgumentParser();ap.add_argument('group',choices=GROUPS);args=ap.parse_args()
    return execute(args.group)


if __name__=='__main__':raise SystemExit(main())
