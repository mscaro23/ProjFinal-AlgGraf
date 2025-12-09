from models.graph_objects import PageResponse, LinkBase
from services.pagerank import build_graph, pagerank


def criar_grafo_teste():
    """
    Cria um grafo pequeno para testar:

        A (0) → B (1)
        A (0) → C (2)
        B (1) → C (2)
        C (2) → A (0)
        D (3) → C (2)

    Intuição:
      - C deve ter o maior PageRank
      - Depois A
      - Depois B
      - D deve ser o menor
    """

    nodes = [
        PageResponse(
            page_id=0,
            title="A",
            url="A",
            length_chars=0,
            num_editors=0,
            num_revisions=0,
            links_out_count=2,  # A -> B e A -> C
        ),
        PageResponse(
            page_id=1,
            title="B",
            url="B",
            length_chars=0,
            num_editors=0,
            num_revisions=0,
            links_out_count=1,  # B -> C
        ),
        PageResponse(
            page_id=2,
            title="C",
            url="C",
            length_chars=0,
            num_editors=0,
            num_revisions=0,
            links_out_count=1,  # C -> A
        ),
        PageResponse(
            page_id=3,
            title="D",
            url="D",
            length_chars=0,
            num_editors=0,
            num_revisions=0,
            links_out_count=1,  # D -> C
        ),
    ]

    edges = [
        LinkBase(source_page_id=0, target_page_id=1, anchor_text="A→B"),
        LinkBase(source_page_id=0, target_page_id=2, anchor_text="A→C"),
        LinkBase(source_page_id=1, target_page_id=2, anchor_text="B→C"),
        LinkBase(source_page_id=2, target_page_id=0, anchor_text="C→A"),
        LinkBase(source_page_id=3, target_page_id=2, anchor_text="D→C"),
    ]

    return nodes, edges


def testar_build_graph():
    print("=== Teste build_graph ===")
    nodes, edges = criar_grafo_teste()

    node_ids, out_neighbors, out_degree = build_graph(nodes, edges)

    print("IDs dos nós:", node_ids)
    print("Vizinhos de saída (out_neighbors):")
    for u in node_ids:
        print(f"  {u} -> {sorted(out_neighbors[u])}")
    print("Graus de saída (out_degree):")
    for u in node_ids:
        print(f"  {u}: {out_degree[u]}")

    # Asserts simples
    assert set(node_ids) == {0, 1, 2, 3}, "IDs dos nós não batem"
    assert out_degree[0] == 2, "Nó 0 (A) deveria ter grau de saída 2"
    assert out_degree[1] == 1, "Nó 1 (B) deveria ter grau de saída 1"
    assert out_degree[2] == 1, "Nó 2 (C) deveria ter grau de saída 1"
    assert out_degree[3] == 1, "Nó 3 (D) deveria ter grau de saída 1"

    print("✅ build_graph parece correto.\n")


def testar_pagerank():
    print("=== Teste pagerank ===")
    nodes, edges = criar_grafo_teste()

    ranks = pagerank(nodes, edges, d=0.85, max_iter=100, tol=1e-8)

    print("Valores de PageRank:")
    for n in nodes:
        print(f"  Página {n.page_id} ({n.title}): {ranks[n.page_id]:.6f}")

    soma = sum(ranks.values())
    print(f"\nSoma dos PageRanks = {soma:.6f}")

    # A soma dos PageRanks deve ser ~1
    assert abs(soma - 1.0) < 1e-6, "Soma dos PageRanks deveria ser 1"

    # Ordem esperada: C > A > B > D
    r_a = ranks[0]
    r_b = ranks[1]
    r_c = ranks[2]
    r_d = ranks[3]

    assert r_c > r_a > r_b > r_d, "Ordem de importância esperada: C > A > B > D"

    print("✅ pagerank parece consistente (ordem e soma ok).\n")


if __name__ == "__main__":
    testar_build_graph()
    testar_pagerank()
    print("Todos os testes manuais passaram ✅")
