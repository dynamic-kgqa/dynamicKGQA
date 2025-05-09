# Knowledge Graph Hosting

This directory contains the README and other documentation files related to the hosting of the knowledge graph (KG) used in the DynamicKGQA project. 

The KG is hosted using Docker Blazegraph, which is a high-performance graph database that can be used to host large-scale knowledge graphs. 

## Yago Blazegraph Setup

This subsection provides instructions to host Yago on Blazegraph using Docker, on Ubuntu. While these instructions have only been tested on Ubuntu, they should work on other operating systems with minor modifications.

Note: There are also other ways that we have tried to host Yago, such as AWS Neptune, Virtuoso, and some other Docker solutions. We talk about these alternatives on a high level in the [KG_hosting_alternatives.md](./KG_hosting_alternatives.md) file.

### TL;DR

1. Install Docker Engine on Ubuntu.
2. Run the Blazegraph Docker container with custom configurations.
Run the following command from this directory:
```bash
sudo docker run --name blazegraph -d   -e BLAZEGRAPH_UID=$BLAZEGRAPH_UID   -e BLAZEGRAPH_GID=$BLAZEGRAPH_GID   -e JAVA_OPTS="-Xmx64g -XX:+UseParallelGC"   -p 9999:8080   -v $PWD/yago/RWStore_scaled.properties:/RWStore.properties   -v $PWD/yago-4.5.0.2:/data   lyrasis/blazegraph:2.1.4
```
3. Load the Yago KG into Blazegraph.
Run the following command from this directory:
```bash
curl -vvv -X POST   --data-binary @yago/dataloader.txt   --header 'Content-Type:text/plain'   http://localhost:9999/bigdata/dataloader
```
4. Access the Blazegraph Sparql endpoint at `http://localhost:9999/bigdata/sparql` and query the KG using SPARQL queries.


### Context

The hosting was done on a AWS EC2 Ubuntu instance. We have tested the setup on the following releases:
- Ubuntu 24.04.1 LTS
- Ubuntu 20.04.6 LTS

The Blazegraph documentation in its current state, is not very detailed, and the community support is limited. We have thus tried to provide a detailed guide to help you get started with hosting Yago on Blazegraph. 
For the following method of setup, the we recommend using an instance with at least 64 GB of RAM and 400 GB of storage.

The total time taken to set up the Blazegraph instance and load the Yago KG was around 36 hours. This time can be reduced to around 8 hours if we do not load the `yago-beyond-wikipedia.ttl` file.

Customizing the `RWStore.properties` file, garbage collection settings, and heap size can help in optimizing the performance of Blazegraph. 


### Custom Configuration Files

In order to host Yago on Blazegraph, which has some scalability issues, we need to modify the default configuration of Blazegraph.

To facilitate this, we have provided a custom `RWStore.properties` file and a `dataloader.txt` file in the `yago` directory. These files are used to configure Blazegraph and load the Yago KG into it.

1. RWStore.properties

The RWStore.properties file that we used is available in [RWStore.properties](./yago/RWStore.properties). This file is used for configuring some of the primary settings of Blazegraph, such as the storage engine, the journal size, and the buffer size.

The file that we provide tries to optimize the read performance of Blazegraph. It disables QUADS mode, full text-search on literals, and platform statistics as they are not required for our use case. 

