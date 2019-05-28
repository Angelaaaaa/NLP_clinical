directory = '/Users/yuanpan/Documents/NLP_project/input/mttest/mtsamples-type-3-sample-343.txt'
file_name = "test"
import json
import csv

index_tracker = {}


def find_column_name(input_dict,column_name):
    if type(input_dict) == dict:
        for key,value in input_dict.items():
            if(key == "output"):
                column_name.append(value)
            # print(key,column_name)
            find_column_name(value,column_name)


def init(csv_file_name,config_file_name):
    fo = open(config_file_name, 'r')
    input_dict = json.load(fo)
    column_name= []
    find_column_name(input_dict,column_name)
    row = []
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

    return row
    # csvfile.close()

init(csv_file_name = "1.csv",config_file_name="test")