from scraper.html_parser import HTMLParser

HTML_SAMPLE = """
<p>A engenharia é relacionada ao <a href="/wiki/Desenho">desenho</a>
e também ao <a href="/wiki/C%C3%A1lculo">cálculo</a>.</p>
"""


def test_extract_links():
    parser = HTMLParser()
    links = parser.extract_links(HTML_SAMPLE)

    titles = [t for t, anchor in links]
    anchors = [anchor for t, anchor in links]

    assert "Desenho" in titles
    assert "desenho" in anchors

    assert "Cálculo" in titles
    assert "cálculo" in anchors
