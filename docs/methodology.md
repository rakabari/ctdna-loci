# Statistical model

## Observations

For each tracked, tumor-confirmed variant, the assay supplies independent alternate-molecule and callable-molecule counts. This release does not collapse UMI families or perform tumor-informed variant selection.

## Background estimation

A Beta prior and aggregated negative-control counts define a per-locus posterior distribution for the background alternate-molecule probability. The posterior predictive event is the observation of one or more alternate molecules at that locus. Its probability changes with the plasma sample's callable molecular depth.

The model treats control molecules as exchangeable within a locus. This assumption can be violated by reagent lot, sequence context, sequencing run, sample preparation, or correlated molecular errors.

## Sample-level test

Let Z_i indicate whether locus i has at least one alternate molecule. Under the null, Z_i follows a Bernoulli distribution with posterior predictive probability q_i. For K = sum(Z_i), the exact one-sided p-value P(K >= k_observed) is calculated by dynamic programming.

This statistic does not use the number of alternate molecules beyond the first within a locus. It therefore sacrifices power and is best interpreted as a transparent baseline. The method also assumes independence between loci after conditioning on the background model. Correlation from sample-level artifacts can inflate significance.

## Calibration and acceptance criteria

Thresholds, locus eligibility, background priors, and minimum molecular depths are configurable. The defaults support software demonstrations and are not clinical acceptance criteria. Repeated negative-control samples, dilution series, and independent plasma specimens are needed to establish sample-level false-positive behavior and empirical detection limits.

The software does not estimate tumor fraction, longitudinal recurrence risk, or clinical MRD status.
