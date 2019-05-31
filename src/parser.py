import json
import string
import pandas as pd
import re
import json
import csv
import tokenize
import nltk
# nltk.download('punkt')
from nltk.classify import NaiveBayesClassifier
from nltk.tokenize import regexp
word_tokenizer = regexp.WhitespaceTokenizer()
docID = ""
index_tracker = {}
input_dict = {}
# initialise
def find_column_name(input_dict,column_name):
    if type(input_dict) == dict:
        for key,value in input_dict.items():
            if(key == "output"):
                column_name.append(value)
            # print(key,column_name)
            find_column_name(value,column_name)


def init(csv_file_name,config_file_name):
    global csv_file
    csv_file = csv_file_name
    fo = open(config_file_name, 'r')
    global input_dict
    input_dict = json.load(fo)
    column_name= []
    find_column_name(input_dict,column_name)
    row = ["doc_id"]
    for item in column_name:
        for key,value in item.items():
            if key not in row:
                row.append(key)
    with open(csv_file, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(row)

    for i in row:
        index_tracker[i] = 0
    return input_dict
    # csvfile.close()




# parser
def clear(outputQ):
    for k,v in index_tracker.items():
        index_tracker[k] = 0
        outputQ.drop(outputQ.index, inplace=True)

def flush(outputQ):
    outputQ.to_csv(csv_file, mode='a', header=False)


def parseSearch(searchlevel,cmd,tokens,outputQ,pointer):
    resultList = []
    counter = 0
    temp_point = 0
    # assume search defo has attribute "find" and "output"
    tokens_preceeding = len(tokens)

    tokens_following = len(tokens)
    if type(cmd) == dict:
        if ("window" in cmd.keys()):
            if "tokens_preceeding" in cmd["window"].keys():
                tokens_preceeding = int(cmd["window"]["tokens_preceeding"])
            if "tokens_following" in cmd["window"].keys():
                tokens_following = int(cmd["window"]["tokens_following"])

        if "find" in cmd.keys():
            if pointer - tokens_preceeding < 0:
                temp1 = pointer
            else:
                temp1 = pointer - tokens_preceeding

            if pointer + tokens_following > len(tokens) -1:
                temp2 = len(tokens)
            else:
                temp2 = pointer + tokens_following

            if "token" in cmd["find"].keys():
                for i in tokens[temp1:temp2]:
                    counter += 1
                    if i in [i.lower() for i in cmd["find"]["token"]]:
                        resultList.append((i,counter))
                        print("token: "+ i)

        if"output" in cmd.keys():
            tempdict = cmd["output"]
            for k, v in tempdict.items():
                index = index_tracker[k]
                put_value_into_outputQ(outputQ, index, k, v)
                index += 1
                index_tracker[k] = index
        if ("refine" in cmd.keys()):
                for i in resultList:
                    # searchlevel = cmd["refine"].keys()
                    for key in cmd["refine"].keys():
                        print("search: "+key)
                        parseSearch(key,cmd["refine"][key],tokens,outputQ,i[1])
        if "action" in cmd.keys():
            if "flush" in cmd["action"]:
                flush(outputQ)
            if "clear" in cmd["action"]:
                clear(outputQ)


    # if resultList == []:
    #     outputQ.put((searchlevel,'not found','not found',0))
    return resultList

def put_value_into_outputQ(outputQ, index,k, v):
    outputQ.loc[index, k] = v
    outputQ.loc[index,"doc_id"] = docID
    # print(outputQ)


def parseRegex(cmd,tokens):
    # print(cmd,tokens)
    tokens = "".join(tokens)
    matches = re.findall(cmd, tokens)
    return matches

def parseOutput(searchLevel,searchDict,cmd,outputQ):
    keywordList = searchDict[searchLevel]
    for key,value in cmd.items():
        for k in keywordList:
            if(k[0] == key):
                outputQ.put((key,value))
                # print(value)



def parseQuery(input_dict,tokens,outputQ):
    value = None
    searchDict= {}
    searchLevel = ""
    # print(input_dict)
    # lv1
    for query, cmd in input_dict.items():
        searchLevel = query
        print("search: " + searchLevel)
        searchDict[query] = parseSearch(searchLevel,cmd,tokens,outputQ,0)

        # if ("otherwise" == query):
        #     # print(searchDict)
        #     if(searchDict[searchLevel] == []):
        #         searchLevel = searchLevel + "(otherwise)"
        #         parseOtherwise(searchLevel,cmd,tokens,outputQ)

        #     if len(searchDict.keys()):
        #         parseOutput(searchLevel,searchDict,cmd,outputQ)

    return value


def parseOtherwise(searchLevel,input_dict,tokens,outputQ):
    parseSearch(searchLevel,input_dict,tokens,outputQ)




def readtokens(clinical_note_file_name):
    fo = open(clinical_note_file_name , "r")
    # lines = str(fo.read().lower().translate(str.maketrans('','',string.punctuation))).split()
    tokens =[word.lower() for word in  nltk.word_tokenize(fo.read())]


    print(tokens)
    return tokens



# outputQ
def parserFile(doc_id,config_file_name,clinical_note_file_name):
    global docID
    docID = doc_id
    fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())
    tokens = readtokens(clinical_note_file_name)
    input_dict = json.load(fo)
    value = parseQuery(input_dict,tokens,outputQ)

def processDocument(docID,content):

    # fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())

    tokens = str(content.lower().translate(str.maketrans('','',string.punctuation))).split()
    # input_dict = json.load(fo)
    # print(input_dict)
    parseQuery(input_dict,tokens,outputQ)


def parser(doc_id,config_file_name,tokens):
    docID = doc_id

    tokens = str(tokens.lower().translate(str.maketrans('','',string.punctuation))).split()
    fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())
    input_dict = json.load(fo)
    parseQuery(input_dict,tokens,outputQ)


    print(outputQ)
