# Knowledge Graph

This submodule contains the code to work with the Yago Knowledge Graph (KG) for the DynamicKGQA framework.

We host Yago 4.5 on Blazegraph using Docker. The KG is queried using SPARQL queries to retrieve information about entities and their relationships.
The hosting was done on a AWS EC2 Ubuntu instance. We have tested the setup on the following releases:
- Ubuntu 24.04.1 LTS
- Ubuntu 20.04.6 LTS

For the following method of setup, the we recommend using an instance with at least 64 GB of RAM and 400 GB of storage.

## Yago Blazegraph Setup

This subsection provides instructions to host Yago on Blazegraph using Docker, on Ubuntu. While these instructions have only been tested on Ubuntu, they should work on other operating systems with minor modifications.

### Step 1: Install Docker Engine

We installed Docker using the instructions given in [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository), using the `apt` repository.

### Step 2: Run Blazegraph Docker Container

We can directly run the Blazegraph Docker container, and have it pull the latest image from the Docker Hub. 
However, in order to host Yago on Blazegraph, which has some scalability issues, we need to modify the default configuration of Blazegraph.

1. RWStore.properties

The RWStore.properties file that we used is available in [RWStore.properties](./yago/RWStore.properties). This file is used for configuring some of the primary settings of Blazegraph, such as the storage engine, the journal size, and the buffer size.

The file that we provide tries to optimize the read performance of Blazegraph. It disables QUADS mode, full text-search on literals, and platform statistics as they are not required for our use case. 

Feel free to modify this file according to your requirements. 