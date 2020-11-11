# Wikipedia Search Engine
## About
A Search Engine that is designed based on Block sort based indexing. It uses TF-IDF statistics to calculate the relevance of a page and ranks them according to this score for query results.

## Usage
* ### Indexer
  The `indexer.py` script takes in wikipedia dump file path as an argument.</br>
  Format : `python index.py <wikipedia-xml-dump-path>` </br>
  
 * ### Query
   Run the script `query.py`, it will ask for your query, enter your query, and top ten most relevant results with their title and url will be printed for the query.
   A prompt will then ask you whether you would like to query again, respond accordingly.</br>
   Make sure that `query.py` is in the same folder as `data\` folder which was created by `indexer.py` during the index generation process.
   
   There is also a feature using which you can limit your queries to only look at titles, categories, or body of a page using tags `-t`, `-c`, and `-b` respectively.</br>
   To use tags simply put the corresponding tag before your query, e.g. `Enter your query: -t <your-query>`.

## Query Example:
   ![Query Example](https://github.com/Bufftowel/Wikipedia-Search-Engine/blob/master/src/wikipedia_query_example.png)

## Work flow of Scripts
* ### Indexer
  * The indexer script, when run creates a folder named `data/` in the same directory as itself, having subfolders `indexes/`, `posting_lists/` and `temp/` (Which will be deleted later).
  * It also creates two files in `data/` named `titles.txt` (contains titles of all pages) and `titles_location.pkl` (Dump of a data structure containing locations of titles in `title.txt`).
  The indexer uses block sort based indexing and therefore create a lot of small indexes and posting files for each tag while parsing the wikipedia corpus. These files are stored in `temp\` folder.</br>
  * The indexer parses the corpus and extracts information about the title, catagories and body(text) of every page, it then cleans the text, and stems it using PorterStemmer from nltk pyhton library.
  * The text is then tokenized and stopwords removed, the words are then indexed in a dictionary and its corresponding posting list is also created (Different for each tag).
  * When the indexer has completed parsing the wikipedia corpus then it moves on to combining them and creating a single file for index and posting lists for each tag.</br>
  * When all files are merged, these are placed in `indexes` and `posting lists` with their respective tag names. Rather than the count of words, there TF-IDF scores are stored in posting lists for every word in every document this time (again different files for each tag).
  * At last the script deletes the `temp` folder and all files in it as they are no longer needed.
  
* ### Query
  * When a user enters his/her query, the script first checks whether it contains a tag or not (e.g. `-t`), if it does then it strips out the tag and processes according to the tag.
  * Depending upon the tags, the script looks for query words in indexes of all tags (if no tag was specified in the query) or of a specific tag (if tag was specified) and for all candidate pages it adds up TF-IDF scores multipled by approopriate weights according to the tags.
  * It then ranks those documents according to their scores and prints top ten most relevant resutls with their titles and urls.