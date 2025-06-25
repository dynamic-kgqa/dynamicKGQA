"""
Constants for the YAGO database.
Some of these need to eventually be moved to a configuration file.
"""
import os

DEFAULT_DB_NAME = "yago.db"

YAGO_FACTS_ENTITY_COUNT = 5600415
YAGO_ALL_ENTITY_COUNT = 49687885

TTL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-facts.ttl')
TTL_ALL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-beyond-wikipedia.ttl')

PREFIX_PATH = os.path.join(os.path.dirname(__file__), 'info/prefixes.txt')
ERROR_PATH = os.path.join(os.path.dirname(__file__), 'info/error.txt')