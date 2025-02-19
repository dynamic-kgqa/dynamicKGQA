# Baselines

This submodule contains the information and subprojects of the baselines used in the DynamicKGQA project. 

The following are the baselines used in the project:

## Language Model (LM) Baselines

The Language Models used to run the baselines were set up using AWS Bedrock. 
The instructions to set up AWS Bedrock will be provided in the [README](../../README.md) of the project.

All the models were tested with both IO and CoT prompts.

The following are the LMs used in the project:

### 1. Llama 3.2 3B

[Llama 3.2 3B](https://doi.org/10.48550/arXiv.2407.21783) is a language model trained on a diverse range of text sources, including books, articles, and websites. 

### 2. Command-R

[Command-R](https://docs.cohere.com/v2/docs/command-r-plus) is a language model optimized for conversational interaction and long-context tasks. It aims at being extremely performant, enabling companies to move beyond proof of concept and into production.

### 3. Mistral Small (24.02)

[Mistral Small (24.02)](https://mistral.ai/en/news/mistral-small-3) is a pre-trained and instructed model catered to the ‘80%’ of generative AI tasks—those that require robust language and instruction following performance, with very low latency.

### 4. Claude 3.5 Sonnet v2

[Claude 3.5 Sonnet v2](https://www-cdn.anthropic.com/de8ba9b01c9ab7cbabf5c33b80b7bbc618857627/Model_Card_Claude_3.pdf) is a language model developed by Anthropic that can perform complex tasks like reasoning, coding, and creative writing.

### 5. GPT-4o-mini

[GPT-4o-mini](https://openai.com/index/gpt-4o-system-card/) is a cost-efficient language model that can be used for a variety of tasks, including question answering, summarization, and translation.

### 6. GPT-4o

[GPT-4o](https://openai.com/index/gpt-4o-system-card/) is currently the flagship model of OpenAI that can reason across audio, vision, and text in real time.


## Knowledge Graph Question Answering (KGQA) Baselines

### 1. Think on Graph (ToG)

Think on Graph is a Knowledge-Graph Question Answering approach which treats the LLM as an agent to interactively explore related entities and relations on KGs and perform reasoning based on the retrieved knowledge.

ToG can work with any kind of LLM and KG, and it is designed to be a general framework for KGQA. We experimented with ToG on a variety of LLMs, and also a variety of KGs, including YAGO. While the original repository was designed to only work with Wikidata and Freebase, we have made modifications in our forked repository, to make it work with YAGO as well.

We forked the original repository and made several modifications to adapt it to our project. 
- The original repository can be found [here](https://github.com/IDEA-FinAI/ToG)
- Our forked repository can be found [here](https://github.com/himanshunaidu/ToG)

While in the current state, adding this forked repository as a submodule does not bring any additional value, one can still do so to keep the overall codebase centralized.

Run the following command to add the submodule to the project:
```bash
git submodule add https://github.com/himanshunaidu/ToG.git
```
