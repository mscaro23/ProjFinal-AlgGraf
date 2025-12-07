from typing import Dict, Iterable
from collections import defaultdict
from models.graph_objects import PageResponse, LinkBase


def build_graph(nodes: Iterable[PageResponse], edges: Iterable[LinkBase]):
    """
    Constrói as estruturas de saída do grafo a partir dos nós e arestas.
    """
    node_ids = [node.page_id for node in nodes]
    node_set = set(node_ids)

    out_neighbors = defaultdict(set)
    out_degree = defaultdict(int)

    for edge in edges:
        # garante que só considera arestas entre nós conhecidos
        if edge.source_page_id in node_set and edge.target_page_id in node_set:
            out_neighbors[edge.source_page_id].add(edge.target_page_id)

    for u in node_ids:
        out_degree[u] = len(out_neighbors[u])

    return node_ids, out_neighbors, out_degree


def pagerank(
    nodes: Iterable[PageResponse],
    edges: Iterable[LinkBase],
    d: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> Dict[int, float]:
    """
    Calcula o PageRank e retorna um dicionário {page_id: score}.
    """
    node_ids, out_neighbors, out_degree = build_graph(nodes, edges)
    N = len(node_ids)

    if N == 0:
        return {}

    # rank inicial uniforme
    rank = {pid: 1.0 / N for pid in node_ids}

    for _ in range(max_iter):
        # parte do teleporte
        new_rank = {pid: (1.0 - d) / N for pid in node_ids}

        # soma da massa nos dangling nodes (sem saída)
        dangling_sum = sum(rank[pid] for pid in node_ids if out_degree[pid] == 0)
        dangling_contrib = d * dangling_sum / N

        for pid in node_ids:
            new_rank[pid] += dangling_contrib

        # contribuições normais
        for u in node_ids:
            if out_degree[u] == 0:
                continue
            contrib = d * rank[u] / out_degree[u]
            for v in out_neighbors[u]:
                new_rank[v] += contrib

        # checa convergência
        diff = sum(abs(new_rank[pid] - rank[pid]) for pid in node_ids)
        rank = new_rank

        if diff < tol:
            break

    return rank
