import json
import string
import re
import pandas as pd
import re
import json
import csv
import tokenize
import nltk
from nltk.tokenize import regexp
word_tokenizer = regexp.WhitespaceTokenizer()
docID = ""
index_tracker = {}
input_dict = {}
import yaml

# initialise
def find_column_name(input_dict,column_name):
    if type(input_dict) == dict:
        for key,value in input_dict.items():
            if type(value)==dict:
                if "find" in value.keys():
                    column_name.append(key)
            if(key == "output"):
                for i in value.keys():
                    column_name.append(i)
            # print(key,column_name)
            find_column_name(value,column_name)


def init(csv_file_name,config_file_name):
    global csv_file
    csv_file = csv_file_name
    fo = open(config_file_name, 'r')
    global input_dict
    # input_dict = json.load(fo)
    input_dict = yaml.safe_load(fo)
    # print(input_dict)
    column_name= []
    find_column_name(input_dict,column_name)
    # print("columnname"+ str(column_name))
    row = ["doc_id"]
    for item in column_name:
        # for key,value in item.items():
        if item not in row:
            row.append(item)
    with open(csv_file, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(row)
    for i in row:
        index_tracker[i] = 0
    return input_dict
    # csvfile.close()

def isNaturalLanguage(str):
    str = str.split(" ")
    # print("".join(str))
    str = "".join(str)
    valid = re.match('^[\w-]+$', str) is not None
    # print(valid)
    return valid

# parser
def clear(outputQ):
    for k,v in index_tracker.items():
        index_tracker[k] = 0
        outputQ.drop(outputQ.index, inplace=True)

def flush(outputQ):
    # print(outputQ)
    outputQ.to_csv("test", mode='a', header=False,index=False)
    df = outputQ.dropna(subset=[outputQ.columns[-1]])
    df.to_csv(csv_file, mode='a', header=False,index=False)
    clear(outputQ)

def isNaturalLanguage(str):
    str = str.split(" ")
    str = "".join((str))
    valid = re.match('^[\w-]+$', str) is not None
    # print(valid)
    return valid

def parseSearch(searchlevel,cmd,tokens,outputQ,pointer, level):
    level+=1
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
                tokenlist = cmd["find"]["token"]
                # case 1 token is a token
                if type(tokenlist) == str:
                    if isNaturalLanguage(tokenlist) is False:
                        res = re.findall(tokenlist, " ".join(tokens[temp1:temp2]))
                        if res != None:
                            for i in res:
                                index = index_tracker[searchlevel]
                                put_value_into_outputQ(outputQ, index, searchlevel, i)
                                index += 1
                                index_tracker[searchlevel] = index
                                print("token: " + str(i))
                                parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2,level)
                        else:
                            flush(outputQ)
                    else:
                        if (" " not in tokenlist):
                            # if tokenlist.lower() not in tokens[temp1:temp2]:
                            #     flush(outputQ)
                            for i in tokens[temp1:temp2]:
                                counter += 1
                                if i == tokenlist.lower():
                                    resultList.append((i, counter))
                                    print("token: " + i)
                                    index = index_tracker[searchlevel]
                                    put_value_into_outputQ(outputQ, index, searchlevel, i)
                                    index += 1
                                    index_tracker[searchlevel] = index
                                    parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2,level)
                        else:
                            length = len(tokenlist.split(" "))
                            # if tokenlist.lower() not in tokens[temp1:temp2]:
                            #     flush(outputQ)
                            for i in tokens[temp1:temp2]:
                                counter += 1
                                if i == tokenlist.split(" ")[0].lower():
                                    flag = 0
                                    for j in range(1, length - 1):
                                        if tokens[temp1 + counter + j - 1] == tokenlist.split(" ")[j].lower():
                                            flag = 1
                                            continue
                                        else:
                                            flag = 0
                                            break
                                    if flag == 1:
                                        resultList.append((tokenlist, counter))
                                        print("token: " + tokenlist)
                                        index = index_tracker[searchlevel]
                                        put_value_into_outputQ(outputQ, index, searchlevel, i)
                                        index += 1
                                        index_tracker[searchlevel] = index
                                        parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2,level)


                # case 2 token is a list of token
                else:
                    for token in tokenlist:
                        counter = 0
                        if isNaturalLanguage(token) is False:
                            res = re.findall(token, " ".join(tokens[temp1:temp2]))
                            if res != None:
                                for i in res:
                                    index = index_tracker[searchlevel]
                                    put_value_into_outputQ(outputQ, index, searchlevel, i)
                                    index += 1
                                    index_tracker[searchlevel] = index
                                    print("token: "+str(i))
                            else:
                                flush(outputQ)

                        else:
                            if (" " not in token):
                                # if token.lower() not in tokens[temp1:temp2]:
                                    # print(1)

                                for i in tokens[temp1:temp2]:
                                    counter += 1
                                    if i == token.lower():
                                        resultList.append((i,counter))
                                        print("token: "+ i)
                                        index = index_tracker[searchlevel]
                                        put_value_into_outputQ(outputQ, index, searchlevel, i)
                                        index += 1
                                        index_tracker[searchlevel] = index
                                        parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2,level)

                            else:
                                length = len(token.split(" "))
                                # if token.lower() not in tokens[temp1:temp2]:
                                #     flush(outputQ)
                                for i in tokens[temp1:temp2]:
                                    counter += 1
                                    if i == token.split(" ")[0].lower():
                                        flag = 0
                                        for j in range (1, length-1):
                                            if tokens[temp1+counter+j-1] == token.split(" ")[j].lower():
                                                flag = 1
                                                continue
                                            else:
                                                flag = 0
                                                break
                                        if flag == 1:
                                            resultList.append((token,counter))
                                            print("token: "+ token)
                                            index = index_tracker[searchlevel]
                                            put_value_into_outputQ(outputQ, index, searchlevel, i)
                                            index += 1
                                            index_tracker[searchlevel] = index
                                            parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2,level)



    # if resultList == []:
    #     outputQ.put((searchlevel,'not found','not found',0))
    return resultList

