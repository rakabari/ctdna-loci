"""Molecule-count background estimates and multi-locus sample evidence."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Background:
    locus_id: str
    alt_molecules: int
    total_molecules: int
    alpha: float
    beta: float

    def probability_positive(self, depth: int) -> float:
        """Posterior predictive probability of >=1 alternate molecule under the null."""
        a = self.alpha + self.alt_molecules
        b = self.beta + self.total_molecules - self.alt_molecules
        log_zero = math.lgamma(b + depth) - math.lgamma(a + b + depth)
        log_zero += math.lgamma(a + b) - math.lgamma(b)
        return -math.expm1(min(0.0, log_zero))


def _count(value: str, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field}: {value!r}") from exc
    if number < 0:
        raise ValueError(f"negative {field}: {value!r}")
    return number


def read_counts(path: str | Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        required = {"sample_id", "locus_id", "alt_molecules", "total_molecules"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: required columns: {', '.join(sorted(required))}")
        rows = []
        seen = set()
        for line, row in enumerate(reader, 2):
            key = (row["sample_id"], row["locus_id"])
            if not all(key) or key in seen:
                raise ValueError(f"{path}:{line}: duplicate or empty sample/locus key")
            seen.add(key)
            alt = _count(row["alt_molecules"], "alt_molecules")
            total = _count(row["total_molecules"], "total_molecules")
            if alt > total:
                raise ValueError(f"{path}:{line}: alt_molecules exceeds total_molecules")
            rows.append({"sample_id": key[0], "locus_id": key[1],
                         "alt_molecules": alt, "total_molecules": total})
    return rows


def fit_background(rows: list[dict], prior_alpha: float = 0.5,
                   prior_beta: float = 499.5) -> list[Background]:
    if prior_alpha <= 0 or prior_beta <= 0:
        raise ValueError("prior parameters must be positive")
    sums = defaultdict(lambda: [0, 0])
    for row in rows:
        agg = sums[row["locus_id"]]
        agg[0] += row["alt_molecules"]
        agg[1] += row["total_molecules"]
    return [Background(locus, a, n, prior_alpha, prior_beta)
            for locus, (a, n) in sorted(sums.items())]


def tail_poisson_binomial(probabilities: list[float], observed: int) -> float:
    """Exact upper-tail probability for independent Bernoulli variables."""
    if observed <= 0:
        return 1.0
    if observed > len(probabilities):
        return 0.0
    dist = [1.0] + [0.0] * len(probabilities)
    for j, p in enumerate(probabilities, 1):
        if not 0 <= p <= 1:
            raise ValueError("probabilities must be in [0, 1]")
        for k in range(j, 0, -1):
            dist[k] = dist[k] * (1 - p) + dist[k - 1] * p
        dist[0] *= 1 - p
    return min(1.0, max(0.0, math.fsum(dist[observed:])))


def evaluate(rows: list[dict], backgrounds: list[Background],
             min_control_depth: int = 1000, min_sample_depth: int = 100,
             min_loci: int = 3, alpha: float = 0.01) -> list[dict]:
    if min_control_depth < 0 or min_sample_depth < 0 or min_loci < 1:
        raise ValueError("invalid depth or locus thresholds")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie between 0 and 1")
    bg = {b.locus_id: b for b in backgrounds}
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["sample_id"]].append(row)
    output = []
    for sample, group in sorted(grouped.items()):
        eligible = []
        omitted = {"missing_background": 0, "control_depth": 0, "sample_depth": 0}
        for row in group:
            b = bg.get(row["locus_id"])
            if b is None:
                omitted["missing_background"] += 1
            elif b.total_molecules < min_control_depth:
                omitted["control_depth"] += 1
            elif row["total_molecules"] < min_sample_depth:
                omitted["sample_depth"] += 1
            else:
                eligible.append((row, b))
        n_positive = sum(r["alt_molecules"] > 0 for r, _ in eligible)
        total_depth = sum(r["total_molecules"] for r, _ in eligible)
        result = {
            "sample_id": sample,
            "tracked_loci": len(group),
            "evaluable_loci": len(eligible),
            "positive_loci": n_positive,
            "total_molecules": total_depth,
            "excluded_loci": omitted,
            "threshold": alpha,
            "statistic": "count_of_loci_with_one_or_more_alternate_molecules",
        }
        if len(eligible) < min_loci:
            result.update(status="insufficient_data", p_value=None, expected_positive_loci=None)
        else:
            probs = [b.probability_positive(r["total_molecules"]) for r, b in eligible]
            pvalue = tail_poisson_binomial(probs, n_positive)
            result.update(status="evidence_detected" if pvalue <= alpha else "not_detected",
                          p_value=pvalue, expected_positive_loci=math.fsum(probs))
        output.append(result)
    return output


def write_background(path: str | Path, backgrounds: list[Background]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"schema_version": 1, "model": "beta_binomial_locus_background",
                   "loci": [asdict(b) for b in backgrounds]}, handle, indent=2)
        handle.write("\n")


def read_background(path: str | Path) -> list[Background]:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if payload.get("schema_version") != 1 or payload.get("model") != "beta_binomial_locus_background":
        raise ValueError("unsupported background model")
    loci = [Background(**item) for item in payload["loci"]]
    if len(set(b.locus_id for b in loci)) != len(loci):
        raise ValueError("duplicate background loci")
    return loci
