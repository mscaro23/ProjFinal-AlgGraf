import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.session import SessionLocal
from db.engine import engine
from db.base import Base
from scraper.wiki_scraper import WikiScraper
from services.graph_builder import save_graph
from db.db_models import Page, Link


def main():
    print("Creating tables if not exist...")
    Base.metadata.create_all(bind=engine)

    scraper = WikiScraper()
    session = SessionLocal()

    start_page = "química"
    max_depth = 2
    max_neighbors = 1000  # Limit neighbors per page to avoid explosion

    # Queue stores (title, depth)
    queue = [(start_page, 0)]
    visited_in_run = set()

    print(
        f"Starting BFS scrape from: {start_page} (Max depth: {max_depth}, Max neighbors/page: {max_neighbors})"
    )

    try:
        while queue:
            print(f"Queue size: {len(queue)}")
            current_title, current_depth = queue.pop(0)

            if current_depth > max_depth:
                continue

            if current_title in visited_in_run:
                continue
            visited_in_run.add(current_title)

            # Check if already exists in DB (simple check by title)
            existing = session.query(Page).filter(Page.title == current_title).first()
            if existing:
                print(
                    f"Skipping '{current_title}' (already in DB). Loading links for queue..."
                )
                if current_depth < max_depth:
                    links = (
                        session.query(Link)
                        .filter(Link.source_page_id == existing.page_id)
                        .all()
                    )

                    added_count = 0
                    for link in links:
                        if added_count >= max_neighbors:
                            break
                        if (
                            link.target_title
                            and link.target_title not in visited_in_run
                        ):
                            queue.append((link.target_title, current_depth + 1))
                            added_count += 1
                continue

            try:
                print(f"\n--- Scraping [Depth {current_depth}]: {current_title} ---")
                node, edges = scraper.scrape_page(current_title)

                existing_by_id = (
                    session.query(Page).filter(Page.page_id == node.page_id).first()
                )
                if existing_by_id:
                    print(
                        f"Page '{node.title}' (ID: {node.page_id}) already in DB. Updating..."
                    )

                save_graph(session, node, edges)

                # Add neighbors to queue
                if current_depth < max_depth:
                    added_count = 0
                    for edge in edges:
                        if added_count >= max_neighbors:
                            break
                        if (
                            edge.target_title
                            and edge.target_title not in visited_in_run
                        ):
                            queue.append((edge.target_title, current_depth + 1))
                            added_count += 1

            except Exception as e:
                print(f"Error scraping '{current_title}': {e}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
