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
stats_output_csv = ""

index_tracker = {}
input_dict = {}
df = pd.DataFrame(columns=index_tracker.keys())
column_name = []
stats_dict = {}
import yaml
import os
import pandas as pd
import json
from DataPointConfig import DataPointConfig


# test
# original
# directory = '/Users/yuanpan/Documents/NLP_project/input/mtsamples/'

config_directory = 'stats_config.txt'

# statistical analysis


def count_frequency(word, surrouding_words_frequency, distance):
    if len(surrouding_words_frequency.loc[(surrouding_words_frequency['word'] == word)].values) == 0:
        temp = pd.DataFrame([[word, 1, distance]], columns=['word', 'frequency', 'total_distance'])
        result = pd.concat([surrouding_words_frequency, temp], ignore_index=True, sort=False)
    else:
        surrouding_words_frequency.loc[surrouding_words_frequency['word'] == word, 'frequency'] = \
        surrouding_words_frequency.loc[(surrouding_words_frequency['word'] == word)]["frequency"].values[0] + 1
        surrouding_words_frequency.loc[surrouding_words_frequency['word'] == word, 'total_distance'] = \
        surrouding_words_frequency.loc[(surrouding_words_frequency['word'] == word)]["total_distance"].values[
            0] + distance

        result = surrouding_words_frequency
    return result


# add a switch case later for filters
def process_keywords(wordlist, index, surrouding_words_frequency, config):
    for i in range(-config.self_window_size, config.self_window_size):
        # fix the out of range problem
        if (i != 0 and wordlist[index + i] != "" and wordlist[index + i] not in config.self_ignore_wordlist):
            surrouding_words_frequency = count_frequency(wordlist[index + i], surrouding_words_frequency, abs(i))
    return surrouding_words_frequency


def compare_word_with_dp(word, config):
    #     basic comparason for single word
    if (word == config.self_dp_name):
        return 1
    return 0


def extract_surrouding_words(tokens, surrouding_words_frequency, config):
    index = 0
    for word in tokens:
        if (compare_word_with_dp(word, config) == 1):
            surrouding_words_frequency = process_keywords(tokens, index, surrouding_words_frequency, config)
        index += 1
    return surrouding_words_frequency


# print here
def analyse_dp(surrouding_words_frequency, config, tokens):
    surrouding_words_frequency = extract_surrouding_words(tokens, surrouding_words_frequency, config)
    # return surrouding_words_frequency
    surrouding_words_frequency['average_distance'] = surrouding_words_frequency['total_distance'] / \
                                                     surrouding_words_frequency['frequency']
    # print(surrouding_words_frequency.nlargest(config.self_present_row_limit, 'frequency'))
    return surrouding_words_frequency


#     write an output file to the output folder


def read_config(token):
    # datapoints =[]

    fo = open(config_directory, 'r')
    data = json.loads(fo.read())
    datapoint = DataPointConfig(dp_name=token, window_size=data['window_size'],
                                select_numerical=data['select_numerical'], present_row_limit=data['present_row_limit'],
                                ignore_wordlist=data['ignore_wordlist'])
    global stats_output_csv
    stats_output_csv = data['path']
    return datapoint


# initialise
def find_column_name(input_dict, column_name):
    if type(input_dict) == dict:
        for key, value in input_dict.items():
            if type(value) == dict:
                if "find" in value.keys():
                    column_name.append(key)
            if (key == "output"):
                for i in value.keys():
                    column_name.append(i)
            # print(key,column_name)
            find_column_name(value, column_name)


def init(csv_file_name, config_file_name):
    global stats_dict
    global stats_output_csv
    global csv_file
    csv_file = csv_file_name
    fo = open(config_file_name, 'r')
    global input_dict
    # input_dict = json.load(fo)
    input_dict = yaml.safe_load(fo)
    # print(input_dict)
    global column_name
    column_name = []
    find_column_name(input_dict, column_name)
    # print("columnname"+ str(column_name))
    row = ["doc_id"]
    column_name.append("sentence")
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
    for k, v in index_tracker.items():
        index_tracker[k] = 0
        outputQ.drop(outputQ.index, inplace=True)


