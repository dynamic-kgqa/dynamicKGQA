# Knowledge Graph Hosting Alternatives

This file outlines the other methods that we used to host the KG before switching to Docker Blazegraph. We list the end results of each method, along with the pros and cons of each approach.

## Blazegraph (Java)

[Blazegraph](https://blazegraph.com/) is a high-performance graph database that can be used to host large-scale knowledge graphs. It is written in Java and is based on the Bigdata RDF database. It is known to host Wikidata and other large-scale knowledge graphs, although there have been [efforts to move to other solutions](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/WDQS_backend_update) due to scalability issues.

We initially tried to host Yago on Blazegraph using the [Java version of Blazegraph](https://github.com/blazegraph/database/releases). However, we faced several issues with this approach. Most of these revolved around the lack of detailed documentation, and scalability issues. We were initially unable to load the full Yago 4.5 KG into Blazegraph due to memory constraints and performance issues.

We believe that with the right configuration and optimization, Blazegraph can be a viable option for hosting large-scale knowledge graphs. The most important changes involve tweaking the heap size and garbage collection settings of the JVM used by Blazegraph. However, we did not pursue this approach further due to the success of Docker Blazegraph.

### Pros
- Initial setup is relatively straightforward
While some debugging was required, the initial setup did not pose too many challenges. The Blazegraph documentation at least provides a good starting point for hosting knowledge graphs.

### Cons
- Lack of detailed documentation
- Bulk Data Loading slows down rapidly
This does depend on the configuration of the JVM and Blazegraph, and perhaps the configurations that we eventually used for Docker Blazegraph could have been applied here as well. 

## AWS Neptune

[AWS Neptune](https://aws.amazon.com/neptune/) is a fully managed graph database service provided by Amazon Web Services. It supports both property graph and RDF graph models, and is compatible with popular graph query languages such as Gremlin and SPARQL.

Out of all the solutions that we tried, AWS Neptune was the easiest to set up. We were able to host the full Yago 4.5 KG on AWS Neptune within a day. The service is fully managed, which means that we did not have to worry about the underlying infrastructure. However, the extremely high costs associated with Neptune, difficulty of setting up public endpoints, and the lack of control over the underlying infrastructure, made us reconsider this approach.

### Pros
- Fully managed service
- Supports auto-scaling for bulk data loading and querying
- Supports bulk loading directly from Amazon S3

### Cons
- Internal implementation details are not exposed
- Does not directly support public endpoints
- High costs associated with the service

### Instructions for Public Access

To enable public access to your Neptune cluster, you need to follow these steps:
- Set up an EC2 instance in the same VPC as your Neptune cluster
- Set up a connection between the EC2 instance and the Neptune cluster and expose the Neptune cluster to a port on the EC2 instance
- Use a reverse proxy such as Nginx or a simple ssh tunnel to expose the EC2 instance to the public internet

Issues with this approach:
- Will be slow due to the additional hops
- SSH tunneling is unreliable and not recommended for production use
- Nginx is a better option, but requires additional configuration

## Docker Wikidata Query Service

The [Wikidata Query Service (WDQS)](https://query.wikidata.org/) is a service provided by the Wikimedia Foundation that allows users to query the Wikidata knowledge graph using SPARQL. The service is based on Blazegraph, and is used to power the Wikidata Query Service. The [Docker version](https://hub.docker.com/r/wikibase/wdqs) of the Wikidata Query Service is a multi-container setup that includes Blazegraph, QuickStatements, and other services.

We tried to host Yago on the Docker version of the Wikidata Query Service. This approach was relatively straightforward compared to the Java version of Blazegraph. However, bulk data loading was still an issue, and we faced similar scalability issues as with the Java version of Blazegraph.

### Pros
- Easier initial setup compared to Java Blazegraph
- Based on the Wikidata Query Service, which is a proven solution for hosting large-scale knowledge graphs
- Internal implementation details are exposed

### Cons
- Bulk data loading is still slow, and not documented


## TheQACompany QEndpoint

The [QEndpoint](https://hub.docker.com/r/qacompany/qendpoint-wikidata) is a Docker image provided by TheQACompany that hosts a pre-configured Wikidata Query Service. It is based on the Wikidata Query Service, and is designed to be a drop-in replacement for the official Wikidata Query Service.

We tried to host Yago on the QEndpoint Docker image. This approach was the easiest of all the methods we tried. The QEndpoint image comes pre-configured with the necessary settings for hosting a large-scale knowledge graph. This service is also very well-documented. 

However, the QEndpoint image is hard-coded to use the Wikidata KG, and we were unable to load the Yago KG into it. We believe that with some modifications to the QEndpoint image, it could be a viable solution for hosting Yago.

### Pros
- Easiest initial setup
- Well-documented
- Based on the Wikidata Query Service

### Cons
- Hard-coded to use the Wikidata KG
- Unable to load custom KGs