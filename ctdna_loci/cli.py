"""Command-line interface for locus-level ctDNA evidence analysis."""

import argparse
import json
from pathlib import Path

from .core import evaluate, fit_background, read_background, read_counts, write_background


def main(argv=None):
    parser = argparse.ArgumentParser(prog="ctdna-loci")
    commands = parser.add_subparsers(dest="command", required=True)
    fit = commands.add_parser("fit", help="fit locus-specific background from negative controls")
    fit.add_argument("--controls", required=True)
    fit.add_argument("--output", required=True)
    fit.add_argument("--prior-alpha", type=float, default=0.5)
    fit.add_argument("--prior-beta", type=float, default=499.5)

    call = commands.add_parser("call", help="evaluate tumor-informed loci for each sample")
    call.add_argument("--counts", required=True)
    call.add_argument("--background", required=True)
    call.add_argument("--output", required=True)
    call.add_argument("--alpha", type=float, default=0.01)
    call.add_argument("--min-loci", type=int, default=3)
    call.add_argument("--min-control-depth", type=int, default=1000)
    call.add_argument("--min-sample-depth", type=int, default=100)

    args = parser.parse_args(argv)
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    if args.command == "fit":
        write_background(args.output, fit_background(read_counts(args.controls), args.prior_alpha, args.prior_beta))
    else:
        results = evaluate(read_counts(args.counts), read_background(args.background),
                           args.min_control_depth, args.min_sample_depth, args.min_loci, args.alpha)
        with open(args.output, "w", encoding="utf-8") as handle:
            json.dump({"schema_version": 1, "method": "poisson_binomial_positive_loci",
                       "results": results}, handle, indent=2)
            handle.write("\n")


if __name__ == "__main__":
    main()
