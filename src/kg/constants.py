import os

# TODO: Replace the constant with a configuration variable
YAGO_ENTITY_STORE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yago_all.db")

YAGO_PREFIXES_PATH = os.path.join(os.path.dirname(__file__), "db/info/prefixes.txt")

# TODO: Replace the constant with a configuration variable
YAGO_ENDPOINT_URL = "http://localhost:9999/bigdata/sparql"

PREFIXES = {
    "yago": "http://yago-knowledge.org/resource/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "owl": "http://www.w3.org/2002/07/owl#"
}

INVALID_PROPERTIES = {
    "schema:image",
    "schema:mainEntityOfPage",
    "schema:dateCreated",
    "schema:iataCode",
    "yago:iswcCode",
    "owl:sameAs",
    "yago:unemploymentRate",
    "schema:isbn",
    "schema:postalCode",
    "schema:icaoCode",
    "schema:url",
    "rdfs:comment",
    "schema:leiCode",
    "yago:humanDevelopmentIndex",
    "yago:length",
    "schema:gtin",
    "schema:logo",
    "schema:geo"
}