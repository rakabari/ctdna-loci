# ctDNA Loci

Locus-specific background estimation and sample-level evidence aggregation for tumor-informed circulating tumor DNA analysis.

The current method estimates background alternate-molecule rates from negative controls using beta-binomial predictive distributions. A sample-level test counts tracked loci with at least one alternate molecule and calculates an exact Poisson-binomial upper-tail probability under the independent-locus null model.

This implementation operates on **deduplicated, independent molecular counts**, not raw read counts. UMI consensus construction, tumor mutation selection, germline exclusion, and matched-white-blood-cell filtering are upstream processes.

## Install

```bash
python3 -m pip install .
```

The package uses only the Python standard library. No `requirements.txt` or application container is required for the scoring code.

## Input

Both input tables are tab-separated with the following columns:

| Column | Description |
| --- | --- |
| `sample_id` | Control or plasma sample identifier |
| `locus_id` | Tracked variant identifier, consistent between tables |
| `alt_molecules` | Independent molecules supporting the tracked alternate allele |
| `total_molecules` | Independent callable molecules at the locus |

A row corresponds to one sample–locus pair. Control samples must be negative for the tracked variants. Counts should reflect molecular families rather than sequencing reads. Control and sample processing should be matched.

## Run

```bash
ctdna-loci fit \
  --controls examples/controls.tsv \
  --output results/background.json

ctdna-loci call \
  --counts examples/samples.tsv \
  --background results/background.json \
  --output results/calls.json
```

Or run both stages from the source checkout:

```bash
bash scripts/run.sh
```

`examples/` contains constructed counts for functional testing, **not patient data or measured assay results**.

## Model

Negative-control alternate and total molecular counts are aggregated independently for each tracked locus. With a Beta(a, b) prior, the posterior predictive probability of observing at least one alternate molecule in a sample with molecular depth n is

$$
q=1-\frac{B(a+k, b+N-k+n)}{B(a+k,b+N-k)}
$$

where k alternate molecules were observed among N control molecules. The number of sample loci with alternate evidence is evaluated against a Poisson-binomial distribution with success probabilities q. The resulting upper-tail probability is **model-based evidence under the null**, not a posterior probability that a patient has cancer.

The prior defaults to Beta(0.5, 499.5); this is a configurable modeling assumption, not an experimentally determined sequencing error rate. The sample-level threshold defaults to 0.01 and is illustrative rather than clinically validated. Loci with inadequate control coverage or plasma molecular depth are excluded, and samples with too few evaluable loci return `insufficient_data`.

See [methodology](docs/methodology.md), [research direction](docs/research.md), [benchmark design](docs/benchmark.md), and [execution](docs/execution.md).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Scope

The independent-locus assumption, treatment of background-rate uncertainty, and use of binary locus evidence are limitations of this baseline. A statistically significant result is not equivalent to an MRD diagnosis. Assay LoD, specificity, and reproducibility require representative controls and independently validated experimental samples.

## License

MIT.
