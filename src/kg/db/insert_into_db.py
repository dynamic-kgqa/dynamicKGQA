"""
This script contains helper functions to insert data into a database, specifically for managing items, properties, and claims. It provides methods to insert new items, properties, and claims, as well as to update existing ones. The script also includes functions to retrieve items and properties from the database.
"""
import os
import sys
import argparse
from typing import List, Tuple
import sqlite3

from tqdm import tqdm

from classes import Item, Property, Claim
from constants import PREFIX_PATH
from yago_db import YagoDB

def check_prefix(entities: List[str]) -> bool:
    """
    Check if the entities of a line contains a prefix.

    Parameters:
    ----------
    entities: List[str]
        The entities of the line
    
    Returns:
    --------
    bool
        True if the line contains a prefix, False otherwise.
    """
    if len(entities) != 4:
        return False
    if entities[0] == '@prefix':
        return True
    return False

def check_triple(entities: List[str]) -> bool:
    """
    Check if the line contains a triple.
    A simple check at the moment, just checking if the line contains 3 entities.
    The logic may be updated in the future.
    
    Parameters:
    ----------
    entities: List[str]
        The entities of the line
    
    Returns:
    --------
    bool
        True if the line contains a triple, False otherwise.
    """
    if len(entities) != 4:
        return False
    return True

def insert_entities(entities: List[Tuple[str, str, str]], db: YagoDB) -> int:
    """
    Insert the entities into the database.

    Parameters:
    ----------
    entities: List[Tuple[str, str, str]]
        The entities to be inserted.

    db: YagoDB
        The database object.

    Returns:
    --------
    int
        The number of entities inserted.
    """
    items = [Item(*entity) for entity in entities]
    try:
        return db.insert_items(items)
    except Exception as e:
        # error_file.write(f'Error inserting items:\n')
        return 0

def insert_properties(properties: List[Tuple[str, str]], db: YagoDB) -> int:
    """
    Insert the properties into the database.

    Parameters:
    ----------
    properties: List[Tuple[str, str]]
        The properties to be inserted.

    db: YagoDB
        The database object.

    Returns:
    --------
    int
        The number of properties inserted.
    """
    properties = [Property(*property) for property in properties]
    try:
        return db.insert_properties(properties)
    except Exception as e:
        # error_file.write(f'Error inserting properties:\n')
        return 0

def read_ttl_line(line: str, prefix_dict: dict) -> Tuple[str, str, str]:
    """
    Read a line of the ttl file and return the entities and property.
    Also, if the line contains a prefix, insert the prefix into a json file, 
        and insert the prefix into the prefix_dict.

    Parameters:
    ----------
    line: str
        The line to be read.
    
    Returns:
    --------
    Tuple[str, str, str]
        The entities of the line.
    """
    entities = line.split()
    # print(entities)
    if check_prefix(entities):
        prefix = entities[1].replace(':', '')
        prefix_dict[prefix] = entities[2].replace('>', '').replace('<', '')
        # Insert the prefix into a json file
        with open(PREFIX_PATH, 'a') as f:
            f.write(f"{prefix}: {prefix_dict[prefix]}\n")
        return None
    if check_triple(entities):
        return entities
    return None

def read_ttl_file(ttl_path: str, db: YagoDB, batch_length: int) -> None:
    """
    Read the file in chunks and insert the entities into the database.
    Insert the entities in batches of `batch_length`.

    Parameters:
    ----------
    ttl_path: str
        The path to the ttl file.
    
    db: YagoDB
        The database object.

    batch_length: int
        The number of entities to be inserted in a batch.
        Currently, not in use for anything except logging.
    """
    # For Dev
    TOTAL = 10

    def createEntityLabel(entity: str) -> str:
        entity_string_list = entity.split(':')
        if len(entity_string_list) == 1:
            return entity
        if entity_string_list[0] not in prefix_dict:
            return entity
        return f"{prefix_dict[entity_string_list[0]]}{entity_string_list[1]}"

    prefix_dict = dict()

    entities_count = 0
    entities_set = dict()
    properties_count = 0
    properties_set = set()
    with open(ttl_path, 'r') as f:
        for line in tqdm(f):
            entities = read_ttl_line(line, prefix_dict)
            if not entities:
                continue
            
            if entities[0] not in entities_set:
                entities_set[entities[0]] = 1
            else:
                entities_set[entities[0]] += 1
            properties_set.add(entities[1])
            if len(entities_set) == batch_length:
                entities_list = list([entity, createEntityLabel(entity), None, count] 
                                     for (entity, count) in entities_set.items())

                res = insert_entities(entities_list, db)
                entities_set = dict()
                entities_count += res if res else 0
                print(f'Inserted {batch_length} entities. Total: {entities_count}')
            
            if len(properties_set) == batch_length:
                # Insert properties
                properties_list = list([property, None] for property in properties_set)

                res = insert_properties(properties_list, db)
                properties_set = set()
                properties_count += res if res else 0
                print(f'Inserted {batch_length} properties. Total: {properties_count}')
            # if count == TOTAL:
            #     return
        
        if entities_set:
            entities_list = list([entity, createEntityLabel(entity), None, count] 
                                 for (entity, count) in entities_set.items())
            # print(entities_list)
            res = insert_entities(entities_list, db)
            entities_count += res if res else 0
        if properties_set:
            properties_list = list([property, None] for property in properties_set)
            res = insert_properties(properties_list, db)
            properties_count += res if res else 0

        print(f'Inserted {entities_count} entities. Inserted {properties_count} properties.')

def main(ttl_path: str, db_name: str, batch_length: int) -> None:
    """
    Main function to insert entities into the database.

    Parameters:
    ----------
    ttl_path: str
        The path to the ttl file.
    
    db_name: str
        The name of the database.
    
    batch_length: int
        The number of entities to be inserted in a batch.
    """
    db = YagoDB(db_name)
    read_ttl_file(ttl_path, db, batch_length)

if __name__=="__main__":
    from constants import TTL_PATH, TTL_ALL_PATH, DEFAULT_DB_NAME, ERROR_PATH
    parser = argparse.ArgumentParser(description='Insert entities into the Yago database.')
    parser.add_argument('--ttl_path', type=str, default=TTL_PATH, help='Path to the ttl file.')
    parser.add_argument('--db_name', type=str, default=DEFAULT_DB_NAME, help='Name of the database.')
    parser.add_argument('--batch_length', type=int, default=1000000, help='Number of entities to be inserted in a batch.')
    args = parser.parse_args()
    
    error_file = open(ERROR_PATH, 'a')
    main(args.ttl_path, args.db_name, args.batch_length)
    args.ttl_path = TTL_ALL_PATH
    main(args.ttl_path, args.db_name, args.batch_length)
    error_file.close()