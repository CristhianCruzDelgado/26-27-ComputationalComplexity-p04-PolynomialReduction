# SAT to 3-SAT Polynomial Reduction

A command-line tool that reads a SAT instance in CNF, applies the classic 
polynomial-time reduction **SAT ≤ₚ 3-SAT**, and writes the resulting 3-SAT 
instance in JSON. It can also verify the equivalence of both instances and draw 
them as graphs.

## Overview

The program performs three steps:

1. **Read** a SAT instance (a CNF formula) from a JSON file.
2. **Reduce** it to an equivalent 3-SAT instance using the reduction algorithm.
3. **Write** the resulting instance as a JSON file.

The reduction preserves satisfiability: the original formula is satisfiable 
**if and only if** the generated 3-SAT formula is satisfiable. It runs in 
linear time with respect to the size of the input, so it is a valid 
polynomial-time reduction.

## The Reduction

Each clause is transformed independently, depending on its number of literals 
`k`. Every `y` below is a **fresh variable** that does not appear anywhere else 
in the formula.

| Clause size | Original clause | Resulting clauses |
|---|---|---|
| `k = 1` | `(l1)` | `(l1 ∨ y1 ∨ y2)`, `(l1 ∨ ¬y1 ∨ y2)`, `(l1 ∨ y1 ∨ ¬y2)`, `(l1 ∨ ¬y1 ∨ ¬y2)` |
| `k = 2` | `(l1 ∨ l2)` | `(l1 ∨ l2 ∨ y1)`, `(l1 ∨ l2 ∨ ¬y1)` |
| `k = 3` | `(l1 ∨ l2 ∨ l3)` | Unchanged |
| `k > 3` | `(l1 ∨ l2 ∨ ... ∨ lk)` | `(l1 ∨ l2 ∨ y1)`, `(¬y1 ∨ l3 ∨ y2)`, `(¬y2 ∨ l4 ∨ y3)`, ..., `(¬y(k-3) ∨ l(k-1) ∨ lk)` |

Properties:

- A clause with `k` literals produces at most `max(4, k - 2)` clauses and at most `k - 3` new variables (for `k > 3`).
- Every clause in the output has **exactly 3 literals**.
- Clauses are assumed to contain at least one literal (an empty clause makes the formula trivially unsatisfiable).

## Project Structure

```
26-27-ComputationalComplexity-p04-PolynomialReduction/
├── README.md                  # Documentation and dependencies
├── main.py                    # Entry point: read -> reduce -> write
│
├── src/
│   ├── io_utils.py            # Read/validate and write JSON
│   ├── reduction.py           # SAT -> 3-SAT reduction algorithm
│   ├── verify.py              # Equivalence check using PySAT
│   └── visualize.py           # Graph drawing of the instances
│
├── schemas/
│   └── cnf_schema.json        # JSON Schema used to validate the input
│
├── instances/
│   ├── input/                 # Sample SAT instances
│   └── output/                # Generated 3-SAT instances
│
└── figures/
    └── example_graph.png      # Generated images
```

## Dependencies

| Package | Purpose | Required |
|---|---|---|
| Python >= 3.9 | Runtime | Yes |
| `jsonschema` | Validate the input format | Yes |
| `python-sat` | SAT solver used for the equivalence check | Only for `--verify` |
| `networkx` | Build the variable-clause graphs | Only for `--plot` |
| `matplotlib` | Draw and save the graphs as images | Only for `--plot` |

## Installation (Linux/macOS)

```bash
# 1. Clone the repository
git clone <repository-url>
cd 26-27-ComputationalComplexity-p04-PolynomialReduction

# 2. Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# 3. Check the version (the project requires 3.9 or higher)
python3 --version

# 4. (Recommended) Create and activate a virtual environment
sudo apt install python3-venv
python3 -m venv venv
source venv/bin/activate

# 5. Install the dependencies
pip install jsonschema python-sat networkx matplotlib
```

## Data Format

Input and output instances use the same JSON structure:

```json
{
  "num_vars": 4,
  "clauses": [[1, -2], [1, 2, -3, 4]]
}
```

- `num_vars`: number of variables.
- `clauses`: list of clauses in CNF. Each clause is a list of non-zero integers.
  - A positive integer `i` represents the variable.
  - A negative integer `-i` represents its negation.

## Usage

```bash
python main.py <input_file> [-o <output_file>] [--plot] [--verify]
```

| Argument | Description |
|---|---|
| `input_file` | Path to the input SAT instance. |
| `-o`, `--output` | Path of the output 3-SAT instance. If omitted, the result is printed to standard output. |
| `--plot` | Save graph images of both instances in `figures/`. |
| `--verify` | Check with a SAT solver that both instances are equisatisfiable. |

**Typical run**

```bash
python main.py instances/input/example_sat_1.json -o instances/output/example_3sat_1.json --plot --verify
```

## Visualization

Each instance is drawn as a **bipartite variable-clause graph**:

- One node per variable and one node per clause.
- One edge for each literal occurrence in a clause.
  - **Solid line:** positive literal.
  - **Dashed line:** negated literal.
- Two figures are produced: the original SAT instance and the resulting 3-SAT instance.
- Variables introduced by the reduction are shown in a different color, so it is easy to see what the algorithm added.

Images are saved in the `figures/` directory.

## Verification

With `--verify`, the program uses PySAT to solve both the original and the 
reduced formula and checks that:

```
SAT(original formula)  <=>  SAT(reduced formula)
```

It also checks that every clause of the output has exactly 3 literals.