def flush(outputQ):
    outputQ.to_csv("test", mode='a', header=False, index=False)
    global df
    df = outputQ.dropna(subset=[outputQ.columns[-1]])
    df.to_csv(csv_file, mode='a', header=False, index=False)
    clear(outputQ)


def isNaturalLanguage(str):
    str = str.split(" ")
    str = "".join((str))
    valid = re.match('^[\w-]+$', str) is not None
    return valid


def printlevel(level, prefix, content, tokens):
    level = column_name.index(level)
    str = ""
    for i in range(0, level):
        str = str + "\t\t\t"
    print(str + prefix + ": " + content)

    if (prefix == "token"):
        config = read_config(content)
        if content in stats_dict.keys():
            stats_dict[content] = analyse_dp(stats_dict[content], config, tokens=tokens)
        else:
            stats_dict[content] = analyse_dp(pd.DataFrame({"word": [""], "frequency": [0], "total_distance": [0]}),
                                             config, tokens)

        write_stats_output_to_csv()


def write_stats_output_to_csv():
    fo = open(stats_output_csv, "w")
    fo.write('')
    fo.close()

    for token, df in stats_dict.items():
        fo = open(stats_output_csv, "a")
        fo.write(token + '\n')
        fo.close()

        # 关闭文件
        df.to_csv(stats_output_csv, mode='a', index=False)
        fo = open(stats_output_csv, "a")
        fo.write("\n\n\n")
        fo.close()

    # with open(stats_output_csv, 'w') as csvfile:
    #     filewriter = csv.writer(csvfile, delimiter=',',
    #                             quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     filewriter.writerow(token)


def parseSearch(searchlevel, cmd, tokens, outputQ, pointer, level):
    level = searchlevel
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
            if pointer + tokens_following > len(tokens) - 1:
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
                                resultList.append((i, counter))
                                index = index_tracker[searchlevel]
                                put_value_into_outputQ(outputQ, index, searchlevel, i)
                                index += 1
                                index_tracker[searchlevel] = index
                                printlevel(searchlevel, "token", str(i), tokens)
                                parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level)

                    else:
                        if (" " not in tokenlist):
                            for i in tokens[temp1:temp2]:
                                counter += 1
                                if i == tokenlist.lower():
                                    resultList.append((i, counter))
                                    # print("token: " + i)
                                    printlevel(searchlevel, "token", i, tokens)
                                    index = index_tracker[searchlevel]
                                    put_value_into_outputQ(outputQ, index, searchlevel, i)
                                    index += 1
                                    index_tracker[searchlevel] = index
                                    parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level)
                        else:
                            length = len(tokenlist.split(" "))

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
                                        printlevel(searchlevel, "token", tokenlist, tokens)
                                        index = index_tracker[searchlevel]
                                        put_value_into_outputQ(outputQ, index, searchlevel, tokenlist)
                                        index += 1
                                        index_tracker[searchlevel] = index
                                        parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level)


                # case 2 token is a list of token
                else:
                    for token in tokenlist:
                        counter = 0
                        if isNaturalLanguage(token) is False:
                            res = re.findall(token, " ".join(tokens[temp1:temp2]))
                            if res != None:
                                for i in res:
                                    resultList.append((i, counter))
                                    index = index_tracker[searchlevel]
                                    put_value_into_outputQ(outputQ, index, searchlevel, i)
                                    index += 1
                                    index_tracker[searchlevel] = index
                                    printlevel(searchlevel, "token", str(i), tokens)
                                    parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level)



                        else:
                            if (" " not in token):
                                for i in tokens[temp1:temp2]:
                                    counter += 1
                                    if i == token.lower():
                                        resultList.append((i, counter))
                                        printlevel(searchlevel, "token", i, tokens)
                                        index = index_tracker[searchlevel]
                                        put_value_into_outputQ(outputQ, index, searchlevel, i)
                                        index += 1
                                        index_tracker[searchlevel] = index
                                        parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level)

                            else:
                                length = len(token.split(" "))
                                for i in tokens[temp1:temp2]:
                                    counter += 1
                                    if i == token.split(" ")[0].lower():
                                        flag = 0
                                        for j in range(1, length):
                                            if tokens[temp1 + counter + j - 1] == token.split(" ")[j].lower():
                                                flag = 1
                                                continue
                                            else:
                                                flag = 0
                                                break
                                        if flag == 1:
                                            resultList.append((token, counter))
                                            printlevel(searchlevel, "token", token, tokens)
                                            index = index_tracker[searchlevel]
                                            put_value_into_outputQ(outputQ, index, searchlevel, token)
                                            index += 1
                                            index_tracker[searchlevel] = index
                                            parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level)
    # if resultList == []:
    #     outputQ.put((searchlevel,'not found','not found',0))

    return resultList


