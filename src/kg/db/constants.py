"""
Constants for the YAGO database.
Some of these need to eventually be moved to a configuration file.
"""
import os

DEFAULT_DB_NAME = "yago.db"

YAGO_FACTS_ENTITY_COUNT = 5600415
YAGO_ALL_ENTITY_COUNT = 49687885

PREFIX_PATH = os.path.join(os.path.dirname(__file__), 'info/prefixes.txt')
ERROR_PATH = os.path.join(os.path.dirname(__file__), 'info/error.txt')

# NOTE: Replace the constants with configuration variables
# NOTE: These paths are relative to the current file's directory. 
# They only work if the .ttl files are present in the data directory.
# These are optional constants, and in real-time setting, these paths would be set in a configuration file.
TTL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-facts.ttl')
TTL_ALL_PATH = os.path.join(os.path.dirname(__file__), 'data/yago-beyond-wikipedia.ttl')