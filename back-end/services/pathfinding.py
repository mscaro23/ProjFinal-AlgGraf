"""
Serviço para encontrar caminhos entre páginas no grafo.
Implementa busca do caminho mais curto e caminho mais lógico (baseado em PageRank).
"""
from typing import List, Optional, Dict, Tuple, Any
from collections import deque, defaultdict
from sqlalchemy.orm import Session
from db.db_models import Page, Link
from services.pagerank_service import load_graph_from_db


def build_adjacency_list(edges: List[Any]) -> Dict[int, List[int]]:
    """
    Constrói lista de adjacência a partir das arestas.
    
    Args:
        edges: Lista de objetos com source_page_id e target_page_id
    
    Returns:
        dict: {page_id: [lista de page_ids vizinhos]}
    """
    adj = defaultdict(list)
    for edge in edges:
        adj[edge.source_page_id].append(edge.target_page_id)
    return adj


def shortest_path_bfs(
    session: Session,
    source_page_id: int,
    target_page_id: int,
) -> Optional[List[int]]:
    """
    Encontra o caminho mais curto entre duas páginas usando BFS.
    
    Args:
        session: Sessão do banco de dados
        source_page_id: ID da página origem
        target_page_id: ID da página destino
    
    Returns:
        Lista de page_ids representando o caminho, ou None se não houver caminho
    """
    # Verifica se as páginas existem
    source_page = session.query(Page).filter_by(page_id=source_page_id).first()
    target_page = session.query(Page).filter_by(page_id=target_page_id).first()
    
    if not source_page or not target_page:
        return None
    
    if source_page_id == target_page_id:
        return [source_page_id]
    
    # Carrega grafo do banco
    nodes, edges = load_graph_from_db(session)
    
    # Constrói lista de adjacência
    adj = build_adjacency_list(edges)
    
    # BFS
    queue = deque([(source_page_id, [source_page_id])])
    visited = {source_page_id}
    
    while queue:
        current, path = queue.popleft()
        
        # Verifica se chegou ao destino
        if current == target_page_id:
            return path
        
        # Explora vizinhos
        for neighbor in adj.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    # Não encontrou caminho
    return None


def logical_path_by_pagerank(
    session: Session,
    source_page_id: int,
    target_page_id: int,
    max_depth: int = 10,
) -> Optional[List[int]]:
    """
    Encontra o caminho mais lógico entre duas páginas baseado em PageRank.
    Usa busca em largura com priorização por PageRank.
    
    Args:
        session: Sessão do banco de dados
        source_page_id: ID da página origem
        target_page_id: ID da página destino
        max_depth: Profundidade máxima de busca (default: 10)
    
    Returns:
        Lista de page_ids representando o caminho, ou None se não houver caminho
    """
    # Verifica se as páginas existem
    source_page = session.query(Page).filter_by(page_id=source_page_id).first()
    target_page = session.query(Page).filter_by(page_id=target_page_id).first()
    
    if not source_page or not target_page:
        return None
    
    if source_page_id == target_page_id:
        return [source_page_id]
    
    # Carrega grafo e PageRanks do banco
    nodes, edges = load_graph_from_db(session)
    
    # Cria dicionário de PageRanks
    pagerank_scores = {}
    pages = session.query(Page).all()
    for page in pages:
        pagerank_scores[page.page_id] = page.pagerank_score or 0.0
    
    # Constrói lista de adjacência
    adj = build_adjacency_list(edges)
    
    # Busca com priorização por PageRank
    # Usa uma fila de prioridade simulada (ordena por PageRank)
    queue = deque([(source_page_id, [source_page_id], 0)])
    visited = {source_page_id}
    best_path = None
    best_score = -1
    
    while queue:
        current, path, depth = queue.popleft()
        
        # Limita profundidade
        if depth >= max_depth:
            continue
        
        # Verifica se chegou ao destino
        if current == target_page_id:
            # Calcula score do caminho (soma dos PageRanks)
            path_score = sum(pagerank_scores.get(pid, 0.0) for pid in path)
            if path_score > best_score:
                best_score = path_score
                best_path = path
            continue
        
        # Ordena vizinhos por PageRank (maior primeiro)
        neighbors = adj.get(current, [])
        neighbors_sorted = sorted(
            neighbors,
            key=lambda n: pagerank_scores.get(n, 0.0),
            reverse=True
        )
        
        # Explora vizinhos priorizando os com maior PageRank
        for neighbor in neighbors_sorted:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor], depth + 1))
    
    return best_path


def find_paths(
    session: Session,
    source_page_id: int,
    target_page_id: int,
    max_depth: int = 10,
) -> Dict[str, Optional[List[Dict]]]:
    """
    Encontra ambos os caminhos (mais curto e mais lógico) entre duas páginas.
    
    Args:
        session: Sessão do banco de dados
        source_page_id: ID da página origem
        target_page_id: ID da página destino
        max_depth: Profundidade máxima para busca lógica (default: 10)
    
    Returns:
        dict com:
            - shortest_path: caminho mais curto (lista de dicts com page_id, title, url)
            - logical_path: caminho mais lógico (lista de dicts com page_id, title, url)
            - shortest_length: número de vértices no caminho mais curto
            - logical_length: número de vértices no caminho mais lógico
    """
    # Busca caminho mais curto
    shortest_path_ids = shortest_path_bfs(session, source_page_id, target_page_id)
    
    # Busca caminho mais lógico
    logical_path_ids = logical_path_by_pagerank(
        session, source_page_id, target_page_id, max_depth
    )
    
    # Converte IDs para objetos com informações das páginas
    def path_ids_to_objects(path_ids: Optional[List[int]]) -> Optional[List[Dict]]:
        if path_ids is None:
            return None
        
        result = []
        for page_id in path_ids:
            page = session.query(Page).filter_by(page_id=page_id).first()
            if page:
                result.append({
                    "page_id": page.page_id,
                    "title": page.title,
                    "url": page.url,
                    "pagerank_score": page.pagerank_score or 0.0,
                })
        return result
    
    shortest_path = path_ids_to_objects(shortest_path_ids)
    logical_path = path_ids_to_objects(logical_path_ids)
    
    return {
        "shortest_path": shortest_path,
        "logical_path": logical_path,
        "shortest_length": len(shortest_path_ids) if shortest_path_ids else None,
        "logical_length": len(logical_path_ids) if logical_path_ids else None,
        "source_page_id": source_page_id,
        "target_page_id": target_page_id,
    }

