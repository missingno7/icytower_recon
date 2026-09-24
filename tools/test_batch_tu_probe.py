import unittest

import batch_tu_probe as batch
import effective_outcomes


class BatchDiagnosticsTests(unittest.TestCase):
    def function(self, unknown_call=False):
        return {
            "candidate_offset": 100,
            "candidate_size": 16,
            "original_size": 16,
            "first_difference": {"offset": 6},
            "difference_offsets": [6],
            "instructions": [
                {"address": 100, "bytes": "55", "mnemonic": "push", "assembly": "push %ebp"},
                {"address": 101, "bytes": "83ec10", "mnemonic": "sub", "assembly": "sub $0x10,%esp"},
                {"address": 104, "bytes": "e800000000", "mnemonic": "call", "assembly": "call target"},
                {"address": 109, "bytes": "7502", "mnemonic": "jne", "assembly": "jne target"},
                {"address": 111, "bytes": "8b0500000000", "mnemonic": "mov", "assembly": "mov data,%eax"},
            ],
            "relocations": [
                {"function_offset": 5, "symbol": "_callee", "equal": True},
                {"function_offset": 13, "symbol": ".rdata", "equal": False},
            ] if not unknown_call else [
                {"function_offset": 13, "symbol": ".rdata", "equal": False},
            ],
            "direct_transfers": [],
        }

    def test_mechanical_metrics_and_first_instruction(self):
        detail = batch.codegen_diagnostics(
            self.function(), {"function_matches": 1, "functions_total": 2}, effective_outcomes)
        self.assertEqual(detail["frame"], "0x10")
        self.assertEqual((detail["branches"], detail["calls"]), (1, 1))
        self.assertEqual(detail["call_targets"], ["_callee"])
        self.assertEqual((detail["non_call_relocations"], detail["unequal_non_call_relocations"]), (1, 1))
        self.assertEqual(detail["first_candidate_instruction"]["offset"], 4)
        self.assertTrue(detail["first_candidate_instruction"]["relocation_operand"])

    def test_unknown_call_owner_does_not_claim_order(self):
        report = {"function_matches": 1, "functions_total": 2}
        known = batch.codegen_diagnostics(self.function(), report, effective_outcomes)
        unknown = batch.codegen_diagnostics(self.function(unknown_call=True), report, effective_outcomes)
        self.assertEqual(batch.baseline_delta(known, known)["call_target_order_equal"], True)
        self.assertIsNone(batch.baseline_delta(unknown, known)["call_target_order_equal"])
        self.assertEqual(batch.baseline_delta(unknown, known)["calls"], 0)

    def test_same_cu_direct_transfer_identifies_call(self):
        function = self.function(unknown_call=True)
        function["direct_transfers"] = [{"instruction_offset": 4,
                                         "transfer_kind": "call",
                                         "target_function": "helper"}]
        detail = batch.codegen_diagnostics(
            function, {"function_matches": 1, "functions_total": 2}, effective_outcomes)
        self.assertEqual(detail["call_targets"], ["helper"])


if __name__ == "__main__":
    unittest.main()
