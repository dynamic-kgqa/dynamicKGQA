import json
from kg.query import query_kg, query_kg_endpoint, get_triples_from_response
from concurrent.futures import ThreadPoolExecutor
from typing import List


yago_endpoint_url = "http://localhost:9999/bigdata/sparql"
exclude_props = ['schema:image','schema:about', 'rdfs:comment', 'schema:gtin', 'schema:url', 'rdfs:label', 'schema:postalCode', 'schema:isbn', 'schema:sameAs', 'schema:mainEntityOfPage', 'schema:leiCode', 'rdf:type', 'schema:dateCreated', 'yago:unemploymentRate', 'yago:length', 'schema:description', 'yago:iswcCode', 'schema:iataCode', 'schema:logo', 'schema:alternateName', 'schema:geo', 'rdfs:subclassOf', 'schema:icaoCode', 'yago:humanDevelopmentIndex', 'owl:sameAs', 'schema:dateCreated', 'schema:startDate', 'schema:endDate', 'yago:follows', 'schema:superEvent']

def load_json(file_path):
    """
    Convenience function to load a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        dict or list: The loaded JSON data.
        None: If there is an error loading the file.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print("JSON data loaded successfully!")
            return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    return None

def combine_lists_from_dict(input_dict):
    """
    Combines all list values in a dictionary into a single list,
    excluding non-list values.

    Args:
        input_dict (dict): The dictionary with potential list values.

    Returns:
        list: A combined list of all list values.
    """
    combined_list = []
    for value in input_dict.values():
        if isinstance(value, list):  # Check if the value is a list
            combined_list.extend(value)
    return combined_list

def extract_ids_with_prefix(entries):
    """
    Extracts the 'id' value from each entry in a list of dictionaries
    and appends a "Q" prefix to each ID.

    Args:
        entries (list): List of dictionaries containing an 'id' key.

    Returns:
        list: A list of 'id' values prefixed with "Q".
    """
    return [f"Q{entry.get('id')}" for entry in entries if 'id' in entry]



# def get_yago_query_direct_neighbors(entity_id, max_limit=1000, format_yago_prefix = True):
#     """
#     Generates a SPARQL query for a given YAGO entity ID.

#     Args:
#             entity_id (str): The YAGO entity ID.

#     Returns:
#             str: A SPARQL query as a string.
#     """
    
#     if format_yago_prefix:
#         entity_id = entity_id.replace('http://yago-knowledge.org/resource/', 'yago:')
    
#     query_template = """
#     PREFIX schema: <http://schema.org/>
#     PREFIX yago: <http://yago-knowledge.org/resource/>
#     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

#     SELECT DISTINCT ?sub ?pred ?obj WHERE {{
#         {{
#             {entity_id} ?pred ?obj .
#         }}
#         UNION
#         {{
#             ?sub ?pred {entity_id} .
#         }}
#         FILTER (?pred NOT IN (rdfs:comment, rdfs:subClassOf, rdfs:label, rdf:type,  schema:description, schema:alternateName, schema:mainEntityOfPage, schema:image, schema:sameAs))
#     }}
#     LIMIT {max_limit}
#     """
#     return query_template.format(entity_id=entity_id, max_limit=max_limit)

def get_yago_query_direct_neighbors(entity_id, max_limit=1000, exclude_properties=exclude_props, format_yago_prefix=True):
    """
    Generates a SPARQL query for a given YAGO entity ID, with an option to exclude specific properties.

    Args:
        entity_id (str): The YAGO entity ID.
        max_limit (int): Maximum number of results to return.
        exclude_properties (list): List of properties to exclude.
        format_yago_prefix (bool): Whether to format the entity ID to use the YAGO prefix.

    Returns:
        str: A SPARQL query as a string.
    """
    if format_yago_prefix:
        entity_id = entity_id.replace('http://yago-knowledge.org/resource/', 'yago:')
    
    # Default exclusion list if none provided
    if exclude_properties is None:
        exclude_properties = [
            "rdfs:comment", "rdfs:label", "rdf:type", 
            "schema:description", "schema:alternateName", 
            "schema:mainEntityOfPage", "schema:image", "schema:sameAs"
        ]
        
    
    
    # Dynamically create the FILTER clause
    exclude_filter = "FILTER (?pred NOT IN ({}))".format(", ".join(exclude_properties))
    
    query_template = f"""
    PREFIX schema: <http://schema.org/>
    PREFIX yago: <http://yago-knowledge.org/resource/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT DISTINCT ?sub ?pred ?obj WHERE {{
        {{
            {entity_id} ?pred ?obj .
        }}
        UNION
        {{
            ?sub ?pred {entity_id} .
        }}
        {exclude_filter}
    }}
    LIMIT {max_limit}
    """
    return query_template


