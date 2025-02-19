# Baselines

This submodule contains the code and the subprojects of the baselines used in the DynamicKGQA project. 

The following are the baselines used in the project:

## Think on Graph

Think on Graph is a Knowledge-Graph Question Answering approach which treats the LLM as an agent to interactively explore related entities and relations on KGs and perform reasoning based on the retrieved knowledge.

We forked the original repository and made several modifications to adapt it to our project. 
- The original repository can be found [here](https://github.com/IDEA-FinAI/ToG)
- Our forked repository can be found [here](https://github.com/himanshunaidu/ToG)

While in the current state, adding this forked repository as a submodule does not bring any additional value, one can still do so to keep the overall codebase centralized.

Run the following command to add the submodule to the project:
```bash
git submodule add https://github.com/himanshunaidu/ToG.git
```