def parseRefine(cmd, resultList, tokens, outputQ, pointer, temp1, temp2, level):
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
            if k == level:
                index = index_tracker[k]
                index -= 1
                index -= 1
                put_value_into_outputQ(outputQ, index, k, v)
                index += 1
                pd.options.display.width = 0

    if ("refine" in cmd.keys()):

        for key in cmd["refine"].keys():
            # print(level)
            printlevel(key, "search", key, tokens)
            parseSearch(key, cmd["refine"][key], tokens, outputQ, pointer + resultList[-1][1], level)

    if "action" in cmd.keys():
        if "flush" in cmd["action"]:
            index = index_tracker['sentence']
            if(pointer==0):
                print(resultList)
                pointer = sum([i[1] for i in resultList])
            put_value_into_outputQ(outputQ, index, 'sentence', " ".join(tokens[pointer - 20:pointer + 20]))
            flush(outputQ)
        if "clear" in cmd["action"]:
            clear(outputQ)


def put_value_into_outputQ(outputQ, index, k, v):
    if outputQ.empty is True and df.empty is False:
        outputQ.loc[0] = df.loc[0]
    if "," in v:
        v = "\"" + v + "\""
    outputQ.loc[index, k] = v
    outputQ.loc[index, "doc_id"] = docID


def parseRegex(cmd, tokens):
    # print(cmd,tokens)
    tokens = "".join(tokens)
    matches = re.findall(cmd, tokens)
    return matches


def parseOutput(searchLevel, searchDict, cmd, outputQ):
    keywordList = searchDict[searchLevel]
    for key, value in cmd.items():
        for k in keywordList:
            if (k[0] == key):
                outputQ.put((key, value))
                # print(value)


def parseQuery(input_dict, tokens, outputQ):
    value = None
    searchDict = {}
    searchLevel = ""
    # print(input_dict)
    # lv1
    for query, cmd in input_dict.items():
        searchLevel = query
        print("search: " + searchLevel)
        searchDict[query] = parseSearch(searchLevel, cmd, tokens, outputQ, 0, 0)
        # if ("otherwise" == query):
        #     # print(searchDict)
        #     if(searchDict[searchLevel] == []):
        #         searchLevel = searchLevel + "(otherwise)"
        #         parseOtherwise(searchLevel,cmd,tokens,outputQ)

        #     if len(searchDict.keys()):
        #        parseOutput(searchLevel,searchDict,cmd,outputQ)
    return value


def parseOtherwise(searchLevel, input_dict, tokens, outputQ):
    parseSearch(searchLevel, input_dict, tokens, outputQ)


def readtokens(clinical_note_file_name):
    fo = open(clinical_note_file_name, "r")
    tokens = [word.lower() for word in nltk.word_tokenize(fo.read())]
    return tokens


# outputQ
def parserFile(doc_id, clinical_note_file_name):
    global docID
    docID = doc_id
    outputQ = pd.DataFrame(columns=index_tracker.keys())
    tokens = readtokens(clinical_note_file_name)
    parseQuery(input_dict, tokens, outputQ)


def processDocument(docID, content):
    # fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame(columns=index_tracker.keys())
    tokens = str(content.lower().translate(str.maketrans('', '', string.punctuation))).split()
    # input_dict = json.load(fo)
    # print(input_dict)
    parseQuery(input_dict, tokens, outputQ)


def parser(doc_id, tokens):
    docID = doc_id
    # tokens = str(tokens.lower().translate(str.maketrans('','',string.punctuation))).split()
    # fo = open(config_file_name, 'r')
    outputQ = pd.DataFrame(columns=index_tracker.keys())
    # input_dict = json.load(fo)
    parseQuery(input_dict, tokens, outputQ)
    # print(outputQ)

