import logging
from fastapi import Depends
from db.repositories.page import (
    PageRepository,
    get_page_repository,
)
from models.graph_objects import (
    PageResponse,
    GraphInput,
    PageBase,
    GraphResponse,
    GraphLink,
)
from scraper.wiki_scraper import WikiScraper
from services.graph_builder import save_graph
from db.db_models import Page, Link
from sqlalchemy import text
from services.pagerank import pagerank


class PageService:
    def __init__(self, page_repository: PageRepository):
        self.repository = page_repository
        self.scraper = WikiScraper()

    def run_bfs(
        self, seed_title: str, max_depth: int, max_neighbors: int = 50
    ) -> set[int]:
        """
        Executa BFS a partir de uma página semente.
        Retorna conjunto de page_ids visitados.
        """
        queue = [(seed_title, 0)]  # (title, depth)
        visited_titles = set()
        visited_ids = set()

        while queue:
            current_title, current_depth = queue.pop(0)

            if current_depth > max_depth:
                continue

            if current_title in visited_titles:
                continue
            visited_titles.add(current_title)

            # Verificar se já existe no DB
            page_dict = self.repository.get_page_by_title(current_title)
            if page_dict:
                current_page_id = page_dict["page_id"]
                print(
                    f"[BFS] Página '{current_title}' já existe (ID: {current_page_id})"
                )
            else:
                # Não existe, fazer scraping
                try:
                    print(
                        f"[BFS] Scraping página '{current_title}' (depth {current_depth})..."
                    )
                    node, edges = self.scraper.scrape_page(title=current_title)
                    self.repository.save_page_with_links(node, edges)
                    current_page_id = node.page_id
                    print(f"[BFS] Página salva: {node.title} (ID: {current_page_id})")
                except Exception as e:
                    print(f"[BFS] Erro ao fazer scraping de '{current_title}': {e}")
                    continue

            visited_ids.add(current_page_id)

            # Adicionar vizinhos à fila (até o limite)
            if current_depth < max_depth:
                # Buscar links da página atual
                from sqlalchemy import text

                query = text(
                    "SELECT target_page_id FROM links WHERE source_page_id = :page_id LIMIT :limit"
                )
                result = self.repository.db_session.execute(
                    query, {"page_id": current_page_id, "limit": max_neighbors}
                )
                links = result.fetchall()

                for link in links:
                    target_page_id = link[0]
                    # Buscar página alvo
                    target_page_dict = self.repository.get_page_by_id(target_page_id)
                    if not target_page_dict:
                        node, edges = self.scraper.scrape_page(page_id=target_page_id)
                        self.repository.save_page_with_links(node, edges)
                        target_page_dict = self.repository.get_page_by_id(
                            target_page_id
                        )

                    if (
                        target_page_dict
                        and target_page_dict["title"] not in visited_titles
                    ):
                        queue.append((target_page_dict["title"], current_depth + 1))

        return visited_ids

    def generate_graph(self, seed: str, depth: int) -> GraphResponse | None:
        """
        Gera um grafo a partir do título semente e profundidade.
        Faz BFS, scraping quando necessário, e retorna o grafo.
        """
        try:
            print(f"[PageService] Gerando grafo: seed='{seed}', depth={depth}")

            # Executar BFS para coletar todas as páginas
            visited_ids = self.run_bfs(seed, depth, max_neighbors=50)

            if not visited_ids:
                print("[PageService] Nenhuma página visitada no BFS")
                return None

            # Buscar subgrafo do banco
            pages, links = self.repository.get_subgraph(list(visited_ids))

            # Criar mapa de page_id -> title
            id_to_title = {p["page_id"]: p["title"] for p in pages}

            # Montar resposta
            nodes = [p["title"] for p in pages]
            graph_links = [
                GraphLink(
                    source=id_to_title.get(link["source_page_id"], ""),
                    target=id_to_title.get(link["target_page_id"], ""),
                )
                for link in links
                if link["source_page_id"] in id_to_title
                and link["target_page_id"] in id_to_title
            ]

            print(
                f"[PageService] Grafo gerado: {len(nodes)} nós, {len(graph_links)} arestas"
            )

            return GraphResponse(nodes=nodes, links=graph_links)

        except Exception as e:
            print(f"[PageService] Erro ao gerar grafo: {e}")
            return None

    def get_page_by_id(self, page_id: int) -> PageResponse | None:
        page_dict = self.repository.get_page_by_id(page_id)
        if not page_dict:
            return None
        # Converte dict para PageResponse (validação automática)
        return PageResponse(**page_dict)

    def get_or_scrape_page_by_title(self, title: str) -> PageResponse | None:
        """
        Busca página por título. Se não existir, faz scraping da Wikipedia e salva.
        """
        # Primeiro tenta buscar no banco
        page_dict = self.repository.get_page_by_title(title)
        if page_dict:
            return PageResponse(**page_dict)

        # Se não encontrou, faz scraping
        try:
            print(f"[PageService] Página '{title}' não encontrada. Fazendo scraping...")
            node, edges = self.scraper.scrape_page(title)

            # Salva no banco
            self.repository.save_page_with_links(node, edges)

            # Busca novamente para retornar com o formato correto
            page_dict = self.repository.get_page_by_id(node.page_id)
            if page_dict:
                return PageResponse(**page_dict)

            return None
        except Exception as e:
            print(f"[PageService] Erro ao fazer scraping: {e}")
            return None

    def calculate_pagerank(self, nodes: list[str]) -> dict[str, float] | None:
        """
        Calcula o PageRank para um conjunto de nós (títulos).
        Atualiza o banco de dados com os scores e retorna o resultado.
        """
        try:
            logging.info(f"[PageService] Calculando PageRank para {len(nodes)} nós...")

            # Buscar page_ids dos títulos
            title_to_id = {}
            page_responses = []

            for title in nodes:
                page_dict = self.repository.get_page_by_title(title)
                if page_dict:
                    title_to_id[title] = page_dict["page_id"]
                    page_responses.append(PageResponse(**page_dict))

            if not page_responses:
                logging.warning(
                    "[PageService] Nenhuma página encontrada para cálculo de PageRank"
                )
                return None

            # Buscar links entre essas páginas
            page_ids = list(title_to_id.values())
            _, links_dicts = self.repository.get_subgraph(page_ids)

            # Converter para LinkBase
            from models.graph_objects import LinkBase

            links = [
                LinkBase(
                    source_page_id=link["source_page_id"],
                    target_page_id=link["target_page_id"],
                    anchor_text=link.get("anchor_text"),
                )
                for link in links_dicts
            ]

            pagerank_scores = pagerank(page_responses, links)

            # Atualizar banco de dados
            for page_id, score in pagerank_scores.items():
                query = text(
                    "UPDATE pages SET pagerank_score = :score WHERE page_id = :page_id"
                )
                self.repository.db_session.execute(
                    query, {"score": score, "page_id": page_id}
                )

            self.repository.db_session.commit()

            id_to_title = {v: k for k, v in title_to_id.items()}
            result = {
                id_to_title[page_id]: score
                for page_id, score in pagerank_scores.items()
            }

            logging.info(
                f"[PageService] PageRank calculado e salvo para {len(result)} páginas"
            )
            return result

        except Exception as e:
            logging.error(f"[PageService] Erro ao calcular PageRank: {e}")
            return None


def get_page_service(
    page_repository: PageRepository = Depends(get_page_repository),
) -> PageService:
    """Dependency injection factory para PageService"""
    return PageService(page_repository)
