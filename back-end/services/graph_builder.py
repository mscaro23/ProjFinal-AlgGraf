from db.repositories.page import PageRepository
from models.graph_objects import PageBase, LinkBase


def save_graph(repository: PageRepository, node: PageBase, edges: list[LinkBase]):
    """
    Salva um nó (Page) e suas arestas (Links) no banco de dados.
    Wrapper para manter compatibilidade com código existente.
    """
    repository.save_page_with_links(node, edges)
    print("Página salva.")
