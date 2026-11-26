# Research direction

## Question

Can a quality-aware, molecule-level background model improve tumor-informed ctDNA sample detection at a controlled empirical false-positive rate across laboratories and assay conditions?

## Existing work

Multi-locus tumor-informed detection, molecular error correction, and very-low-frequency ctDNA tracking are established methods. GeneBits/umiVar (2025) and related work provide relevant algorithmic comparisons. The current Poisson-binomial test is a baseline, not a new contribution.

## Method development

The intended extension is a hierarchical model of background error that permits shared batch-level effects and locus-specific uncertainty, followed by a sample-level test calibrated against independent negative controls. A second extension will treat molecule availability and expected signal explicitly, rather than reducing each locus to a binary positive/negative indicator.

Key methodological questions include whether conditional correlation invalidates naive independent-locus p-values and whether adapting the null to observed batch-level QC can recover specificity without suppressing true ctDNA signals.

## Evaluation criteria

- Prespecified sample-level false-positive rates evaluated on independent negative controls.
- Sensitivity evaluated on a dilution series with independent replicates and recorded unique-molecule input.
- Empirical calibration against matched control material across batches, panels, and library preparations.
- Comparison with fixed-locus thresholds, pooled-background models, and available tumor-informed methods under equivalent inputs.
- Uncertainty intervals based on independent sample replicates, not on treating loci as independent patients.
- Ablation of locus-specific rates, batch effects, molecular depth adjustment, and alternate-count likelihood.

## Constraints

The current pipeline assumes a fixed tumor-informed variant list and unbiased molecule family counts. It does not infer tumor mutations, normalize matched WBC evidence, or estimate recurrence risk. Analytical LoD95 is not inferable from computational dilution alone. Available public oncopanel benchmarks may lack the UMI family information needed for molecule-level reanalysis.
