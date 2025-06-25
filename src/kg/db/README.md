# Yago Knowledge Graph Entity Database

This directory contains the code and other relevant files to set up an entity database for the Yago knowledge graph (KG) used in the DynamicKGQA project.
This entity database is currently the most efficient way to query entities from the Yago KG, especially random sampling since Blazegraph/SparQL does not support efficient random sampling queries.

The entity database is built using the Yago KG dump files and is designed to be used with the DynamicKGQA project. It provides a way to efficiently query entities from the Yago KG, especially for random sampling queries.

## Yago Entity Database Setup

The Yago entity database is a sqlite3 database that contains entities and their properties from the Yago KG. The database is built using the Yago KG dump files.