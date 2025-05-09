"""
This module contains utility functions for working with subgraphs of a Knowledge Graph.

MARK: Find a more appropriate place for this module.
"""
from kg.query import query_kg, query_kg_endpoint, get_triples_from_response
import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.approximation import steiner_tree


from kg.kg_functions import load_json, extract_ids_with_prefix, convert_QID_yagoID
from kg.kg_functions import combine_lists_from_dict, get_yago_direct_neighbors, sparql_to_triples_with_main_entity
from kg.kg_functions import parallel_process_nodes, extract_ids_with_prefix, parallel_convert_QID_yagoID

# TODO: Move this to a config file
yago_endpoint_url = "http://localhost:9999/bigdata/sparql"


def create_graph_from_triples(triples):
    """
    Creates a NetworkX graph from a list of triples.

    Args:
        triples (list of tuples): List of triples in the format (subj, pred, obj).

    Returns:
        nx.DiGraph: A directed graph representing the triples.
    """
    graph = nx.DiGraph()  # Create a directed graph

    for triple in triples:
        if len(triple) != 3:
            raise ValueError(f"Triple '{triple}' does not have 3 elements.")
        subj, pred, obj = triple
        # Add nodes and edges
        graph.add_edge(subj, obj, relation=pred)

    return graph

def get_interesting_entities(main_node_qid, entities):
    qids = extract_ids_with_prefix(entities)
    qids = qids + [main_node_qid]
    qids = list(set(qids))

    yago_ids = parallel_convert_QID_yagoID(qids)
    yago_ids_list = list(yago_ids.values())
    yago_ids_list = [x for x in yago_ids_list if x != 'NA']
    
    return yago_ids_list

def filter_triples_by_predicates(triples, exclude_predicates):
    # print(f'Length of Triples = {len(triples)}')
    processed_triples = []
    try:
        for i in range(len(triples)):
            triple = triples[i]
            # print(triple)
            predicate = str(triple[1]).lower()
            # print(predicate)
            exclude = False
            for substring in exclude_predicates:
                substring = substring.lower()
                if substring in predicate:
                    
                    exclude = True
                    break
            if exclude:
                # print(f'{predicate}, {substring} - excluded')
                continue
            else:
                processed_triples.append(triple)
    except Exception as e:
        print(e)
    # print(len(processed_triples))
    return processed_triples

def plot_graph_with_simplified_labels(graph, title="Graph Visualization", figsize=(8, 8)):
    """
    Plot a graph with node and edge labels simplified to text after the last '/'.

    Parameters:
    - graph: NetworkX graph
    - title: Title for the plot
    """
    # Determine layout dynamically based on graph size
    num_nodes = graph.number_of_nodes()
    num_edges = graph.number_of_edges()

    if num_nodes < 10:
        layout = nx.shell_layout(graph)  # Good for small graphs
    elif num_edges > num_nodes * 2:
        layout = nx.circular_layout(graph)  # For dense graphs
    elif nx.is_tree(graph):
        layout = nx.kamada_kawai_layout(graph)  # Tree-like structure
    else:
        layout = nx.spring_layout(graph, seed=42)  # General-purpose layout

    plt.figure(figsize=figsize)

    # Simplify node labels
    node_labels = {node: node.split('/')[-1] for node in graph.nodes()}

    # Simplify edge labels
    edge_labels = {
        (u, v): data['relation'].split('/')[-1]
        for u, v, data in graph.edges(data=True)
    }

    # Get node positions
    pos = layout

    # Draw the graph with simplified labels
    nx.draw_networkx(
        graph,
        pos=pos,
        labels=node_labels,
        node_color="orange",
        with_labels=True
    )

    # Draw edge labels
    nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels)

    # Adjust axis limits dynamically to ensure all nodes/edges are visible
    x_vals, y_vals = zip(*pos.values())
    x_margin = (max(x_vals) - min(x_vals)) * 0.1  # Add 10% margin
    y_margin = (max(y_vals) - min(y_vals)) * 0.1
    plt.xlim(min(x_vals) - x_margin, max(x_vals) + x_margin)
    plt.ylim(min(y_vals) - y_margin, max(y_vals) + y_margin)

    # Add title and adjust layout
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
def plot_full_graph(graph, interesting_entities):
    # Assign colors based on whether a node is in interesting_nodes
    node_colors = [
        "red" if node in interesting_entities else "skyblue"
        for node in graph.nodes()
    ]

    # Draw the graph with labels and highlighted nodes
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph)  # Layout for nodes
    nx.draw(graph, pos, node_size=300, node_color=node_colors, arrowsize=10, edge_color="gray")
    plt.title("Graph with Highlighted Nodes and Labels")
    plt.show()

