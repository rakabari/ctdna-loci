# ctDNA Loci

Locus specific background error modeling and sample level statistical assessment for tumor informed circulating tumor DNA (ctDNA) detection

This method characterizes locus specific background error rates using molecular count data from negative controls. Beta binomial predictive distributions account for uncertainty and variability in background error rates and estimate the probability of observing alternate molecules at individual loci. Statistical evidence is aggregated at the sample level based on the number of tracked tumor specific loci with at least one alternate molecule. An exact Poisson binomial upper tail probability quantifies the statistical significance of the observed signal under the null hypothesis of independent background errors among loci.

The implementation uses deduplicated, independent molecular counts rather than raw sequencing read counts. Unique molecular identifier (UMI) consensus generation, tumor specific mutation selection, germline variant exclusion, and matched white blood cell filtering to remove potential hematopoietic variants are performed upstream and are outside the scope of this implementation.

## Install

```bash
python3 -m pip install .
```

The package uses only the Python standard library. No `requirements.txt` or application container is required for the scoring code.

## Input

Both input tables are tab separated with the following columns:

| Column | Description |
| --- | --- |
| `sample_id` | Control or plasma sample identifier |
| `locus_id` | Tracked variant identifier, consistent between tables |
| `alt_molecules` | Independent molecules supporting the tracked alternate allele |
| `total_molecules` | Independent callable molecules at the locus |

A row corresponds to one sample locus pair. Control samples must be negative for the tracked variants. Counts should reflect molecular families rather than sequencing reads. Control and sample processing should be matched.

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

Negative control alternate and total molecular counts are aggregated independently for each tracked locus. With a Beta(a, b) prior, the posterior predictive probability of observing at least one alternate molecule in a sample with molecular depth n is

$$
q=1-\frac{B(a+k, b+N-k+n)}{B(a+k,b+N-k)}
$$

where k alternate molecules were observed among N control molecules. The number of sample loci with alternate evidence is evaluated against a Poisson binomial distribution with success probabilities q. The resulting upper tail probability is **model based evidence under the null**, not a posterior probability that a patient has cancer.

The prior defaults to Beta(0.5, 499.5); this is a configurable modeling assumption, not an experimentally determined sequencing error rate. The sample level threshold defaults to 0.01 and is illustrative rather than clinically validated. Loci with inadequate control coverage or plasma molecular depth are excluded, and samples with too few valuable loci return `insufficient_data`.

See [methodology](docs/methodology.md), [research direction](docs/research.md), [benchmark design](docs/benchmark.md), and [execution](docs/execution.md).

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Scope

The independent locus assumption, treatment of background rate uncertainty, and use of binary locus evidence are limitations of this baseline. A statistically significant result is not equivalent to an MRD diagnosis. Assay LoD, specificity, and reproducibility require representative controls and independently validated experimental samples.

## License

MIT.
