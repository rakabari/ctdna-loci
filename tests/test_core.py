import math
import tempfile
import unittest
from pathlib import Path

from ctdna_loci.cli import main
from ctdna_loci.core import Background, evaluate, fit_background, read_counts, tail_poisson_binomial


class CountsTest(unittest.TestCase):
    def test_invalid_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "counts.tsv"
            path.write_text("sample_id\tlocus_id\talt_molecules\ttotal_molecules\nA\tx\t4\t3\n")
            with self.assertRaises(ValueError):
                read_counts(path)

    def test_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "counts.tsv"
            path.write_text("sample_id\tlocus_id\talt_molecules\ttotal_molecules\nA\tx\t0\t3\nA\tx\t0\t3\n")
            with self.assertRaises(ValueError):
                read_counts(path)

    def test_predictive_probability(self):
        b = Background("x", 0, 10000, 0.5, 499.5)
        self.assertEqual(b.probability_positive(0), 0.0)
        self.assertGreater(b.probability_positive(100), 0)
        self.assertLess(b.probability_positive(100), 1)

    def test_poisson_binomial(self):
        self.assertAlmostEqual(tail_poisson_binomial([.1, .2], 2), .02)
        self.assertAlmostEqual(tail_poisson_binomial([.1, .2], 1), .28)
        self.assertEqual(tail_poisson_binomial([.1, .2], 0), 1)

    def test_insufficient_loci(self):
        b = [Background("x", 0, 5000, .5, 499.5)]
        samples = [{"sample_id": "A", "locus_id": "x", "alt_molecules": 1, "total_molecules": 500}]
        result = evaluate(samples, b)
        self.assertEqual(result[0]["status"], "insufficient_data")
        self.assertIsNone(result[0]["p_value"])

    def test_fixture_end_to_end(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as temp:
            model, output = Path(temp) / "background.json", Path(temp) / "calls.json"
            main(["fit", "--controls", str(root / "examples/controls.tsv"), "--output", str(model)])
            main(["call", "--counts", str(root / "examples/samples.tsv"), "--background", str(model),
                  "--output", str(output)])
            import json
            results = {r["sample_id"]: r for r in json.loads(output.read_text())["results"]}
            self.assertEqual(results["mock_negative"]["status"], "not_detected")
            self.assertEqual(results["mock_negative"]["p_value"], 1)
            self.assertEqual(results["mock_positive"]["positive_loci"], 4)
            self.assertLess(results["mock_positive"]["p_value"], 0.01)


if __name__ == "__main__":
    unittest.main()
