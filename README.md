# swagger-graph
Generates a graph visualisation from Paths in swagger-based RESTful APIs definitions.


## What is it for?
During API maintenance or evolution, Architects and API developers might lost track of the existing resources and path parameters.
Keeping the definied URL's standards is a challenging task if one has either dozens of APIs and/or hundread of methods and paths.
A graph visualization of how all URLs are structured, with a user friendly view of all resources and path parameters, helps Architects to make better decisions.


## How it works?
1. Import from a repository to a database all APIs definitions. We call it "Ingestion";
    * Note 1: Currently only SVN (repository) and MongoDB (database) is supported;
    * Note 2: It' assumed you have them installed.
2. Traverse all Paths from an API in the database and generate a graph such as the one below.
    * Note: Graph generation is done using GraphViz, which is assumed it is installed.


