import spacy
import json

# Initialize the language model
nlp = spacy.load("en_core_web_md")

# Add the entity linker pipeline
nlp.add_pipe("entityLinker", last=True)

def remove_duplicates(json_data):
    """
    Remove duplicate entries from a list of dictionaries based on the 'id' field.

    :param json_data: List of dictionaries (JSON data)
    :return: List of dictionaries with duplicates removed
    """
    # Use a dictionary to store unique entries by ID
    unique_entries = {}
    for entry in json_data:
        unique_entries[entry["id"]] = entry  # Overwrites duplicates automatically

    # Return the unique entries as a list
    return list(unique_entries.values())



def extract_entities_to_json(text):
    """
    Extract entities and related metadata from text and return as a JSON object.

    :param text: Input text
    :return: JSON object with entities and metadata
    """
    # Process the text with the NLP pipeline
    doc = nlp(text)

    # Extract linked entities
    all_linked_entities = doc._.linkedEntities

    # Prepare the data structure for JSON
    entities = []
    for entity in all_linked_entities:
        entities.append({
            "id": entity.get_id(),
            "label": entity.get_label(),
            "description": entity.get_description(),
            "span": str(entity.get_span()),
            "url": entity.get_url()
        })
        
    # Remove duplicates based on the 'id' field
    entities = remove_duplicates(entities)

    # Return the JSON representation
    return json.dumps(entities, indent=4, ensure_ascii=False), entities

