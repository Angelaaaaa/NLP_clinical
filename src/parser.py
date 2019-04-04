import json
import string
import queue
fo = open("test", 'r')
directory = '/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-343.txt'
import re
#
# def parseFind(cmd,paragraph):
#     pointer = []
#     counter = 0
#     if type(cmd) == dict:
#         for key, item in cmd.items():
#             pointer.append(parseQuery(key, item,paragraph))
#     else:
#         for i in paragraph:
#             counter += 1
#             if i in [i.lower() for i in cmd]:
#                 pointer.append(counter)
#     return pointer

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

    return resultList

def parseRefineSearch(key,cmd,paragraph,outputQ):
    resultList = []
    counter = 0
    refineParagraph = (0,len(paragraph)-1,paragraph)
    # assume search defo has attribute "find" and "output"

    if type(cmd) == dict:
        if ("window" in cmd.keys()):
            refineParagraph = (cmd["window"]["chars_preceeding"], cmd["window"]["chars_following"], paragraph)
        if "find" in cmd.keys():
            if "token" in cmd["find"].keys():
                for i in refineParagraph[2][refineParagraph[0]:refineParagraph[1]]:
                    counter += 1
                    if i in [i.lower() for i in cmd["find"]["token"]]:
                        resultList.append((i,counter))
        if"output" in cmd.keys():
            tempdict = cmd["output"]
            for k,v in tempdict.items():
                for key in resultList:
                    if (k == key[0]):
                        outputQ.put((k, v))

    return resultList


def parseRefine(searchLevel,searchDict,input_dict,outputQ,paragraph):
    refineSearchLevel = ""
    for query, cmd in input_dict.items():
        if re.findall("^.*search.*$", query):
            refineSearchLevel = query
            searchDict[query] = parseRefineSearch(query, cmd, paragraph, outputQ)

        if ("refine" in query):
            parseRefine(searchLevel, searchDict, cmd, outputQ)



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
        if ("refine" in query):
            parseRefine(searchLevel,searchDict,cmd,outputQ,paragraph)
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
    print(outputQ.qsize())


parser()
