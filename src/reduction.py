"""Polynomial-time reduction SAT to 3-SAT.

Each clause is rewritten independently according to its size k. Every `y`
below is a fresh variable that appears nowhere else in the formula.

    k = 1 : (l1)  ->  (l1 v y1 v y2) (l1 v -y1 v y2) (l1 v y1 v -y2) (l1 v -y1 v -y2)
    k = 2 : (l1 v l2)  ->  (l1 v l2 v y1) (l1 v l2 v -y1)
    k = 3 : unchanged
    k > 3 : (l1 v l2 v ... v lk)  ->
            (l1 v l2 v y1) (-y1 v l3 v y2) ... (-y(k-3) v l(k-1) v lk)

The output formula is satisfiable if and only if the input formula is.
The running time and the output size are linear in the input size.
"""

from typing import Dict, List


def reduce_sat_to_3sat(instance: Dict) -> Dict:
    """Reduce a SAT (CNF) instance to an equisatisfiable 3-SAT instance.

    Raises:
        ValueError: if the instance contains an empty clause.
    """
    last_var = instance["num_vars"]
    result: List[List[int]] = []

    def fresh_var() -> int:
        nonlocal last_var
        last_var += 1
        return last_var

    for clause in instance["clauses"]:
        size = len(clause)

        if size == 0:
            raise ValueError("empty clauses are not supported")

        elif size == 1:
            (l1,) = clause
            y1, y2 = fresh_var(), fresh_var()
            result.extend([
                [l1, y1, y2],
                [l1, -y1, y2],
                [l1, y1, -y2],
                [l1, -y1, -y2],
            ])

        elif size == 2:
            l1, l2 = clause
            y1 = fresh_var()
            result.extend([
                [l1, l2, y1],
                [l1, l2, -y1],
            ])

        elif size == 3:
            result.append(list(clause))

        else:
            # Chain of k - 2 clauses linked by k - 3 fresh variables.
            y_prev = fresh_var()
            result.append([clause[0], clause[1], y_prev])
            for literal in clause[2:-2]:
                y_next = fresh_var()
                result.append([-y_prev, literal, y_next])
                y_prev = y_next
            result.append([-y_prev, clause[-2], clause[-1]])

    return {"num_vars": last_var, "clauses": result}