def build_minimal_subgraph_Steiner(
    G: nx.DiGraph, 
    interesting_nodes
) -> nx.DiGraph:
    """
    
    :param G: Original directed graph (nx.DiGraph) with possible attributes (e.g. "predicate").
    :param interesting_nodes: Collection of terminal (interesting) nodes.
    :return: Directed subgraph containing:
             - all interesting nodes 
             - the minimal set of intermediate nodes 
             - edges (with original predicates) that are necessary for connectivity.
    """
    # Step 1: Filter out invalid interesting nodes
    valid_interesting = [n for n in interesting_nodes if n in G]
    # print(f'Number of valid interesting nodes: {len(valid_interesting)}')
    # print(f'Number of interesting nodes: {len(interesting_nodes)}')
    # print(f'Removing nodes as they are not in the graph: {[n for n in interesting_nodes if n not in G]}')
    if not valid_interesting:
        # No valid interesting nodes => Return empty subgraph
        return nx.DiGraph()

    # Step 2: Convert G to an undirected graph (for Steiner Tree)
    G_und = G.to_undirected(as_view=False)

    # Step 3: Compute the Steiner Tree subgraph (UNDIRECTED)
    steiner_subgraph_und = steiner_tree(G_und, valid_interesting)

    # Step 4: Build a directed subgraph from the Steiner Tree
    #    We'll add all nodes from the Steiner subgraph
    H = nx.DiGraph()
    H.add_nodes_from(steiner_subgraph_und.nodes())

    # For each undirected edge (u, v) in the Steiner subgraph:
    #  - check if G has (u->v), and if so, copy that edge + attributes
    #  - check if G has (v->u), and if so, copy that edge + attributes
    for (u, v) in steiner_subgraph_und.edges():
        # print(f'u = {u}, v = {v}')
        if G.has_edge(u, v):
            # print(G[u][v])
            # Copy **all** attributes from the original graph edge
            # (including "predicate" if it exists)
            H.add_edge(u, v, **G[u][v])

        if G.has_edge(v, u):
            # Copy **all** attributes from the original graph edge
            H.add_edge(v, u, **G[v][u])


    return H


def largest_connected_subgraph(G: nx.Graph) -> nx.Graph:
    """
    Returns the subgraph of G corresponding to its largest connected component
    (in the undirected sense).

    If G is directed, we still compute connected components on the undirected 
    version, then return the induced subgraph (including original directed edges).
    """
    # 1. Convert to undirected for connected-component analysis
    G_und = G.to_undirected(as_view=False)

    # 2. Find all connected components in the undirected version
    components = list(nx.connected_components(G_und))

    # 3. Identify the largest connected component by number of nodes
    largest_cc = max(components, key=len)  # set of node IDs

    # 4. Return the induced subgraph from the original graph
    #    (preserves direction/edges if G is directed)
    largest_subgraph = G.subgraph(largest_cc).copy()

    return largest_subgraph