# def get_yago_query_direct_neighbors(entity_id, max_limit=1000, format_yago_prefix = True):
#     """
#     Generates a SPARQL query for a given YAGO entity ID.

#     Args:
#             entity_id (str): The YAGO entity ID.

#     Returns:
#             str: A SPARQL query as a string.
#     """
    
#     if format_yago_prefix:
#         entity_id = entity_id.replace('http://yago-knowledge.org/resource/', 'yago:')
    
#     query_template = """
#     PREFIX schema: <http://schema.org/>
#     PREFIX yago: <http://yago-knowledge.org/resource/>
#     PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
#     PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

#     SELECT DISTINCT ?sub ?pred ?obj WHERE {{
#         {{
#             {entity_id} ?pred ?obj .
#         }}
#         UNION
#         {{
#             ?sub ?pred {entity_id} .
#         }}
#         FILTER (?pred NOT IN (rdfs:comment, rdfs:label, rdf:type, schema:description, schema:alternateName, schema:mainEntityOfPage, schema:image, schema:sameAs))
#     }}
#     LIMIT {max_limit}
#     """
#     return query_template.format(entity_id=entity_id, max_limit=max_limit)




def get_yago_query_entity_label(QID):
    """
    Generates a SPARQL query for a retrieving YAGO entity ID for a given Wikidata QID.

    Args:
            entity_id (str): Wiki entity ID.

    Returns:
            str: A SPARQL query as a string.
    """
    
    query = """
    PREFIX schema: <http://schema.org/>
    PREFIX yago: <http://yago-knowledge.org/resource/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX wd: <http://www.wikidata.org/entity/>


    SELECT ?yagoEntity
    WHERE {{
        ?yagoEntity owl:sameAs wd:{QID} .
    }}
    """.format(QID=QID)
    
    return query




def convert_QID_yagoID(QID):
    query = get_yago_query_entity_label(QID)
    # response = query_kg(yago_endpoint_url, query)
    response = query_kg_endpoint(yago_endpoint_url, query)

    if len(response["results"]["bindings"]) == 1:
        yagoID = response["results"]["bindings"][0]['yagoEntity']['value']#.replace('http://yago-knowledge.org/resource/', 'yago:')
    else:
        yagoID = 'NA'
        # print("Error converting QID to YagoID")
    return yagoID

def sparql_to_triples_with_main_entity(sparql_results, main_entity):
    triples = []

    for result in sparql_results:
        # Extract subject, predicate, and object
        subj = result.get('sub', {}).get('value')
        pred = result.get('pred', {}).get('value')
        obj = result.get('obj', {}).get('value')

        # Add outgoing links (main_entity as obj)
        if subj and pred:
            triples.append((subj, pred, main_entity))
        # Add incoming links (main_entity as sub)
        elif obj and pred:
            triples.append((main_entity, pred, obj))

    return triples


def get_yago_direct_neighbors(entity_id):
    # yagoID = convert_QID_yagoID(entity_id)
    query = get_yago_query_direct_neighbors(entity_id)
    # print(query)
    response = query_kg_endpoint(yago_endpoint_url, query)
    
    return response, entity_id

def process_node(node):
    """
    Process a single candidate node by getting its neighbors and returning the result.
    """
    response, yagoID = get_yago_direct_neighbors(node)
    if response is not None:
        res = response["results"]["bindings"]
        triples_list  = sparql_to_triples_with_main_entity(res, yagoID)
        # print("done")
        return triples_list
    else:
        return {"error": "not found"}

def parallel_process_nodes(candidate_nodes: List[str], max_workers_limit = 5):
    """
    Parallelize the processing of candidate nodes using multithreading.
    """
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers_limit) as executor:
        # Submit all tasks
        futures = {
            executor.submit(process_node, node): index 
            for index, node in enumerate(candidate_nodes)
        }
        # Collect results
        for future in futures:
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as e:
                results[index] = {"error": str(e)}
    return results



def parallel_convert_QID_yagoID(list_QID: List[str], max_workers_limit = 5):
    """
    Parallelize the processing of candidate nodes using multithreading.
    """
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers_limit) as executor:
        # Submit all tasks
        futures = {
            executor.submit(convert_QID_yagoID, node): index 
            for index, node in enumerate(list_QID)
        }
        # Collect results
        for future in futures:
            index = futures[future]
            try:
                results[index] = future.result()
            except Exception as e:
                results[index] = {"error": str(e)}
    return results


