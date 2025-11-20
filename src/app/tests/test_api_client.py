from app.scraper.api_client import APIClient


def test_resolve_title():
    api = APIClient()
    page_id, title = api.resolve_title("Engenharia")

    assert isinstance(page_id, int)
    assert "Engenharia" in title


def test_fetch_metadata():
    api = APIClient()
    page_id, _ = api.resolve_title("Engenharia")
    data = api.fetch_metadata(page_id)

    page_data = data["query"]["pages"][str(page_id)]
    assert "title" in page_data
    assert "revisions" in page_data
    assert "contributors" in page_data
