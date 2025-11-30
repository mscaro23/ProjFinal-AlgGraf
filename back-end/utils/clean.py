UNWANTED_PREFIXES = [
    "Ficheiro:",
    "Arquivo:",
    "Categoria:",
    "Especial:",
    "Ajuda:",
    "Portal:",
]


def is_valid_wiki_link(title: str) -> bool:
    """Filtra namespaces indesejados."""
    return not any(title.startswith(prefix) for prefix in UNWANTED_PREFIXES)


def normalize_title(title: str) -> str:
    """Converte underscores para espaços."""
    return title.replace("_", " ")
