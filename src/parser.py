import json
import string
import pandas as pd
import re
import json
import csv
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
    with open(csv_file_name, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        filewriter.writerow(row)

    for i in row:
        index_tracker[i] = 0
    return input_dict
    # csvfile.close()




# parser
def clear(outputQ):
    # for i in range(0, outputQ.qsize()):
    #     continue
    for k,v in index_tracker.items():
        index_tracker[k] = 0
        outputQ.drop(outputQ.index, inplace=True)

def flush(outputQ):
    # with open('persons.csv', 'a') as f:
    #     df1 = pd.read_csv('persons.csv', index_col=0)
    # df = df1.append(outputQ,sort = False)
    outputQ.to_csv('persons.csv', mode='a', header=False)


# modify outputQ, create search dictionary
def parseSearch(searchLevel,cmd,paragraph,outputQ):
    resultList = []
    counter = 0
    # assume search defo has attribute "find" and "output"
    if type(cmd) == dict:
        if "find" in cmd.keys():
            if "token" in cmd["find"].keys():
                for i in paragraph:
                    counter += 1
                    if i in [i.lower() for i in cmd["find"]["token"]]:
                        resultList.append((i,counter))
        if"output" in cmd.keys():
            tempdict = cmd["output"]
            for k, v in tempdict.items():
                put_value_into_outputQ(outputQ, index_tracker[k], k, v)
                # index_tracker[k] = index_tracker[k]+1
                        # print(v)
        if ("refine" in cmd) and resultList!=[]:
            for k, v in  cmd["refine"].items():

                        # outputQ.put((searchLevel,k, v,resultList[0][1]) )
                parseRefine(searchLevel, cmd, paragraph, outputQ)
    # if resultList == []:
        # outputQ.put((searchLevel,'not found','not found',0))
    return resultList

def parseRefineSearch(searchlevel,cmd,paragraph,outputQ):
    resultList = []
    counter = 0
    temp_point = 0
    # assume search defo has attribute "find" and "output"
    chars_preceeding = len(paragraph)

    chars_following = len(paragraph)
    if type(cmd) == dict:
        if ("window" in cmd.keys()):
            if "chars_preceeding" in cmd["window"].keys():
                chars_preceeding = int(cmd["window"]["chars_preceeding"])
            if "chars_following" in cmd["window"].keys():
                chars_following = int(cmd["window"]["chars_following"])
        if "find" in cmd.keys():
            if "token" in cmd["find"].keys():
                for i in paragraph:
                    counter += 1
                    if i in [i.lower() for i in cmd["find"]["token"]]:
                        resultList.append((i,counter))
        if"output" in cmd.keys():
            tempdict = cmd["output"]
            for k, v in tempdict.items():
                index = index_tracker[k]
                put_value_into_outputQ(outputQ, index, k, v)
                index += 1
                index_tracker[k] = index
        if ("refine" in cmd.keys()):
            for keyword, pointer in resultList:
                tempdict = cmd["output"]
                if pointer - chars_preceeding < 0:
                    temp1 = pointer
                else:
                    temp1 = pointer - chars_preceeding

                if pointer + chars_following > len(paragraph) - 1:
                    temp2 = pointer
                else:
                    temp2 = pointer + chars_following
                point = temp1
                for k, v in tempdict.items():
                    # k = k.lower().translate(str.maketrans('','',string.punctuation))
                    for key in paragraph[temp1:temp2]:
                        pointer += 1
                        if (k == key) and (searchlevel, k, v, pointer) != temp_point:
                            parseRefine(searchlevel, cmd, paragraph, outputQ)
                            temp_point = (searchlevel, k, v, pointer)

        if "flush" in cmd.keys():
            flush(outputQ)
        if "clear" in cmd.keys():
            clear(outputQ)


    # if resultList == []:
    #     outputQ.put((searchlevel,'not found','not found',0))
    return resultList
def put_value_into_outputQ(outputQ, index,k, v):
    outputQ.loc[index, k] = v
    outputQ.loc[index,"doc_id"] = docID

def parseRefine(searchLevel,input_dict,paragraph,outputQ):
    refineSearchLevel = ""
    searchDict = {}
    for query, cmd in input_dict.items():
        refineSearchLevel = query
        searchDict[query] = parseRefineSearch(searchLevel+"->"+refineSearchLevel, cmd, paragraph,outputQ)

        if ("refine" in query):
            parseRefine(searchLevel+refineSearchLevel, cmd,paragraph,outputQ)


def parseRegex(cmd,paragraph):
    # print(cmd,paragraph)
    paragraph = "".join(paragraph)
    matches = re.findall(cmd, paragraph)
    return matches

def parseOutput(searchLevel,searchDict,cmd,outputQ):
    keywordList = searchDict[searchLevel]
    for key,value in cmd.items():
        for k in keywordList:
            if(k[0] == key):
                outputQ.put((key,value))
                # print(value)



def parseQuery(input_dict,paragraph,outputQ):
    value = None
    searchDict= {}
    searchLevel = ""
    # print(input_dict)
    # lv1
    for query, cmd in input_dict.items():
        # if re.findall("^.*search.*$", query):
        searchLevel = query
        searchDict[query] = parseSearch(searchLevel,cmd,paragraph,outputQ)

        # if ("otherwise" == query):
        #     # print(searchDict)
        #     if(searchDict[searchLevel] == []):
        #         searchLevel = searchLevel + "(otherwise)"
        #         parseOtherwise(searchLevel,cmd,paragraph,outputQ)

        #     if len(searchDict.keys()):
        #         parseOutput(searchLevel,searchDict,cmd,outputQ)

    return value


def parseOtherwise(searchLevel,input_dict,paragraph,outputQ):
    parseSearch(searchLevel,input_dict,paragraph,outputQ)


def readParagraph(clinical_note_file_name):
    fo = open(clinical_note_file_name , "r")
    lines = str(fo.read().lower().translate(str.maketrans('','',string.punctuation))).split()
    return lines

# outputQ
def parserFile(doc_id,config_file_name,clinical_note_file_name):


    fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())

    paragraph = readParagraph(clinical_note_file_name)
    input_dict = json.load(fo)
    value = parseQuery(input_dict,paragraph,outputQ)

def processDocument(docID,content):


    # fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame( columns=index_tracker.keys())

    paragraph = str(content.lower().translate(str.maketrans('','',string.punctuation))).split()
    # input_dict = json.load(fo)
    # print(input_dict)
    value = parseQuery(input_dict,paragraph,outputQ)


def parser(doc_id,config_file_name,paragraph):
    global docID
    docID = doc_id

    paragraph = str(paragraph.lower().translate(str.maketrans('','',string.punctuation))).split()
    fo = open(config_file_name, 'r')

    outputQ = pd.DataFrame( columns=index_tracker.keys())

    input_dict = json.load(fo)
    parseQuery(input_dict,paragraph,outputQ)

    print(outputQ)
