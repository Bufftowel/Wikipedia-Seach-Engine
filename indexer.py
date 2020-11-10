import re
import os
import sys
import nltk
import math
import time
import heapq 
import pickle
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import xml.etree.ElementTree as ET

# Setup
file_path = sys.argv[1]
stem = PorterStemmer().stem
t1 = time.time()
log = math.log
heappush = heapq.heappush
heappop = heapq.heappop
StopWords = set(stopwords.words("english"))
pattern_alpha = re.compile("[^A-Za-z0-9]")
pattern_catagory = re.compile("\[\[Category:(.*?)\]\]")
tags = ["titles", "catagories", "body"]
params = 3                                                    # Number of parameters for caculating scores.
numOfFiles = 0                                                # Number of files that will be temporariy generated.
doc_cnt = 0                                                   # To keep track of total number of pages.



def createDirectories():
    os.makedirs("data", exist_ok = True)
    os.makedirs("data/indexes/", exist_ok = True)
    os.makedirs("data/posting_lists/", exist_ok = True)
    for i in tags:
        os.makedirs("data/temp/indexes/" + i, exist_ok = True)       # automatically makes all intermediate directories as well
        os.makedirs("data/temp/posting_lists/" + i, exist_ok = True)



def strip_tag_name(elem): 
    '''gets proper tag name from element, as in xml tags may have namespaces attached'''
    tag = elem.tag
    pos = tag.rfind("}")
    if pos > -1:
        tag = tag[pos + 1:]
    return tag



def process_txt(text):
    
    '''Funtion to process text, basically formating, tokenising,
   removing stopwords and stemming the text.'''
    
    text = str(text)
    text = pattern_alpha.sub(" ", text)               # removing all special characters and brackets
    text = text.lower()                               # Converting all characters to lowercase (casefolding)
    words = nltk.word_tokenize(text)                  # Tokenizing words
    return [stem(word) for word in words if word not in StopWords]



def build_index_and_dump(pages):
    '''
        index style = [
            word : [[dicId, count]...]
        ] * 3
        Seperate indexes are built for title, catagories and body.
    '''
    global numOfFiles
    if len(pages) == 0:
        return
    
    index = [{}, {}, {}]
    for page in pages:
        for i in range(params):
            for word in page[i]:
                if word in index[i]:
                    if index[i][word][-1][0] == page[3]:
                        index[i][word][-1][1] += 1
                    else:
                        index[i][word].append([page[3], 1])
                else:
                    index[i][word] = [[page[3], 1]]
                    
    for i in range(params):
        index_file = open("data/temp/indexes/{}/index_".format(tags[i]) + str(numOfFiles), "w")
        posting_list = open("data/temp/posting_lists/{}/list_".format(tags[i]) + str(numOfFiles), "w")
        word_index = []
        for word in index[i]:
            arr = index[i][word]
            s = " ".join([str(elem[0]) + ":" + str(elem[1]) for elem in arr])    # Format -> docId:cnt
            word_index.append((word, posting_list.tell()))
            posting_list.write(s)
            posting_list.write("\n")
        posting_list.close()
        word_index.sort(key = lambda arg:arg[0])         # Sorting words before writing them to file, for efficient merging. 
        index_file.write("\n".join([elem[0] + ":" + str(elem[1]) for elem in word_index]))
        index_file.close()
        
    numOfFiles += 1
    pages.clear()



