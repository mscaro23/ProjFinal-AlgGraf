def compute_links_in(nodes, edges):
    counts = {n.page_id: 0 for n in nodes}

    for e in edges:
        if e.target_page_id in counts:
            counts[e.target_page_id] += 1

    for n in nodes:
        n.links_in_count = counts[n.page_id]

    return nodes
