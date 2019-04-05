import json
import string
import queue
fo = open("test", 'r')
directory = '/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-343.txt'
import re


# modify outputQ, create search dictionary
def parseSearch(key,cmd,paragraph,outputQ):
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
            for k,v in tempdict.items():
                for key in resultList:
                    if (k == key[0]):
                        outputQ.put((k, v))
                        # print(v)
        if ("refine" in cmd):
            parseRefine(key, cmd,  paragraph,outputQ)

    return resultList

def parseRefineSearch(searchlevel,cmd,paragraph,outputQ):
    resultList = []
    counter = 0
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
            for keyword,pointer in resultList:
                tempdict = cmd["output"]
                if pointer - chars_preceeding < 0:
                    temp1 = pointer
                else:
                    temp1 = pointer - chars_preceeding

                if pointer + chars_following > len(paragraph) - 1:
                    temp2 = pointer
                else:
                    temp2 = pointer + chars_following


                for k,v in tempdict.items():
                    k = k.lower().translate(str.maketrans('','',string.punctuation))
                    for key in paragraph[temp1:temp2]:
                        if (k == key):
                            outputQ.put((searchlevel,k, v,pointer))
            if ("refine" in cmd):
                parseRefine(searchlevel, cmd, paragraph, outputQ)
    return resultList


def parseRefine(searchLevel,input_dict,outputQ,paragraph):
    refineSearchLevel = ""
    searchDict = {}
    for query, cmd in input_dict.items():
        if re.findall("^.*search.*$", query):
            # for keyword,pointer in searchDict[searchLevel]:
            refineSearchLevel = query
            searchDict[query] = parseRefineSearch(refineSearchLevel, cmd, paragraph, outputQ)

        if ("refine" in query):
            parseRefine(refineSearchLevel, cmd, paragraph,outputQ)



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
    # lv1
    for query, cmd in input_dict.items():
        if re.findall("^.*search.*$", query):
            searchLevel = query
            searchDict[query] = parseSearch(query,cmd, paragraph,outputQ)
        # if ("output" in query):
        #     if len(searchDict.keys()):
        #         parseOutput(searchLevel,searchDict,cmd,outputQ)

    return value




def readParagraph():
    fo = open(directory , "r")
    lines = str(fo.read().lower().translate(str.maketrans('','',string.punctuation))).split()
    return lines

# outputQ
def parser():
    # value = {}
    outputQ = queue.Queue()
    paragraph = readParagraph()
    input_dict = json.load(fo)
    value = parseQuery(input_dict,paragraph,outputQ)
    # print(outputQ.qsize())
    for i in range (0,outputQ.qsize()):
        print(outputQ.get())


parser()
