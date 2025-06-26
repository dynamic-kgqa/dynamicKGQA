"""
This module contains RandomWalk2 class.
It takes into account the number of facts an entity is involved in to weight the sampling.
It also returns the description of the entities and predicates.

NOTE: Most of the functions work with entity_labels instead of entity_ids.
"""
import os
import sys
import random
import requests
import argparse
from typing import List, Set
import re

import numpy as np
import pandas as pd

from kg.db.yago_db import YagoDB
from kg.db.constants import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT
from kg.db.queries import get_random_entities_query, \
    get_entity_count_from_label_multiple_query_parameterized
from kg.query import get_triples_multiple_subjects_query, get_description_multiple_entities_query, \
    query_kg, get_triples_from_response
from kg.constants import YAGO_ENTITY_STORE_DB_PATH, YAGO_PREFIXES_PATH, YAGO_ENDPOINT_URL, \
    PREFIXES, INVALID_PROPERTIES
from kg.prefix import get_prefixes, get_url_from_prefix_and_id

SPARQL_COLUMNS_DICT = {
    "subject": "subject",
    "predicate": "predicate",
    "object": "object",
    "object_count": "object_count",
    "description": "description"
}

class RandomWalk:
    """
    RandomWalk2 class.
    It takes into account the number of facts an entity is involved in to weight the sampling.
    It also returns the description of the entities and predicates.

    NOTE: Most of the functions work with entity_labels instead of entity_ids.
    """
    def __init__(self, yago_db: YagoDB, *, yago_endpoint_url = YAGO_ENDPOINT_URL,
        sparql_columns_dict: dict = SPARQL_COLUMNS_DICT):
        """
        Initialize the RandomWalk2 object.

        Parameters:
        ----------
        yago_db: YagoDB
            The YagoDB object

        yago_endpoint_url: str
            The YAGO endpoint URL

        sparql_columns_dict: dict
            The SPARQL columns dictionary
        """
        self.yago_db = yago_db
        self.yago_endpoint_url = yago_endpoint_url
        self.sparql_columns_dict = sparql_columns_dict

    def random_walk_batch(self, num_of_entities: int = 10, depth: int = 3) -> pd.DataFrame:
        """
        Random walks on the YAGO knowledge graph.
        This algorithm weights the neighbouring entities based on the number of facts they are involved in.

        Parameters:
        ----------
        num_of_entities: int
            Number of entities to start the random walk with

        depth: int
            Depth of the random walk

        Returns:
        ----------
        entities_df: pd.DataFrame
            The dataframe of entities and their neighbors
            Schema: entity0, predicate1, entity1, predicate2, entity2, ...
        """
        random_entities_query = get_random_entities_query(num_of_entities=num_of_entities)
        entities = self.yago_db.query(random_entities_query)
        entities_df = pd.DataFrame([f"{entity[1]}" for entity in entities], columns=["entity0"])

        for i in range(depth - 1):
            entities_single_hop = self.single_hop_batch(entity_df=entities_df, entity_column_label=f"entity{i}",)
            entities_df[[f"predicate{i+1}", f"entity{i+1}"]] = entities_single_hop

        return entities_df

    def random_walk_description_batch(self, num_of_entities: int = 10, depth: int = 3) -> pd.DataFrame:
        """
        Random walks on the YAGO knowledge graph.
        This algorithm weights the neighbouring entities based on the number of facts they are involved in.
        This algorithm also returns the description of the entities and predicates.

        Parameters:
        ----------
        num_of_entities: int
            Number of entities to start the random walk with

        depth: int
            Depth of the random walk

        Returns:
        ----------
        entity_df: pd.DataFrame
            The dataframe of entities and their neighbors
            Schema: entity0, predicate1, entity1, predicate2, entity2, ...
        """
        # First, randomly select the entities
        random_entities_query = get_random_entities_query(num_of_entities=num_of_entities)
        entities = self.yago_db.query(random_entities_query)
        entity_df = pd.DataFrame([f"{entity[1]}" for entity in entities], columns=["entity0"])
        # Add descriptions for the entities
        entity_df["description0"] = self._get_descriptions_for_entities(entity_df=entity_df, 
            entity_column_label="entity0", description_label="description0")["description0"]

        for i in range(depth - 1):
            # Get the entities for the next hop
            entities_single_hop = self.single_hop_batch(entity_df=entity_df, entity_column_label=f"entity{i}",)
            entity_df[[f"predicate{i+1}", f"entity{i+1}"]] = entities_single_hop
            # Add descriptions for the entities
            entity_df[f"description{i+1}"] = self._get_descriptions_for_entities(entity_df=entity_df, 
                entity_column_label=f"entity{i+1}", description_label=f"description{i+1}")[f"description{i+1}"]

        return entity_df

    def single_hop_batch(self, entity_df: pd.DataFrame, entity_column_label: str, *,
        entities_hop_1_cols: dict = None) -> pd.DataFrame:
        """
        Single-hop random walk on the YAGO knowledge graph.
        Takes a dataframe of entities and returns a dataframe of entities and their neighbors.

        Parameters:
        ----------
        entity_df: pd.DataFrame
            The dataframe of entities
        
        entity_column_label: str
            The entity column label from which to perform the single hop

        entities_hop_1_cols: dict
            The dictionary of columns to use for the returned entities in the first hop

        Returns:
        ----------
        entity_df: pd.DataFrame
            The dataframe of entities and their neighbors
        """
        if entities_hop_1_cols is None:
            entities_hop_1_cols = {0: "predicate1", 1: "entity1"}
        
        # First, get the triples for the entities
        entities = self._get_valid_entity_list(entity_list=entity_df[entity_column_label].tolist())
        # [f"<{entity}>" for entity in entity_df[entity_column_label].tolist() if entity is not None]
        columns_dict = {
            key: value for key, value in self.sparql_columns_dict.items() 
            if key in ["subject", "predicate", "object", "object_count"]
        }
        try:
            query2 = get_triples_multiple_subjects_query(
                entities=entities, 
                columns_dict=columns_dict,
                prefixes=PREFIXES,
                invalid_properties=INVALID_PROPERTIES,
                filter_literals=False
            )
            response = query_kg(self.yago_endpoint_url, query2)
            triples = get_triples_from_response(response)
        except Exception as e:
            print(f"Single hop query failed for: {entity_column_label}", e)
            triples = pd.DataFrame(columns=columns_dict.values())

        # Get the counts for the objects
        try:
            triples_object_counts = self._get_counts_for_entities(entity_df=triples,
                entity_column_label=columns_dict["object"], 
                count_label=columns_dict["object_count"])
            ## The counts returned by _get_counts_for_entities align with the triples
            triples[columns_dict["object_count"]] = \
                triples_object_counts[columns_dict["object_count"]].values
        except Exception as e:
            print(f"Single hop object counts failed for: {entity_column_label}", e)
            triples[columns_dict["object_count"]] = 0

        # Finally, use the objects and their counts to get one entity each for the first hop
        entities_hop_1 = entity_df.apply(
            lambda row: self._sample_triple_for_entity_by_count(triples_df=triples, entity=row[entity_column_label], 
                weight_column_label=columns_dict["object_count"]),
            axis=1, result_type="expand").rename(columns=entities_hop_1_cols)
        return entities_hop_1


    def _get_counts_for_entities(self, entity_df: pd.DataFrame, entity_column_label: str, *,
        count_label: str = 'count') -> pd.DataFrame:
        """
        Get the counts for the entities.

        Parameters:
        ----------
        entity_df: pd.DataFrame
            The dataframe of entities

        entity_column_label: str
            The entity column label to use in the returned dataframe

        count_label: str
            The count label to use in the returned dataframe

        Returns:
        ----------
        counts_df: pd.DataFrame
            The dataframe of entities and their counts
        """
        entity_series = entity_df[entity_column_label]
        entity_labels = entity_series.tolist()

        query = get_entity_count_from_label_multiple_query_parameterized(entity_labels=entity_labels)
        # Need to utilize the cursor of YagoDB directly because the query is parameterized
        entity_counts = self.yago_db._curr.execute(query, entity_labels).fetchall()

        entity_counts_df = pd.DataFrame(entity_counts, columns=["entity_id", entity_column_label, count_label])
        entity_counts_df = entity_series.to_frame(name=entity_column_label)\
            .merge(entity_counts_df, left_on=entity_column_label, right_on=entity_column_label, how="left")
        # Fill count_label with 0 for entities with no counts
        entity_counts_df[count_label] = entity_counts_df[count_label].fillna(0)
        return entity_counts_df[[entity_column_label, count_label]]

    def _sample_triple_for_entity_by_count(self, triples_df: pd.DataFrame, entity: str, 
        weight_column_label: str = None) -> List[str]:
        """
        Samples triples for a given entity.
        Uses the count of the entities to weight the sampling.

        Parameters:
        ----------
        triples_df: pd.DataFrame
            The dataframe of triples with object count

        entity: str
            The entity to sample triples for

        Returns:
        ----------
        sampled_triple: List[str]
            The sampled triple as a list (predicate, object)
        """
        if entity is None:
            return [None, None]

        matched_triples_columns = [self.sparql_columns_dict["predicate"], self.sparql_columns_dict["object"], 
            self.sparql_columns_dict["object_count"]]
        matched_triples_df = triples_df\
            [triples_df[self.sparql_columns_dict["subject"]] == entity][matched_triples_columns]
        if len(matched_triples_df) == 0:
            return [None, None]
        
        if weight_column_label is None or matched_triples_df[weight_column_label].sum() == 0:
            sampled_triple = matched_triples_df.sample(n=1, replace=False).iloc[0]
        else:
            sampled_triple = matched_triples_df.sample(n=1, replace=False, weights=weight_column_label).iloc[0]
        return [sampled_triple[self.sparql_columns_dict["predicate"]], 
            sampled_triple[self.sparql_columns_dict["object"]]]

    def _get_descriptions_for_entities(self, entity_df: pd.DataFrame, entity_column_label: str, *,
        description_label: str = 'description') -> pd.DataFrame:
        """
        Add the English description of the entity.
        WARNING: Gets only the first description for each entity.

        Parameters:
        ----------
        entity_df: str
            The dataframe of entities

        entity_column_label: str
            The entity column label to use in the returned dataframe

        Returns:
        ----------
        description: pd.DataFrame
            The dataframe of entities and their descriptions
        """
        entity_series = entity_df[entity_column_label]
        entities = self._get_valid_entity_list(entity_list=entity_series.tolist())
        #[f"<{entity}>" for entity in entity_series.tolist() if entity is not None]
        columns_dict = {
            key: value for key, value in self.sparql_columns_dict.items() 
            if key in ["subject", "description"]
        }

        try:
            query = get_description_multiple_entities_query(
                entities=entities, 
                columns_dict=columns_dict
            )
            response = query_kg(self.yago_endpoint_url, query)
            entity_description_df = get_triples_from_response(
                response=response,
                columns_dict=columns_dict
            )
        except Exception as e:
            print(f"Description query failed for: {entity_column_label}", e)
            entity_description_df = pd.DataFrame(columns=columns_dict.values())

        # Get only the first description for each entity
        entity_description_df = entity_description_df.groupby(columns_dict["subject"]).first().reset_index()

        entity_description_df = entity_series.to_frame(name=entity_column_label)\
            .merge(entity_description_df, left_on=entity_column_label, right_on=columns_dict["subject"], 
            how="left")\
            .drop(columns=[columns_dict["subject"]])\
            .rename(columns={columns_dict["description"]: description_label})
        
        return entity_description_df[[entity_column_label, description_label]]

    def _get_valid_entity_list(self, entity_list: List[str]) -> List[str]:
        """
        Get the valid entities from the list.
        Filter out the entities that are not valid URLs.

        Parameters:
        ----------
        entity_list: List[str]
            The list of entities

        Returns:
        ----------
        entity_list: List[str]
            The list of filtered entities
        """
        
        url_validation_regex = r"^http[s]?://.*$"
        entity_list = [f"<{entity}>" for entity in entity_list if entity is not None and re.match(url_validation_regex, entity)]
        return entity_list
        

if __name__=='__main__':
    yago_db = YagoDB(db_name=YAGO_ENTITY_STORE_DB_PATH)
    random_walk = RandomWalk(yago_db=yago_db)
    entity_df = random_walk.random_walk_batch(num_of_entities=5, depth=3)
    print(entity_df.head(2))