def parseRefine(cmd,resultList,tokens,outputQ,pointer,temp1,temp2,level):

    if "output" in cmd.keys():
        tempdict = cmd["output"]
        for k, v in tempdict.items():
            index = index_tracker[k]
            # if it is a regex sentence (need to fix this if statement)
            if isNaturalLanguage(v) is False:
                res = re.findall(v, " ".join(tokens[temp1:temp2]))
                if res != None:
                    for i in res:
                        put_value_into_outputQ(outputQ, index, k, i)
                        index += 1
                        index_tracker[k] = index
            else:
                put_value_into_outputQ(outputQ, index, k, v)
                index += 1
                index_tracker[k] = index

    if ("refine" in cmd.keys()):
        # for i in resultList:
            # searchlevel = cmd["refine"].keys()
        for key in cmd["refine"].keys():
            print("search: " + key)
            parseSearch(key, cmd["refine"][key], tokens, outputQ, pointer + resultList[-1][1],level)

    if "action" in cmd.keys():
        if "flush" in cmd["action"]:
            flush(outputQ)
        if "clear" in cmd["action"]:
            clear(outputQ)


def put_value_into_outputQ(outputQ, index,k, v):
    if "," in v:
        v = "\""+v + "\""
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
        searchDict[query] = parseSearch(searchLevel,cmd,tokens,outputQ,0,0)
        # if ("otherwise" == query):
        #     # print(searchDict)
        #     if(searchDict[searchLevel] == []):
        #         searchLevel = searchLevel + "(otherwise)"
        #         parseOtherwise(searchLevel,cmd,tokens,outputQ)

        #     if len(searchDict.keys()):
        #        parseOutput(searchLevel,searchDict,cmd,outputQ)
    return value


def parseOtherwise(searchLevel,input_dict,tokens,outputQ):
    parseSearch(searchLevel,input_dict,tokens,outputQ)

def readtokens(clinical_note_file_name):
    fo = open(clinical_note_file_name , "r")
    # lines = str(fo.read().lower().translate(str.maketrans('','',string.punctuation))).split()
    tokens =[word.lower() for word in  nltk.word_tokenize(fo.read())]
    # print(tokens)
    return tokens

# outputQ
def parserFile(doc_id,clinical_note_file_name):
    global docID
    docID = doc_id
    outputQ = pd.DataFrame(columns=index_tracker.keys())
    tokens = readtokens(clinical_note_file_name)
    parseQuery(input_dict,tokens,outputQ)

def processDocument(docID,content):
    # fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())
    tokens = str(content.lower().translate(str.maketrans('','',string.punctuation))).split()
    # input_dict = json.load(fo)
    # print(input_dict)
    parseQuery(input_dict,tokens,outputQ)

def parser(doc_id,tokens):
    docID = doc_id
    # tokens = str(tokens.lower().translate(str.maketrans('','',string.punctuation))).split()
    # fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())
    # input_dict = json.load(fo)
    parseQuery(input_dict,tokens,outputQ)
    # print(outputQ)
