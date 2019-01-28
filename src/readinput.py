import os
import pandas as pd
import json
from DataPointConfig import DataPointConfig

# test
# directory = '/Users/yuanpan/Documents/NLP_project/input/mttest/'
# original
directory = '/Users/yuanpan/Documents/NLP_project/input/mtsamples/'

config_directory = '/Users/yuanpan/Documents/NLP_project/input/config/'

# config
dp = "age"
window = 10
# global surrouding_words_frequency
# surrouding_words_frequency = pd.DataFrame({"word": [""], "frequency": [0]})


def count_frequency(word,surrouding_words_frequency):
    if len(surrouding_words_frequency.loc[(surrouding_words_frequency['word']== word)].values)==0:
        temp = pd.DataFrame([[word,1]], columns=['word', 'frequency'])
        result = pd.concat([surrouding_words_frequency, temp], ignore_index=True, sort=False)
    else:
        surrouding_words_frequency.loc[surrouding_words_frequency['word']==word, 'frequency'] = surrouding_words_frequency.loc[(surrouding_words_frequency['word'] == word)]["frequency"].values[0]+1

        result = surrouding_words_frequency
    return result

# add a switch case later for filters
def process_keywords(wordlist,index,surrouding_words_frequency,config):
    for i in range (-config.self_window_size,config.self_window_size):
        if(i!=0 and wordlist[index+i]!= "" and wordlist[index+i] not in config.self_ignore_wordlist):
            surrouding_words_frequency = count_frequency(wordlist[index+i],surrouding_words_frequency)
    return surrouding_words_frequency


def compare_word_with_dp(word,config):
#     basic comparason for single word
    if(word == config.self_dp_name):
        return 1
    return 0


def extract_surrouding_words(fo,surrouding_words_frequency,config):
    wordlist = str(fo.read()).split(' ')
    index = 0
    for word in wordlist:
        if(compare_word_with_dp(word,config)==1):
            surrouding_words_frequency = process_keywords(wordlist,index,surrouding_words_frequency,config)
        index += 1
    return surrouding_words_frequency


def open_file(fileName,surrouding_words_frequency,config):
    fo = open(directory+fileName, "rb")
    return extract_surrouding_words(fo,surrouding_words_frequency,config)


def analyse_dp(surrouding_words_frequency,config):
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            surrouding_words_frequency = open_file(filename,surrouding_words_frequency,config)
            continue
        else:
            continue
    # return surrouding_words_frequency
    print(surrouding_words_frequency.nlargest(config.self_present_row_limit, 'frequency'))


def analyse_all_dp(configs):
    for config in configs:
        analyse_dp(pd.DataFrame({"word": [""], "frequency": [0]}), config)

def read_config():
    datapoints =[]
    for filename in os.listdir(config_directory):
        if filename.endswith(".txt"):
            fo = open(config_directory+filename,'r')
            data = json.loads(fo.read())
            datapoint = DataPointConfig(dp_name=data['dp_name'],window_size=data['window_size'],select_numerical=data['select_numerical'],present_row_limit=data['present_row_limit'],ignore_wordlist=data['ignore_wordlist'])
            datapoints.append(datapoint)
    return datapoints


configs = read_config()
analyse_all_dp(configs)

# print(frequency_df.nlargest(50, 'frequency'))
