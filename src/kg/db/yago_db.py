import os
from typing import Set, List
from abc import ABC
import sqlite3
import argparse

from classes import Item, Property, Claim
from constants import DEFAULT_DB_NAME

class YagoDB:
    """Class for interacting with a Yago DB.
    
    Note: At the moment, we will not be using the logic related to property and claim. 
    We will only be using the logic related to items.
    
    """
    def __init__(self, db_name: str = DEFAULT_DB_NAME):
        """Instantiate the database helper."""
        self._conn = sqlite3.connect(db_name)
        self._curr = self._conn.cursor()

    def getConnection(self):
        return self._conn
    
    def getCursor(self):
        return self._curr

    def create_db(self):
        """Create the database."""
        self._curr.execute('''
            CREATE TABLE items (
                item_id TEXT PRIMARY KEY,
                item_label TEXT,
                item_description TEXT,
                count INTEGER DEFAULT 0
            )
        ''')
        self._curr.execute('''
            CREATE TABLE properties (
                property_id TEXT PRIMARY KEY,
                property_label TEXT,
                count INTEGER DEFAULT 0
            )
        ''')
        self._curr.execute('''
            CREATE TABLE claims (
                claim_id INTEGER PRIMARY KEY,
                item_id TEXT,
                property_id TEXT,
                target_id TEXT
            )
        ''')
        self._conn.commit()

    def get_item(self, item_id: str) -> Item:
        """Get an item from the database.

        Args:
        - item_id: ID of the item to be returned

        Returns:
        - The `Item` if it exists
        """
        self._curr.execute('''
            SELECT * FROM items WHERE item_id = ?
        ''', (item_id,))
        row = self._curr.fetchone()
        return Item(*row)
    
    def insert_item(self, item: Item) -> int:
        """Insert an item into the database.

        Args:
        - item: `Item` to be inserted
        """
        self._curr.execute('''
            INSERT OR IGNORE INTO items (item_id, item_label, item_description)
                           VALUES (?, ?, ?)
                           RETURNING item_id
        ''', (item.item_id, item.item_label, item.item_description))
        id = self._curr.fetchone()[0]
        self._conn.commit()
        return id
    
    def insert_items(self, items: List[Item]) -> int:
        """Insert multiple items into the database.
        Used for efficient inserts with executemany.
        Also updates the count of the items.

        Args:
        - items: List of `Item` to be inserted
        """
        self._curr.executemany('''
            INSERT INTO items (item_id, item_label, item_description, count) 
                               VALUES (?, ?, ?, ?)
                               ON CONFLICT(item_id) DO UPDATE SET count = count + ?
        ''', [(item.item_id, item.item_label, item.item_description, item.count, item.count) for item in items])
        rows_inserted = self._curr.rowcount
        self._conn.commit()
        return rows_inserted

    
    def get_property(self, property_id: str) -> Property:
        """Get a property from the database.

        Args:
        - property_id: ID of the property to be returned

        Returns:
        - The `Property` if it exists
        """
        self._curr.execute('''
            SELECT * FROM properties WHERE property_id = ?
        ''', (property_id,))
        row = self._curr.fetchone()
        return Property(*row)
    
    def insert_property(self, property: Property) -> int:
        """Insert a property into the database.

        Args:
        - property: `Property` to be inserted
        """
        self._curr.execute('''
            INSERT OR IGNORE INTO properties VALUES (?, ?)
                           RETURNING property_id
        ''', (property.property_id, property.property_label))
        id = self._curr.fetchone()[0]
        self._conn.commit()
        return id

    def insert_properties(self, properties: List[Property]) -> int:
        """Insert multiple properties into the database.
        Used for efficient inserts with executemany.

        Args:
        - properties: List of `Property` to be inserted
        """
        self._curr.executemany('''
            INSERT OR IGNORE INTO properties VALUES (?, ?)
        ''', [(property.property_id, property.property_label) for property in properties])
        rows_inserted = self._curr.rowcount
        self._conn.commit()
        return rows_inserted

    def insert_properties_with_counts(self, properties: List[Property]) -> int:
        """
        Insert multiple properties into the database.
        Also updates the count of the properties.

        Args:
        - properties: List of `Property` to be inserted
        """
        self._curr.executemany('''
            INSERT INTO properties (property_id, property_label, count) 
                               VALUES (?, ?, ?)
                               ON CONFLICT(property_id) DO UPDATE SET count = count + ?
        ''', [(property_.property_id, property_.property_label, property_.count, property_.count) for property_ in properties])
        rows_inserted = self._curr.rowcount
        self._conn.commit()
        return rows_inserted


    def get_claim(self, claim_id: int) -> Claim:
        """Get a claim from the database.

        Args:
        - claim_id: ID of the claim to be returned

        Returns:
        - The `Claim` if it exists
        """
        self._curr.execute('''
            SELECT * FROM claims WHERE claim_id = ?
        ''', (claim_id,))
        row = self._curr.fetchone()
        return Claim(*row)
    
    def claims_from_subject(self, subject_id: str) -> Set[Claim]:
        """Get outgoing claims relating to an item.

        Args:
        - subject_id: ID of the `Item` to get outgoing claims from

        Returns:
        - Claims where `item_id` is the subject of the claim
        """
        self._curr.execute('''
            SELECT * FROM claims WHERE subject_id = ?
        ''', (subject_id,))
        return {Claim(*row) for row in self._curr.fetchall()}
    
    def random_item(self) -> Item:
        """Get a random item from the database.

        Returns:
        - Randomly selected `Item`
        """
        self._curr.execute('''
            SELECT * FROM items WHERE item_id IN (SELECT item_id FROM items ORDER BY RANDOM() LIMIT 1)
        ''', ())
        return Item(*self._curr.fetchone())
    
    def claims_from_target(self, target_id: str) -> Set[Claim]:
        """Get incoming claims relating to an item.

        Args:
        - target_id: ID of the `Item` to get incoming claims from

        Returns:
        - Claims where `target_id` is the target of the claim
        """
        self._curr.execute('''
            SELECT * FROM claims WHERE target_id = ?
        ''', (target_id,))
        return {Claim(*row) for row in self._curr.fetchall()}

    def close(self) -> None:
        """Close the connection to the database."""
        self._curr.close()
        self._conn.close()

    def query(self, query: str):
        """Query the database.

        Args:
        - query: The query to be run

        Returns:
        - The result of the query
        """
        self._curr.execute(query)
        return self._curr.fetchall()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default=DEFAULT_DB_NAME)
    args = parser.parse_args()
    db = YagoDB(args.db)
    db.create_db()
    db.close()

if __name__ == '__main__':
    main()