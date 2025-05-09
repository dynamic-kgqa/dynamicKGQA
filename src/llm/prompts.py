"""
This module contains functions to generate prompts for various tasks in the DynamicKGQA project.
"""

def generate_question_evaluation_prompt(question):
    prompt = f"""As an expert evaluator, your role is to assess the quality and validity of trivia or natural questions. These questions aim to test the responder's knowledge, which may require implicit or external information. Your goal is to analyze the question based on the following criteria:

- **Logical Structure**: Verify if the grammar and syntax are correct. (True if grammatically and syntactically correct; False if there are issues with grammar or syntax.)
- **Redundancy**: Confirm that the question does not contain its own answer explicitly or through overly obvious phrasing. (True if it contains its answer; False if it does not.)
    
#### Output JSON Keys:
- question: The input question.
- logical_structure_flag: (True/False)
- logical_structure_reasoning: Reason for the logical structure flag.
- redundancy_flag: (True/False)
- redundancy_reasoning: Reason for the redundancy flag.

#### Task:
Analyze the following question and provide a JSON object containing flags and reasons for potential issues:

**Question**: {question}

#### Output:
Return a JSON object that evaluates the question based on the criteria above.
"""
    return prompt

def generate_answer_evaluation_prompt(question, answer, supporting_facts):
    prompt = f"""As an expert evaluator, your role is to assess the validity and adequacy of an answer to a given question based on a provided set of supporting facts (triples). The goal is to determine if the answer is logically supported by the facts and if it sufficiently addresses the question. Your evaluation should consider the following criteria:

- **Answer Support**: Verify if the answer is explicitly or implicitly supported by the provided supporting facts. (True if the supporting facts justify the answer; False if they do not.)
- **Answer Adequacy**: Determine if the answer fully and clearly addresses the question. An adequate answer should provide a direct and comprehensive response to the question. (True if the answer is adequate; False if the answer is incomplete or does not directly address the question.)

#### Output JSON Keys:
- answer_support_flag: (True/False)
- answer_support_reasoning: Reason for the answer support flag.
- answer_adequacy_flag: (True/False)
- answer_adequacy_reasoning: Reason for the answer adequacy flag.

#### Inputs:
- **Question**: {question}
- **Answer**: {answer}
- **Supporting Facts**: {supporting_facts}

#### Task:
Analyze the question, answer, and supporting facts. Return a JSON object containing flags and reasoning based on the criteria above.

#### Output:
Return only the JSON object based on the criteria above.
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


def get_cot_kgqa_prompt(question_string, system_message):
    cot_prompt = """Q: What state is home to the university that is represented in sports by George Washington Colonials men's basketball?
A: First, the education institution has a sports team named George Washington Colonials men's basketball in is George Washington University , Second, George Washington University is in Washington D.C. The answer is {Washington, D.C.}.

Q: Who lists Pramatha Chaudhuri as an influence and wrote Jana Gana Mana?
A: First, Bharoto Bhagyo Bidhata wrote Jana Gana Mana. Second, Bharoto Bhagyo Bidhata lists Pramatha Chaudhuri as an influence. The answer is {Bharoto Bhagyo Bidhata}.

Q: Who was the artist nominated for an award for You Drive Me Crazy?
A: First, the artist nominated for an award for You Drive Me Crazy is Britney Spears. The answer is {Jason Allen Alexander}.

Q: What person born in Siegen influenced the work of Vincent Van Gogh?
A: First, Peter Paul Rubens, Claude Monet and etc. influenced the work of Vincent Van Gogh. Second, Peter Paul Rubens born in Siegen. The answer is {Peter Paul Rubens}.

Q: What is the country close to Russia where Mikheil Saakashvii holds a government position?
A: First, China, Norway, Finland, Estonia and Georgia is close to Russia. Second, Mikheil Saakashvii holds a government position at Georgia. The answer is {Georgia}.

Q: What drug did the actor who portrayed the character Urethane Wheels Guy overdosed on?
A: First, Mitchell Lee Hedberg portrayed character Urethane Wheels Guy. Second, Mitchell Lee Hedberg overdose Heroin. The answer is {Heroin}."""

    prompt = system_message + "\n\n" + cot_prompt + "\n\nQ: " + question_string + "\nA: "
    return prompt

def get_io_kgqa_prompt(question_string, system_message):
    io_prompt = """Q: What state is home to the university that is represented in sports by George Washington Colonials men's basketball?
A: {Washington, D.C.}.

Q: Who lists Pramatha Chaudhuri as an influence and wrote Jana Gana Mana?
A: {Bharoto Bhagyo Bidhata}.

Q: Who was the artist nominated for an award for You Drive Me Crazy?
A: {Jason Allen Alexander}.

Q: What person born in Siegen influenced the work of Vincent Van Gogh?
A: {Peter Paul Rubens}.

Q: What is the country close to Russia where Mikheil Saakashvii holds a government position?
A: {Georgia}.

Q: What drug did the actor who portrayed the character Urethane Wheels Guy overdosed on?
A: {Heroin}."""

    
    prompt = system_message + "\n\n" + io_prompt + "\n\nQ: " + question_string + "\nA: "
    
    return prompt