def edges_to_triples(G, relation_key='relation'):
    """
    Convert edges with a specific attribute (relation_key)
    into a list of triples: (subject, predicate, object).

    :param G: A NetworkX Graph, DiGraph, etc.
    :param relation_key: The key under which the relation is stored in the edge attributes
    :return: A list of triples (source_node, relation_value, target_node)
    """
    triple_list = []

    # Try to fetch edges from the graph
    try:
        edges = G.edges(data=True)
    except Exception as e:
        raise TypeError(
            "Error: `G` does not appear to be a valid NetworkX graph object "
            "(missing or invalid `.edges` method)."
        ) from e

    # If relation_key isn't a string, just warn (or you could raise an error)
    if not isinstance(relation_key, str):
        print(f"Warning: `relation_key` should be a string, got: {type(relation_key).__name__}")

    # Iterate through edges and try to extract the relation_key attribute
    for source, target, data in edges:
        try:
            # Attempt to retrieve the predicate
            predicate = data[relation_key]
            triple_list.append((source, predicate, target))
        except KeyError:
            print(f"Warning: Edge {source} -> {target} has no '{relation_key}' attribute.")
            # If you want a default, uncomment the following:
            # triple_list.append((source, "connectedTo", target))

    return triple_list

def prune_triples(triples):
    """
    Given a list of triples, where each element is a list [subject, predicate, object]
    containing URIs, return a new list of triples with each URI pruned to the part 
    after its last '/'.
    """
    pruned_triples = []
    for triple in triples:
        pruned_triples.append([ part.split('/')[-1] for part in triple ])
    return pruned_triples

# def restore_full_triples(pruned_subset, full_triples):
#     """
#     Given:
#       pruned_subset: A list of 'pruned' triples
#       full_triples:  A list of full triples
#     Returns:
#       A list of the corresponding full triples for each pruned triple in pruned_subset.
#       If a pruned triple is not found in the dictionary, this example returns None for that triple.
#     """

#     # 1. Build a lookup dict from pruned -> full
#     pruned_to_full = {}
#     for s_full, p_full, o_full in full_triples:
#         s_pruned = s_full.rsplit('/', 1)[-1]
#         p_pruned = p_full.rsplit('/', 1)[-1]
#         o_pruned = o_full.rsplit('/', 1)[-1]
#         pruned_to_full[(s_pruned, p_pruned, o_pruned)] = (s_full, p_full, o_full)

#     # 2. Restore the full triples for each pruned triple
#     restored = []
#     for s_pruned, p_pruned, o_pruned in pruned_subset:
#         key = (s_pruned, p_pruned, o_pruned)
#         if key in pruned_to_full:
#             restored.append(pruned_to_full[key])
#         else:
#             # Handle case when the pruned triple is not found in the dictionary
#             restored.append(None)
#     return restored