Feel free to modify this file according to your requirements. For further reference, you can refer to the [official Blazegraph documentation](https://blazegraph.com/database/apidocs/help-doc.html) and get some sample configurations from the [Blazegraph GitHub repository](https://github.com/blazegraph/database). 

2. dataloader.txt

The dataloader.txt is the file used to load the Yago KG into Blazegraph. The file is available in [dataloader.txt](./yago/dataloader.txt).

The file has been pulled from the [Docker Blazegraph GitHub repository](https://github.com/lyrasis/docker-blazegraph/blob/master/data/dataloader.txt.example). We have not made any modifications to this file.


### Step 1: Download Yago KG

Download the Yago 4.5 KG from the downloads repository of the [official Yago website](https://yago-knowledge.org/data/yago4.5/). The KG is available in several formats, such as TTL, NT, and RDF. We recommend using the TTL format, as it is the most widely used format for knowledge graphs.

As of February 2025, download the yago-4.5.0.2.zip file. Unzip the file and place the yago-4.5.0.2 directory in the [yago](./yago) directory.


### Step 2: Install Docker Engine

We installed Docker using the instructions given in [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository), using the `apt` repository.

### Step 3: Run Blazegraph Docker Container

We can directly run the Blazegraph Docker container, and have it pull the latest image from the Docker Hub. 
However, 

However, to load a Knowledge Graph as large as the full Yago 4.5, we had to tweak the garbage collections and heap size settings of the JVM used by the Blazegraph container. We used the following command to run the Blazegraph container. 
This command assumes that you are running it from [this directory](./) and that you have the yago-4.5 KG in this directory:

```bash
sudo docker run --name blazegraph -d   -e BLAZEGRAPH_UID=$BLAZEGRAPH_UID   -e BLAZEGRAPH_GID=$BLAZEGRAPH_GID   -e JAVA_OPTS="-Xmx64g -XX:+UseParallelGC"   -p 9999:8080   -v $PWD/yago/RWStore_scaled.properties:/RWStore.properties   -v $PWD/yago-4.5.0.2:/data   lyrasis/blazegraph:2.1.4
```

In this command:
- `BLAZEGRAPH_UID` and `BLAZEGRAPH_GID` are the user and group IDs of the user running the container. You can find these by running `id -u` and `id -g` in the terminal. Although these are optional, they are recommended to avoid permission issues.
- `JAVA_OPTS` sets the heap size to 64 GB and uses the Parallel Garbage Collector. You can modify this according to your requirements.
- `BLAZEGRAPH_PORT` is the port on which Blazegraph will be accessible. We have set it to 9999 in this case. You can modify this according to your requirements, however, remember to change the port in the data loading command as well.
- `RWStore.properties` is the custom configuration file that we provide. It is mounted to the container at `/RWStore.properties`. The path `$PWD/yago/RWStore_scaled.properties` should be modified according to the location of the file on your system.
- `yago-4.5.0.2` is the directory containing the Yago KG. It is mounted to the container at `/data`. The path `$PWD/yago-4.5.0.2` should be modified according to the location of the KG on your system.
- `lyrasis/blazegraph:2.1.4` is the Blazegraph Docker image that we used.

### Step 4: Load Yago KG into Blazegraph

Trigger the data loading process by running the following command:

```bash
curl -vvv -X POST   --data-binary @yago/dataloader.txt   --header 'Content-Type:text/plain'   http://localhost:9999/bigdata/dataloader
```

This command sends a POST request to the Blazegraph server, which loads the Yago KG into the Blazegraph instance. The process may take some time, depending on the size of the KG.
In this command:
- `yago/dataloader.txt` is the file that contains the data loading instructions. The path should be modified according to the location of the file on your system.
- `localhost:9999` is the address and port of the Blazegraph server. The port should be modified according to the port on which Blazegraph is running.

### Step 5: Access Blazegraph

Once the data loading process is complete, you can access the Blazegraph Sparql endpoint at `http://localhost:9999/bigdata/sparql`. You can use this endpoint to query the Yago KG using SPARQL queries.

Here's a sample CURL command to query the KG:

```bash
curl -X POST -H "Content-Type: application/sparql-query" -H "Accept: application/sparql-results+json" --data 'SELECT * WHERE {?s ?p ?o} LIMIT 10' http://localhost:9999/bigdata/sparql
```

You can also get the status of the Blazegraph server by visiting `http://localhost:9999/bigdata/status`.

```bash
curl -X GET http://localhost:9999/bigdata/status
```

### Extra Notes

1. Running the Docker container in another directory

Reference: [Docker Forum](https://forums.docker.com/t/configure-and-store-the-images-and-containers-to-the-different-folders/135593)

Owing to the large size of the Yago KG, you may want to run the Docker container in a different directory. In this case, you can configure the docker data-root folder to use a different folder than /var/lib/docker like this:
- Add the data-root entry to /etc/docker/daemon.json (needs to be created if it doesn’t already exist):
```json
{
  "data-root": "/path/to/your/docker-data"
}
```
- Restart the Docker service:
```bash
sudo systemctl restart docker
```