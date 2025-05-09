"""
This module generates subgraphs for a given set of QIDs. It uses the Steiner tree algorithm to build a minimal subgraph
that connects the interesting entities for each QID. The resulting subgraphs are saved as triples in JSON format.
"""
import logging
import os
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from kg.query import query_kg, query_kg_endpoint, get_triples_from_response
from kg.kg_functions import (load_json, extract_ids_with_prefix, convert_QID_yagoID, 
                                combine_lists_from_dict, get_yago_direct_neighbors, 
                                sparql_to_triples_with_main_entity, parallel_process_nodes)

from utils.subgraph_functions import (create_graph_from_triples, build_minimal_subgraph_Steiner, 
                                      largest_connected_subgraph, edges_to_triples, 
                                      get_interesting_entities, filter_triples_by_predicates)

# Setup logging
log_location = './logs/'
output_location = './outputs/'
output_intermediate_location = './outputs/intermediate/'
os.makedirs(log_location, exist_ok=True)
os.makedirs(output_location, exist_ok=True)
os.makedirs(output_intermediate_location, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_location, 'processing.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.info("Starting multithreaded KG processing.")

input_location = './inputs/'


exclude_props = ['knowsLanguage', 'location', 'image', 'about', 'comment', 'gtin', 'url', 'label', 
                 'postalCode', 'isbn', 'sameAs', 'mainEntityOfPage', 'leiCode', 'type', 'dateCreated', 
                 'unemploymentRate', 'length', 'description', 'iswcCode', 'iataCode', 'logo', 'alternateName', 
                 'geo', 'subclassOf', 'icaoCode', 'humanDevelopmentIndex', 'sameAs', 'dateCreated', 
                 'startDate', 'endDate', 'follows', 'superEvent']

# Function to process a single QID
def process_qid(QID):
    try:
        # logging.info(f"Processing QID: {QID}")
        
        interesting_entities = get_interesting_entities(QID, data[QID]['entities'])
        results = parallel_process_nodes(interesting_entities)
        comb_list = combine_lists_from_dict(results)
        comb_list = filter_triples_by_predicates(comb_list, exclude_props)
        graph = create_graph_from_triples(comb_list)

        subgraph_Steiner = build_minimal_subgraph_Steiner(graph, interesting_entities)
        subgraph_Steiner_largest_connected = largest_connected_subgraph(subgraph_Steiner)

        subgraph_Steiner_triples = edges_to_triples(subgraph_Steiner)
        subgraph_Steiner_largest_connected_triples = edges_to_triples(subgraph_Steiner_largest_connected)

        result = {
            'subgraph_Steiner': subgraph_Steiner_triples,
            'subgraph_Steiner_length': len(subgraph_Steiner_triples),
            'subgraph_Steiner_largest_connected': subgraph_Steiner_largest_connected_triples,
            'subgraph_Steiner_largest_connected_length': len(subgraph_Steiner_largest_connected_triples)
        }

        # logging.info(f"Finished processing QID: {QID}")
        return QID, result

    except Exception as e:
        logging.error(f"Error processing QID {QID}: {e}")
        return QID, None

# Process all QIDs using multithreading
def process_all_qids(keys, save_interval=1000):
    final_results = {}
    batch_counter = 0

    with ThreadPoolExecutor() as executor: #max_workers=10
        futures = {executor.submit(process_qid, QID): QID for QID in keys}
        
        for idx, future in enumerate(tqdm(as_completed(futures), total=len(keys), desc="Processing QIDs")):
            QID = futures[future]
            try:
                result = future.result()
                if result[1] is not None:
                    final_results[result[0]] = result[1]
            except Exception as e:
                logging.error(f"Exception in future for QID {QID}: {e}")

            # Save intermediate results every `save_interval`
            if (idx + 1) % save_interval == 0:
                intermediate_path = os.path.join(output_intermediate_location, f'intermediate_results_batch_{batch_counter}.json')
                with open(intermediate_path, 'w') as f:
                    json.dump(final_results, f)
                logging.info(f"Saved intermediate results to {intermediate_path}")
                batch_counter += 1
                final_results.clear()  # Clear memory to prevent RAM overflow

    # Save final results
    final_path = os.path.join(output_location, 'final_results.json')
    with open(final_path, 'w') as f:
        json.dump(final_results, f)
    logging.info(f"Final results saved to {final_path}")
    
# Load data
data = load_json('./inputs/final_results_train10K_wiki40B.json')
keys = list(data.keys())
# Execute processing
process_all_qids(keys, save_interval=500)  # Limit to first 10 for testing
