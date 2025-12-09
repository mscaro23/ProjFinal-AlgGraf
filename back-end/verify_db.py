import sys
import os

# Add the current directory to sys.path to make sure we can import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import SessionLocal
from db.db_models import Page, Link
from sqlalchemy import func


def verify_database():
    session = SessionLocal()
    try:
        # Count pages
        page_count = session.query(func.count(Page.page_id)).scalar()
        print(f"Total de Páginas no banco de dados: {page_count}")

        # Count links
        link_count = session.query(func.count(Link.id)).scalar()
        print(f"Total de Links no banco de dados: {link_count}")

        if page_count > 0:
            print("\nÚltimas 5 Páginas:")
            pages = session.query(Page).order_by(Page.page_id.desc()).limit(5).all()
            for p in pages:
                print(f" - [{p.page_id}] {p.title} (URL: {p.url})")

        if link_count > 0:
            print("\nÚltimos 5 Links:")
            links = session.query(Link).order_by(Link.id.desc()).limit(5).all()
            for l in links:
                print(
                    f" - Link ID {l.id}: Page {l.source_page_id} -> Page {l.target_page_id} (Anchor: {l.anchor_text})"
                )

    except Exception as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    verify_database()