def mergeFiles():

    for i in range(params):    
        index_pointer = [0] * numOfFiles          # Pointer to every index file
        posting_pointer = [0] * numOfFiles        # Pointer to every posting list
        atEOF = [False] * numOfFiles              # To keep track of file ending
        words = [0] * numOfFiles                  # Tracks the current topmost word of a index file
        pq = []                                   # Priority Queue
        final_index = {}
        final_posting = open("data/posting_lists/{}.txt".format(tags[i]), "w")
        
        for file_num in range(numOfFiles):
            index_pointer[file_num] = open("data/temp/indexes/{}/index_".format(tags[i]) + str(file_num))
            posting_pointer[file_num] = open("data/temp/posting_lists/{}/list_".format(tags[i]) + str(file_num))
            atEOF[file_num] = False
            words[file_num] = index_pointer[file_num].readline().split(":")
            if not words[file_num]:
                atEOF[file_num] = True
            heappush(pq, words[file_num][0])
        
        while(not all(atEOF)):
            smallest = heappop(pq)
            posting_list = []
            for file_num in range(numOfFiles):
                if smallest == words[file_num][0]:
                    posting_pointer[file_num].seek(int(words[file_num][1]))
                    arr = posting_pointer[file_num].readline().strip().split()
                    posting_list.extend([elem.split(":") for elem in arr])
                    nxt = index_pointer[file_num].readline()
                    if not nxt:
                        atEOF[file_num] = True
                    else:
                        words[file_num] = nxt.split(":")
                        heappush(pq, words[file_num][0])
                else:
                    pass
            final_index[smallest] = final_posting.tell()
            m = len(posting_list)
            
            for j in range(m):
                TF_IDF_score = int(posting_list[j][1])
                TF_IDF_score = TF_IDF_score * log(doc_cnt / m)   # calculating TF-IDF Scores
                posting_list[j][1] = round(TF_IDF_score, 3)      # Rounding TF-IDF scores to 3 decimal places to 
                                                                 # save some disk space.
            final_posting.write(" ".join([elem[0] + ":" + str(elem[1]) for elem in posting_list]))
            final_posting.write("\n")
            while len(pq) > 0 and pq[0] == smallest: 
                heappop(pq)                                   # Removing all duplicates of smallest
                
        for file_num in range(numOfFiles):
            index_pointer[file_num].close()
            posting_pointer[file_num].close()
        final_posting.close()
        with open("data/indexes/{}.pkl".format(tags[i]), "wb") as f:
            pickle.dump(final_index, f)



def parseCorpus():
    global doc_cnt
    
    inPage = False
    curPage = [0] * 4        # Keeps track of paramerter for current page.
    pages = []               # list of pages.
    titles_loc = []          # titles_loc[i] Stores location of title of page having pageId i
    titles_file = open("data/titles.txt", "w", encoding = "utf-8")

    for event, elem in ET.iterparse(file_path, events = ("start", "end")):
        tag = strip_tag_name(elem)
        
        if event == "end":
            if tag == "page":

                inPage = False
                pages.append(curPage)
                curPage = [0] * 4
                doc_cnt += 1
                if len(pages) >= 40000:
                    build_index_and_dump(pages)

            elif tag == "title" and inPage:

                curPage[0] = process_txt(elem.text)
                titles_loc.append(titles_file.tell())
                titles_file.write(str(elem.text) + "\n")

            elif tag == "redirect" and inPage:
                curPage[0] += process_txt(elem.attrib["title"])

            elif tag == "text" and inPage:
                if elem.text is None:                               # elem.text can be empty.
                    text = ""
                else:
                    text = str(elem.text)
                catag = pattern_catagory.findall(text)
                curPage[1] = process_txt(" ".join(catag))
                curPage[2] = process_txt(text)
                    
            elem.clear()                                            # Clearing memeory occupied by this node.
        else:
            if tag == "page":
                inPage = True
                curPage[3] = doc_cnt

    build_index_and_dump(pages)                                     # To process leftover pages
    titles_file.close()

    with open("data/titles_location.pkl", "wb") as f:
        pickle.dump(titles_loc, f)



def removeTempFiles():
    for i in range(params):
        for file_num in range(numOfFiles):
            os.remove("data/temp/indexes/{}/index_".format(tags[i]) + str(file_num))
            os.remove("data/temp/posting_lists/{}/list_".format(tags[i]) + str(file_num))
        os.rmdir("data/temp/indexes/{}".format(tags[i]))
        os.rmdir("data/temp/posting_lists/{}".format(tags[i]))
    os.rmdir("data/temp/indexes")
    os.rmdir("data/temp/posting_lists")
    os.rmdir("data/temp")



def main():
    createDirectories()
    parseCorpus()
    mergeFiles()
    removeTempFiles()
    t2 = time.time()        # Timing Code
    total = t2 - t1
    print("Index Generation Completed!")
    print("Time Taken :", str(math.floor(total / 3600)) + " hours " + str(math.floor(total / 60)) + " minutes " + str(math.floor(total % 60)) + " secs")
    print("In seconds : ", math.floor(total))
    print("Records Parsed : ", doc_cnt)


main()



