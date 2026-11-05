#!/usr/bin/env python3

# Universidad de La Laguna ULL
# Degree: Computer Engineering
# Signature: Computational Complexity
# Practice 04: Polynomial Reduction
# Authors: Adrián Castro Rodríguez, 
#          Cristhian Adoney Cruz Delgado, 
#          Michelangelo Da Cruz Bochicchio and 
#          Samuel Montoya Díaz
# Emails: alu0101649931@ull.edu.es, 
#         alu0101648293@ull.edu.es,
#         alu0101651217@ull.edu.es and 
#         alu0101564395@ull.edu.es

"""Entry point of the SAT -> 3-SAT reduction tool.

Pipeline:
    1. Read a SAT instance (CNF formula) from a JSON file.
    2. Reduce it to an equivalent 3-SAT instance.
    3. Write the resulting instance as JSON (file or standard output).

Optional steps:
    --verify  Check with a SAT solver that both instances are equisatisfiable.
    --plot    Save graph images of both instances in the figures/ directory.

Usage:
    python main.py <input_file> [-o <output_file>] [--plot] [--verify]
"""

import argparse
import sys
from pathlib import Path

from src.io_utils import load_instance, save_instance
from src.reduction import reduce_sat_to_3sat

FIGURES_DIR = Path("figures")


def build_parser() -> argparse.ArgumentParser:
    """Define the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Reduce a SAT instance (CNF, JSON) to an equivalent 3-SAT instance.",
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input SAT instance (JSON).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Path of the output 3-SAT instance. If omitted, it is printed to standard output.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Save graph images of both instances in the figures/ directory.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Check with a SAT solver that both instances are equisatisfiable.",
    )
    return parser


def log(message: str) -> None:
    """Print status messages to stderr so stdout stays clean for the JSON output."""
    print(message, file=sys.stderr)


def run_verification(original: dict, reduced: dict) -> bool:
    """Run the equivalence checks. Returns True if every check passes."""
    # Imported lazily: python-sat is only required when --verify is used.
    from src.verify import all_clauses_have_three_literals, verify_equivalence

    three_literals = all_clauses_have_three_literals(reduced)
    equivalent = verify_equivalence(original, reduced)

    log(f"[verify] Every clause has exactly 3 literals: {'OK' if three_literals else 'FAILED'}")
    log(f"[verify] SAT(original) <=> SAT(reduced):      {'OK' if equivalent else 'FAILED'}")
    return three_literals and equivalent


def run_plots(original: dict, reduced: dict, stem: str) -> None:
    """Save one graph per instance in the figures/ directory."""
    # Imported lazily: networkx and matplotlib are only required when --plot is used.
    from src.visualize import plot_instance

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    original_path = FIGURES_DIR / f"{stem}_sat.png"
    reduced_path = FIGURES_DIR / f"{stem}_3sat.png"

    plot_instance(original, original_path, title="Original SAT instance")
    plot_instance(
        reduced,
        reduced_path,
        title="Reduced 3-SAT instance",
        original_num_vars=original["num_vars"],  # variables above this are new
    )

    log(f"[plot] Saved {original_path}")
    log(f"[plot] Saved {reduced_path}")


def main() -> int:
    args = build_parser().parse_args()

    # Step 1: read and validate the SAT instance.
    try:
        original = load_instance(args.input_file)
    except (OSError, ValueError) as error:
        log(f"Error reading '{args.input_file}': {error}")
        return 1

    # Step 2: apply the reduction.
    reduced = reduce_sat_to_3sat(original)
    log(
        f"[reduce] {len(original['clauses'])} clauses / {original['num_vars']} variables "
        f"-> {len(reduced['clauses'])} clauses / {reduced['num_vars']} variables"
    )

    # Step 3: write the resulting instance.
    try:
        save_instance(reduced, args.output)
    except OSError as error:
        log(f"Error writing output: {error}")
        return 1
    if args.output is not None:
        log(f"[write] Saved {args.output}")

    # Optional: equivalence check.
    verified = True
    if args.verify:
        try:
            verified = run_verification(original, reduced)
        except ImportError:
            log("Error: --verify requires 'python-sat' (pip install python-sat).")
            return 1

    # Optional: graphs.
    if args.plot:
        try:
            run_plots(original, reduced, args.input_file.stem)
        except ImportError:
            log("Error: --plot requires 'networkx' and 'matplotlib' (pip install networkx matplotlib).")
            return 1

    return 0 if verified else 2


if __name__ == "__main__":
    sys.exit(main())
