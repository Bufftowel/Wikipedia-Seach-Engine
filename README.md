# Wikipedia Search Engine
## About
A Search Engine that is designed based on Block sort based indexing. It uses TF-IDF statistics to calculate the relevance of a page and ranks them according to this score for query results.

## Usage
* ### Indexer
  The `indexer.py` script takes in wikipedia dump file path as an argument.</br>
  Format : `python index.py <wikipedia-xml-dump-path>` </br>
  
 * ### Query
   Run the script `query.py`, it will ask for your query, enter your query, and at the max top ten most relevant results will be shown for the query.
   A prompt will then ask you whether you would like to query again, respond accordingly.</br>
   Make sure that `query.py` is in the same folder as `data\` folder which was created by `indexer.py` during index generation process.
   
   There is also a feature using which you can limit your queries to only look at titles, categories, or body of a page using tags `-t`, `-c`, and `-b` respectively.</br>
   To use tags simply put the corresponding tag before your query, e.g. `Enter your query: -t <your-query>`.

   ## Query Example:
   ![Query Example](https://github.com/Bufftowel/Wikipedia-Search-Engine/blob/master/src/wikipedia_query_example.png)