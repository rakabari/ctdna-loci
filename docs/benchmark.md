# Benchmark design

## Reference material

The SEQC2 oncopanel liquid-biopsy study (BioProject [PRJNA677999](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA677999)) and its associated data descriptor provide a public analytical benchmarking starting point: https://www.nature.com/articles/s41597-022-01276-8.

The initial raw-data integration requires confirmation of which assays retain UMI tags or molecule-family output. Read depth and variant allele fraction are not substitutes for independent molecular counts. This repository does not claim that SEQC2 provides ready-to-use molecule-count tables.

## Study partitions

Negative-control data establish the background model. Separate negative controls estimate sample-level false-positive rates. Dilution series evaluate sensitivity across expected tumor fractions and molecule input levels. Replicates assess repeatability and between-run effects.

Control and evaluation samples must be partitioned by originating specimen and run where possible. Synthetic mixtures can supplement but do not replace experimental LoD studies.

## Comparisons

- A fixed minimum number of positive loci.
- Simple binomial or pooled-background null models.
- The locus-specific Poisson-binomial model in this repository.
- A later correlated-error or hierarchical extension.

Report sensitivity at fixed empirical sample-level specificity, false positives per blank sample, molecular-input stratification, and detection probability versus dilution. Estimate LoD95 only from an appropriate set of experimental replicates and a prespecified model.

## References

- BLOODPAC MRD analytical validation consensus (2026): https://pmc.ncbi.nlm.nih.gov/articles/PMC12834287/
- BLOODPAC ctDNA analytical validation protocols v2.0 (2026): https://pmc.ncbi.nlm.nih.gov/articles/PMC13182804/
- GeneBits and umiVar (2025): https://pmc.ncbi.nlm.nih.gov/articles/PMC12382282/
- SEQC2 proficiency data: https://www.nature.com/articles/s41597-022-01276-8
