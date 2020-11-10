import re
import nltk
import time
import pickle
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


# Setup
stem = PorterStemmer().stem
StopWords = set(stopwords.words("english"))
tags = ["titles", "catagories", "body"]
flags = {"-t": 0, "-c": 1, "-b": 2}
rel_scores = [2, 1.3, 1]                       # Relative scores, to increase impact of title on final score of a doc as
pattern_alpha = re.compile("[^A-Za-z0-9]")     # compared to its body.
posting_pointer = [0] * 3
index = [0] * 3
titles_file = None
titles_loc = None
params = 3



def configure():
    global titles_file, index, titles_loc, posting_pointer
    
    for i in range(params):
        with open("data/indexes/{}.pkl".format(tags[i]), "rb") as f:
            index[i] = pickle.load(f)
        posting_pointer[i] = open("data/posting_lists/{}.txt".format(tags[i]), "r", encoding = "utf-8")
    with open("data/titles_location.pkl", "rb") as f:
            titles_loc = pickle.load(f)
    titles_file = open("data/titles.txt", "r", encoding = "utf-8")



def cleanUp():
    global titles_file, posting_pointer
    
    titles_file.close()
    for i in range(params):
        posting_pointer[i].close()



def process_txt(text):
    
    '''Funtion to process text, basically formating, tokenising,
   removing stopwords and stemming the text.'''
    
    text = str(text)
    text = pattern_alpha.sub(" ", text)               # removing all special characters and brackets
    text = text.lower()                               # Converting all characters to lowercase (casefolding)
    words = nltk.word_tokenize(text)                  # Tokenizing words
    return [stem(word) for word in words if word not in StopWords]



def query_i(docs, words, i):
    '''Sub Function to find relevant docs for a specific tag'''
    
    for word in words:
        if word in index[i]:  
            posting_pointer[i].seek(index[i][word])
            posting_list = [elem.split(":") for elem in posting_pointer[i].readline().strip().split()]
            for doc in posting_list:
                docId = int(doc[0])
                TF_IDF_score = float(doc[1]) * rel_scores[i]
                if docId in docs:
                    docs[docId] += TF_IDF_score
                else:
                    docs[docId] = TF_IDF_score



def query(queryString, mode = None):
    '''
        queryString : Accepts a string of words, searches index for most relevant docs based on these words.
        mode: Accepts one of three arguments (-t, -c, -b), if provided searches for most relevant docs but only 
              considering fields corresponding to the mode. (-t for titles, -c for catagory, -b for body/text)
              P.S. if you actually want to search for these tag (idk why) then put a backslash infornt of it, e.g. \-t.
    '''
    t1 = time.time()
    words = process_txt(queryString)
    docs = {}
    
    if mode is not None:
        query_i(docs, words, mode)
    else:
        for i in range(params):
             query_i(docs, words, i)
                
    docs = sorted(docs.items(), key = lambda elem:elem[1], reverse = True)
    pages = []
    
    for i in range(min(10, len(docs))):                         # Getting Top 10 most relevant pages
        titles_file.seek(titles_loc[docs[i][0]])
        title = titles_file.readline().strip()
        pages.append([title, "https://en.wikipedia.org/wiki/" + re.sub(" ", "_", title)])
    t2 = time.time()
    print("\nQuery Time :", round(t2 - t1, 4), "Seconds")
    
    return pages



def main():
    configure()
    exit = False
    
    while not exit:
        Q = input("Enter your query : ")
        flag = Q[:3].strip()
        mode = None
        
        if flag in flags:                  # Checking for tag in input
            mode = flags[flag]
            Q = Q[3:]
        
        pages = query(Q, mode)
        print("Top {} results :".format(min(10, len(pages))), end = "\n\n")
        for page in pages:
            print(page[0], ":", page[1])
        print("")                           # for en extra endline
        char = input("Query Again? [y/n] ")
        if not (char == "Y" or char == "y"):
            exit = True
            
    cleanUp()



main()





