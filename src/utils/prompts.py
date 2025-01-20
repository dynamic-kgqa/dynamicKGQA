def generate_question_evaluation_prompt_v3(question):
    prompt = f"""As an expert evaluator, your role is to assess the quality and validity of trivia or natural questions. These questions aim to test the responder's knowledge, which may require implicit or external information. Your goal is to analyze the question based on the following criteria:

- **Logical Structure**: Verify if the grammar and syntax are correct. (True if grammatically and syntactically correct; False if there are issues with grammar or syntax.)
- **Redundancy**: Confirm that the question does not contain its own answer explicitly or through overly obvious phrasing. (True if it contains its answer; False if it does not.)
- **Multiple Answers**: Determine if the question allows for multiple valid answers. This is acceptable in some cases, but flag it if it reduces the question's effectiveness or specificity. (True if multiple answers are plausible; False if only one valid answer is expected.)
    
#### Output JSON Keys:
- question: The input question.
- logical_structure_flag: (True/False)
- logical_structure_reasoning: Reason for the logical structure flag.
- redundancy_flag: (True/False)
- redundancy_reasoning: Reason for the redundancy flag.
- multiple_answers_flag: (True/False)
- multiple_answers_reasoning: Reason for the multiple answers flag.

#### Task:
Analyze the following question and provide a JSON object containing flags and reasons for potential issues:

**Question**: {question}

#### Output:
Return a JSON object that evaluates the question based on the criteria above.
"""
    return prompt


def generate_question_evaluation_prompt_v2(question):
    prompt = f"""As an expert evaluator, your role is to assess the quality and validity of trivia or natural questions. These questions aim to test the responder's knowledge, which may require implicit or external information. Your goal is to analyze the question based on the following criteria:

- **Logical Structure**: Verify if the grammar and syntax are correct. (True if grammatically and syntactically correct; False if there are issues with grammar or syntax.)
- **Redundancy**: Confirm that the question does not contain its own answer explicitly or through overly obvious phrasing. (True if it contains its answer; False if it does not.)
- **Multiple Answers**: Determine if the question allows for multiple valid answers. This is acceptable in some cases, but flag it if it reduces the question's effectiveness or specificity. (True if multiple answers are plausible; False if only one valid answer is expected.)
    
#### Output JSON Keys:
- `question`: The input question.
- `logical_structure_flag`: (True/False)
- `logical_structure_reasoning`: Reason for the logical structure flag.
- `redundancy_flag`: (True/False)
- `redundancy_reasoning`: Reason for the redundancy flag.
- `multiple_answers_flag`: (True/False)
- `multiple_answers_reasoning`: Reason for the multiple answers flag.

#### Task:
Analyze the following question and provide a JSON object containing flags and reasons for potential issues:

**Question**: "{question}"

#### Output:
Return a JSON object that evaluates the question based on the criteria above.
"""
    return prompt

def generate_question_evaluation_prompt(question):
    prompt = f"""As an expert evaluator, your role is to assess the quality and validity of trivia or natural questions. These questions aim to test the responder's knowledge, which may require implicit or external information. Your goal is to analyze the question based on the following criteria:

- **Logical Structure**: Verify if the grammar and syntax are correct. (True if grammatically and syntactically correct; False if there are issues with grammar or syntax.)
- **Redundancy**: Confirm that the question does not contain its own answer explicitly or through overly obvious phrasing. (True if it contains its answer; False if it does not.)
- **Multiple Answers**: Determine if the question allows for multiple valid answers. This is acceptable in some cases, but flag it if it reduces the question's effectiveness or specificity. (True if multiple answers are plausible; False if only one valid answer is expected.)
    
#### Output JSON Keys:
- `question`: The input question.
- `flags`: 
    - `logical_structure`: (True/False)
    - `redundancy`: (True/False)
    - `multiple_answers`: (True/False)
    
- `reasoning`: 
    - `logical_structure`: Reason for the logical structure flag.
    - `redundancy`: Reason for the redundancy flag.
    - `multiple_answers`: Reason for the multiple answers flag.

#### Task:
Analyze the following question and provide a JSON object containing flags and reasons for potential issues:

**Question**: "{question}"

#### Output:
Return a JSON object that evaluates the question based on the criteria above.
"""
    return prompt

def gen_qa_prompt(triples_str):
    prompt = f"""You are an AI assistant tasked with generating question-answer pairs from knowledge graph triples. Your goal is to create natural, human-like questions and their corresponding answers based on the provided graph data.

Task Overview:
Generate **multi-hop, complex Q&A pairs** where the questions appear simple and natural but require reasoning across multiple connected relationships within the graph to infer the answer.

Guidelines for Generating Q&A Pairs:
1. **Question Design**:
- Questions should utilize multiple connected relationships in the graph, requiring multi-hop reasoning.
- Avoid single-hop or trivial questions directly derived from a single triple.
- The answer should be an entity or node in the graph.

2. **Multi-Hop Reasoning**:
- Use paths connecting entities indirectly through multiple relationships to infer answers.
- Questions should reflect meaningful and interesting connections within the graph.
- Aim for question with at least 4 hops or higher whenever possible.

3. **Answer Validation**:
- Ensure each answer is fully supported by one or more triples from the graph.
- Include the exact path (a sequence of triples) that justifies the answer.

4. **Comprehensive Coverage**:
- Generate as many high-quality Q&A pairs as possible, exploring all meaningful paths and connections within the graph.

5. **Fallback Condition**:
- If no valid Q&A pairs can be generated from the graph, explicitly indicate this in the response.

Graph Data:
Below is the graph data for your task:
{triples_str}

Repond ONLY with JSON with the following structure:

- **valid_qa_pairs**: Boolean indicating if valid QA pairs were generated.
- **number_of_qa_pairs**: Integer specifying the total number of QA pairs.
- **qa_pairs**: A list of QA pairs, where each pair includes:
- **question**: String representing the question.
- **answer**: String representing the answer.
- **supporting_path**: A list of triples, where each triple includes:
    - **subject**: String representing the subject.
    - **predicate**: String representing the predicate.
    - **object**: String representing the object.
""".format(triples_str)
    return prompt