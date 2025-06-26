"""
This script contains some utility functions to generate queries for the YAGO knowledge graph, for entities.
"""
from typing import List

def get_random_entities_query(*, 
    num_of_entities: int = 1) -> str:
    """Generate a query to get a fixed number of random entities from the YAGO knowledge graph.

    Parameters:
    ----------
    num_of_entities: int
        The number of entities to query
    
    Returns:
    ----------
    query: str
        The query to get the random entities
    """
    query = f"""
    SELECT item_id, item_label FROM items ORDER BY RANDOM() LIMIT {num_of_entities}
    """
    return query

def get_entity_count_multiple_query(entity_ids: List[str]) -> str:
    """Generate a query to get the count of multiple entities from the YAGO knowledge graph.

    Parameters:
    ----------
    entity_ids: List[str]
        The list of entity IDs to query

    Returns:
    ----------
    query: str
        The sqlite3 query to get the count of the entities
    """
    query = f"""
    SELECT item_id, count FROM items WHERE item_id IN ({", ".join([f"'{entity_id}'" for entity_id in entity_ids])})
    """
    return query

def get_entity_count_from_label_multiple_query_parameterized(entity_labels: List[str]) -> str:
    """Generate a parameterized query to get the count of multiple entities from the YAGO knowledge graph.
    This query uses placeholders for the entity labels.

    Parameters:
    ----------
    entity_labels: List[str]
        The list of entity labels to query

    Returns:
    ----------
    query: str
        The sqlite3 query to get the count of the entities, along with their ids and labels
    """
    placeholders = ", ".join(["?"] * len(entity_labels))
    query = f"""
    SELECT item_id, item_label, count FROM items WHERE item_label IN ({placeholders})
    """
    return query

def get_entity_description_multiple_query(entity_ids: List[str]) -> str:
    """Generate a query to get the description of multiple entities from the YAGO knowledge graph.
    DEPRECATED: Do not use the DB for getting descriptions. Use the YAGO Knowledge Graph instead.

    Parameters:
    ----------
    entity_ids: List[str]
        The list of entity IDs to query

    Returns:
    ----------
    query: str
        The sqlite3 query to get the description of the entities
    """
    query = f"""
    SELECT item_description FROM items WHERE item_id IN ({", ".join([f"'{entity_id}'" for entity_id in entity_ids])})
    """
    return query