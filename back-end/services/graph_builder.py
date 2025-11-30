from sqlalchemy.orm import Session
from db.models.page import Page
from db.models.link import Link
from models.graph_objects import PageNode, PageLink


def save_graph(session: Session, node: PageNode, edges: list[PageLink]):
    """
    Salva um nó (Page) e suas arestas (Links) no banco de dados.
    """

    existing_page = session.query(Page).filter_by(page_id=node.page_id).first()

    if existing_page:
        existing_page.title = node.title
        existing_page.url = node.url
        existing_page.length_chars = node.length_chars
        existing_page.num_editors = node.num_editors
        existing_page.num_revisions = node.num_revisions
        existing_page.links_out_count = node.links_out_count
    else:
        new_page = Page(
            page_id=node.page_id,
            title=node.title,
            url=node.url,
            length_chars=node.length_chars,
            num_editors=node.num_editors,
            num_revisions=node.num_revisions,
            links_out_count=node.links_out_count,
            links_in_count=0,
            pagerank_score=0.0,
        )
        session.add(new_page)

    session.query(Link).filter_by(source_page_id=node.page_id).delete()

    for edge in edges:
        new_link = Link(
            source_page_id=edge.source_page_id,
            target_page_id=edge.target_page_id,
            anchor_text=edge.anchor_text,
        )
        session.add(new_link)

    session.commit()
    print("Página salva.")
