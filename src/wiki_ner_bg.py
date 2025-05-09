"""
This module extracts named entities from the Wiki40B dataset using spaCy and the Entity Linker pipeline.
"""
from ner.wiki_ner import extract_entities_to_json
from datasets import load_dataset
from tqdm import tqdm
import json
import logging

split = "validation"
dataset = load_dataset("google/wiki40b", "en", split=split)

save_interval = 10000
result_dict = {}
error_indices = [] 

# Configure logging
log_file = f"logs/wiki_ner_logging_{split}.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

save_loc = f'outputs/wiki_ner/{split}/'

print("Save location: ", save_loc)
for i in tqdm(range(len(dataset))): #maxlimit len(dataset)
    try:
        entry = dataset[i]  
        entry_dict = dict(entry) 
        
        # Extract entities from the text
        text = entry_dict["text"]
        wikidata_id = entry_dict["wikidata_id"]
        _, entities = extract_entities_to_json(text)
        # entry_dict["entities"] = entities
        
        result_dict[wikidata_id] = entities
        
        # Save intermediate file every n iterations
        if (i + 1) % save_interval == 0:
            with open(save_loc + 'intermediates/'+f"intermediate_results_intermediate_{i + 1}.json", "w", encoding="utf-8") as f:
                json.dump(result_dict, f, indent=4, ensure_ascii=False)
            # print(f"Saved intermediate results to intermediate_results_{i + 1}.json")
            logging.info(f"Saved intermediate results to intermediate_results_{i + 1}.json")
            result_dict = {}
            # print("cleared result_dict")
            logging.info("cleared result_dict")
            
    except Exception as e:
        # Log errors and store the index
        error_indices.append(i)
        print(f"Error at index {i}: {e}")
        logging.error(f"Error at index {i}: {e}")
        
        # Save error indices
        with open(save_loc + 'intermediates/' + f"error_indices_intermediate_{i + 1}.json", "w", encoding="utf-8") as f:
            json.dump(error_indices, f, indent=4, ensure_ascii=False)
        # print(f"Saved error indices to error_indices_{i + 1}.json")
        logging.info(f"Saved error indices to error_indices_{i + 1}.json")
    

# Save final results
with open(save_loc+"final_results.json", "w", encoding="utf-8") as f:
    json.dump(result_dict, f, indent=4, ensure_ascii=False)
print("Saved final results to final_results.json")
logging.info("Saved final results to final_results.json")

# Save final error indices
with open(save_loc + "final_error_indices.json", "w", encoding="utf-8") as f:
    json.dump(error_indices, f, indent=4, ensure_ascii=False)
print("Saved final error indices to final_error_indices.json")
logging.info("Saved final error indices to final_error_indices.json")

logging.info("Process completed successfully")
