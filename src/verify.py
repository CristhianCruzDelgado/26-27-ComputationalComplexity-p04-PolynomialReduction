"""Verification of the reduction using the PySAT solver."""

from typing import Dict, List, Optional

from pysat.solvers import Solver


def solve(instance: Dict) -> Optional[List[int]]:
    """Solve an instance. Returns a satisfying assignment (list of literals) or None."""
    with Solver(name="glucose3", bootstrap_with=instance["clauses"]) as solver:
        if solver.solve():
            return solver.get_model()
        return None


def is_satisfiable(instance: Dict) -> bool:
    """Return True if the instance has a satisfying assignment."""
    return solve(instance) is not None


def _satisfies(clauses: List[List[int]], model: List[int]) -> bool:
    """Check that an assignment (list of true literals) satisfies every clause."""
    true_literals = set(model)
    return all(any(literal in true_literals for literal in clause) for clause in clauses)


def verify_equivalence(original: Dict, reduced: Dict) -> bool:
    """Check that SAT(original) <=> SAT(reduced).

    Besides comparing the two answers, when both are satisfiable the model of the
    reduced formula is used to confirm that it also satisfies the original one.
    """
    original_sat = is_satisfiable(original)
    reduced_model = solve(reduced)

    if original_sat != (reduced_model is not None):
        return False
    if reduced_model is None:
        return True  # Both unsatisfiable.
    return _satisfies(original["clauses"], reduced_model)


def all_clauses_have_three_literals(instance: Dict) -> bool:
    """Check that every clause has exactly 3 literals."""
    return all(len(clause) == 3 for clause in instance["clauses"])
