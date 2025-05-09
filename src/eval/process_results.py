"""
This module contains functions to process the results of the model predictions.
"""
import re
import string
from sklearn.metrics import precision_score

def normalize(s: str) -> str:
    """Lower text and remove punctuation, articles and extra whitespace."""
    s = s.lower()
    exclude = set(string.punctuation)
    s = "".join(char for char in s if char not in exclude)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    # remove <pad> token:
    s = re.sub(r"\b(<pad>)\b", " ", s)
    s = " ".join(s.split())
    return s


# def match_presence(s1: str, s2: str) -> bool:
#     s1 = normalize(s1)
#     s2 = normalize(s2)
#     return s2 in s1
def match_presence(prediction, answer):
    if type(answer) == str:
        prediction = normalize(prediction)
        answer = normalize(answer)
        return answer in prediction
    if type(answer) == list:
        for a in answer:
            if match_presence(prediction, a):
                return True
        return False

def eval_acc(prediction, answer):
    matched = 0.
    for a in answer:
        if match_presence(prediction, a):
            matched += 1
    return matched / len(answer)

def eval_hit(prediction, answer):
    for a in answer:
        if match_presence(prediction, a):
            return 1
    return 0

def eval_result(predictions):
    """Evaluate a list of predictions and return evaluation metrics."""
    
    hit_list = []
    results = []
    
    for data in predictions:
        prediction = data['prediction']
        answer = data['ground_truth']
            
        
        prediction_str = prediction

        hit = match_presence(prediction_str, answer)
        hit_list.append(hit)

        results.append({
            'id': data['id'],
            'prediction': prediction,
            'ground_truth': answer,
            'hit': hit,
        })

    aggregated_results = {
        "hit": sum(hit_list) * 100 / len(hit_list),
        "detailed_results": results
    }

    return aggregated_results
