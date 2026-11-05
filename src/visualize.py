"""Graph drawing of CNF instances.

An instance is drawn as a bipartite variable-clause graph:
    - one circular node per variable (left) and one square node per clause (right);
    - one edge per literal occurrence: solid if positive, dashed if negated;
    - variables introduced by the reduction get a different color.
"""

from pathlib import Path
from typing import Dict, Optional, Union

import matplotlib

matplotlib.use("Agg")  # Render to files only; no display is needed.

import matplotlib.pyplot as plt  # noqa: E402
import networkx as nx  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

ORIGINAL_VAR_COLOR = "#4C78A8"
NEW_VAR_COLOR = "#F58518"
CLAUSE_COLOR = "#B0B0B0"
EDGE_COLOR = "#444444"


def _layout(var_nodes: list, clause_nodes: list) -> dict:
    """Place variables in a left column and clauses in a right column, top to bottom."""
    pos = {}
    for nodes, x in ((var_nodes, 0.0), (clause_nodes, 1.0)):
        count = len(nodes)
        for index, node in enumerate(nodes):
            y = 0.5 if count == 1 else 1.0 - index / (count - 1)
            pos[node] = (x, y)
    return pos


def plot_instance(
    instance: Dict,
    output_path: Union[str, Path],
    title: str = "CNF instance",
    original_num_vars: Optional[int] = None,
) -> None:
    """Draw an instance as a variable-clause graph and save it as an image.

    Args:
        instance: {"num_vars": int, "clauses": [[int, ...], ...]}.
        output_path: where the image is saved (e.g. figures/example_sat.png).
        title: title shown above the graph.
        original_num_vars: if given, variables numbered above it are drawn as
            "new" variables (those introduced by the reduction).
    """
    clauses = instance["clauses"]
    used_vars = sorted({abs(literal) for clause in clauses for literal in clause})

    var_nodes = [("v", i) for i in used_vars]
    clause_nodes = [("c", j) for j in range(len(clauses))]

    graph = nx.Graph()
    graph.add_nodes_from(var_nodes)
    graph.add_nodes_from(clause_nodes)

    positive_edges, negated_edges = [], []
    for j, clause in enumerate(clauses):
        for literal in clause:
            edge = (("v", abs(literal)), ("c", j))
            graph.add_edge(*edge)
            (positive_edges if literal > 0 else negated_edges).append(edge)

    pos = _layout(var_nodes, clause_nodes)

    biggest_side = max(len(var_nodes), len(clause_nodes), 1)
    node_size = max(80, min(600, 12000 // biggest_side))
    font_size = 8 if node_size >= 300 else 6

    fig, ax = plt.subplots(figsize=(8, max(5.0, 0.35 * biggest_side)))

    # Edges first, so nodes are drawn on top of them.
    nx.draw_networkx_edges(
        graph, pos, edgelist=positive_edges, style="solid",
        edge_color=EDGE_COLOR, width=1.0, ax=ax,
    )
    nx.draw_networkx_edges(
        graph, pos, edgelist=negated_edges, style="dashed",
        edge_color=EDGE_COLOR, width=1.0, ax=ax,
    )

    is_new = lambda node: original_num_vars is not None and node[1] > original_num_vars
    original_vars = [n for n in var_nodes if not is_new(n)]
    new_vars = [n for n in var_nodes if is_new(n)]

    nx.draw_networkx_nodes(
        graph, pos, nodelist=original_vars, node_color=ORIGINAL_VAR_COLOR,
        node_shape="o", node_size=node_size, ax=ax,
    )
    nx.draw_networkx_nodes(
        graph, pos, nodelist=new_vars, node_color=NEW_VAR_COLOR,
        node_shape="o", node_size=node_size, ax=ax,
    )
    nx.draw_networkx_nodes(
        graph, pos, nodelist=clause_nodes, node_color=CLAUSE_COLOR,
        node_shape="s", node_size=node_size, ax=ax,
    )

    labels = {node: f"x{node[1]}" for node in var_nodes}
    labels.update({node: f"C{node[1] + 1}" for node in clause_nodes})
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=font_size, ax=ax)

    legend = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=ORIGINAL_VAR_COLOR,
               markersize=10, label="Original variable"),
    ]
    if new_vars:
        legend.append(
            Line2D([0], [0], marker="o", color="w", markerfacecolor=NEW_VAR_COLOR,
                   markersize=10, label="Variable added by the reduction")
        )
    legend += [
        Line2D([0], [0], marker="s", color="w", markerfacecolor=CLAUSE_COLOR,
               markersize=10, label="Clause"),
        Line2D([0], [0], color=EDGE_COLOR, linestyle="-", label="Positive literal"),
        Line2D([0], [0], color=EDGE_COLOR, linestyle="--", label="Negated literal"),
    ]
    ax.legend(handles=legend, loc="upper center", bbox_to_anchor=(0.5, 0.0),
              ncol=2, frameon=False)

    ax.set_title(f"{title}\n{len(used_vars)} variables, {len(clauses)} clauses")
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-0.08, 1.08)
    ax.axis("off")

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
