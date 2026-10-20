import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts' / 'ledger.py'
spec = importlib.util.spec_from_file_location('ledger', SCRIPT)
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'record.json'
        self.cli('init', '--project', 'Bottle', '--currency', 'USD', '--members', 'Matt', 'Ana', 'Sam')

    def cli(self, *args, fails=False):
        result = subprocess.run([sys.executable, str(SCRIPT), '--file', str(self.path), *args],
                                capture_output=True, text=True)
        if fails:
            self.assertNotEqual(result.returncode, 0)
            return result.stderr
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def cost(self, *extra, **kw):
        return self.cli('cost', '--key', 'cost-1', '--vendor', 'Supabase', '--payer', 'Matt',
                        '--amount', '25.00', '--date', '2026-10-20', *extra, **kw)

    def test_three_way_split_and_partial_then_full_reimbursement(self):
        result = self.cost()
        self.assertEqual(result['entry']['shares'], {'Matt': 834, 'Ana': 833, 'Sam': 833})
        self.assertEqual(result['balance_cents'], {'Matt': 1666, 'Ana': -833, 'Sam': -833})
        part = self.cli('settle', '--key', 'pay-1', '--from', 'Ana', '--to', 'Matt',
                        '--amount', '5', '--date', '2026-10-21')
        self.assertEqual(part['balance_cents'], {'Matt': 1166, 'Ana': -333, 'Sam': -833})
        self.cli('settle', '--key', 'pay-2', '--from', 'Ana', '--to', 'Matt',
                 '--amount', '3.33', '--date', '2026-10-21')
        done = self.cli('settle', '--key', 'pay-3', '--from', 'Sam', '--to', 'Matt',
                        '--amount', '8.33', '--date', '2026-10-21')
        self.assertTrue(all(value == 0 for value in done['balance_cents'].values()))
        self.assertEqual(done['total_cost_cents'], 2500)

    def test_retry_does_not_duplicate_and_conflicting_key_fails(self):
        self.cost()
        original = self.path.read_bytes()
        self.assertTrue(self.cost()['already_saved'])
        self.assertEqual(self.path.read_bytes(), original)
        self.cost('--amount', '30.00', fails=True)
        self.assertEqual(self.path.read_bytes(), original)

    def test_rejected_input_never_changes_record(self):
        self.cost()
        original = self.path.read_bytes()
        for invalid in ['-10', '0', 'NaN', '1.001', '1,234.50', '$25', 'Infinity']:
            self.cost('--amount', invalid, fails=True)
        self.cost('--payer', 'Stranger', fails=True)
        self.cost('--date', '2026-02-30', fails=True)
        self.cli('settle', '--key', 'wrong', '--from', 'Matt', '--to', 'Ana',
                 '--amount', '1', '--date', '2026-10-21', fails=True)
        self.cli('settle', '--key', 'too-much', '--from', 'Ana', '--to', 'Matt',
                 '--amount', '9', '--date', '2026-10-21', fails=True)
        self.cli('init', '--project', 'Overwrite', '--currency', 'USD', '--members', 'A', 'B', fails=True)
        self.assertEqual(self.path.read_bytes(), original)

    def test_status_is_read_only(self):
        self.cost()
        original = self.path.read_bytes()
        result = self.cli('status')
        self.assertEqual(sum(x['cents'] for x in result['suggested_payments']), 1666)
        self.assertEqual(self.path.read_bytes(), original)

    def test_exact_weighted_allocations_and_tiny_amounts(self):
        self.assertEqual(ledger.allocate(2500, {'A': '60', 'B': '40'}), {'A': 1500, 'B': 1000})
        for cents in range(1, 1000):
            weights = {'A': '33.33', 'B': '33.33', 'C': '33.34'}
            shares = ledger.allocate(cents, weights)
            self.assertEqual(sum(shares.values()), cents)
            self.assertTrue(all(x >= 0 for x in shares.values()))
        self.assertEqual(ledger.allocate(1, {'A': '1', 'B': '1', 'C': '1'}), {'A': 1, 'B': 0, 'C': 0})

    def test_invalid_weights_and_corrupt_ledger_are_rejected(self):
        for weights in [['A=0', 'B=1'], ['A=NaN', 'B=1'], ['A=Infinity', 'B=1'], ['A', 'A']]:
            with self.assertRaises(ValueError):
                ledger.members(weights)
        self.cost()
        data = json.loads(self.path.read_text())
        data['entries'][0]['shares']['Ana'] += 1
        self.path.write_text(json.dumps(data))
        damaged = self.path.read_bytes()
        self.cli('status', fails=True)
        self.assertEqual(damaged, self.path.read_bytes())


if __name__ == '__main__':
    unittest.main()
