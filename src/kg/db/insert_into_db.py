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
from constants import DEFAULT_DB_NAME
from yago_db import YagoDB