def restore_full_triples(pruned_subset, full_triples):
    """
    Given a pruned subset of triples and a full list of triples, both of which 
    can be in one of two formats:
    
      1) List-based: e.g. [subject_uri, predicate_uri, object_uri]
      2) Dict-based: e.g. {'subject': ..., 'predicate': ..., 'object': ...}
    
    This function returns a tuple of:
      - A list of the restored full triples (in the same format as 'full_triples').
      - A boolean flag (True/False) indicating if all conversions were successful.
    
    If a pruned triple is not found in the lookup dictionary, that element in the 
    restored list is None.
    """

    # --------------------------------------------------------------------------
    # 1) Detect the format of 'full_triples'
    # --------------------------------------------------------------------------
    if not full_triples:
        raise ValueError("full_triples is empty. Cannot build a lookup dictionary.")
    
    full_is_dict_format = isinstance(full_triples[0], dict)
    
    # --------------------------------------------------------------------------
    # 2) Helper functions
    # --------------------------------------------------------------------------
    def prune_value(uri):
        """Return the substring after the last slash, or the entire string if no slash."""
        return uri.rsplit('/', 1)[-1]

    def get_spo(triple, is_dict):
        """
        Extract subject, predicate, object from the triple, 
        depending on list or dict format.
        """
        if is_dict:
            return triple["subject"], triple["predicate"], triple["object"]
        else:
            return triple[0], triple[1], triple[2]

    def make_triple(s, p, o, is_dict):
        """Reconstruct a triple in the given format (list or dict)."""
        if is_dict:
            return {"subject": s, "predicate": p, "object": o}
        else:
            return [s, p, o]

    # --------------------------------------------------------------------------
    # 3) Build a lookup dict: pruned (s, p, o) -> the full triple
    # --------------------------------------------------------------------------
    pruned_to_full = {}
    for triple in full_triples:
        s_full, p_full, o_full = get_spo(triple, full_is_dict_format)
        # Build pruned version
        s_pruned = prune_value(s_full)
        p_pruned = prune_value(p_full)
        o_pruned = prune_value(o_full)
        pruned_to_full[(s_pruned, p_pruned, o_pruned)] = triple

    # --------------------------------------------------------------------------
    # 4) Detect format of 'pruned_subset'
    #    (We'll restore them to the same format as 'full_triples'.)
    # --------------------------------------------------------------------------
    pruned_is_dict_format = False
    if pruned_subset:
        pruned_is_dict_format = isinstance(pruned_subset[0], dict)

    # --------------------------------------------------------------------------
    # 5) Restore the full triples from 'pruned_subset' 
    #    by looking up the pruned (s, p, o) in pruned_to_full
    # --------------------------------------------------------------------------
    restored_result = []
    for triple in pruned_subset:
        s_p, p_p, o_p = get_spo(triple, pruned_is_dict_format)
        found = pruned_to_full.get((s_p, p_p, o_p), None)
        restored_result.append(found)

    # --------------------------------------------------------------------------
    # 6) Determine if *all* pruned triples were successfully converted
    # --------------------------------------------------------------------------
    all_converted = all(x is not None for x in restored_result)

    # Return the restored list and the boolean flag
    return restored_result, all_converted


# def get_full_uri(pruned_node, triples):
#     """
#     Finds the full URI of a node given its pruned form and a list of triples.

#     Args:
#         pruned_node (str): The pruned node name (last part of the URI).
#         triples (list): A list of triples, where each triple is a list of the form [subject, predicate, object].

#     Returns:
#         str: The full URI of the node if found, otherwise None.
#     """
#     for triple in triples:
#         for element in triple:
#             if element.endswith('/' + pruned_node):
#                 return element
#     return None

def encode_to_underscored_unicode(s: str) -> str:
    """
    Encodes a string so that:
      1. Every space ' ' becomes an underscore '_'.
      2. Every non-alphanumeric, non-underscore character c becomes `_uXXXX_`
         where XXXX is the 4-digit uppercase hex code of that character.
      3. Alphanumeric characters (letters/digits) and underscores remain as is.
    """
    result = []
    for c in s:
        if c == ' ':
            # Convert spaces to underscores
            result.append('_')
        elif c.isalnum() or c == '_':
            # Keep letters, digits, and underscores as is
            result.append(c)
        else:
            # Convert everything else to _uXXXX_
            result.append(f"_u{ord(c):04X}_")
    return "".join(result)


def get_full_uri(pruned_node, triples):
    """
    Finds the full URI of a node given its pruned form and a list of triples.
    If a direct match is not found, it tries one more time after
    encoding the node name using `encode_to_underscored_unicode`.

    Args:
        pruned_node (str): The pruned node name (last part of the URI).
        triples (list): A list of triples, where each triple is a list of
            the form [subject, predicate, object].

    Returns:
        str: The full URI of the node if found, otherwise None.
    """
    # First pass: try matching the pruned_node exactly
    for triple in triples:
        for element in triple:
            if element.endswith('/' + pruned_node):
                return element

    # If not found, transform the node name and try again
    transformed_node = encode_to_underscored_unicode(pruned_node)
    if transformed_node != pruned_node:
        for triple in triples:
            for element in triple:
                if element.endswith('/' + transformed_node):
                    return element

    # If still not found, give up
    return None
