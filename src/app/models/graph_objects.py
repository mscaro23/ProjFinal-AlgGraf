from dataclasses import dataclass


@dataclass
class PageNode:
    page_id: int
    title: str
    url: str
    length_chars: int
    num_editors: int
    num_revisions: int
    links_out_count: int
    links_in_count: int = 0


@dataclass
class LinkNode:
    source_page_id: int
    target_page_id: int
    anchor_text: str
    target_title: str = ""
