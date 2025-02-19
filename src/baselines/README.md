# Baselines

This submodule contains the information and subprojects of the baselines used in the DynamicKGQA project. 

The following are the baselines used in the project:

## Language Model (LM) Baselines

The Large Language Models (LLMs) used to run the baselines were set up using AWS Bedrock. 
The instructions to set up AWS Bedrock are given in the [README](../../README.md) of the project.

The following are the LLMs used in the project:



## Knowledge Graph Question Answering (KGQA) Baselines

### Think on Graph (ToG)

Think on Graph is a Knowledge-Graph Question Answering approach which treats the LLM as an agent to interactively explore related entities and relations on KGs and perform reasoning based on the retrieved knowledge.

We forked the original repository and made several modifications to adapt it to our project. 
- The original repository can be found [here](https://github.com/IDEA-FinAI/ToG)
- Our forked repository can be found [here](https://github.com/himanshunaidu/ToG)

While in the current state, adding this forked repository as a submodule does not bring any additional value, one can still do so to keep the overall codebase centralized.

Run the following command to add the submodule to the project:
```bash
git submodule add https://github.com/himanshunaidu/ToG.git
```
